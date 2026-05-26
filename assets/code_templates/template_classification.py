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
        "figure_stub": project_root / "图片" / f"图_{PROBLEM_TAG}_分类结果说明.txt",
    }


def load_inputs(paths: dict[str, Path]) -> dict[str, str]:
    return {"data_source": str(paths["data_dir"]), "task_type": "classification"}


def build_model(data: dict[str, str]) -> dict[str, str]:
    return {"model_family": "classification", "note": "replace with clustering, logistic regression, or tree model"}


def solve_model(model: dict[str, str], data: dict[str, str]) -> dict[str, str]:
    return {"classification_metric": "0", "model_family": model["model_family"], "note": model["note"]}


def export_results(result: dict[str, str], paths: dict[str, Path]) -> None:
    paths["result_csv"].parent.mkdir(parents=True, exist_ok=True)
    with paths["result_csv"].open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["指标", "数值", "说明", "来源脚本"])
        writer.writerow(["classification_metric", result["classification_metric"], result["note"], Path(__file__).name])


def build_figures(result: dict[str, str], paths: dict[str, Path]) -> None:
    paths["figure_stub"].parent.mkdir(parents=True, exist_ok=True)
    paths["figure_stub"].write_text(
        "在此替换为真实分类图，例如混淆矩阵、聚类图或特征重要性图。\n",
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
