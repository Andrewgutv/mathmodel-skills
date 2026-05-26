from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


SECTION_MARKER = "<!-- AUTO_RESULT_SUMMARY -->"
QUESTION_RESULTS_START = "<!-- AUTO_QUESTION_RESULTS_START -->"
QUESTION_RESULTS_END = "<!-- AUTO_QUESTION_RESULTS_END -->"
DEFENSE_RESULTS_START = "<!-- AUTO_DEFENSE_RESULTS_START -->"
DEFENSE_RESULTS_END = "<!-- AUTO_DEFENSE_RESULTS_END -->"
QUESTION_RESULT_PATTERN = re.compile(r"(问题\d+)_结果汇总\.csv$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Backfill mathmodel result summaries into core project documents."
    )
    parser.add_argument("project_dir", help="Project root directory")
    return parser.parse_args()


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def collect_result_summaries(result_dir: Path) -> dict[str, list[dict[str, str]]]:
    summaries: dict[str, list[dict[str, str]]] = {}
    for path in sorted(result_dir.glob("问题*_结果汇总.csv")):
        match = QUESTION_RESULT_PATTERN.search(path.name)
        if not match:
            continue
        summaries[match.group(1)] = load_csv_rows(path)
    summaries["综合"] = load_csv_rows(result_dir / "综合结果汇总.csv")
    return summaries


def format_result_summary_block(summaries: dict[str, list[dict[str, str]]]) -> str:
    lines = [SECTION_MARKER, "## 自动回填结果摘要", ""]
    if summaries.get("综合"):
        lines.append("### 综合结果")
        lines.extend(format_rows(summaries["综合"]))
        lines.append("")

    for question in sorted(key for key in summaries.keys() if key != "综合"):
        lines.append(f"### {question}")
        rows = summaries[question]
        lines.extend(format_rows(rows) if rows else ["- 暂无结果"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def build_conclusion_sentence(question: str, rows: list[dict[str, str]]) -> str:
    if not rows:
        return f"{question}当前暂无可引用结果。"
    first = rows[0]
    metric = first.get("指标", "").strip()
    value = first.get("数值", "").strip()
    note = first.get("说明", "").strip()
    return f"{question}当前关键结果为：{metric} = {value}，可支撑“{note}”这一结论。"


def build_paper_sentence(question: str, rows: list[dict[str, str]]) -> str:
    if not rows:
        return f"{question}目前暂无可写入正文的结果。"
    first = rows[0]
    metric = first.get("指标", "").strip()
    value = first.get("数值", "").strip()
    note = first.get("说明", "").strip()
    return f"对于{question}，由计算结果可知，{metric}为{value}，这说明{note}。"


def build_defense_sentence(question: str, rows: list[dict[str, str]]) -> str:
    if not rows:
        return f"{question}目前还没有稳定结果。"
    first = rows[0]
    metric = first.get("指标", "").strip()
    value = first.get("数值", "").strip()
    note = first.get("说明", "").strip()
    return f"{question}的核心结论是：{metric}等于{value}，它直接支撑“{note}”这一判断。"


def build_evidence_file_string(question: str) -> str:
    return f"`结果/{question}_结果汇总.csv`"


def build_figure_hint_string(question: str) -> str:
    return f"`图片/{question}_配图说明.md`"


def build_question_section_block(summaries: dict[str, list[dict[str, str]]]) -> str:
    lines: list[str] = [QUESTION_RESULTS_START]
    for question in sorted(key for key in summaries.keys() if key != "综合"):
        rows = summaries[question]
        lines.extend(
            [
                f"## {question}结果回填",
                "",
                "### 关键指标",
            ]
        )
        if rows:
            for row in rows:
                lines.append(f"- {row.get('指标', '').strip()}: {row.get('数值', '').strip()}")
        else:
            lines.append("- 暂无结果")
        lines.extend(
            [
                "",
                "### 支撑图表",
                f"- {build_figure_hint_string(question)}",
                "",
                "### 结论句",
                f"- {build_paper_sentence(question, rows)}",
                "",
            ]
        )
    lines.append(QUESTION_RESULTS_END)
    return "\n".join(lines).rstrip() + "\n"


def build_defense_section_block(summaries: dict[str, list[dict[str, str]]]) -> str:
    lines: list[str] = [DEFENSE_RESULTS_START]
    for question in sorted(key for key in summaries.keys() if key != "综合"):
        rows = summaries[question]
        lines.extend(
            [
                f"## {question}答辩结论",
                f"- 结论：{build_defense_sentence(question, rows)}",
                f"- 证据：{build_evidence_file_string(question)}",
                f"- 配图：{build_figure_hint_string(question)}",
                "",
            ]
        )
    lines.append(DEFENSE_RESULTS_END)
    return "\n".join(lines).rstrip() + "\n"


def format_rows(rows: list[dict[str, str]]) -> list[str]:
    formatted: list[str] = []
    for row in rows:
        metric = row.get("指标", "").strip()
        value = row.get("数值", "").strip()
        note = row.get("说明", "").strip()
        source = row.get("来源脚本", "").strip()
        formatted.append(f"- {metric}: {value}。说明：{note}。来源：{source}")
    return formatted or ["- 暂无结果"]


def replace_or_append_summary(path: Path, summary_block: str) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    if SECTION_MARKER in text:
        before, after = text.split(SECTION_MARKER, 1)
        after = re.sub(
            r"^\s*## 自动回填结果摘要.*?(?=(\n# |\n## |\Z))",
            "",
            after,
            flags=re.DOTALL,
        )
        after = re.sub(
            rf"(?s){re.escape(QUESTION_RESULTS_START)}.*?{re.escape(QUESTION_RESULTS_END)}",
            "",
            after,
        )
        after = re.sub(
            rf"(?s){re.escape(DEFENSE_RESULTS_START)}.*?{re.escape(DEFENSE_RESULTS_END)}",
            "",
            after,
        )
        updated = before.rstrip() + "\n\n" + summary_block.rstrip() + "\n" + after.lstrip("\n")
        path.write_text(updated, encoding="utf-8")
        return
    updated = text.rstrip() + "\n\n" + summary_block
    path.write_text(updated, encoding="utf-8")


def replace_between_markers(path: Path, start_marker: str, end_marker: str, block: str) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    replacement = block.rstrip()
    if start_marker in text and end_marker in text:
        before, remainder = text.split(start_marker, 1)
        _, after = remainder.split(end_marker, 1)
        updated = before.rstrip() + "\n\n" + replacement + "\n" + after.lstrip("\n")
    else:
        updated = text.rstrip() + "\n\n" + replacement + "\n"
    updated = re.sub(r"\n{3,}", "\n\n", updated)
    path.write_text(updated, encoding="utf-8")


def update_mapping_table(path: Path, summaries: dict[str, list[dict[str, str]]]) -> None:
    if not path.exists():
        return
    lines = path.read_text(encoding="utf-8").splitlines()
    updated_lines: list[str] = []
    for line in lines:
        if line.startswith("| 问题") and "待补充" in line:
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            question = cells[0]
            if question in summaries:
                cells[6] = build_evidence_file_string(question)
                cells[7] = build_figure_hint_string(question)
                cells[8] = build_conclusion_sentence(question, summaries[question])
                line = "| " + " | ".join(cells) + " |"
        updated_lines.append(line)
    path.write_text("\n".join(updated_lines) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_dir).resolve()
    result_dir = project_root / "结果"
    doc_dir = project_root / "文档"
    defense_dir = project_root / "答辩"

    summaries = collect_result_summaries(result_dir)
    summary_block = format_result_summary_block(summaries)
    question_block = build_question_section_block(summaries)
    defense_block = build_defense_section_block(summaries)

    replace_or_append_summary(doc_dir / "问题-方法对照表.md", summary_block)
    replace_or_append_summary(doc_dir / "论文.md", summary_block)
    replace_or_append_summary(defense_dir / "答辩准备.md", summary_block)
    replace_between_markers(doc_dir / "论文.md", QUESTION_RESULTS_START, QUESTION_RESULTS_END, question_block)
    replace_between_markers(defense_dir / "答辩准备.md", DEFENSE_RESULTS_START, DEFENSE_RESULTS_END, defense_block)
    update_mapping_table(doc_dir / "问题-方法对照表.md", summaries)

    print(f"Backfilled results into: {doc_dir / '问题-方法对照表.md'}")
    print(f"Backfilled results into: {doc_dir / '论文.md'}")
    print(f"Backfilled results into: {defense_dir / '答辩准备.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
