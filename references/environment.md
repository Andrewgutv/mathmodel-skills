# Environment

## Default Assumptions
- Use this skill primarily on Windows with PowerShell.
- Prefer Python 3.10 or newer.
- Prefer `pandoc` for Markdown to DOCX conversion.
- Treat teacher or school DOCX templates as user-provided assets unless they already exist in the project folder.

## Basic Dependency Checklist
- `python --version`
- `pandoc --version`
- A working Python environment that can install packages if scripts need `python-docx`, `pandas`, `matplotlib`, `numpy`, or `scipy`

## Recommended Python Packages
- `python-docx` for DOCX post-processing
- `pandas` for tabular data
- `numpy` for numerical work
- `scipy` for optimization, interpolation, and statistics
- `matplotlib` for figures

Install only what the current task actually needs. Do not force heavy dependencies for paper-only tasks.

## Windows Command Pattern

Run Python scripts through PowerShell when path or encoding behavior is inconsistent:

```bash
powershell.exe -Command "python build_word.py"
```

If `python` does not resolve, use the explicit interpreter path available on the machine.

## Template Dependency Rule
- If the user wants a teacher-template DOCX, check whether the template file already exists in `文档/`.
- If it does not exist, state the missing dependency explicitly and continue with the closest reproducible Markdown or plain DOCX output.
