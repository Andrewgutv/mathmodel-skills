# pdf_text_prompt 预期说明

## 输入类型

- 文字型 PDF 题面

## 预期用途

- 验证 `parse_prompt_modern.py` 能发现 PDF 题面
- 验证在无需 OCR 时进入 `text_extracted`

## 当前预期

- 当前版本主要提供完整项目骨架与求解回归结构
- 待替换为真实文字型 PDF 后，再升级为严格的 PDF 文本抽取回归样例
- 因当前占位 PDF 不是可抽取题面，不应将本目录视为完整 parse 回归样例

## 后续可扩展

- 补充真实文字版 PDF
- 补充配套附件与完整项目回归
