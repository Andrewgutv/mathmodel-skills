from __future__ import annotations

import csv
import itertools
import math
from pathlib import Path


POINTS = {
    "A": (1.0, 1.0),
    "B": (4.0, 5.0),
    "C": (7.0, 1.0),
}


def path_length(order: tuple[str, ...]) -> float:
    total = 0.0
    for i in range(len(order) - 1):
        total += math.dist(POINTS[order[i]], POINTS[order[i + 1]])
    return total


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result_path = project_root / "结果" / "问题2_结果汇总.csv"

    best_order: tuple[str, ...] | None = None
    best_length = float("inf")
    for order in itertools.permutations(POINTS.keys()):
        current = path_length(order)
        if current < best_length:
            best_order = order
            best_length = current

    with result_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["指标", "数值", "说明", "来源脚本"])
        writer.writeheader()
        writer.writerow(
            {
                "指标": "最短访问路径长度",
                "数值": f"{best_length:.3f}",
                "说明": f"三点最短访问顺序为 {'-'.join(best_order or ())}",
                "来源脚本": "code_问题2_optimization.py",
            }
        )


if __name__ == "__main__":
    main()
