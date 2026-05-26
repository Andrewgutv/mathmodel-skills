# MathModel Skill

Repository for a delivery-oriented math modeling workflow: prompt parsing, project scaffolding, result aggregation, paper backfill, Word generation, and delivery checks.

## Recommended Entry Points

Use the modern entry points by default:

- [scripts/run_pipeline_modern.py](/D:/workspace/skills/mathmodel/scripts/run_pipeline_modern.py)
- [scripts/parse_prompt_modern.py](/D:/workspace/skills/mathmodel/scripts/parse_prompt_modern.py)
- [scripts/summarize_results_modern.py](/D:/workspace/skills/mathmodel/scripts/summarize_results_modern.py)
- [scripts/backfill_results_modern.py](/D:/workspace/skills/mathmodel/scripts/backfill_results_modern.py)
- [scripts/check_paper_v2.py](/D:/workspace/skills/mathmodel/scripts/check_paper_v2.py)
- [scripts/build_word_modern.py](/D:/workspace/skills/mathmodel/scripts/build_word_modern.py)
- [scripts/merge_template_word_modern.py](/D:/workspace/skills/mathmodel/scripts/merge_template_word_modern.py)

Compatibility wrappers still exist:

- [scripts/run_pipeline.py](/D:/workspace/skills/mathmodel/scripts/run_pipeline.py)
- [scripts/parse_prompt.py](/D:/workspace/skills/mathmodel/scripts/parse_prompt.py)
- [scripts/check_paper.py](/D:/workspace/skills/mathmodel/scripts/check_paper.py)
- [scripts/build_word.py](/D:/workspace/skills/mathmodel/scripts/build_word.py)
- [scripts/merge_template_word.py](/D:/workspace/skills/mathmodel/scripts/merge_template_word.py)

## Supported Prompt Inputs

The modern parse flow supports:

- `pdf`
- `docx`
- `md`
- single-image prompts

The parser distinguishes:

- direct text extraction
- OCR success
- OCR unavailable
- OCR failure
- empty prompt
- text extracted but zero structured questions detected

## Pipeline Stages

Standard stages:

- `parse`
- `solve`
- `summarize`
- `write`
- `word`
- `check`

The current modernized areas include:

- input discovery and failure classification
- per-question result completeness checks
- result aggregation
- result backfill
- paper checking
- Word full-body generation
- template merge environment detection

## Check Modes

[check_paper_v2.py](/D:/workspace/skills/mathmodel/scripts/check_paper_v2.py) supports:

- `paper`
- `full_delivery`
- `defense`

Recommended usage:

```powershell
python scripts/check_paper_v2.py <project>\文档\论文.md --project-root <project> --mode paper
```

Only require an AI declaration when explicitly needed:

```powershell
--require-ai-declaration
```

## Examples And Tests

Examples:

- [examples/](/D:/workspace/skills/mathmodel/examples)

Current example coverage:

- PDF complete regression example
- DOCX complete regression example
- Markdown complete regression example
- scanned PDF prompt skeleton
- single-image prompt skeleton

Smoke test:

- [tests/smoke_test.py](/D:/workspace/skills/mathmodel/tests/smoke_test.py)

Run:

```powershell
python tests/smoke_test.py
```

The smoke test covers:

- Markdown complete regression example
- DOCX complete regression example
- PDF complete regression example
- Word full-body generation for the Markdown example

## Object Quality Priority

The repository allows small paper-formatting defects for now, but these objects must not be wrong:

- tables
- figures
- formulas

The current regression system already covers these objects with real examples in the Markdown and DOCX example projects.

## Word Merge

Modern template merge entry:

- [scripts/merge_template_word_modern.py](/D:/workspace/skills/mathmodel/scripts/merge_template_word_modern.py)

Reference:

- [references/word-pipeline-modern.md](/D:/workspace/skills/mathmodel/references/word-pipeline-modern.md)

Current behavior:

- fail fast on unsupported platform or missing Word COM automation
- fail fast on obviously incompatible templates
- preserve the full-body DOCX as the stable fallback artifact
- report explicit failure categories

## Current Known Boundaries

- template merge still depends on Windows + Microsoft Word
- template-aligned DOCX is not yet covered by smoke tests
- scanned PDF and single-image prompt examples are still skeletons
- some legacy documentation outside the modern path may still contain historical encoding issues

## Minimum Release Standard

Before calling the repository stable for delivery, the minimum bar should be:

- modern entry scripts are present and parse cleanly
- prompt examples exist for the supported input classes
- smoke test passes
- at least one complete example runs `parse -> solve -> summarize -> write -> check -> word`
- Word merge failure categories are explicit and actionable

## Related Documents

- [RECTIFICATION_PLAN.md](/D:/workspace/skills/mathmodel/RECTIFICATION_PLAN.md)
- [P0_MIGRATION_NOTE.md](/D:/workspace/skills/mathmodel/P0_MIGRATION_NOTE.md)
- [SKILL_MODERN_CONTRACT.md](/D:/workspace/skills/mathmodel/SKILL_MODERN_CONTRACT.md)
- [references/word-pipeline-modern.md](/D:/workspace/skills/mathmodel/references/word-pipeline-modern.md)
