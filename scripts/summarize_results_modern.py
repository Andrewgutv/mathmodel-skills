from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path


QUESTION_RESULT_PATTERN = re.compile(r"问题(\d+)_结果汇总\.csv$")
QUESTION_SECTION_PATTERN = re.compile(r"##\s+问题(\d+)")
QUESTION_TABLE_PATTERN = re.compile(r"^\|\s*问题(\d+)\s*\|", flags=re.MULTILINE)
PLACEHOLDER_TOKENS = ("待填写", "示例指标")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate per-question result CSVs into 结果/综合结果汇总.csv."
    )
    parser.add_argument("project_dir", help="Project root directory")
    return parser.parse_args()


def load_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def normalize_row(question: str, row: dict[str, str], source_name: str) -> dict[str, str]:
    return {
        "问题": question,
        "指标": row.get("指标", "").strip(),
        "数值": row.get("数值", "").strip(),
        "说明": row.get("说明", "").strip(),
        "来源脚本": row.get("来源脚本", "").strip() or source_name,
    }


def detect_expected_question_numbers(project_root: Path) -> list[int]:
    mapping_path = project_root / "文档" / "问题-方法对照表.md"
    if not mapping_path.exists():
        return []

    text = mapping_path.read_text(encoding="utf-8")
    numbers = {
        int(match)
        for match in QUESTION_SECTION_PATTERN.findall(text) + QUESTION_TABLE_PATTERN.findall(text)
    }
    return sorted(numbers)


def collect_question_files(result_dir: Path, expected_numbers: list[int]) -> list[Path]:
    if expected_numbers:
        files = []
        missing_numbers = []
        for number in expected_numbers:
            path = result_dir / f"问题{number}_结果汇总.csv"
            if path.exists():
                files.append(path)
            else:
                missing_numbers.append(number)
        if missing_numbers:
            formatted = ", ".join(str(number) for number in missing_numbers)
            raise ValueError(f"Missing per-question result CSVs for: {formatted}")
        return files

    def sort_key(path: Path) -> tuple[int, str]:
        match = QUESTION_RESULT_PATTERN.search(path.name)
        index = int(match.group(1)) if match else 9999
        return index, path.name

    return sorted(result_dir.glob("问题*_结果汇总.csv"), key=sort_key)


def csv_has_meaningful_rows(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except OSError:
        return False
    normalized = content.strip()
    if not normalized or "数值" not in normalized:
        return False
    return not any(token in normalized for token in PLACEHOLDER_TOKENS)


def summarize(project_root: Path) -> tuple[Path, int]:
    result_dir = project_root / "结果"
    result_dir.mkdir(parents=True, exist_ok=True)

    expected_numbers = detect_expected_question_numbers(project_root)
    question_files = collect_question_files(result_dir, expected_numbers)
    if not question_files:
        raise ValueError("No per-question result CSVs found under 结果/.")

    combined_rows: list[dict[str, str]] = []
    for path in question_files:
        if not csv_has_meaningful_rows(path):
            raise ValueError(f"Result CSV is empty or still looks like a placeholder: {path}")
        match = QUESTION_RESULT_PATTERN.search(path.name)
        if not match:
            continue
        question = f"问题{match.group(1)}"
        rows = load_rows(path)
        if not rows:
            raise ValueError(f"Result CSV is header-only: {path}")
        for row in rows:
            normalized = normalize_row(question, row, path.name)
            if any(normalized.values()):
                combined_rows.append(normalized)

    if not combined_rows:
        raise ValueError("No meaningful rows were collected from per-question result CSVs.")

    output_path = result_dir / "综合结果汇总.csv"
    fieldnames = ["问题", "指标", "数值", "说明", "来源脚本"]
    with output_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(combined_rows)

    return output_path, len(combined_rows)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_dir).resolve()
    try:
        output_path, row_count = summarize(project_root)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"Generated summary CSV: {output_path}")
    print(f"Rows written: {row_count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
