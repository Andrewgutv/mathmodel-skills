from __future__ import annotations

import csv
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image
import pdfplumber
from pypdf import PdfReader


PROBLEM_TAG = "问题X"


def get_paths() -> dict[str, Path]:
    project_root = Path(__file__).resolve().parents[1]
    prompt_pdf = next(iter(sorted(project_root.glob("*.pdf"))), None)
    return {
        "project_root": project_root,
        "attachment_root": find_attachment_root(project_root),
        "mapping_table": project_root / "文档" / "问题-方法对照表.md",
        "solution_notes": project_root / "文档" / "解题思路.md",
        "prompt_pdf": prompt_pdf,
        "result_csv": project_root / "结果" / f"{PROBLEM_TAG}_结果汇总.csv",
        "figure_stub": project_root / "图片" / f"图_{PROBLEM_TAG}_估算结果说明.txt",
    }


def find_attachment_root(project_root: Path) -> Path:
    for candidate in [project_root / "附件", project_root / "9个附件", project_root / "数据"]:
        if candidate.exists():
            return candidate
    return project_root


def load_question_text(paths: dict[str, Path]) -> str:
    notes_path = paths["solution_notes"]
    if notes_path.exists():
        text = notes_path.read_text(encoding="utf-8")
        pattern = rf"## {re.escape(PROBLEM_TAG)}\n(.*?)(?=\n## 问题\d+\n|\Z)"
        match = re.search(pattern, text, flags=re.DOTALL)
        if match:
            block = match.group(1)
            raw_match = re.search(r"### 原题要求\n(.*?)(?=\n### |\Z)", block, flags=re.DOTALL)
            if raw_match:
                return re.sub(r"\s+", " ", raw_match.group(1)).strip()

    mapping = paths["mapping_table"].read_text(encoding="utf-8")
    for line in mapping.splitlines():
        if line.startswith(f"| {PROBLEM_TAG} |"):
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) >= 2:
                return cells[1]
    return ""


def extract_attachment_refs(question_text: str) -> list[str]:
    refs = re.findall(r"Pic\d+\.(?:jpg|png|jpeg|bmp|gif)", question_text, flags=re.IGNORECASE)
    seen: list[str] = []
    for ref in refs:
        if ref not in seen:
            seen.append(ref)
    return seen


def resolve_attachment_path(attachment_root: Path, ref: str) -> Path | None:
    exact = attachment_root / ref
    if exact.exists():
        return exact

    stem = Path(ref).stem
    suffix = Path(ref).suffix.lower()
    for candidate in sorted(attachment_root.glob(f"{stem}*{suffix}")):
        if candidate.is_file():
            return candidate
    return None


def extract_prompt_text(prompt_pdf: Path | None) -> str:
    if prompt_pdf is None or not prompt_pdf.exists():
        return ""

    text_parts: list[str] = []
    try:
        with pdfplumber.open(prompt_pdf) as pdf:
            for page in pdf.pages:
                text_parts.append(page.extract_text() or "")
    except Exception:
        reader = PdfReader(str(prompt_pdf))
        for page in reader.pages:
            text_parts.append(page.extract_text() or "")
    return "\n".join(part for part in text_parts if part).strip()


def parse_table_entities(prompt_text: str) -> dict[str, dict[str, float]]:
    entities: dict[str, dict[str, float]] = {}
    patterns = {
        "Zhinyu": r"Zhinyu\s+织女\s+\S+\s+([0-9.]+)°E\s+([0-9.]+)°S\s+([0-9.]+)",
        "Hegu": r"Hegu\s+河鼓\s+\S+\s+([0-9.]+)°E\s+([0-9.]+)°S\s+([0-9.]+)",
        "Tianjin": r"Tianjin\s+天津\s+\S+\s+([0-9.]+)°E\s+([0-9.]+)°S\s+([0-9.]+)",
        "MonsTai": r"MonsTai\s+泰山\s+\S+\s+([0-9.]+)°E\s+([0-9.]+)°S\s+([0-9.]+)",
        "Pingle": r"Pingle\s+8\.2\s+([0-9.]+)\s+([0-9.]+)",
        "Wenjiashi": r"Wenjiashi\s+18\s+([0-9.]+)\s+([0-9.]+)",
        "WenjiashiMensa": r"Wenjiashi\s+Mensa\s+4\s+([0-9.]+)\s+([0-9.]+)",
    }
    for name, pattern in patterns.items():
        match = re.search(pattern, prompt_text)
        if not match:
            continue
        values = [float(v) for v in match.groups()]
        if name in {"Zhinyu", "Hegu", "Tianjin", "MonsTai"}:
            entities[name] = {"lon": values[0], "lat": -values[1], "diameter_km": values[2]}
        elif name in {"Pingle", "Wenjiashi", "WenjiashiMensa"}:
            entities[name] = {"lat": values[0], "lon": values[1], "diameter_km": {"Pingle": 8.2, "Wenjiashi": 18.0, "WenjiashiMensa": 4.0}[name]}

    if "WenjiashiMensa" not in entities and re.search(r"22\s+方山\s+4\s+24\.81\s+109\.57", prompt_text):
        entities["WenjiashiMensa"] = {"lat": 24.81, "lon": 109.57, "diameter_km": 4.0}
    if "Wenjiashi" not in entities and re.search(r"Wenjiashi\s+18\s+25\.22\s+109\.44", prompt_text):
        entities["Wenjiashi"] = {"lat": 25.22, "lon": 109.44, "diameter_km": 18.0}
    return entities


def detect_named_entity(question_text: str) -> str | None:
    mapping = [
        ("织女", "Zhinyu"),
        ("河鼓", "Hegu"),
        ("天津", "Tianjin"),
        ("泰山", "MonsTai"),
        ("平乐", "Pingle"),
        ("文家市方山", "WenjiashiMensa"),
        ("文家市", "Wenjiashi"),
    ]
    for key, name in mapping:
        if key in question_text:
            return name
    return None


def detect_named_entities(question_text: str) -> list[str]:
    mapping = [
        ("文家市方山", "WenjiashiMensa"),
        ("织女", "Zhinyu"),
        ("河鼓", "Hegu"),
        ("天津", "Tianjin"),
        ("泰山", "MonsTai"),
        ("平乐", "Pingle"),
        ("文家市", "Wenjiashi"),
    ]
    names: list[str] = []
    for key, name in mapping:
        if key in question_text and name not in names:
            names.append(name)
    return names


def extract_depth_km(question_text: str) -> float | None:
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*m", question_text)
    if match:
        return float(match.group(1)) / 1000.0
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*km", question_text)
    if match and "深度" in question_text:
        return float(match.group(1))
    return None


def extract_speed_kmph(question_text: str) -> float | None:
    match = re.search(r"([0-9]+(?:\.[0-9]+)?)\s*(?:公里/小时|km/h)", question_text)
    return float(match.group(1)) if match else None


def conical_surface_area_km2(diameter_km: float, depth_km: float) -> float:
    radius = diameter_km / 2.0
    slant = math.sqrt(radius * radius + depth_km * depth_km)
    return math.pi * radius * slant


def estimate_height_km(diameter_km: float, bbox_width_px: float, bbox_height_px: float) -> float:
    if bbox_width_px <= 0:
        return 0.0
    return diameter_km * (bbox_height_px / bbox_width_px)


def infer_ref_entity_pairs(question_text: str, refs: list[str]) -> list[tuple[str, str | None]]:
    entity_names = detect_named_entities(question_text)
    explicit_map = {
        "Pic02.jpg": "Zhinyu",
        "Pic03.jpg": "Hegu",
        "Pic04.jpg": "Tianjin",
        "Pic05.jpg": "MonsTai",
        "Pic07.jpg": "Pingle",
        "Pic08.jpg": "Wenjiashi",
        "Pic09.jpg": "WenjiashiMensa",
    }
    pairs: list[tuple[str, str | None]] = []
    for idx, ref in enumerate(refs):
        if ref in explicit_map:
            pairs.append((ref, explicit_map[ref]))
        elif idx < len(entity_names):
            pairs.append((ref, entity_names[idx]))
        else:
            pairs.append((ref, None))
    return pairs


def spherical_distance_km(lon1: float, lat1: float, lon2: float, lat2: float, radius_km: float) -> float:
    lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
    cos_c = math.sin(lat1) * math.sin(lat2) + math.cos(lat1) * math.cos(lat2) * math.cos(lon1 - lon2)
    cos_c = max(-1.0, min(1.0, cos_c))
    return radius_km * math.acos(cos_c)


def summarize_image(path: Path) -> dict[str, float]:
    image = Image.open(path).convert("L")
    arr = np.array(image, dtype=np.uint8)
    dark = arr < 200
    ys, xs = np.where(dark)
    bbox_width = int(xs.max() - xs.min() + 1) if len(xs) else 0
    bbox_height = int(ys.max() - ys.min() + 1) if len(ys) else 0
    return {
        "width_px": float(arr.shape[1]),
        "height_px": float(arr.shape[0]),
        "dark_ratio": float(dark.mean()),
        "bbox_width_px": float(bbox_width),
        "bbox_height_px": float(bbox_height),
    }


def solve_estimation(paths: dict[str, Path]) -> list[dict[str, str]]:
    question_text = load_question_text(paths)
    refs = extract_attachment_refs(question_text)
    prompt_text = extract_prompt_text(paths["prompt_pdf"])
    entities = parse_table_entities(prompt_text)
    rows: list[dict[str, str]] = []

    if "球面距离" in question_text and "天河基地" in question_text and "织女" in question_text:
        zhinyu = entities.get("Zhinyu")
        tianhe = {"lon": 177.60, "lat": -45.45}
        if zhinyu:
            distance = spherical_distance_km(tianhe["lon"], tianhe["lat"], zhinyu["lon"], zhinyu["lat"], 1737.4)
            speed = extract_speed_kmph(question_text) or 20.0
            travel_hours = distance / speed
            rows.extend(
                [
                    {
                        "指标": "moon_surface_distance_km",
                        "数值": f"{distance:.6f}",
                        "说明": "按月球半径1737.4km计算的天河基地到织女坑球面距离",
                        "来源脚本": Path(__file__).name,
                    },
                    {
                        "指标": "moon_rover_travel_hours",
                        "数值": f"{travel_hours:.6f}",
                        "说明": f"按{speed:.2f}km/h估算的单程行驶时间",
                        "来源脚本": Path(__file__).name,
                    },
                ]
            )
        rows.append(
            {
                "指标": "estimation_note",
                "数值": "1",
                "说明": "当前已自动完成球面距离粗估，后续可继续补充地形修正。",
                "来源脚本": Path(__file__).name,
            }
        )
        return rows

    if "国际天文联合会" in question_text and "飞行的距离" in question_text:
        rows.append(
            {
                "指标": "distance_estimation_status",
                "数值": "1",
                "说明": "当前模板已识别为跨天体距离估算问题，建议后续补充星历数据或平均轨道模型。",
                "来源脚本": Path(__file__).name,
            }
        )
        return rows

    if not refs:
        rows.append(
            {
                "指标": "estimation_ready",
                "数值": "0",
                "说明": "未从题面中识别到图片附件，请补充数据提取逻辑。",
                "来源脚本": Path(__file__).name,
            }
        )
        return rows

    ref_entity_pairs = infer_ref_entity_pairs(question_text, refs)
    for ref, entity_name in ref_entity_pairs:
        image_path = resolve_attachment_path(paths["attachment_root"], ref)
        if image_path is None:
            rows.append(
                {
                    "指标": f"{ref}_missing",
                    "数值": "0",
                    "说明": f"未找到附件 {ref}",
                    "来源脚本": Path(__file__).name,
                }
            )
            continue

        metrics = summarize_image(image_path)
        for key, value in metrics.items():
            rows.append(
                {
                    "指标": f"{ref}_{key}",
                    "数值": f"{value:.6f}" if isinstance(value, float) else str(value),
                    "说明": "自动生成的第一版图像估算指标",
                    "来源脚本": Path(__file__).name,
                }
            )

        entity = entities.get(entity_name) if entity_name else None
        if entity and "diameter_km" in entity and metrics["bbox_width_px"] > 0:
            scale = entity["diameter_km"] / metrics["bbox_width_px"]
            rows.append(
                {
                    "指标": f"{ref}_km_per_bbox_px",
                    "数值": f"{scale:.9f}",
                    "说明": f"基于 {entity_name} 已知直径得到的第一版尺度映射",
                    "来源脚本": Path(__file__).name,
                }
            )
            rows.append(
                {
                    "指标": f"{ref}_known_diameter_km",
                    "数值": f"{entity['diameter_km']:.6f}",
                    "说明": f"{entity_name} 在题面表格中的已知直径",
                    "来源脚本": Path(__file__).name,
                }
            )

            if "表面积" in question_text:
                rows.append(
                    {
                        "指标": f"{entity_name}_planar_area_km2",
                        "数值": f"{math.pi * (entity['diameter_km'] / 2.0) ** 2:.6f}",
                        "说明": f"按圆形平面近似得到的 {entity_name} 口径面积",
                        "来源脚本": Path(__file__).name,
                    }
                )

            depth_km = extract_depth_km(question_text)
            if depth_km is not None and "表面积" in question_text:
                rows.append(
                    {
                        "指标": f"{entity_name}_conical_surface_area_km2",
                        "数值": f"{conical_surface_area_km2(entity['diameter_km'], depth_km):.6f}",
                        "说明": f"按圆锥侧面积近似得到的 {entity_name} 坑内表面积",
                        "来源脚本": Path(__file__).name,
                    }
                )

            if "高度" in question_text and entity_name in {"MonsTai", "WenjiashiMensa"}:
                rows.append(
                    {
                        "指标": f"{entity_name}_height_proxy_km",
                        "数值": f"{estimate_height_km(entity['diameter_km'], metrics['bbox_width_px'], metrics['bbox_height_px']):.6f}",
                        "说明": f"按包围框高宽比与已知口径构造的 {entity_name} 第一版高度粗估",
                        "来源脚本": Path(__file__).name,
                    }
                )

    if "A、B两个撞击坑" in question_text or ("A" in question_text and "B" in question_text and "直径" in question_text):
        rows.append(
            {
                "指标": "AB_crater_estimation_status",
                "数值": "1",
                "说明": "当前模板已识别为多目标撞击坑估算问题，下一步应增加图像目标分割与像素标注逻辑。",
                "来源脚本": Path(__file__).name,
            }
        )

    rows.append(
        {
            "指标": "estimation_note",
            "数值": "1",
            "说明": "当前为第一版估算模板，已完成附件读取、基础图像测量和部分尺度映射，后续应补充目标边界识别。",
            "来源脚本": Path(__file__).name,
        }
    )
    return rows


def export_results(rows: list[dict[str, str]], paths: dict[str, Path]) -> None:
    paths["result_csv"].parent.mkdir(parents=True, exist_ok=True)
    with paths["result_csv"].open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["指标", "数值", "说明", "来源脚本"])
        writer.writeheader()
        writer.writerows(rows)


def build_figures(rows: list[dict[str, str]], paths: dict[str, Path]) -> None:
    refs = [row["指标"] for row in rows if row["指标"].endswith("_width_px")]
    paths["figure_stub"].parent.mkdir(parents=True, exist_ok=True)
    paths["figure_stub"].write_text(
        "自动估算模板已运行。可继续替换为轮廓标注图、尺度估计图或面积/高度示意图。\n"
        + "\n".join(refs)
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    paths = get_paths()
    rows = solve_estimation(paths)
    export_results(rows, paths)
    build_figures(rows, paths)
    print(f"Generated: {paths['result_csv']}")
    print(f"Generated: {paths['figure_stub']}")


if __name__ == "__main__":
    main()
