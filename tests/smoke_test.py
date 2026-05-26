from __future__ import annotations

import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES_DIR = REPO_ROOT / "examples"
SCRIPTS_DIR = REPO_ROOT / "scripts"
MARKDOWN_EXAMPLE = EXAMPLES_DIR / "markdown_prompt"
DOCX_EXAMPLE = EXAMPLES_DIR / "docx_prompt"
PDF_TEXT_EXAMPLE = EXAMPLES_DIR / "pdf_text_prompt"

REQUIRED_EXAMPLE_DIRS = [
    "pdf_text_prompt",
    "pdf_scanned_prompt",
    "docx_prompt",
    "markdown_prompt",
]

REQUIRED_SCRIPT_FILES = [
    "parse_prompt.py",
    "parse_prompt_modern.py",
    "run_pipeline.py",
    "run_pipeline_modern.py",
    "check_paper.py",
    "check_paper_v2.py",
    "summarize_results_modern.py",
    "backfill_results_modern.py",
    "build_word_modern.py",
    "merge_template_word_modern.py",
]


def require(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def check_examples(failures: list[str]) -> None:
    require(EXAMPLES_DIR.exists(), f"Missing examples directory: {EXAMPLES_DIR}", failures)
    for name in REQUIRED_EXAMPLE_DIRS:
        example_dir = EXAMPLES_DIR / name
        require(example_dir.exists(), f"Missing example directory: {example_dir}", failures)
        require((example_dir / "EXPECTATION.md").exists(), f"Missing EXPECTATION.md in {example_dir}", failures)


def check_scripts(failures: list[str]) -> None:
    for name in REQUIRED_SCRIPT_FILES:
        path = SCRIPTS_DIR / name
        require(path.exists(), f"Missing script: {path}", failures)


def check_wrappers(failures: list[str]) -> None:
    wrapper_expectations = {
        "parse_prompt.py": "from parse_prompt_modern import main",
        "run_pipeline.py": "from run_pipeline_modern import main",
        "check_paper.py": "from check_paper_v2 import main",
    }
    for name, needle in wrapper_expectations.items():
        text = (SCRIPTS_DIR / name).read_text(encoding="utf-8")
        require(needle in text, f"{name} does not delegate to its current implementation", failures)


def run_pipeline(example_root: Path, args: list[str], failures: list[str], label: str) -> None:
    command = [sys.executable, str(SCRIPTS_DIR / "run_pipeline_modern.py"), str(example_root), *args]
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    require(completed.returncode == 0, f"{label} failed: {completed.stderr or completed.stdout}", failures)


def check_markdown_pipeline(failures: list[str]) -> None:
    run_pipeline(MARKDOWN_EXAMPLE, ["--stage", "all", "--skip-word"], failures, "Markdown example pipeline")
    result_files = [
        MARKDOWN_EXAMPLE / "结果" / "问题1_结果汇总.csv",
        MARKDOWN_EXAMPLE / "结果" / "问题2_结果汇总.csv",
        MARKDOWN_EXAMPLE / "结果" / "综合结果汇总.csv",
        MARKDOWN_EXAMPLE / "结果" / "pipeline_report.md",
        MARKDOWN_EXAMPLE / "结果" / "run_log.md",
    ]
    for path in result_files:
        require(path.exists(), f"Expected pipeline artifact missing: {path}", failures)


def check_word_stage(failures: list[str]) -> None:
    run_pipeline(MARKDOWN_EXAMPLE, ["--stage", "word"], failures, "Markdown example word stage")
    output_docx = MARKDOWN_EXAMPLE / "文档" / "论文_完整终稿.docx"
    require(output_docx.exists(), f"Expected DOCX missing after word stage: {output_docx}", failures)


def check_docx_pipeline(failures: list[str]) -> None:
    run_pipeline(DOCX_EXAMPLE, ["--stage", "all", "--skip-word"], failures, "DOCX example pipeline")
    result_files = [
        DOCX_EXAMPLE / "结果" / "问题1_结果汇总.csv",
        DOCX_EXAMPLE / "结果" / "问题2_结果汇总.csv",
        DOCX_EXAMPLE / "结果" / "综合结果汇总.csv",
        DOCX_EXAMPLE / "结果" / "pipeline_report.md",
        DOCX_EXAMPLE / "结果" / "run_log.md",
    ]
    for path in result_files:
        require(path.exists(), f"Expected DOCX pipeline artifact missing: {path}", failures)


def check_pdf_text_pipeline(failures: list[str]) -> None:
    command = [
        sys.executable,
        str(SCRIPTS_DIR / "run_pipeline_modern.py"),
        str(PDF_TEXT_EXAMPLE),
        "--stage",
        "all",
        "--skip-word",
    ]
    completed = subprocess.run(
        command,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    require(completed.returncode == 0, f"PDF text example pipeline failed: {completed.stderr or completed.stdout}", failures)

    result_files = [
        PDF_TEXT_EXAMPLE / "结果" / "问题1_结果汇总.csv",
        PDF_TEXT_EXAMPLE / "结果" / "问题2_结果汇总.csv",
        PDF_TEXT_EXAMPLE / "结果" / "综合结果汇总.csv",
        PDF_TEXT_EXAMPLE / "结果" / "pipeline_report.md",
        PDF_TEXT_EXAMPLE / "结果" / "run_log.md",
    ]
    for path in result_files:
        require(path.exists(), f"Expected PDF text pipeline artifact missing: {path}", failures)


def main() -> int:
    failures: list[str] = []
    check_examples(failures)
    check_scripts(failures)
    check_wrappers(failures)
    check_markdown_pipeline(failures)
    check_word_stage(failures)
    check_docx_pipeline(failures)
    check_pdf_text_pipeline(failures)

    if failures:
        print("SMOKE TEST FAILED")
        for item in failures:
            safe = item.encode("ascii", "backslashreplace").decode("ascii")
            print(f"- {safe}")
        return 1

    print("SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
