from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    code_dir = project_root / "代码"
    scripts = sorted(code_dir.glob("code_问题*_*.py"))
    if not scripts:
        raise SystemExit("No question scripts found.")

    for script in scripts:
        completed = subprocess.run([sys.executable, str(script)], cwd=str(project_root), check=False)
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
