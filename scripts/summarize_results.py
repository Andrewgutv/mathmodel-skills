from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


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


def collect_question_files(result_dir: Path) -> list[Path]:
    def sort_key(path: Path) -> tuple[int, str]:
        match = re.search(r"问题(\d+)_结果汇总\.csv$", path.name)
        index = int(match.group(1)) if match else 9999
        return index, path.name

    return sorted(result_dir.glob("问题*_结果汇总.csv"), key=sort_key)


def summarize(project_root: Path) -> tuple[Path, int]:
    result_dir = project_root / "结果"
    result_dir.mkdir(parents=True, exist_ok=True)

    combined_rows: list[dict[str, str]] = []
    question_files = collect_question_files(result_dir)
    for path in question_files:
        match = re.search(r"(问题\d+)_结果汇总\.csv$", path.name)
        if not match:
            continue
        question = match.group(1)
        rows = load_rows(path)
        for row in rows:
            normalized = normalize_row(question, row, path.name)
            if any(normalized.values()):
                combined_rows.append(normalized)

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
    output_path, row_count = summarize(project_root)
    print(f"Generated summary CSV: {output_path}")
    print(f"Rows written: {row_count}")
    return 0 if row_count > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
