from __future__ import annotations

import argparse
import shutil
from pathlib import Path


DEFAULT_DIRS = (
    "代码",
    "图片",
    "数据",
    "结果",
    "文档",
    "答辩",
)


COMMON_FILES = {
    "代码/README.md": """# 代码说明

## 推荐结构

- `main.py`: 总入口
- `preprocess.py`: 数据预处理
- `plot_figures.py`: 图表统一生成
- `export_results.py`: 结果汇总导出
- `code_问题1_xxx.py` ~ `code_问题N_xxx.py`: 按问题拆分的核心脚本

## 原则

- 每个问题尽量对应一个主脚本
- 每个脚本都应说明输入、输出、生成的图表
- 结果必须可追溯到 `结果/`

## 推荐执行入口

- 项目根目录下的 `run_mathmodel.ps1`
- 或技能脚本 `scripts/run_pipeline_modern.py`
""",
    "代码/main.py": '''from pathlib import Path
import subprocess
import sys


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    code_dir = project_root / "代码"
    scripts = sorted(code_dir.glob("code_问题*_*.py"))
    if not scripts:
        print(f"No question scripts found under: {code_dir}")
        return

    for script in scripts:
        print(f"Running {script.name} ...")
        completed = subprocess.run([sys.executable, str(script)], cwd=str(project_root), check=False)
        if completed.returncode != 0:
            raise SystemExit(completed.returncode)


if __name__ == "__main__":
    main()
''',
    "代码/preprocess.py": '''def preprocess() -> None:
    """Load, clean, and normalize raw input data here."""
    pass
''',
    "代码/plot_figures.py": '''def build_figures() -> None:
    """Generate final paper figures and save them to 图片/."""
    pass
''',
    "代码/export_results.py": '''def export_results() -> None:
    """Collect per-question outputs and write final summaries to 结果/."""
    pass
''',
    "代码/backfill_results.ps1": """python ..\\..\\.codex\\skills\\mathmodel\\scripts\\backfill_results.py ..\\
""",
    "代码/parse_prompt.ps1": """python ..\\..\\.codex\\skills\\mathmodel\\scripts\\parse_prompt_modern.py ..\\
""",
    "run_mathmodel.ps1": """param(
    [string]$Stage = "all",
    [string]$Prompt = "",
    [string]$Template = "",
    [switch]$SkipParse,
    [switch]$SkipSolve,
    [switch]$SkipSummarize,
    [switch]$SkipWrite,
    [switch]$SkipWord,
    [switch]$SkipCheck
)

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
python $HOME\\.codex\\skills\\mathmodel\\scripts\\run_pipeline_modern.py $projectRoot --stage $Stage --prompt $Prompt --template $Template @(
    if ($SkipParse) { '--skip-parse' }
    if ($SkipSolve) { '--skip-solve' }
    if ($SkipSummarize) { '--skip-summarize' }
    if ($SkipWrite) { '--skip-write' }
    if ($SkipWord) { '--skip-word' }
    if ($SkipCheck) { '--skip-check' }
)
""",
    "数据/README.md": """# 数据说明

## 放置内容

- 原始数据
- 清洗后数据
- 中间处理结果

## 原则

- 保留原始文件，不覆盖
- 所有字段含义记录到 `数据说明表.md`
""",
    "数据/数据说明表.md": """# 数据说明表

| 文件名 | 类型 | 来源 | 用途 | 预处理方式 |
|---|---|---|---|---|
| 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |
""",
    "结果/README.md": """# 结果说明

## 放置内容

- 各问题结果汇总
- 关键中间表
- 论文可直接引用的结论
""",
    "结果/综合结果汇总.csv": "问题,指标,数值,说明,来源脚本\n问题1,示例指标,0,待填写,待填写\n",
    "结果/运行日志.md": """# 运行日志

## 本次运行了哪些脚本

## 使用了哪些输入数据

## 生成了哪些结果文件

## 是否存在报错或警告
""",
    "文档/方案.md": """# 方案

## 题目重述

## 子问题拆解

## 数据盘点

## 候选方法

## 选定方法

## 风险点
""",
    "文档/解题思路.md": """# 解题思路

## 题目想考什么

## 每一问怎么拆

## 为什么选这些模型

## 备选方案为什么不选

## 每一步准备如何落到代码和结果
""",
    "文档/问题-方法对照表.md": """# 问题-方法对照表

| 问题 | 题目要求 | 判定题型 | 选用方法 | 不选的方法 | 对应代码 | 证据文件 | 支撑图表 | 最终结论句 |
|---|---|---|---|---|---|---|---|---|
| 问题1 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 | 待补充 |

<!-- AUTO_RESULT_SUMMARY -->
""",
    "文档/解题过程.md": """# 解题过程

## 数据处理过程

## 建模过程

## 求解过程

## 调参与检验过程

## 实际运行记录与输出文件
""",
    "文档/模型解释_小白版.md": """# 模型解释（小白版）

## 这个模型在解决什么问题

## 输入是什么

## 输出是什么

## 模型核心逻辑是什么

## 为什么这个模型是合理的

## 局限性在哪里

## 用一句话告诉完全不懂的人结论是什么
""",
    "文档/模型解释_专业版.md": """# 模型解释（专业版）

## 模型定义

## 参数说明

## 约束条件

## 求解方法

## 复杂度与适用边界

## 与最终代码和结果的对应关系
""",
    "文档/论文.md": """# 摘要

# 一、问题的提出

# 二、问题的分析

# 三、模型假设

# 四、符号说明

# 五、建模与求解

# 六、模型的检验/敏感性分析

# 七、模型的评价与推广

# 参考文献

# 附录

<!-- AUTO_RESULT_SUMMARY -->

<!-- AUTO_QUESTION_RESULTS_START -->
<!-- AUTO_QUESTION_RESULTS_END -->
""",
    "文档/交付物清单.md": """# 交付物清单

- [ ] 方案.md
- [ ] 解题思路.md
- [ ] 问题-方法对照表.md
- [ ] 解题过程.md
- [ ] 模型解释_小白版.md
- [ ] 模型解释_专业版.md
- [ ] 论文.md
- [ ] 论文_完整终稿.docx
- [ ] 论文_模板一致版.docx
- [ ] 综合结果汇总.csv
- [ ] 运行日志.md
- [ ] 数据说明表.md
- [ ] 图表清单.md
- [ ] PPT设计文档.md
- [ ] 答辩准备.md
- [ ] 答辩讲稿.md
- [ ] 老师高频问题与回答.md
""",
    "文档/使用说明.md": """# 使用说明

## 一键运行

在项目根目录执行：

```powershell
./run_mathmodel.ps1
```

## 常见阶段

- 只解析题目：

```powershell
./run_mathmodel.ps1 -Stage parse
```

- 只运行求解：

```powershell
./run_mathmodel.ps1 -Stage solve
```

- 只聚合结果：

```powershell
./run_mathmodel.ps1 -Stage summarize
```

- 只回填文档：

```powershell
./run_mathmodel.ps1 -Stage write
```

- 只生成 Word：

```powershell
./run_mathmodel.ps1 -Stage word
```

- 只检查论文：

```powershell
./run_mathmodel.ps1 -Stage check
```

## 带模板生成

```powershell
./run_mathmodel.ps1 -Stage word -Template "文档\\数学建模论文2026模板.docx"
```

## 输出位置

- 流水线报告：`结果/流水线报告.md`
- 完整 Word：`文档/论文_完整终稿.docx`
- 模板版 Word：`文档/论文_模板一致版.docx`
""",
    "答辩/答辩准备.md": """# 答辩准备

## 一句话概述

## 模型亮点

## 模型弱点

## 可能追问

## 标准回答提纲

<!-- AUTO_RESULT_SUMMARY -->

<!-- AUTO_DEFENSE_RESULTS_START -->
<!-- AUTO_DEFENSE_RESULTS_END -->
""",
    "答辩/答辩讲稿.md": """# 答辩讲稿

## 开场

## 题目理解

## 模型方法

## 结果展示

## 创新点

## 结束语
""",
    "答辩/老师高频问题与回答.md": """# 老师高频问题与回答

## 模型假设相关

## 参数选取相关

## 方法选型相关

## 结果解释相关

## 模型缺陷与改进相关
""",
    "答辩/PPT设计文档.md": """# PPT设计文档

## 封面页

## 问题背景页

## 问题分析页

## 模型方法页

## 结果展示页

## 敏感性分析页

## 优缺点页

## 结束页
""",
    "图片/README.md": """# 图片说明

## 放置内容

- 论文图
- 答辩图
- 中间分析图

## 命名建议

- `图1_xxx.png`
- `图2_xxx.png`
""",
    "图片/图表清单.md": """# 图表清单

| 编号 | 文件名 | 对应问题 | 用途 | 是否已在正文引用 |
|---|---|---|---|---|
| 图1 | 待补充 | 问题1 | 待补充 | 否 |
| 表1 | 待补充 | 问题1 | 待补充 | 否 |
""",
}

TYPE_TO_TEMPLATE = {
    "prediction": "template_prediction.py",
    "evaluation": "template_evaluation.py",
    "optimization": "template_optimization.py",
    "classification": "template_classification.py",
    "simulation": "template_simulation.py",
    "estimation": "template_estimation.py",
}


QUESTION_SCRIPT_TEMPLATE = '''def solve_question_{index}() -> None:
    """
    问题{index}核心求解脚本。

    需要补充：
    1. 输入数据路径
    2. 模型定义
    3. 求解过程
    4. 输出结果到 结果/
    5. 如有需要，生成图表到 图片/
    """
    pass


if __name__ == "__main__":
    solve_question_{index}()
'''


QUESTION_RESULT_TEMPLATE = "指标,数值,说明,来源脚本\n示例指标,0,待填写,{script_name}\n"


QUESTION_DOC_TEMPLATE = """## 问题{index}

### 目标

### 输入

### 输出

### 选用模型

### 代码文件

### 结果文件

### 图表文件

### 证据文件

### 支撑图表

### 最终结论句
"""


def ensure_dirs(root: Path) -> None:
    for dirname in DEFAULT_DIRS:
        (root / dirname).mkdir(parents=True, exist_ok=True)


def write_if_missing(path: Path, content: str) -> None:
    if not path.exists():
        path.write_text(content, encoding="utf-8")


def ensure_common_files(root: Path) -> None:
    for relative_path, content in COMMON_FILES.items():
        write_if_missing(root / relative_path, content)


def ensure_question_files(root: Path, question_count: int, types: list[str]) -> None:
    skill_root = Path(__file__).resolve().parents[1]
    template_root = skill_root / "assets" / "code_templates"

    for index in range(1, question_count + 1):
        problem_type = types[index - 1] if index - 1 < len(types) else "unknown"
        if problem_type in TYPE_TO_TEMPLATE:
            script_name = f"代码/code_问题{index}_{problem_type}.py"
        else:
            script_name = f"代码/code_问题{index}_待定模型.py"
        result_name = f"结果/问题{index}_结果汇总.csv"
        figure_note_name = f"图片/问题{index}_配图说明.md"

        target_script = root / script_name
        if not target_script.exists():
            template_name = TYPE_TO_TEMPLATE.get(problem_type)
            if template_name:
                shutil.copyfile(template_root / template_name, target_script)
                replace_problem_tag(target_script, f"问题{index}")
            else:
                target_script.write_text(
                    QUESTION_SCRIPT_TEMPLATE.format(index=index), encoding="utf-8"
                )
        write_if_missing(
            root / result_name,
            QUESTION_RESULT_TEMPLATE.format(index=index, script_name=Path(script_name).name),
        )
        write_if_missing(
            root / figure_note_name,
            f"# 问题{index}配图说明\n\n## 建议生成哪些图\n\n## 每张图对应什么结论\n",
        )

    append_question_sections(root / "文档/方案.md", question_count)
    append_question_sections(root / "文档/解题思路.md", question_count)
    append_question_sections(root / "文档/问题-方法对照表.md", question_count)
    append_question_sections(root / "文档/解题过程.md", question_count)
    append_question_sections(root / "文档/模型解释_小白版.md", question_count)
    append_question_sections(root / "文档/模型解释_专业版.md", question_count)


def append_question_sections(path: Path, question_count: int) -> None:
    text = path.read_text(encoding="utf-8")
    updated = text
    for index in range(1, question_count + 1):
        marker = f"## 问题{index}"
        if marker not in updated:
            updated = updated.rstrip() + "\n\n" + QUESTION_DOC_TEMPLATE.format(index=index)
    if updated != text:
        path.write_text(updated + "\n", encoding="utf-8")


def replace_problem_tag(path: Path, tag: str) -> None:
    text = path.read_text(encoding="utf-8")
    path.write_text(text.replace("问题X", tag), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Initialize a full math modeling contest project scaffold."
    )
    parser.add_argument("project_dir", help="Target project directory")
    parser.add_argument(
        "--questions",
        type=int,
        default=4,
        help="How many question-specific code/result skeletons to generate (default: 4).",
    )
    parser.add_argument(
        "--types",
        nargs="*",
        default=[],
        help=(
            "Optional per-question types such as prediction evaluation optimization "
            "classification simulation."
        ),
    )
    args = parser.parse_args()

    root = Path(args.project_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)

    ensure_dirs(root)
    ensure_common_files(root)
    ensure_question_files(root, max(1, args.questions), [t.lower() for t in args.types])

    print(f"Initialized mathmodel scaffold at: {root}")
    print(f"Question scaffolds created: {max(1, args.questions)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

