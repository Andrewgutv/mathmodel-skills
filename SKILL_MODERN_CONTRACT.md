# MathModel Modern Contract

This document defines the practical contract for the modernized workflow.

Use this file as the source of truth for the current modern entry points until the legacy `SKILL.md` is fully replaced or cleaned.

## Core Goal

The repository is not just a prompt parser or paper formatter.

The real goal is:

- solve math modeling problems in a stable way
- produce traceable result files
- backfill those results into a paper
- generate a Word paper whose format may tolerate minor defects
- but never let tables, figures, or formulas become incorrect or misleading

## Quality Priority

The quality order for this repository is:

1. Correct modeling logic
2. Correct numeric results
3. Correct traceability from code -> results -> paper
4. Correct tables, figures, and formulas
5. Acceptable paper formatting

This means:

- small formatting defects are acceptable for now
- incorrect tables are not acceptable
- incorrect figures are not acceptable
- incorrect formulas are not acceptable

## Recommended Entry Points

- `scripts/run_pipeline_modern.py`
- `scripts/parse_prompt_modern.py`
- `scripts/summarize_results_modern.py`
- `scripts/backfill_results_modern.py`
- `scripts/check_paper_v2.py`
- `scripts/build_word_modern.py`
- `scripts/merge_template_word_modern.py`

## Supported Prompt Inputs

The modern parse flow supports:

- `pdf`
- `docx`
- `md`
- single-image prompts

If a prompt is missing, unsupported, empty, OCR-unavailable, or OCR-failed, the parser should fail clearly instead of pretending the problem has zero questions.

## Parse Statuses

The modern parser may emit:

- `text_extracted`
- `ocr_used`
- `ocr_unavailable`
- `ocr_failed`
- `prompt_empty`
- `zero_questions_detected`
- `failed`

Rules:

- `ocr_unavailable / ocr_failed / prompt_empty / failed` with no extracted text means parse failure
- `zero_questions_detected` means text exists but no structured question layout was detected

## Result Validation Rules

The modern `solve` and `summarize` stages require:

- every expected question must have a corresponding result file
- every per-question result file must be non-placeholder
- the combined result file must be built from real per-question results

No partial-question success should silently continue through the rest of the pipeline.

## Paper Check Modes

Modern check supports:

- `paper`
- `full_delivery`
- `defense`

### paper

Required:

- structural paper sections exist
- reference list exists
- result files exist and are non-placeholder
- figure inventory exists
- paper contains result-driven content

Not required by default:

- AI usage declaration
- defense files
- template-aligned DOCX

### full_delivery

On top of `paper`, additionally requires:

- `文档/论文_完整终稿.docx`
- defense materials

### defense

Focuses on:

- paper structure
- result consistency
- defense material existence

## Non-Negotiable Object Rules

These three object classes must not be wrong:

### Tables

- table values must come from result files or explicit data sources
- no placeholder rows may remain
- if a table is mentioned in the paper, its content must be consistent with the result files

### Figures

- figures must correspond to actual generated or declared artifacts
- the paper must not claim a figure that does not exist
- figure references must not point to the wrong question

### Formulas

- formulas must not be silently dropped
- formula text in markdown/docx must remain visible and interpretable
- if a numeric result depends on a formula, the surrounding explanation must still match the computed result

## Current Regression Coverage

Full regression examples:

- Markdown complete regression example
- DOCX complete regression example
- PDF complete regression example

Object-complete regression examples:

- Markdown example: tables + figures + formulas
- DOCX example: tables + figures + formulas

Prompt skeleton examples:

- scanned PDF prompt skeleton
- single-image prompt skeleton

## Current Known Boundaries

- template merge still depends on Windows + Microsoft Word
- `merge_template_word_modern.py` has environment checks, but template-aligned output is not yet in smoke tests
- scanned PDF and single-image prompt examples are still not full regression examples
- some legacy documents outside the modern path may still contain historical encoding issues

## Current Guidance

During the modern migration period:

- prefer modern scripts
- do not treat legacy scripts as the primary implementation
- prioritize correctness of results, tables, figures, and formulas over perfect formatting
