# Prompt Parsing

## Purpose
Use this reference at the very beginning of a full math modeling workflow.

The goal is to convert a raw problem statement plus attachments into a structured problem specification before any model is selected.

This reference is the main defense against:
- answering the wrong question
- missing hidden constraints in the prompt
- treating attachments as decoration instead of required evidence

## Inputs to Parse
Typical contest inputs include:
- a main PDF prompt
- attachments such as CSV, XLSX, TXT, images, or appendices
- sometimes teacher notes or delivery requirements

Treat the main PDF as the primary source of truth unless the user explicitly says otherwise.

## What Must Be Extracted
For the full problem and for each `问题N`, extract:

1. Output target
2. Known inputs
3. Constraints
4. Evaluation standard
5. Scope boundary
6. Attachment dependency

These six fields must be recorded before method selection starts.

## Field Definitions

### 1. Output Target
What exactly must be produced?

Examples:
- rank options
- predict future value
- choose the optimal plan
- classify samples
- simulate a process

Write this as a direct answerable task sentence, not as a vague topic label.

Good:
- “问题2要求给出最优调度方案并报告总成本。”

Bad:
- “问题2是在研究调度问题。”

### 2. Known Inputs
List:
- data files
- variables explicitly provided
- attachment images or tables
- allowed assumptions from the prompt

Record them in:
- `数据/数据说明表.md`
- `文档/方案.md`

### 3. Constraints
Extract:
- explicit numerical constraints
- physical or logical constraints
- policy constraints
- formatting or delivery constraints

Examples:
- must satisfy time windows
- cannot exceed capacity
- must consider uncertainty
- final paper should match the 2026 standard template and target about 25 pages

### 4. Evaluation Standard
How will a good answer be judged?

Examples:
- prediction error
- ranking credibility
- optimization objective value
- robustness under sensitivity analysis
- interpretability or feasibility

If the prompt does not state this clearly, infer the most defensible evaluation standard and mark it as an inference.

### 5. Scope Boundary
What is *not* being asked?

This is critical.

Examples:
- the problem asks for ranking, not forecasting
- the problem asks for a decision recommendation, not a full physical simulation
- the problem asks for scenario comparison, not exact prediction

Write one sentence per question:
- “本问边界：需要解决 X，不要求解决 Y。”

### 6. Attachment Dependency
For each question, identify which attachments matter.

Examples:
- `问题1` depends on Appendix Table A
- `问题2` depends on `data.xlsx`
- `问题3` depends on `Pic01.jpg`

Do not ignore attachments. If an attachment exists, explicitly decide whether it is:
- required
- helpful
- irrelevant

## Parsing Workflow

### Step 1: Read the Main PDF
- Extract the problem background
- Extract all explicitly numbered questions
- Extract delivery instructions
- Extract any explicit wording about assumptions, scoring, or output format

If reading text directly is unreliable, fall back to page rendering or OCR-aware inspection.

### Step 2: Inventory Attachments
Create a file inventory:
- file name
- type
- likely role
- mapped question(s)

Write this into `数据/数据说明表.md`.

### Step 3: Build a Question Card for Each Question
For each `问题N`, create a question card with:

- 问题编号
- 原题要求
- 输出目标
- 已知输入
- 约束
- 评价标准
- 每问边界
- 附件依赖
- 初步题型判断

Store the distilled version across:
- `文档/方案.md`
- `文档/解题思路.md`
- `文档/问题-方法对照表.md`

## Required Question Card Format
Use this structure:

```md
## 问题N

### 原题要求

### 输出目标

### 已知输入

### 约束条件

### 评价标准

### 每问边界

### 附件依赖

### 初步题型判断
```

## Special Rules

### Rule 1: Do Not Select the Model Too Early
If the output target and scope boundary are not clear, delay model selection.

### Rule 2: Separate Stated Facts From Inferences
Mark:
- prompt-stated facts
- your inference

Do not mix them.

### Rule 3: Handle Multi-Question Problems Separately
Never collapse all questions into one generic summary if the prompt distinguishes them.

### Rule 4: Record Delivery Constraints Early
If the prompt or context includes:
- standard Word template
- target page count
- required appendix handling
- expected charts or sensitivity analysis

record those before modeling starts.

## Failure Modes to Avoid
- skipping the attachment inventory
- confusing the topic with the actual required output
- treating a ranking task as a prediction task
- missing an important constraint hidden in one sentence of the prompt
- ignoring the difference between “estimate”, “compare”, “optimize”, and “classify”

## Minimum Acceptance
Prompt parsing is not complete unless every question has:
- a clear output target
- listed inputs
- extracted constraints
- an evaluation standard
- a scope boundary
- an attachment dependency map
