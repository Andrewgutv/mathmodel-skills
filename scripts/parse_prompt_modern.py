from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import fitz
import pdfplumber
from docx import Document
from pypdf import PdfReader

try:
    from rapidocr_onnxruntime import RapidOCR
except Exception:  # pragma: no cover - optional dependency
    RapidOCR = None


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff"}
MARKDOWN_SUFFIXES = {".md", ".markdown"}
SUPPORTED_PROMPT_SUFFIXES = (".pdf", ".docx", ".md", ".markdown", *sorted(IMAGE_SUFFIXES))


@dataclass
class PromptExtractionResult:
    text: str
    status: str
    source_kind: str
    detail: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Parse a math modeling prompt folder into structured project notes."
    )
    parser.add_argument("project_dir", help="Project root directory")
    parser.add_argument(
        "--prompt",
        default=None,
        help="Optional explicit prompt path. If omitted, the script will search the project root.",
    )
    return parser.parse_args()


def find_prompt_source(project_dir: Path, explicit_prompt: str | None) -> Path:
    if explicit_prompt:
        prompt = Path(explicit_prompt).expanduser().resolve()
        if not prompt.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt}")
        validate_prompt_suffix(prompt)
        return prompt

    candidates = [
        path
        for path in sorted(project_dir.iterdir())
        if path.is_file() and path.suffix.lower() in SUPPORTED_PROMPT_SUFFIXES
    ]
    if not candidates:
        supported = ", ".join(SUPPORTED_PROMPT_SUFFIXES)
        raise FileNotFoundError(
            f"No supported prompt file found under: {project_dir}. Supported suffixes: {supported}"
        )
    return sorted(candidates, key=prompt_candidate_priority)[0]


def validate_prompt_suffix(prompt_path: Path) -> None:
    suffix = prompt_path.suffix.lower()
    if suffix not in SUPPORTED_PROMPT_SUFFIXES:
        supported = ", ".join(SUPPORTED_PROMPT_SUFFIXES)
        raise ValueError(
            f"Unsupported prompt file type: {prompt_path.suffix or '<none>'}. Supported suffixes: {supported}"
        )


def prompt_candidate_priority(path: Path) -> tuple[int, str]:
    name = path.name.lower()
    stem = path.stem.lower()

    if stem in {"prompt", "题面"}:
        return (0, name)
    if "prompt" in stem or "题面" in stem:
        return (1, name)
    if "expectation" in stem or "说明" in stem or "readme" in stem:
        return (9, name)
    return (5, name)


def extract_prompt_text(prompt_path: Path) -> PromptExtractionResult:
    suffix = prompt_path.suffix.lower()
    if suffix == ".pdf":
        return extract_pdf_text(prompt_path)
    if suffix == ".docx":
        return extract_docx_text(prompt_path)
    if suffix in MARKDOWN_SUFFIXES:
        return extract_markdown_text(prompt_path)
    if suffix in IMAGE_SUFFIXES:
        return extract_image_text(prompt_path)
    raise ValueError(f"Unsupported prompt file type: {prompt_path.suffix}")


def extract_pdf_text(prompt_pdf: Path) -> PromptExtractionResult:
    text_parts: list[str] = []
    extraction_errors: list[str] = []

    try:
        with pdfplumber.open(prompt_pdf) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
    except Exception as exc:
        extraction_errors.append(f"pdfplumber failed: {exc}")

    text = "\n".join(part for part in text_parts if part).strip()
    if text:
        return PromptExtractionResult(
            text=text,
            status="text_extracted",
            source_kind="pdf",
            detail="Extracted text directly from PDF.",
        )

    text_parts = []
    try:
        reader = PdfReader(str(prompt_pdf))
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    except Exception as exc:
        extraction_errors.append(f"pypdf failed: {exc}")

    text = "\n".join(part for part in text_parts if part).strip()
    if text:
        return PromptExtractionResult(
            text=text,
            status="text_extracted",
            source_kind="pdf",
            detail="Extracted text from PDF using fallback reader.",
        )

    ocr_result = extract_pdf_text_with_ocr(prompt_pdf)
    if extraction_errors:
        details = extraction_errors.copy()
        if ocr_result.detail:
            details.append(ocr_result.detail)
        ocr_result.detail = " | ".join(details)
    return ocr_result


def extract_docx_text(prompt_docx: Path) -> PromptExtractionResult:
    try:
        document = Document(prompt_docx)
    except Exception as exc:
        raise RuntimeError(f"Failed to read DOCX prompt: {prompt_docx} ({exc})") from exc

    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    text = "\n".join(paragraphs).strip()
    if not text:
        return PromptExtractionResult(
            text="",
            status="prompt_empty",
            source_kind="docx",
            detail="DOCX prompt contains no readable paragraph text.",
        )
    return PromptExtractionResult(
        text=text,
        status="text_extracted",
        source_kind="docx",
        detail="Extracted text from DOCX prompt.",
    )


def extract_markdown_text(prompt_markdown: Path) -> PromptExtractionResult:
    text = prompt_markdown.read_text(encoding="utf-8").strip()
    if not text:
        return PromptExtractionResult(
            text="",
            status="prompt_empty",
            source_kind="markdown",
            detail="Markdown prompt is empty.",
        )
    return PromptExtractionResult(
        text=text,
        status="text_extracted",
        source_kind="markdown",
        detail="Extracted text from Markdown prompt.",
    )


def extract_image_text(prompt_image: Path) -> PromptExtractionResult:
    try:
        image_bytes = prompt_image.read_bytes()
    except OSError as exc:
        raise RuntimeError(f"Failed to read image prompt: {prompt_image} ({exc})") from exc
    return run_ocr([image_bytes], source_kind="image", detail_prefix=f"Image prompt: {prompt_image.name}")


def extract_pdf_text_with_ocr(prompt_pdf: Path) -> PromptExtractionResult:
    pdf = fitz.open(str(prompt_pdf))
    try:
        page_images: list[bytes] = []
        for page_index in range(pdf.page_count):
            page = pdf.load_page(page_index)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            page_images.append(pix.tobytes("png"))
    finally:
        pdf.close()
    return run_ocr(page_images, source_kind="pdf", detail_prefix=f"OCR fallback for PDF: {prompt_pdf.name}")


def run_ocr(image_bytes_list: list[bytes], source_kind: str, detail_prefix: str) -> PromptExtractionResult:
    if RapidOCR is None:
        return PromptExtractionResult(
            text="",
            status="ocr_unavailable",
            source_kind=source_kind,
            detail=f"{detail_prefix}. OCR dependency rapidocr_onnxruntime is unavailable.",
        )

    try:
        engine = RapidOCR()
    except Exception as exc:
        return PromptExtractionResult(
            text="",
            status="ocr_failed",
            source_kind=source_kind,
            detail=f"{detail_prefix}. Failed to initialize OCR engine: {exc}",
        )

    text_parts: list[str] = []
    try:
        for image_bytes in image_bytes_list:
            ocr_result, _ = engine(image_bytes)
            if not ocr_result:
                continue
            page_text = "\n".join(
                item[1] for item in ocr_result if len(item) > 1 and isinstance(item[1], str) and item[1].strip()
            )
            if page_text.strip():
                text_parts.append(page_text)
    except Exception as exc:
        return PromptExtractionResult(
            text="",
            status="ocr_failed",
            source_kind=source_kind,
            detail=f"{detail_prefix}. OCR execution failed: {exc}",
        )

    text = "\n".join(text_parts).strip()
    if not text:
        return PromptExtractionResult(
            text="",
            status="ocr_failed",
            source_kind=source_kind,
            detail=f"{detail_prefix}. OCR completed but produced no readable text.",
        )
    return PromptExtractionResult(
        text=text,
        status="ocr_used",
        source_kind=source_kind,
        detail=f"{detail_prefix}. OCR successfully extracted text.",
    )


def inventory_attachments(project_dir: Path, prompt_source: Path) -> list[dict[str, str]]:
    attachments: list[dict[str, str]] = []
    for path in sorted(project_dir.rglob("*")):
        if path.is_dir():
            continue
        if path.resolve() == prompt_source.resolve():
            continue
        rel = path.relative_to(project_dir)
        attachments.append(
            {
                "文件名": str(rel).replace("\\", "/"),
                "类型": path.suffix.lower().lstrip(".") or "unknown",
                "来源": "题目目录附件",
                "用途": "待判断",
                "预处理方式": "待判断",
            }
        )
    return attachments


def extract_question_blocks(text: str) -> list[tuple[str, str]]:
    numbered_blocks = extract_numbered_question_list(text)
    if numbered_blocks:
        return numbered_blocks

    matches = list(re.finditer(r"(问题\s*[一二三四五六七八九十\d]+)", text))
    if not matches:
        return []

    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        title = normalize_question_label(match.group(1))
        start = match.start()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        block_text = text[start:end].strip()
        blocks.append((title, block_text))
    return blocks


def normalize_question_label(raw: str) -> str:
    raw = re.sub(r"\s+", "", raw)
    replacements = {
        "问题一": "问题1",
        "问题二": "问题2",
        "问题三": "问题3",
        "问题四": "问题4",
        "问题五": "问题5",
        "问题六": "问题6",
        "问题七": "问题7",
        "问题八": "问题8",
        "问题九": "问题9",
        "问题十": "问题10",
    }
    for source, target in replacements.items():
        raw = raw.replace(source, target)
    return raw


def extract_numbered_question_list(text: str) -> list[tuple[str, str]]:
    body = normalize_question_body(text)
    pattern = re.compile(r"(?m)(?:^|\n)\s*(\d+)\s*[\.．、]\s*")
    matches = list(pattern.finditer(body))
    if not matches:
        return []

    blocks: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        qid = match.group(1)
        block_start = match.start()
        block_end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        block_text = body[block_start:block_end].strip()
        block_text = re.split(r"同学们请注意[:：]", block_text)[0].strip()
        block_text = re.sub(r"\s+", " ", block_text)
        blocks.append((f"问题{qid}", block_text))
    return blocks


def normalize_question_body(text: str) -> str:
    start_match = re.search(r"(?:回答以下问题|探讨以下问题|建立数学模型解决以下问题)[:：]?", text)
    if start_match:
        start = start_match.end()
    else:
        first_question_match = re.search(r"(?:^|\n)\s*1\s*[\.．、]\s*", text)
        start = first_question_match.start() if first_question_match else 0

    tail = text[start:]
    end_markers = [
        r"同学们请注意[:：]",
        r"数学建模经验分享",
        r"（赵斌老师总结）",
    ]
    end_positions = []
    for marker in end_markers:
        match = re.search(marker, tail)
        if match:
            end_positions.append(match.start())
    end = min(end_positions) if end_positions else len(tail)
    return tail[:end].strip()


def summarize_prompt(text: str, max_chars: int = 600) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[:max_chars] + ("..." if len(compact) > max_chars else "")


def detect_delivery_constraints(text: str) -> list[str]:
    constraints: list[str] = []
    delivery_match = re.search(r"同学们请注意[:：](.*)$", text, flags=re.DOTALL)
    if not delivery_match:
        return constraints

    delivery_text = delivery_match.group(1)
    for line in delivery_text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if not line:
            continue
        if any(key in line for key in ["提交", "PDF", "DOCX", "代码", "支撑材料", "邮件", "压缩", "成绩"]):
            constraints.append(line)
    return constraints[:10]


def detect_table_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = line.strip()
        if re.match(r"^表\d+", line):
            lines.append(line)
    return lines


def detect_attachment_lines(text: str) -> list[str]:
    lines = []
    for line in text.splitlines():
        line = re.sub(r"\s+", " ", line).strip()
        if "附件" in line or "Pic" in line:
            lines.append(line)
    return lines[:12]


def extract_attachment_refs(question_text: str) -> list[str]:
    refs = re.findall(r"Pic\d+\.(?:jpg|png|jpeg|bmp|gif)", question_text, flags=re.IGNORECASE)
    seen: list[str] = []
    for ref in refs:
        if ref not in seen:
            seen.append(ref)
    return seen


def infer_known_inputs(question_text: str) -> list[str]:
    inputs: list[str] = []
    refs = extract_attachment_refs(question_text)
    if refs:
        inputs.append("题面指定的原始图片附件：" + "、".join(refs))
    if "表" in question_text:
        inputs.append("题面中的表格数据")
    if "经纬度" in question_text:
        inputs.append("题面或附件中的经纬度数据")
    return inputs or ["待结合题面与附件进一步补充"]


def infer_constraints(question_text: str) -> list[str]:
    constraints: list[str] = []
    for pattern in [
        r"\d+(?:\.\d+)?\s*km",
        r"\d+(?:\.\d+)?\s*m",
        r"\d+(?:\.\d+)?\s*小时",
        r"\d+(?:\.\d+)?\s*个月",
        r"\d+(?:\.\d+)?\s*年前",
    ]:
        for match in re.findall(pattern, question_text):
            constraints.append(f"题面显式量纲约束：{match}")
    if "不考虑地形起伏与中途停留" in question_text:
        constraints.append("忽略地形起伏与中途停留")
    if "原图见附件" in question_text:
        constraints.append("必须基于题面指定原图估算")
    if "请通过查找" in question_text:
        constraints.append("允许并要求补充查找外部公开数据")
    return constraints or ["待从题面中补充约束"]


def infer_evaluation_standard(question_text: str) -> str:
    if "估算" in question_text or "计算" in question_text:
        return "结果应数值合理、量纲一致，并与题面已知尺度或条件相容。"
    if "距离" in question_text:
        return "结果应与公开位置数据和距离计算过程保持一致。"
    return "待结合题面和解题目标进一步判断。"


def infer_attachment_dependency(question_text: str) -> str:
    refs = extract_attachment_refs(question_text)
    if refs:
        return "必需附件：" + "、".join(refs)
    if "表" in question_text:
        return "依赖题面表格"
    return "待判断"


def infer_output_target(question_text: str) -> str:
    if "估算" in question_text:
        return "需要估算目标对象的数值或几何量。"
    if "计算" in question_text:
        return "需要根据已知条件计算目标量。"
    if "给出" in question_text:
        return "需要给出明确的数值、方案或判断结果。"
    if "设计" in question_text:
        return "需要设计一个可执行方案。"
    if "预测" in question_text:
        return "需要预测未来或未知量。"
    return "待根据题面进一步细化。"


def infer_scope_boundary(question_text: str) -> str:
    if "估算" in question_text:
        return "本问边界：重点在估算目标量，不要求构建过度复杂的长期预测模型。"
    if "计算" in question_text:
        return "本问边界：重点在按给定条件完成计算，不要求额外扩展到无关优化任务。"
    if "给出" in question_text:
        return "本问边界：重点在明确回答题目要求，不要求展开与目标无关的附加分析。"
    return "本问边界：待结合完整题意进一步判断。"


def infer_question_type(question_text: str) -> str:
    if any(key in question_text for key in ["原图见附件", "影像图", "图片", "直径", "表面积", "高度"]):
        return "estimation"
    if any(key in question_text for key in ["微分方程", "动力学模型", "多智能体", "博弈"]):
        return "simulation"
    if any(key in question_text for key in ["回归模型", "概率分布", "预测"]):
        return "prediction"
    if any(key in question_text for key in ["评价", "排序", "评分"]):
        return "evaluation"
    if any(key in question_text for key in ["最优", "最小", "最大", "调度", "规划"]):
        return "optimization"
    if any(key in question_text for key in ["估算", "计算", "距离", "表面积", "高度", "直径"]):
        return "estimation"
    return "unknown"


def update_data_inventory(project_dir: Path, attachments: list[dict[str, str]]) -> None:
    path = project_dir / "数据" / "数据说明表.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# 数据说明表", "", "| 文件名 | 类型 | 来源 | 用途 | 预处理方式 |", "|---|---|---|---|---|"]
    if attachments:
        for row in attachments:
            lines.append(
                f"| {row['文件名']} | {row['类型']} | {row['来源']} | {row['用途']} | {row['预处理方式']} |"
            )
    else:
        lines.append("| 无附件 | - | - | - | - |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def upsert_section(path: Path, marker: str, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("", encoding="utf-8")
    text = path.read_text(encoding="utf-8")
    start_marker = f"<!-- {marker}_START -->"
    end_marker = f"<!-- {marker}_END -->"
    block = f"{start_marker}\n{content.rstrip()}\n{end_marker}"
    if start_marker in text and end_marker in text:
        updated = re.sub(
            rf"{re.escape(start_marker)}.*?{re.escape(end_marker)}",
            block,
            text,
            flags=re.DOTALL,
        )
    else:
        updated = text.rstrip() + "\n\n" + block + "\n"
    path.write_text(updated, encoding="utf-8")


def build_plan_section(
    prompt_source: Path,
    extraction_result: PromptExtractionResult,
    question_blocks: list[tuple[str, str]],
) -> str:
    prompt_text = extraction_result.text
    table_lines = detect_table_lines(prompt_text)
    attachment_lines = detect_attachment_lines(prompt_text)
    delivery_constraints = detect_delivery_constraints(prompt_text)
    lines = [
        "## 题面结构化解析",
        "",
        f"- 题面文件：`{prompt_source.name}`",
        f"- 题面类型：`{prompt_source.suffix.lower()}`",
        f"- 解析状态：`{extraction_result.status}`",
        f"- 解析说明：{extraction_result.detail or '无'}",
        f"- 题面摘要：{summarize_prompt(prompt_text)}",
        f"- 识别到的问题数量：{len(question_blocks)}",
        "",
    ]
    if table_lines:
        lines.append("### 表格线索")
        lines.extend(f"- {line}" for line in table_lines)
        lines.append("")
    if attachment_lines:
        lines.append("### 附件说明线索")
        lines.extend(f"- {line}" for line in attachment_lines)
        lines.append("")
    if delivery_constraints:
        lines.append("### 交付约束")
        lines.extend(f"- {line}" for line in delivery_constraints)
        lines.append("")

    if not question_blocks:
        lines.extend(
            [
                "### 未识别到结构化问题",
                "- 当前题面文本已抽取，但未自动匹配到标准问题结构。",
                "- 需要人工补充子问题拆分后再进入 solve 阶段。",
                "",
            ]
        )
        return "\n".join(lines)

    for label, block in question_blocks:
        lines.extend(
            [
                f"### {label}",
                "",
                "#### 原题要求",
                block,
                "",
                "#### 输出目标",
                infer_output_target(block),
                "",
                "#### 已知输入",
                "\n".join(f"- {item}" for item in infer_known_inputs(block)),
                "",
                "#### 约束条件",
                "\n".join(f"- {item}" for item in infer_constraints(block)),
                "",
                "#### 评价标准",
                infer_evaluation_standard(block),
                "",
                "#### 每问边界",
                infer_scope_boundary(block),
                "",
                "#### 附件依赖",
                infer_attachment_dependency(block),
                "",
                "#### 初步题型判断",
                infer_question_type(block),
                "",
            ]
        )
    return "\n".join(lines)


def build_solution_thought_section(question_blocks: list[tuple[str, str]]) -> str:
    lines = ["## 题面问题卡片", ""]
    if not question_blocks:
        lines.extend(
            [
                "## 待人工补充",
                "",
                "### 当前状态",
                "已抽取题面文本，但未自动识别到标准问题结构。",
                "",
                "### 下一步",
                "需要人工补充子问题拆分，再决定模型与代码结构。",
                "",
            ]
        )
        return "\n".join(lines)

    for label, block in question_blocks:
        lines.extend(
            [
                f"## {label}",
                "",
                "### 原题要求",
                block,
                "",
                "### 输出目标",
                infer_output_target(block),
                "",
                "### 已知输入",
                "\n".join(f"- {item}" for item in infer_known_inputs(block)),
                "",
                "### 约束条件",
                "\n".join(f"- {item}" for item in infer_constraints(block)),
                "",
                "### 评价标准",
                infer_evaluation_standard(block),
                "",
                "### 每问边界",
                infer_scope_boundary(block),
                "",
                "### 附件依赖",
                infer_attachment_dependency(block),
                "",
                "### 初步题型判断",
                infer_question_type(block),
                "",
            ]
        )
    return "\n".join(lines)


def build_mapping_table(question_blocks: list[tuple[str, str]]) -> str:
    lines = [
        "# 问题-方法对照表",
        "",
        "| 问题 | 题目要求 | 判定题型 | 选用方法 | 不选的方法 | 对应代码 | 证据文件 | 支撑图表 | 最终结论句 |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    if question_blocks:
        for label, block in question_blocks:
            lines.append(
                f"| {label} | {summarize_prompt(block, 80)} | {infer_question_type(block)} | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |"
            )
    else:
        lines.append("| 未识别到结构化问题 | 需人工补充子问题拆分 | unknown | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |")

    lines.extend(["", "<!-- AUTO_RESULT_SUMMARY -->", ""])
    for label, _ in question_blocks:
        lines.extend(
            [
                f"## {label}",
                "",
                "### 目标",
                "",
                "### 输入",
                "",
                "### 输出",
                "",
                "### 选用模型",
                "",
                "### 代码文件",
                "",
                "### 结果文件",
                "",
                "### 图表文件",
                "",
                "### 证据文件",
                "",
                "### 支撑图表",
                "",
                "### 最终结论句",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    args = parse_args()
    project_dir = Path(args.project_dir).resolve()
    try:
        prompt_source = find_prompt_source(project_dir, args.prompt)
        extraction_result = extract_prompt_text(prompt_source)
    except Exception as exc:
        print("PARSE_STATUS: failed", file=sys.stderr)
        print(str(exc), file=sys.stderr)
        return 1

    if extraction_result.status in {"ocr_unavailable", "ocr_failed", "prompt_empty"} and not extraction_result.text:
        print(f"PARSE_STATUS: {extraction_result.status}", file=sys.stderr)
        if extraction_result.detail:
            print(extraction_result.detail, file=sys.stderr)
        return 1

    question_blocks = extract_question_blocks(extraction_result.text)
    parse_status = extraction_result.status if question_blocks else "zero_questions_detected"
    attachments = inventory_attachments(project_dir, prompt_source)

    update_data_inventory(project_dir, attachments)
    upsert_section(
        project_dir / "文档" / "方案.md",
        "PROMPT_PARSE",
        build_plan_section(prompt_source, extraction_result, question_blocks),
    )
    upsert_section(
        project_dir / "文档" / "解题思路.md",
        "PROMPT_PARSE",
        build_solution_thought_section(question_blocks),
    )
    mapping_path = project_dir / "文档" / "问题-方法对照表.md"
    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    mapping_path.write_text(build_mapping_table(question_blocks), encoding="utf-8")

    print(f"PARSE_STATUS: {parse_status}")
    print(f"Prompt source: {prompt_source}")
    print(f"Prompt kind: {extraction_result.source_kind}")
    print(f"Prompt detail: {extraction_result.detail or 'N/A'}")
    print(f"Detected questions: {len(question_blocks)}")
    print(f"Attachment inventory written: {project_dir / '数据' / '数据说明表.md'}")
    print(f"Updated: {project_dir / '文档' / '方案.md'}")
    print(f"Updated: {project_dir / '文档' / '解题思路.md'}")
    print(f"Updated: {mapping_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
