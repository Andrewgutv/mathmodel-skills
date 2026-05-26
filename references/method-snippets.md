# Method Snippets

## Purpose
Use this reference when a problem has already been typed and you need a concrete numerical implementation pattern instead of a blank code skeleton.

These snippets are not full solutions. They are reusable cores for common contest methods.

## Available Snippets

### 1. Attrition ODE
Use for:
- force attrition
- phased combat loss
- command-collapse or effectiveness-shift models

Files:
- `assets/method_snippets/attrition_ode.py`

Typical outputs:
- force trajectories
- phase break effects
- war-duration estimates
- sensitivity to strike time

### 2. Nonlinear Regression
Use for:
- response curves
- impact-factor fitting
- nonlinear duration or cost relationships
- probability-linked regression summaries

Files:
- `assets/method_snippets/nonlinear_regression.py`

Typical outputs:
- fitted parameters
- residual metrics
- prediction points
- scenario comparison tables

### 3. Game or Multi-Agent Stub
Use for:
- payoff-matrix analysis
- decentralized resistance
- strategy iteration
- simple multi-agent scenario simulation

Files:
- `assets/method_snippets/game_multiagent.py`

Typical outputs:
- payoff table
- best-response summary
- scenario outcome table
- decentralized action-frequency evolution

## Rules for Use
- Copy or adapt the closest snippet into the per-question code file.
- Keep the final per-question script responsible for project-specific inputs and outputs.
- Do not claim the snippet itself solves the prompt. It only gives the numerical core.
- Document in `问题-方法对照表.md` which snippet was used.
