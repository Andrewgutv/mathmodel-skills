from __future__ import annotations

import csv
from pathlib import Path


PROBLEM_TAG = "问题X"


def get_paths() -> dict[str, Path]:
    project_root = Path(__file__).resolve().parents[1]
    return {
        "project_root": project_root,
        "data_dir": project_root / "数据",
        "result_csv": project_root / "结果" / f"{PROBLEM_TAG}_结果汇总.csv",
        "figure_stub": project_root / "图片" / f"图_{PROBLEM_TAG}_评价结果说明.txt",
    }


def load_inputs(paths: dict[str, Path]) -> dict[str, str]:
    return {"data_source": str(paths["data_dir"]), "task_type": "evaluation"}


def build_model(data: dict[str, str]) -> dict[str, str]:
    return {"model_family": "evaluation", "note": "replace with AHP, TOPSIS, entropy weighting, etc."}


def solve_model(model: dict[str, str], data: dict[str, str]) -> dict[str, str]:
    return {"summary_metric": "0", "model_family": model["model_family"], "note": model["note"]}


def export_results(result: dict[str, str], paths: dict[str, Path]) -> None:
    paths["result_csv"].parent.mkdir(parents=True, exist_ok=True)
    with paths["result_csv"].open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["指标", "数值", "说明", "来源脚本"])
        writer.writerow(["ranking_score", result["summary_metric"], result["note"], Path(__file__).name])


def build_figures(result: dict[str, str], paths: dict[str, Path]) -> None:
    paths["figure_stub"].parent.mkdir(parents=True, exist_ok=True)
    paths["figure_stub"].write_text(
        "在此替换为真实评价图，例如权重图、雷达图或排名对比图。\n",
        encoding="utf-8",
    )


def main() -> None:
    paths = get_paths()
    data = load_inputs(paths)
    model = build_model(data)
    result = solve_model(model, data)
    export_results(result, paths)
    build_figures(result, paths)
    print(f"Generated: {paths['result_csv']}")
    print(f"Generated: {paths['figure_stub']}")


if __name__ == "__main__":
    main()
