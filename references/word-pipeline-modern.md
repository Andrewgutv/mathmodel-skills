# Word Pipeline Modern

## Goal

Generate a stable contest-paper Word delivery without forcing the user to hand-edit large amounts of formatting.

The delivery artifacts are layered:

- `文档/论文_完整终稿.docx`
- `文档/论文_模板一致版.docx` when a teacher template is available and compatible

## Current Entry Points

- `scripts/build_word_modern.py`
- `scripts/merge_template_word_modern.py`

## Environment Rules

Template merge is only supported when all of the following hold:

- Windows environment
- Microsoft Word is installed
- Word COM automation is available

If any of these fail:

- keep the full-body DOCX as the stable delivery artifact
- report the merge failure category clearly

## Failure Categories

Modern template merge reports explicit failure categories:

- `UNSUPPORTED_PLATFORM`
- `WORD_COM_UNAVAILABLE`
- `WORD_COM_UNKNOWN`
- `TEMPLATE_INCOMPATIBLE`
- `WORD_MERGE_RUNTIME`
- `OUTPUT_VALIDATION`

## Compatibility Checks

Before merge, the template should contain:

- an abstract heading `摘要`
- a title placeholder `论文题目`
- detectable front matter such as `目录` or TOC styles

If these are missing, merge should fail fast as a template compatibility problem instead of producing a misleading half-valid file.

## Validation

Minimum validation after merge:

- output DOCX exists and is readable
- exactly one heading-level `摘要`
- front matter still contains expected material such as `目录` and `承诺书` when available

If validation fails:

- keep the full-body DOCX
- report the issue as template-specific
