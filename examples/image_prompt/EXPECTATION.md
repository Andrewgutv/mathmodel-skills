# image_prompt 预期说明

## 输入类型

- 单张图片题面

## 预期用途

- 验证 `parse_prompt_modern.py` 的图片 OCR 输入发现逻辑

## 当前预期

- 在无 OCR 能力时，`parse` 应明确失败，而不是静默继续

## 说明

- 该样例目录用于补充“图片题面”这一输入类型
- 若后续坚持仅保留四类目录，可把它并入 `pdf_scanned_prompt/`
