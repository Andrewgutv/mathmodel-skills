# Pipeline Report

- Project root: `D:\workspace\skills\mathmodel\examples\docx_prompt`
- Template file: not detected

## Steps

### parse_prompt
- Status: success
- Command: `C:\Users\Andrew\AppData\Local\Programs\Python\Python312\python.exe D:\workspace\skills\mathmodel\scripts\parse_prompt_modern.py D:\workspace\skills\mathmodel\examples\docx_prompt`
- Stdout:

```text
PARSE_STATUS: text_extracted
Prompt source: D:\workspace\skills\mathmodel\examples\docx_prompt\PROMPT_PLACEHOLDER.docx
Prompt kind: docx
Prompt detail: Extracted text from DOCX prompt.
Detected questions: 2
Attachment inventory written: D:\workspace\skills\mathmodel\examples\docx_prompt\����\����˵����.md
Updated: D:\workspace\skills\mathmodel\examples\docx_prompt\�ĵ�\����.md
Updated: D:\workspace\skills\mathmodel\examples\docx_prompt\�ĵ�\����˼·.md
Updated: D:\workspace\skills\mathmodel\examples\docx_prompt\�ĵ�\����-�������ձ�.md
```

### solve_main
- Status: success
- Command: `C:\Users\Andrew\AppData\Local\Programs\Python\Python312\python.exe D:\workspace\skills\mathmodel\examples\docx_prompt\代码\main.py`

### summarize_results
- Status: success
- Command: `C:\Users\Andrew\AppData\Local\Programs\Python\Python312\python.exe D:\workspace\skills\mathmodel\scripts\summarize_results_modern.py D:\workspace\skills\mathmodel\examples\docx_prompt`
- Stdout:

```text
Generated summary CSV: D:\workspace\skills\mathmodel\examples\docx_prompt\���\�ۺϽ������.csv
Rows written: 2
```

### backfill_results
- Status: success
- Command: `C:\Users\Andrew\AppData\Local\Programs\Python\Python312\python.exe D:\workspace\skills\mathmodel\scripts\backfill_results_modern.py D:\workspace\skills\mathmodel\examples\docx_prompt`
- Stdout:

```text
Backfilled results into: D:\workspace\skills\mathmodel\examples\docx_prompt\�ĵ�\����-�������ձ�.md
Backfilled results into: D:\workspace\skills\mathmodel\examples\docx_prompt\�ĵ�\����.md
Backfilled results into: D:\workspace\skills\mathmodel\examples\docx_prompt\���\���׼��.md
```

### word
- Status: skipped
- Reason: Stage filter or skip flag prevented execution.

### check_paper
- Status: success
- Command: `C:\Users\Andrew\AppData\Local\Programs\Python\Python312\python.exe D:\workspace\skills\mathmodel\scripts\check_paper_v2.py D:\workspace\skills\mathmodel\examples\docx_prompt\文档\论文.md --project-root D:\workspace\skills\mathmodel\examples\docx_prompt --mode paper`
- Stdout:

```text
STATUS: PASS_WITH_TEMPLATE_WARNING
MODE: paper
Paper check passed.
- Model layer: solver entry detected.
- Model layer: expected question count = 2.
- Model layer: detected 2 per-question result CSV file(s).
- Model layer: �ۺϽ������.csv has 2 row(s).
- Document layer: result summary marker detected in ����.md.
- Object layer: figure inventory exists.
- Object layer: figure refs = 1
- Object layer: table refs = 1
- Object layer: formula markers = 1
- Object layer: markdown images = 1
- Object layer: real figure files = 1
- Delivery layer: required deliverables for current mode are present.
- DOCX checked: ����_�����ո�.docx (paragraphs=35, tables=1)
- Delivery layer: template-aligned DOCX not found; acceptable when no teacher template was requested.
```
