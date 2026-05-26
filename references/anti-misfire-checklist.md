# Anti Misfire Checklist

## Purpose
Use this checklist before choosing a model, during implementation, and before final delivery.

Its purpose is to reduce two failure modes:
- answering the wrong question
- forcing a familiar model onto a problem that does not fit it

This checklist is mandatory for full-workflow requests.

## Gate 1: Problem Meaning Check
Before choosing any model, write down for each `问题N`:

1. What is the question asking us to output?
2. What are the known inputs?
3. What constraints must be respected?
4. What would count as a good answer?

If these four points are not explicit, do not choose a model yet.

Record them in:
- `文档/方案.md`
- `文档/问题-方法对照表.md`

## Gate 2: Problem Type Check
For each `问题N`, label the dominant type:
- prediction
- evaluation
- optimization
- classification
- simulation
- mixed

Then write:
- why this type is appropriate
- why another tempting type is not appropriate

Example:
- choose `evaluation` because the output is a ranking
- do not choose `prediction` because the task is not asking for future values

If you cannot justify the type, do not start coding.

## Gate 3: Method Rejection Check
For each selected method family, write:
- chosen method family
- backup method family
- why the chosen method fits the data and target
- why the backup method was not selected

This is the main defense against “生搬硬套”.

Do not write only “use TOPSIS” or “use regression”.
Always add “why not the other common method”.

## Gate 4: Problem-Method Mapping Table
Create a table in `文档/问题-方法对照表.md` with at least:

| 问题 | 题目要求 | 判定题型 | 选用方法 | 不选的方法 | 对应代码 | 证据文件 | 支撑图表 | 最终结论句 |
|---|---|---|---|---|---|---|---|---|

This table must exist before real modeling code starts.

If the table feels forced, the modeling route is probably wrong.

## Gate 5: Code-to-Question Mapping
Every major code file must answer:
- which question it serves
- what file it reads
- what file it writes
- which figures it generates

If a script cannot be tied back to a question, it is probably off-track.

Record this in:
- `文档/解题过程.md`
- `文档/问题-方法对照表.md`

## Gate 6: Result-to-Question Mapping
Every claimed result must answer:
- which exact sentence or requirement in the prompt it addresses
- which result file contains the evidence
- which figure or table supports the conclusion
- what the final conclusion sentence is

If a numerical result cannot be mapped back to a prompt requirement, do not use it as a final conclusion.

## Gate 7: Branching on Uncertainty
If the prompt is ambiguous, do not fake certainty.

Instead write explicit branches such as:
- if interpreted as an evaluation problem, use route A
- if interpreted as an optimization problem, use route B

Then choose one branch with a short reason.

It is better to expose ambiguity than to silently answer the wrong question.

## Gate 8: Final Anti-Misfire Review
Before final delivery, check every `问题N`:

1. Did we actually answer that question?
2. Did we only produce model outputs, or did we convert them into an answer the question asked for?
3. Are we using a familiar method just because we know it well?
4. Do the code, result files, figures, and paper all point to the same answer?

If any answer is “no” or “not sure”, the workflow is incomplete.

## Red Flags
Stop and re-check the route if any of these happen:
- the model looks sophisticated but the answer does not match the prompt wording
- the code produces outputs that are hard to explain in the paper
- the method was selected before clarifying the output target
- the same method is being reused across all questions without justification
- the final paper has many formulas but weak prompt-to-result mapping

## Minimum Required Artifacts
A full workflow request should include:
- `文档/问题-方法对照表.md`
- explicit per-question output definitions in `方案.md`
- per-question reasoning in `解题思路.md`
- per-question script mapping in `解题过程.md`
- per-question evidence, figure, and conclusion trace in `问题-方法对照表.md`

Without these, the anti-misfire mechanism has not been applied.
