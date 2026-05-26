# pdf_scanned_prompt 预期说明

## 输入类型

- 扫描版 PDF 题面

## 预期用途

- 验证 `parse_prompt_modern.py` 的 OCR 分支和失败分类

## 当前预期

- 在无 OCR 能力时，`parse` 应明确返回 `ocr_unavailable` 或 `ocr_failed`
- 不应误报为 `zero_questions_detected`

## 后续可扩展

- 补充真实扫描版 PDF
- 在可用 OCR 环境下加入成功案例
