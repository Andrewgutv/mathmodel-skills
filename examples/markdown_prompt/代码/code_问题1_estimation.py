from __future__ import annotations

import csv
import math
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    result_path = project_root / "结果" / "问题1_结果汇总.csv"

    point_a = (0.0, 0.0)
    point_b = (3.0, 4.0)
    distance = math.dist(point_a, point_b)

    with result_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["指标", "数值", "说明", "来源脚本"])
        writer.writeheader()
        writer.writerow(
            {
                "指标": "两点欧式距离",
                "数值": f"{distance:.3f}",
                "说明": "A(0,0) 到 B(3,4) 的距离为 5",
                "来源脚本": "code_问题1_estimation.py",
            }
        )


if __name__ == "__main__":
    main()
