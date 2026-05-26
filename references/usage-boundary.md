# Usage Boundary

## Stable Today

以下能力目前已经验证过，属于稳定能力：

- 初始化标准项目结构
- 使用统一入口 `scripts/run_pipeline.py`
- 执行 `parse -> solve -> summarize -> write -> word -> check`
- 将结果统一收束到 `结果/`
- 从 `结果/` 回填论文与答辩材料
- 生成 `文档/论文_完整终稿.docx`
- 对扫描版 PDF 使用 OCR fallback 进行题面识别

## Semi-Automatic Today

以下能力可用，但仍属于半自动或需人工复核：

- `文档/论文_模板一致版.docx` 生成
- 模板前置页保留后的残留提示语清理
- 不同学校模板之间的通用兼容
- 高质量论文正文自动生成
- 高质量答辩 PPT 页内文案自动生成

## Not Promised

当前 skill 不承诺以下事项：

- 任意老师模板都能一次性无人工生成完全干净的模板版 Word
- 任意数学建模题都能自动给出高质量最终模型
- 只靠模板脚本就能替代最终人工检查

## Recommended Usage

最稳的使用方式是：

1. 先跑主链得到真实 `结果/`
2. 再写或完善 `文档/论文.md`
3. 生成 `论文_完整终稿.docx`
4. 如需要，再尝试生成 `论文_模板一致版.docx`
5. 对模板版做一次人工复核

## Status Interpretation

### `check_paper.py`

- `PASS`
  项目主链和交付层通过检查。
- `PASS_WITH_TEMPLATE_WARNING`
  主链通过，但模板版缺失或未要求模板。
- `FAIL_MODEL`
  建模结果层失败。
- `FAIL_DOCUMENT`
  文档层失败。
- `FAIL_WORD`
  Word 交付层失败。

### `merge_template_word.py`

- `MERGE_STATUS: PASS`
  模板版生成并通过当前结构检查。
- `MERGE_STATUS: REVIEW_REQUIRED`
  模板版已生成，但建议人工复核。
- `MERGE_STATUS: FAIL`
  模板版未成功生成或文件不可读。

## Regression Evidence

目前至少有一个真实项目验证过以下能力：

- B 题扫描版 PDF 题面解析
- B 题完整主链跑通
- B 题完整终稿 Word 生成
- B 题模板版 Word 生成

该验证说明 skill 已可用于真实项目，但模板版仍应视为增强交付层，而不是主链硬依赖。
