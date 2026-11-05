"""Portfolio optimization engine for Climate Adaptation Investment Prioritization.

Implements deterministic exhaustive search over candidate adaptation packages
under strict budget and mutual exclusivity constraints, adhering to the mathematical
contract in CONTEXT.md and PROJECT_SPEC.md.
"""

import math
import itertools
from typing import Dict, List, Any, Optional
import pandas as pd


# Authoritative normalized objective preset weights (all sum to 1.00)
OBJECTIVE_WEIGHTS: Dict[str, Dict[str, float]] = {
    "flood": {
        "flood": 0.60,
        "heat": 0.10,
        "equity": 0.15,
        "infrastructure": 0.10,
        "urgency": 0.05,
    },
    "heat": {
        "flood": 0.10,
        "heat": 0.60,
        "equity": 0.15,
        "infrastructure": 0.10,
        "urgency": 0.05,
    },
    "balanced": {
        "flood": 0.35,
        "heat": 0.35,
        "equity": 0.15,
        "infrastructure": 0.10,
        "urgency": 0.05,
    },
    "equity": {
        "flood": 0.15,
        "heat": 0.15,
        "equity": 0.50,
        "infrastructure": 0.15,
        "urgency": 0.05,
    },
}

PRESET_DISPLAY_NAMES: Dict[str, str] = {
    "flood": "Flood Priority",
    "heat": "Heat Priority",
    "balanced": "Balanced Resilience",
    "equity": "Social & Climate Equity",
}


def compute_project_score(project_row: pd.Series, weights: Dict[str, float]) -> float:
    """Computes the additive weighted score for a single adaptation project."""
    return (
        weights["flood"] * float(project_row["flood_benefit_score"])
        + weights["heat"] * float(project_row["heat_benefit_score"])
        + weights["equity"] * float(project_row["equity_benefit_score"])
        + weights["infrastructure"] * float(project_row["infrastructure_benefit_score"])
        + weights["urgency"] * float(project_row["urgency_score"])
    )


def solve_portfolio(
    projects: pd.DataFrame,
    budget_crore: float,
    objective_id: str,
) -> Dict[str, Any]:
    """Finds the optimal adaptation portfolio subject to budget and zone constraints.

    Args:
        projects: Validated DataFrame of candidate projects.
        budget_crore: Total municipal adaptation budget in ₹ Crore.
        objective_id: One of 'flood', 'heat', 'balanced', 'equity'.

    Returns:
        Structured result dict containing:
            - selected_projects (pd.DataFrame)
            - selected_project_ids (List[str])
            - total_cost_crore (float)
            - budget_remaining_crore (float)
            - total_score (float)
            - score_breakdown (Dict[str, float])
            - objective_id (str)
            - weights (Dict[str, float])
            - feasible_portfolio_count (int)
            - combinations_evaluated (int)

    Raises:
        ValueError: If budget is negative, non-finite, or objective_id is invalid.
    """
    # 1. Parameter Validation
    if not isinstance(budget_crore, (int, float)) or math.isnan(budget_crore) or math.isinf(budget_crore):
        raise ValueError(f"budget_crore must be a finite number, received: {budget_crore}")
    if budget_crore < 0:
        raise ValueError(f"budget_crore cannot be negative, received: {budget_crore}")

    clean_obj_id = str(objective_id).strip().lower()
    if clean_obj_id not in OBJECTIVE_WEIGHTS:
        raise ValueError(
            f"Unknown objective_id '{objective_id}'. Allowed values: {list(OBJECTIVE_WEIGHTS.keys())}"
        )

    weights = OBJECTIVE_WEIGHTS[clean_obj_id]

    # 2. Filter feasible projects
    # A project is eligible only if feasible is True
    feasible_mask = projects["feasible"].astype(bool)
    feasible_df = projects[feasible_mask].copy()

    # Precompute project score and project dicts for fast iteration
    if not feasible_df.empty:
        feasible_df["calculated_score"] = feasible_df.apply(
            lambda r: compute_project_score(r, weights), axis=1
        )
        feasible_projects_list = feasible_df.to_dict(orient="records")
    else:
        feasible_projects_list = []

    # Group feasible projects by zone_id
    # Every zone has option None (no project selected) plus its feasible projects
    # Preserve sorted order of zones for deterministic behavior
    all_zones = sorted(projects["zone_id"].unique())
    zone_options: List[List[Optional[Dict[str, Any]]]] = []

    for zid in all_zones:
        z_projects = [p for p in feasible_projects_list if p["zone_id"] == zid]
        # Option None represents selecting no project in this zone
        options: List[Optional[Dict[str, Any]]] = [None] + z_projects
        zone_options.append(options)

    # 3. Exhaustive Deterministic Search
    combinations_evaluated = 0
    feasible_portfolio_count = 0

    best_combo: List[Dict[str, Any]] = []
    best_score = -1.0
    best_cost = float("inf")
    best_project_ids: List[str] = []

    # Evaluate Cartesian product across all zones
    for combo in itertools.product(*zone_options):
        combinations_evaluated += 1

        selected_in_combo = [p for p in combo if p is not None]
        combo_cost = sum(p["cost_crore"] for p in selected_in_combo)

        # Budget constraint check (using small tolerance for float comparison)
        if combo_cost <= budget_crore + 1e-9:
            feasible_portfolio_count += 1
            combo_score = sum(p["calculated_score"] for p in selected_in_combo)
            combo_ids = sorted(p["project_id"] for p in selected_in_combo)

            # Tie-breaking rules from PROJECT_SPEC.md:
            # 1. Higher total score
            # 2. Lower total cost
            # 3. Lexicographical by sorted project_id list
            is_better = False

            score_diff = combo_score - best_score
            if score_diff > 1e-7:
                is_better = True
            elif abs(score_diff) <= 1e-7:
                cost_diff = combo_cost - best_cost
                if cost_diff < -1e-7:
                    is_better = True
                elif abs(cost_diff) <= 1e-7:
                    if combo_ids < best_project_ids:
                        is_better = True

            if is_better:
                best_score = combo_score
                best_cost = combo_cost
                best_combo = selected_in_combo
                best_project_ids = combo_ids

    # 4. Assemble Structured Result
    if best_combo:
        selected_df = pd.DataFrame(best_combo)
        # Drop temporary calculated_score before returning if desired, or keep for transparency
        final_cost = round(float(sum(p["cost_crore"] for p in best_combo)), 4)
        final_score = round(float(best_score), 4)

        # Compute dimension-by-dimension weighted score breakdown
        breakdown = {
            "flood": round(float(sum(weights["flood"] * p["flood_benefit_score"] for p in best_combo)), 4),
            "heat": round(float(sum(weights["heat"] * p["heat_benefit_score"] for p in best_combo)), 4),
            "equity": round(float(sum(weights["equity"] * p["equity_benefit_score"] for p in best_combo)), 4),
            "infrastructure": round(float(sum(weights["infrastructure"] * p["infrastructure_benefit_score"] for p in best_combo)), 4),
            "urgency": round(float(sum(weights["urgency"] * p["urgency_score"] for p in best_combo)), 4),
        }
    else:
        selected_df = pd.DataFrame(columns=projects.columns)
        final_cost = 0.0
        final_score = 0.0
        breakdown = {dim: 0.0 for dim in weights}

    remaining_budget = round(max(0.0, float(budget_crore) - final_cost), 4)

    return {
        "selected_projects": selected_df,
        "selected_project_ids": best_project_ids,
        "total_cost_crore": final_cost,
        "budget_remaining_crore": remaining_budget,
        "total_score": final_score,
        "score_breakdown": breakdown,
        "objective_id": clean_obj_id,
        "weights": weights,
        "feasible_portfolio_count": feasible_portfolio_count,
        "combinations_evaluated": combinations_evaluated,
    }
