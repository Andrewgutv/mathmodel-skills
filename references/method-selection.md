# Method Selection

## Purpose
Use this reference after splitting the prompt into sub-problems and before writing code.

The goal is not to guess a single universal algorithm. The goal is to:
- identify the sub-problem type
- choose a reasonable model family
- justify why that family fits the task
- select the closest code template for implementation

## Decision Rule
For each `问题N`, answer these four questions first:

1. Is the task mainly prediction, evaluation, optimization, classification, or simulation?
2. What are the inputs and outputs?
3. What constraints matter most?
4. What kind of evidence would count as a good answer?

Then choose the method family and matching code template.

## Type 1: Prediction
Use when the question asks for:
- future values
- trends
- estimated continuous outputs
- regression or curve fitting

Common methods:
- linear or nonlinear regression
- time-series models
- interpolation
- response surface models
- machine learning regressors when justified

Typical evidence:
- prediction error
- fit quality
- residual analysis
- sensitivity of inputs

Preferred template:
- `template_prediction.py`
- Useful numerical core:
  - `assets/method_snippets/nonlinear_regression.py`

## Type 2: Evaluation
Use when the question asks for:
- ranking
- scoring
- comprehensive evaluation
- credibility or suitability assessment
- multi-indicator comparison

Common methods:
- AHP
- entropy weighting
- TOPSIS
- fuzzy comprehensive evaluation
- weighted scoring

Typical evidence:
- ranking table
- weight table
- sensitivity of ranking to weights
- consistency or robustness checks

Preferred template:
- `template_evaluation.py`

## Type 3: Optimization
Use when the question asks for:
- best plan
- minimum cost
- maximum benefit
- scheduling
- allocation
- route design
- multi-objective tradeoff

Common methods:
- linear programming
- integer programming
- nonlinear optimization
- dynamic programming
- heuristic or metaheuristic algorithms
- Pareto or weighted-sum methods

Typical evidence:
- objective value
- feasibility under constraints
- comparison to baseline
- sensitivity to parameters

Preferred template:
- `template_optimization.py`

## Type 4: Classification
Use when the question asks for:
- grouping
- diagnosis
- decision boundaries
- binary or multi-class judgement
- anomaly or abnormality identification

Common methods:
- clustering
- logistic regression
- decision trees
- random forest
- discriminant analysis

Typical evidence:
- confusion matrix
- cluster interpretation
- feature importance
- stability under resampling or grouping choices

Preferred template:
- `template_classification.py`

## Type 5: Simulation
Use when the question asks for:
- dynamic process modeling
- mechanism evolution
- scenario simulation
- path evolution
- Monte Carlo style uncertainty experiments

Common methods:
- differential equations
- discrete-event simulation
- Monte Carlo
- agent-based or rule-based simulation
- state-transition models

Typical evidence:
- scenario curves
- trajectory plots
- parameter sensitivity
- repeated-run statistics

Preferred template:
- `template_simulation.py`
- Useful numerical cores:
  - `assets/method_snippets/attrition_ode.py`
  - `assets/method_snippets/game_multiagent.py`

## Mixed Problems
Many contest problems are mixed.

Typical examples:
- `问题1` evaluation, `问题2` optimization, `问题3` prediction
- `问题1` classification, `问题2` evaluation, `问题3` simulation

In those cases:
- assign one dominant type per sub-problem
- generate one primary script per sub-problem
- keep shared utilities separate if needed

Do not force one single model family on all questions just for neatness.

## Rejection Rules
Avoid methods that are:
- hard to justify from the prompt
- impossible to explain in the paper
- disconnected from the available data
- too heavy for the evidence needed

Prefer the simplest defensible method that can produce solid outputs and figures.

## Required Output of Method Selection
Before coding, record in `文档/方案.md` or `文档/解题思路.md`:
- problem type
- selected method family
- backup method family
- why the chosen one is appropriate
- which code template will be used
