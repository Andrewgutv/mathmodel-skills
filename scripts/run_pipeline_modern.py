from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_MARKDOWN = Path("文档") / "论文.md"
DEFAULT_FULL_DOCX = "论文_完整终稿.docx"
DEFAULT_TEMPLATE_DOCX = "论文_模板一致版.docx"
DEFAULT_TEMPLATE_NAMES = (
    "数学建模论文2026模板.docx",
    "数学建模论文2026模板_前置页.docx",
    "数学建模论文2026模板.doc",
)
PIPELINE_REPORT = Path("结果") / "pipeline_report.md"
RUN_LOG = Path("结果") / "run_log.md"
STAGES = ("parse", "solve", "summarize", "write", "word", "check")
STAGE_ORDER = {name: idx for idx, name in enumerate(STAGES)}
PLACEHOLDER_TOKENS = ("待填写", "示例指标")


@dataclass
class StepResult:
    name: str
    command: list[str]
    returncode: int
    stdout: str
    stderr: str
    skipped: bool = False
    reason: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the standard mathmodel pipeline for a project."
    )
    parser.add_argument("project_dir", help="Project root directory")
    parser.add_argument(
        "--stage",
        choices=("all", *STAGES),
        default="all",
        help="Run a single stage or the full pipeline.",
    )
    parser.add_argument(
        "--prompt",
        default="",
        help="Optional explicit prompt file path passed to parse_prompt_modern.py.",
    )
    parser.add_argument(
        "--template",
        default="",
        help="Optional explicit template path used for the template-aligned DOCX.",
    )
    parser.add_argument("--skip-parse", action="store_true")
    parser.add_argument("--skip-solve", action="store_true")
    parser.add_argument("--skip-summarize", action="store_true")
    parser.add_argument("--skip-write", action="store_true")
    parser.add_argument("--skip-word", action="store_true")
    parser.add_argument("--skip-check", action="store_true")
    return parser.parse_args()


def run_command(command: list[str], cwd: Path, name: str) -> StepResult:
    completed = subprocess.run(
        command,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return StepResult(
        name=name,
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )


def make_skipped(name: str, reason: str) -> StepResult:
    return StepResult(name=name, command=[], returncode=0, stdout="", stderr="", skipped=True, reason=reason)


def find_template(project_root: Path, explicit_template: str) -> Path | None:
    if explicit_template:
        path = Path(explicit_template).expanduser().resolve()
        return path if path.exists() else None

    doc_dir = project_root / "文档"
    for name in DEFAULT_TEMPLATE_NAMES:
        candidate = doc_dir / name
        if candidate.exists():
            return candidate

    for name in DEFAULT_TEMPLATE_NAMES:
        candidate = project_root / name
        if candidate.exists():
            return candidate
    return None


def ensure_standard_dirs(project_root: Path) -> None:
    for dirname in ("代码", "图片", "数据", "结果", "文档", "答辩"):
        (project_root / dirname).mkdir(parents=True, exist_ok=True)


def build_parse_command(project_root: Path, prompt: str) -> list[str]:
    command = [sys.executable, str(SCRIPT_DIR / "parse_prompt_modern.py"), str(project_root)]
    if prompt:
        command.extend(["--prompt", prompt])
    return command


def detect_solver_commands(project_root: Path) -> list[tuple[str, list[str]]]:
    code_dir = project_root / "代码"
    candidates = []

    main_script = code_dir / "main.py"
    run_all_script = code_dir / "run_all.py"
    if main_script.exists():
        candidates.append(("solve_main", [sys.executable, str(main_script)]))
        return candidates
    if run_all_script.exists():
        candidates.append(("solve_run_all", [sys.executable, str(run_all_script)]))
        return candidates

    question_scripts = sorted(code_dir.glob("code_问题*_*.py"))
    for script in question_scripts:
        candidates.append((f"solve_{script.stem}", [sys.executable, str(script)]))
    return candidates


def expected_question_numbers(project_root: Path) -> list[int]:
    mapping_path = project_root / "文档" / "问题-方法对照表.md"
    if not mapping_path.exists():
        return []
    text = mapping_path.read_text(encoding="utf-8")
    numbers = set()
    for match in re.findall(r"##\s+问题(\d+)", text):
        numbers.add(int(match))
    for match in re.findall(r"^\|\s*问题(\d+)\s*\|", text, flags=re.MULTILINE):
        numbers.add(int(match))
    return sorted(numbers)


def detect_question_count(project_root: Path) -> int:
    numbers = expected_question_numbers(project_root)
    return max(numbers) if numbers else 0


def detect_question_types(project_root: Path) -> list[str]:
    mapping_path = project_root / "文档" / "问题-方法对照表.md"
    if not mapping_path.exists():
        return []

    lines = mapping_path.read_text(encoding="utf-8").splitlines()
    types: list[str] = []
    for line in lines:
        if not line.startswith("| 问题"):
            continue
        if "|---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        if cells[0] == "问题":
            continue
        inferred = cells[2]
        if inferred in {"prediction", "evaluation", "optimization", "classification", "simulation", "estimation"}:
            types.append(inferred)
        else:
            types.append("unknown")
    return types


def build_init_command(project_root: Path, question_count: int, question_types: list[str]) -> list[str]:
    command = [
        sys.executable,
        str(SCRIPT_DIR / "init_project.py"),
        str(project_root),
        "--questions",
        str(max(1, question_count)),
    ]
    if question_types:
        command.append("--types")
        command.extend(question_types[:question_count])
    return command


def build_summarize_command(project_root: Path) -> list[str]:
    return [sys.executable, str(SCRIPT_DIR / "summarize_results_modern.py"), str(project_root)]


def build_write_command(project_root: Path) -> list[str]:
    return [sys.executable, str(SCRIPT_DIR / "backfill_results_modern.py"), str(project_root)]


def build_full_word_command(project_root: Path) -> list[str]:
    markdown = project_root / DEFAULT_MARKDOWN
    return [
        sys.executable,
        str(SCRIPT_DIR / "build_word_modern.py"),
        str(markdown),
        "--output",
        DEFAULT_FULL_DOCX,
        "--no-template-search",
    ]


def build_template_word_command(project_root: Path, template_path: Path) -> list[str]:
    return [
        sys.executable,
        str(SCRIPT_DIR / "merge_template_word.py"),
        str(project_root / "文档" / DEFAULT_FULL_DOCX),
        "--template",
        str(template_path),
        "--output",
        DEFAULT_TEMPLATE_DOCX,
    ]


def build_check_command(project_root: Path) -> list[str]:
    markdown = project_root / DEFAULT_MARKDOWN
    return [
        sys.executable,
        str(SCRIPT_DIR / "check_paper_v2.py"),
        str(markdown),
        "--project-root",
        str(project_root),
        "--mode",
        "paper",
    ]


def should_stage_run(requested_stage: str, current_stage: str, skip_flag: bool) -> bool:
    if skip_flag:
        return False
    if requested_stage == "all":
        return True
    return requested_stage == current_stage


def stage_allowed_by_dependency(requested_stage: str, current_stage: str) -> bool:
    if requested_stage == "all":
        return True
    return STAGE_ORDER[current_stage] <= STAGE_ORDER[requested_stage]


def record_run_log(project_root: Path, results: list[StepResult]) -> None:
    log_path = project_root / RUN_LOG
    lines = ["# Run Log", ""]
    for result in results:
        lines.append(f"## {result.name}")
        if result.skipped:
            lines.append("- Status: skipped")
            lines.append(f"- Reason: {result.reason}")
        else:
            lines.append(f"- Status: {'success' if result.returncode == 0 else 'failed'}")
            lines.append(f"- Command: `{' '.join(result.command)}`")
            if result.stdout:
                lines.extend(["- Stdout:", "", "```text", result.stdout, "```"])
            if result.stderr:
                lines.extend(["- Stderr:", "", "```text", result.stderr, "```"])
        lines.append("")
    log_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_report(project_root: Path, results: list[StepResult], template_path: Path | None) -> None:
    report_path = project_root / PIPELINE_REPORT
    report_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Pipeline Report",
        "",
        f"- Project root: `{project_root}`",
        f"- Template file: `{template_path}`" if template_path else "- Template file: not detected",
        "",
        "## Steps",
        "",
    ]

    for result in results:
        if result.skipped:
            lines.extend(
                [
                    f"### {result.name}",
                    "- Status: skipped",
                    f"- Reason: {result.reason}",
                    "",
                ]
            )
            continue

        lines.extend(
            [
                f"### {result.name}",
                f"- Status: {'success' if result.returncode == 0 else 'failed'}",
                f"- Command: `{' '.join(result.command)}`",
            ]
        )
        if result.stdout:
            lines.extend(["- Stdout:", "", "```text", result.stdout, "```"])
        if result.stderr:
            lines.extend(["- Stderr:", "", "```text", result.stderr, "```"])
        lines.append("")

    report_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def csv_has_meaningful_rows(path: Path) -> bool:
    try:
        content = path.read_text(encoding="utf-8-sig")
    except OSError:
        return False
    normalized = content.strip()
    if not normalized or "数值" not in normalized:
        return False
    return not any(token in normalized for token in PLACEHOLDER_TOKENS)


def validate_result_outputs(project_root: Path) -> tuple[bool, str]:
    result_dir = project_root / "结果"
    expected_numbers = expected_question_numbers(project_root)
    if expected_numbers:
        missing = []
        placeholders = []
        for number in expected_numbers:
            path = result_dir / f"问题{number}_结果汇总.csv"
            if not path.exists():
                missing.append(number)
                continue
            if not csv_has_meaningful_rows(path):
                placeholders.append(number)
        if missing:
            formatted = ", ".join(str(number) for number in missing)
            return False, f"Missing per-question result CSVs for: {formatted}"
        if placeholders:
            formatted = ", ".join(str(number) for number in placeholders)
            return False, f"Per-question result CSVs still look like placeholders for: {formatted}"
        return True, ""

    discovered = list(result_dir.glob("问题*_结果汇总.csv"))
    if not discovered:
        return False, "No 问题*_结果汇总.csv files were generated under 结果/."
    placeholder_files = [path.name for path in discovered if not csv_has_meaningful_rows(path)]
    if placeholder_files:
        return False, "Per-question result CSVs still look like placeholders: " + ", ".join(placeholder_files)
    return True, ""


def run_parse_stage(project_root: Path, args: argparse.Namespace) -> list[StepResult]:
    return [run_command(build_parse_command(project_root, args.prompt), project_root, "parse_prompt")]


def run_solve_stage(project_root: Path) -> list[StepResult]:
    solver_commands = detect_solver_commands(project_root)
    if not solver_commands:
        question_count = detect_question_count(project_root)
        question_types = detect_question_types(project_root)
        if question_count > 0:
            init_result = run_command(
                build_init_command(project_root, question_count, question_types),
                project_root,
                "auto_init_project",
            )
            solver_commands = detect_solver_commands(project_root)
            if init_result.returncode == 0 and solver_commands:
                results: list[StepResult] = [init_result]
                for name, command in solver_commands:
                    result = run_command(command, project_root, name)
                    results.append(result)
                    if result.returncode != 0:
                        return results

                is_valid, message = validate_result_outputs(project_root)
                if not is_valid:
                    results.append(
                        StepResult(
                            name="solve_output_check",
                            command=[],
                            returncode=1,
                            stdout="",
                            stderr=message,
                        )
                    )
                return results
            return [init_result]

        return [
            StepResult(
                name="solve",
                command=[],
                returncode=1,
                stdout="",
                stderr="No solver entry found under 代码/. Expected 代码/main.py, 代码/run_all.py, or code_问题*_*.py.",
            )
        ]

    results: list[StepResult] = []
    for name, command in solver_commands:
        result = run_command(command, project_root, name)
        results.append(result)
        if result.returncode != 0:
            break

    if all(result.returncode == 0 for result in results):
        is_valid, message = validate_result_outputs(project_root)
        if not is_valid:
            results.append(
                StepResult(
                    name="solve_output_check",
                    command=[],
                    returncode=1,
                    stdout="",
                    stderr=message,
                )
            )
    return results


def run_summarize_stage(project_root: Path) -> list[StepResult]:
    is_valid, message = validate_result_outputs(project_root)
    if not is_valid:
        return [make_skipped("summarize_results", message)]
    return [run_command(build_summarize_command(project_root), project_root, "summarize_results")]


def run_write_stage(project_root: Path) -> list[StepResult]:
    combined = project_root / "结果" / "综合结果汇总.csv"
    if not combined.exists():
        return [make_skipped("backfill_results", "综合结果汇总.csv is missing; summarize stage must succeed first.")]
    return [run_command(build_write_command(project_root), project_root, "backfill_results")]


def run_word_stage(project_root: Path, template_path: Path | None) -> list[StepResult]:
    markdown_path = project_root / DEFAULT_MARKDOWN
    if not markdown_path.exists():
        return [
            make_skipped("build_full_word", f"Markdown file not found: {markdown_path}"),
            make_skipped("build_template_word", "Skipped because markdown input is missing."),
        ]

    combined = project_root / "结果" / "综合结果汇总.csv"
    if not combined.exists():
        return [
            make_skipped("build_full_word", "综合结果汇总.csv is missing; write stage must succeed first."),
            make_skipped("build_template_word", "Skipped because summarize/write prerequisites are missing."),
        ]

    results = [run_command(build_full_word_command(project_root), project_root, "build_full_word")]
    if results[0].returncode != 0:
        results.append(make_skipped("build_template_word", "Skipped because full DOCX generation failed."))
        return results

    if template_path:
        results.append(run_command(build_template_word_command(project_root, template_path), project_root, "build_template_word"))
    else:
        results.append(make_skipped("build_template_word", "No teacher template detected or provided."))
    return results


def run_check_stage(project_root: Path) -> list[StepResult]:
    markdown_path = project_root / DEFAULT_MARKDOWN
    if not markdown_path.exists():
        return [make_skipped("check_paper", f"Markdown file not found: {markdown_path}")]
    return [run_command(build_check_command(project_root), project_root, "check_paper")]


def append_stage(results: list[StepResult], stage_results: list[StepResult]) -> bool:
    results.extend(stage_results)
    return all(result.skipped or result.returncode == 0 for result in stage_results)


def main() -> int:
    args = parse_args()
    project_root = Path(args.project_dir).expanduser().resolve()
    ensure_standard_dirs(project_root)
    template_path = find_template(project_root, args.template)

    results: list[StepResult] = []
    pipeline_ok = True

    stage_configs = [
        ("parse", args.skip_parse, lambda: run_parse_stage(project_root, args)),
        ("solve", args.skip_solve, lambda: run_solve_stage(project_root)),
        ("summarize", args.skip_summarize, lambda: run_summarize_stage(project_root)),
        ("write", args.skip_write, lambda: run_write_stage(project_root)),
        ("word", args.skip_word, lambda: run_word_stage(project_root, template_path)),
        ("check", args.skip_check, lambda: run_check_stage(project_root)),
    ]

    for stage_name, skip_flag, runner in stage_configs:
        if not stage_allowed_by_dependency(args.stage, stage_name):
            continue
        if not should_stage_run(args.stage, stage_name, skip_flag):
            results.append(make_skipped(stage_name, "Stage filter or skip flag prevented execution."))
            continue
        if args.stage == "all" and not pipeline_ok:
            results.append(make_skipped(stage_name, "Skipped because an earlier stage failed."))
            continue
        stage_ok = append_stage(results, runner())
        if not stage_ok:
            pipeline_ok = False

    record_run_log(project_root, results)
    write_report(project_root, results, template_path)

    failures = [result for result in results if not result.skipped and result.returncode != 0]
    for result in results:
        if result.skipped:
            print(f"[SKIP] {result.name}: {result.reason}")
        elif result.returncode == 0:
            print(f"[ OK ] {result.name}")
        else:
            print(f"[FAIL] {result.name}")

    print(f"Pipeline report: {project_root / PIPELINE_REPORT}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
