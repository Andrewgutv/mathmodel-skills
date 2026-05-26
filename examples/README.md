# MathModel 示例项目

本目录用于放置最小样例项目，服务于以下目标：

- 覆盖现代版 `parse` 支持的题面类型
- 为 smoke test 提供稳定输入
- 作为后续回归验证和文档示例

当前包含四类最小样例：

- `pdf_text_prompt/`
- `pdf_scanned_prompt/`
- `docx_prompt/`
- `markdown_prompt/`

每个样例目录都包含：

- 题面文件
- `EXPECTATION.md`
- 最小项目结构占位目录

说明：

- 这些样例当前用于验证输入发现、输入分类和最小结构契约
- 后续可以继续扩展为完整可跑通样例
