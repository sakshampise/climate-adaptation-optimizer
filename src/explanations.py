"""Deterministic explanation engine for Climate Adaptation Investment Prioritization.

Generates structured, human-readable rationale and trade-off summaries
from optimizer results and data inputs without ungrounded assertions or LLM calls,
adhering to the explanation contract in CONTEXT.md and PROJECT_SPEC.md.
"""

from typing import Dict, List, Any
import pandas as pd
from src.optimizer import PRESET_DISPLAY_NAMES


def generate_portfolio_explanation(
    result: Dict[str, Any],
    zones_df: pd.DataFrame,
    projects_df: pd.DataFrame,
) -> Dict[str, Any]:
    """Builds transparent explanations for both selected and unselected packages.

    Args:
        result: Structured result dictionary from solve_portfolio().
        zones_df: Validated zones DataFrame.
        projects_df: Validated projects DataFrame.

    Returns:
        Dictionary containing:
            - summary (str): Overall executive narrative.
            - selected_explanations (List[Dict[str, Any]]): Rationale for selected projects.
            - unselected_explanations (List[Dict[str, Any]]): Clear exclusion reasons.
            - trade_off_analysis (Dict[str, Any]): Breakdown and trade-off summary.
    """
    selected_ids = set(result.get("selected_project_ids", []))
    objective_id = result.get("objective_id", "balanced")
    objective_name = PRESET_DISPLAY_NAMES.get(objective_id, objective_id.title())
    total_cost = result.get("total_cost_crore", 0.0)
    remaining_budget = result.get("budget_remaining_crore", 0.0)
    total_score = result.get("total_score", 0.0)
    weights = result.get("weights", {})
    breakdown = result.get("score_breakdown", {})
    evaluated = result.get("combinations_evaluated", 0)
    feasible_count = result.get("feasible_portfolio_count", 0)

    # Build lookup dictionaries
    zone_lookup = {row["zone_id"]: row for _, row in zones_df.iterrows()}

    # Group selected projects by zone
    selected_zone_map: Dict[str, Dict[str, Any]] = {}
    selected_explanations: List[Dict[str, Any]] = []

    for _, proj in projects_df.iterrows():
        pid = proj["project_id"]
        if pid in selected_ids:
            zid = proj["zone_id"]
            z_row = zone_lookup.get(zid, {})
            z_label = z_row.get("label", zid)

            # Calculate individual contributions
            flood_pts = round(weights.get("flood", 0.0) * proj["flood_benefit_score"], 2)
            heat_pts = round(weights.get("heat", 0.0) * proj["heat_benefit_score"], 2)
            equity_pts = round(weights.get("equity", 0.0) * proj["equity_benefit_score"], 2)
            infra_pts = round(weights.get("infrastructure", 0.0) * proj["infrastructure_benefit_score"], 2)
            urgency_pts = round(weights.get("urgency", 0.0) * proj["urgency_score"], 2)
            item_score = round(flood_pts + heat_pts + equity_pts + infra_pts + urgency_pts, 2)

            narrative = (
                f"Contributes {item_score:.2f} planning points under the {objective_name} preset "
                f"(Flood: {flood_pts:.2f}, Heat: {heat_pts:.2f}, Equity: {equity_pts:.2f}, "
                f"Infrastructure: {infra_pts:.2f}, Urgency: {urgency_pts:.2f})."
            )

            explanation_item = {
                "project_id": pid,
                "project_name": proj["project_name"],
                "zone_id": zid,
                "zone_label": z_label,
                "cost_crore": proj["cost_crore"],
                "calculated_score": item_score,
                "intervention_type": proj["intervention_type"],
                "evidence_quality": proj["evidence_quality"],
                "data_status": proj["data_status"],
                "source_note": proj["source_note"],
                "score_contribution_narrative": narrative,
                "rationale": (
                    f"Selected as the optimal package for {z_label} to maximize overall "
                    f"resilience points while staying within the allocated municipal budget."
                ),
            }
            selected_explanations.append(explanation_item)
            selected_zone_map[zid] = explanation_item

    # Explanations for unselected projects
    unselected_explanations: List[Dict[str, Any]] = []
    for _, proj in projects_df.iterrows():
        pid = proj["project_id"]
        if pid not in selected_ids:
            zid = proj["zone_id"]
            z_row = zone_lookup.get(zid, {})
            z_label = z_row.get("label", zid)
            cost = proj["cost_crore"]
            is_feasible = bool(proj.get("feasible", True))

            if not is_feasible:
                reason = "Infeasible: Marked as ineligible for current municipal planning cycle."
                reason_type = "infeasible"
            elif zid in selected_zone_map:
                chosen_name = selected_zone_map[zid]["project_name"]
                reason = (
                    f"Zone Alternative Chosen: {chosen_name} was selected for {z_label} instead, "
                    f"satisfying the single-intervention constraint per planning area."
                )
                reason_type = "same_zone_alternative_chosen"
            elif cost > remaining_budget:
                reason = (
                    f"Budget Insufficient: Package cost of ₹{cost:.2f} Cr exceeds the remaining "
                    f"unallocated budget of ₹{remaining_budget:.2f} Cr."
                )
                reason_type = "budget_exceeded"
            else:
                reason = (
                    f"Optimization Trade-off: Evaluated across {evaluated} portfolio combinations. "
                    f"Selecting this project yielded a lower total system score than the chosen combination."
                )
                reason_type = "portfolio_tradeoff"

            unselected_explanations.append({
                "project_id": pid,
                "project_name": proj["project_name"],
                "zone_id": zid,
                "zone_label": z_label,
                "cost_crore": cost,
                "reason_type": reason_type,
                "reason": reason,
                "evidence_quality": proj["evidence_quality"],
                "source_note": proj["source_note"],
            })

    # Summary narrative
    num_selected = len(selected_explanations)
    total_budget_entered = round(total_cost + remaining_budget, 2)
    summary = (
        f"Under the {objective_name} preset, the optimizer evaluated {evaluated} candidate combinations "
        f"({feasible_count} budget-feasible portfolios) and identified an optimal allocation of "
        f"₹{total_cost:.2f} Cr across {num_selected} planning zones, generating {total_score:.2f} total "
        f"planning resilience points with ₹{remaining_budget:.2f} Cr unallocated budget remaining."
    )

    # Dimension trade-offs
    trade_off_analysis = {
        "score_breakdown": breakdown,
        "highest_contributing_dimension": max(breakdown, key=breakdown.get) if breakdown else None,
        "budget_utilization_percent": round((total_cost / total_budget_entered * 100), 1) if total_budget_entered > 0 else 0.0,
    }

    return {
        "summary": summary,
        "selected_explanations": selected_explanations,
        "unselected_explanations": unselected_explanations,
        "trade_off_analysis": trade_off_analysis,
    }
