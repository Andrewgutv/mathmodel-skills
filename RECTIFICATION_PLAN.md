# MathModel 技能仓库整改清单

## 目标

把当前 `mathmodel` 技能仓库从“第一版可运行实现”提升到“稳定可交付版本”。

这里的“稳定可交付”指：

- 在技能声明承诺的输入边界内，不会无提示失败
- 不会把未完成项目误判为通过
- 生成链路在失败时能给出明确原因和降级结果
- 至少有最小样例和回归验证证明主流程可用

---

## 当前结论

当前仓库已具备以下基础能力：

- 完整目录结构
- `parse / solve / summarize / write / word / check` 六阶段主流程
- 项目脚手架生成
- 结果回填
- Word 终稿生成
- 模板 Word 合并
- 论文与交付检查

但距离“稳定可交付”仍有以下 release blocker：

1. `parse` 输入边界与 `SKILL.md` 不一致
2. OCR 失败与“没有识别到子问题”未严格区分
3. `solve` 阶段存在“部分完成也可能通过”的风险
4. `check_paper.py` 混入特定题目示例逻辑，不够通用
5. 模板 Word 合并强依赖本机环境和模板结构，缺少兼容性探测与降级说明
6. `check` 规则与技能文档存在契约冲突，例如 AI 使用声明
7. 脚手架入口依赖固定技能安装路径，不够稳定
8. 缺少最小样例和自动化 smoke test，无法证明主流程已回归通过

---

## 整改范围

本次整改涉及以下文件和模块：

- [SKILL.md](/D:/workspace/skills/mathmodel/SKILL.md)
- [scripts/parse_prompt.py](/D:/workspace/skills/mathmodel/scripts/parse_prompt.py)
- [scripts/run_pipeline.py](/D:/workspace/skills/mathmodel/scripts/run_pipeline.py)
- [scripts/init_project.py](/D:/workspace/skills/mathmodel/scripts/init_project.py)
- [scripts/summarize_results.py](/D:/workspace/skills/mathmodel/scripts/summarize_results.py)
- [scripts/backfill_results.py](/D:/workspace/skills/mathmodel/scripts/backfill_results.py)
- [scripts/build_word_modern.py](/D:/workspace/skills/mathmodel/scripts/build_word_modern.py)
- [scripts/merge_template_word_modern.py](/D:/workspace/skills/mathmodel/scripts/merge_template_word_modern.py)
- [scripts/check_paper.py](/D:/workspace/skills/mathmodel/scripts/check_paper.py)
- [references/workflow.md](/D:/workspace/skills/mathmodel/references/workflow.md)
- [references/word-pipeline.md](/D:/workspace/skills/mathmodel/references/word-pipeline.md)

建议新增：

- [examples/](/D:/workspace/skills/mathmodel/examples)
- [tests/](/D:/workspace/skills/mathmodel/tests)
- [README.md](/D:/workspace/skills/mathmodel/README.md)

---

## 优先级划分

### P0：必须先修，未完成前不应视为稳定可交付

1. 扩展并统一题面输入支持
2. 增加 OCR / 抽取失败分类
3. 修正 `solve` 阶段的结果完整性判断
4. 清理 `check_paper.py` 中的题目特定校验
5. 统一 `SKILL.md` 与 `check` 规则的必须项和按需项

### P1：建议紧随其后，决定交付链路是否稳

1. 为 Word 模板合并增加环境探测和兼容性检查
2. 为模板合并失败增加明确降级路径
3. 修正脚手架对技能安装路径的硬依赖

### P2：补齐可验证性，作为发布前门槛

1. 增加最小样例项目
2. 增加 smoke test / 回归验证脚本
3. 增加发布标准与维护说明

---

## 详细整改项

### 1. 统一题面输入边界

状态：`P0`

目标：

- 让实际代码支持 `SKILL.md` 声明的题面输入类型

涉及文件：

- [scripts/parse_prompt.py](/D:/workspace/skills/mathmodel/scripts/parse_prompt.py)
- [SKILL.md](/D:/workspace/skills/mathmodel/SKILL.md)

整改动作：

- 将 `find_prompt_pdf()` 重构为 `find_prompt_source()`
- 支持以下题面输入：
  - `pdf`
  - `docx`
  - `md`
  - 单张图片或图片型题面
- 引入按扩展名分派的提取逻辑
- 在无支持格式时返回结构化错误

验收标准：

- 最小 PDF 样例可进入 `parse`
- 最小 DOCX 样例可进入 `parse`
- 最小 Markdown 样例可进入 `parse`
- 最小图片题面样例可进入 `parse`
- 非法格式会给出明确错误信息

---

### 2. 明确区分 OCR 失败与零问题识别

状态：`P0`

目标：

- 避免把题面抽取失败误报为“没有识别到子问题”

涉及文件：

- [scripts/parse_prompt.py](/D:/workspace/skills/mathmodel/scripts/parse_prompt.py)
- [SKILL.md](/D:/workspace/skills/mathmodel/SKILL.md)

整改动作：

- 为抽取过程增加状态分类，例如：
  - `text_extracted`
  - `ocr_used`
  - `ocr_unavailable`
  - `ocr_failed`
  - `prompt_empty`
  - `zero_questions_detected`
- 当文本为空且 OCR 不可用或失败时，`parse` 直接失败
- 仅当文本真实存在但未匹配到问题结构时，允许记录 `0 questions`
- 将状态写入日志和流水线报告

验收标准：

- 扫描版 PDF 在缺 OCR 依赖时不会伪装成“0 个问题”
- OCR 异常可在日志中直接定位
- 流水线报告中能区分抽取失败和题面异常

---

### 3. 修复 solve 阶段的“假通过”

状态：`P0`

目标：

- 只有所有应解题目都产出真实结果时，`solve` 才通过

涉及文件：

- [scripts/run_pipeline.py](/D:/workspace/skills/mathmodel/scripts/run_pipeline.py)
- [scripts/summarize_results.py](/D:/workspace/skills/mathmodel/scripts/summarize_results.py)

整改动作：

- 从 `文档/问题-方法对照表.md` 推导应有问题数
- 校验每个问题都存在对应结果文件
- 校验每个问题结果文件都不是占位内容
- `summarize` 阶段检测题号缺失、题号不连续、空汇总
- 若仅部分问题完成，直接失败，不进入 `write/word/check`

验收标准：

- 3 问项目只完成 1 问时，`solve` 失败
- 3 问项目中有 1 个占位结果时，`solve` 失败
- 所有问题都完成后才能进入后续阶段

---

### 4. 去掉通用检查中的题目特定逻辑

状态：`P0`

目标：

- 让 `check_paper.py` 成为真正通用的项目交付检查器

涉及文件：

- [scripts/check_paper.py](/D:/workspace/skills/mathmodel/scripts/check_paper.py)

整改动作：

- 删除和特定示例题绑定的关键词检查
- 改用通用结果存在性与引用关系校验：
  - 是否存在 `AUTO_RESULT_SUMMARY`
  - 是否存在来自 `结果/` 的证据引用
  - 是否存在图表清单
  - 是否存在图表在正文中的引用
  - 是否存在参考文献列表
- 将“论文结构检查”和“项目交付检查”分层

验收标准：

- 任意题型项目都使用同一套检查规则
- 示例残留词不会造成误判

---

### 5. 统一必须项与按需项

状态：`P0`

目标：

- 让技能说明、脚手架模板、检查脚本的规则一致

涉及文件：

- [SKILL.md](/D:/workspace/skills/mathmodel/SKILL.md)
- [scripts/check_paper.py](/D:/workspace/skills/mathmodel/scripts/check_paper.py)
- [scripts/init_project.py](/D:/workspace/skills/mathmodel/scripts/init_project.py)

整改动作：

- 明确哪些是始终必需：
  - 方案
  - 解题思路
  - 结果文件
  - 论文正文
- 明确哪些是条件必需：
  - AI 使用声明
  - 模板版 Word
  - 答辩材料
- 为 `check_paper.py` 增加模式参数，例如：
  - `paper`
  - `full_delivery`
  - `defense`

验收标准：

- 只要求论文时，不会因为没有答辩材料失败
- 没要求 AI 声明时，不会无条件失败
- 全量交付模式下仍能严格检查全部交付物

---

### 6. 稳定 Word 模板合并链路

状态：`P1`

目标：

- 模板合并失败时不误伤主交付，并能明确说明失败原因

涉及文件：

- [scripts/merge_template_word_modern.py](/D:/workspace/skills/mathmodel/scripts/merge_template_word_modern.py)
- [scripts/build_word_modern.py](/D:/workspace/skills/mathmodel/scripts/build_word_modern.py)
- [references/word-pipeline.md](/D:/workspace/skills/mathmodel/references/word-pipeline.md)

整改动作：

- 增加环境探测：
  - 是否为 Windows
  - 是否安装 Microsoft Word
  - 是否能创建 COM 对象
- 增加模板兼容性检查：
  - 是否存在摘要一级标题
  - 是否存在目录或 TOC
  - 是否存在可替换标题位
- 明确失败分类：
  - 环境缺失
  - 模板不兼容
  - 正文结构异常
- 模板合并失败时，保留完整终稿并输出说明

验收标准：

- 无 Word 环境时流程不崩溃
- 模板不兼容时仍保留 `论文_完整终稿.docx`
- 报告中能看出失败属于哪一类

---

### 7. 修正脚手架路径依赖

状态：`P1`

目标：

- 生成的新项目应稳定调用当前版本的技能脚本

涉及文件：

- [scripts/init_project.py](/D:/workspace/skills/mathmodel/scripts/init_project.py)

整改动作：

- 不再把 `run_mathmodel.ps1` 写死到 `$HOME\\.codex\\skills\\mathmodel`
- 改为以下二选一：
  - 生成项目内独立 `scripts/` 副本
  - 生成项目时写入当前技能仓库的实际路径
- 在使用说明里明确该入口如何解析技能脚本位置

验收标准：

- 新生成项目不会误调用另一份旧技能
- 当前仓库改动后，新项目入口仍然一致

---

### 8. 增加最小样例项目

状态：`P2`

目标：

- 为主流程提供可重复验证的最小输入集合

建议新增目录：

- [examples/pdf_text_prompt/](/D:/workspace/skills/mathmodel/examples/pdf_text_prompt)
- [examples/pdf_scanned_prompt/](/D:/workspace/skills/mathmodel/examples/pdf_scanned_prompt)
- [examples/docx_prompt/](/D:/workspace/skills/mathmodel/examples/docx_prompt)
- [examples/markdown_prompt/](/D:/workspace/skills/mathmodel/examples/markdown_prompt)

每套样例至少包含：

- 题面文件
- 最小附件
- 预期说明

验收标准：

- 四类题面输入都至少有一个最小样例
- 每个样例都有预期输出说明

---

### 9. 增加 smoke test / 回归验证

状态：`P2`

目标：

- 证明主流程至少在样例项目上可运行

建议新增：

- [tests/](/D:/workspace/skills/mathmodel/tests)
- 或 [scripts/smoke_test.py](/D:/workspace/skills/mathmodel/scripts/smoke_test.py)

测试内容：

- `parse` 是否成功
- `solve` 对占位结果是否会正确失败
- `summarize` 是否会拒绝缺问项目
- `write` 是否能正确回填文档
- `check` 是否能给出稳定结果
- `word` 在有模板和无模板条件下是否行为明确

验收标准：

- 至少一条自动化 smoke test 可运行
- 至少一套完整样例能通过主流程

---

### 10. 补充发布标准和维护文档

状态：`P2`

目标：

- 明确何时可以对外宣称“稳定可交付”

建议新增或更新：

- [README.md](/D:/workspace/skills/mathmodel/README.md)
- [references/workflow.md](/D:/workspace/skills/mathmodel/references/workflow.md)

建议写清：

- 支持的题面格式
- 依赖环境
- 模板 Word 的边界
- 完整交付与论文交付的差异
- 发布前最低验收标准

发布前最低标准建议：

- 四类题面输入各跑通一个最小样例
- 至少一个完整项目通过 `parse -> solve -> summarize -> write -> check`
- Word 合并在无 Word 环境下具备明确降级说明
- 所有失败都有可读错误信息

---

## 建议实施顺序

### 第一轮：先修 blocker

1. `parse_prompt.py` 输入边界扩展
2. `parse_prompt.py` OCR / 抽取失败分类
3. `run_pipeline.py` + `summarize_results.py` 结果完整性校验
4. `check_paper.py` 通用化
5. `SKILL.md` / `check_paper.py` 契约统一

### 第二轮：稳定交付链路

1. `merge_template_word_modern.py` 环境探测
2. 模板兼容性检查和失败分类
3. `init_project.py` 入口路径修复

### 第三轮：补验证闭环

1. 新增 `examples/`
2. 新增 smoke test
3. 补 README 和发布标准

---

## 建议里程碑

### M1：逻辑正确

完成标志：

- 不再出现 OCR 失败误判
- 不再出现 solve 假通过
- 通用检查逻辑已去示例耦合

### M2：交付稳定

完成标志：

- Word 链路失败可解释
- 脚手架入口稳定
- 技能契约统一

### M3：可证明可用

完成标志：

- 样例项目齐全
- smoke test 可运行
- 发布标准成文

---

## 不建议现在做的事

- 不要先扩展复杂建模模板数量
- 不要先美化文档措辞
- 不要先优化小的代码风格问题

当前最重要的是把主流程的正确性、失败可诊断性、和可验证性补齐。

---

## 下一步建议

从第一轮开始，优先修改：

1. [scripts/parse_prompt.py](/D:/workspace/skills/mathmodel/scripts/parse_prompt.py)
2. [scripts/run_pipeline.py](/D:/workspace/skills/mathmodel/scripts/run_pipeline.py)
3. [scripts/summarize_results.py](/D:/workspace/skills/mathmodel/scripts/summarize_results.py)
4. [scripts/check_paper.py](/D:/workspace/skills/mathmodel/scripts/check_paper.py)
5. [SKILL.md](/D:/workspace/skills/mathmodel/SKILL.md)

如果继续推进，建议下一步直接进入“第一轮整改实施”。
