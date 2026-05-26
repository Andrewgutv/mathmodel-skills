# docx_prompt 预期说明

## 输入类型

- DOCX 题面

## 预期用途

- 验证 `parse_prompt_modern.py` 的 DOCX 发现与文本抽取分支

## 当前预期

- 能识别根目录中的 `.docx` 题面
- 若段落非空，应进入 `text_extracted`

## 后续可扩展

- 补充带多问题结构的真实 DOCX 题面
