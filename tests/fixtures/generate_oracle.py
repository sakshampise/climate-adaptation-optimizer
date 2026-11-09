import json
import os
import sys
sys.path.insert(0, os.path.abspath("."))
import pandas as pd
from src.data_loader import load_inputs
from src.optimizer import solve_portfolio, OBJECTIVE_WEIGHTS, PRESET_DISPLAY_NAMES
from src.explanations import generate_portfolio_explanation

zones_df, projects_df = load_inputs("data")

budgets = [0.0, 1.4, 15.0, 30.0, 50.0, 100.0]
presets = list(OBJECTIVE_WEIGHTS.keys())

oracle = {}

for budget in budgets:
    # 1. Compute scenario comparison matrix CSV for this budget
    scenario_rows = []
    for p_key, p_name in PRESET_DISPLAY_NAMES.items():
        res = solve_portfolio(projects_df, budget, p_key)
        scenario_rows.append({
            "Preset ID": p_key,
            "Policy Preset": p_name,
            "Total Score (pts)": res["total_score"],
            "Allocated Cost (₹ Cr)": res["total_cost_crore"],
            "Remaining Budget (₹ Cr)": res["budget_remaining_crore"],
            "Funded Areas Count": len(res["selected_project_ids"]),
            "Selected Project IDs": ", ".join(res["selected_project_ids"]),
            "Flood Points": res["score_breakdown"]["flood"],
            "Heat Points": res["score_breakdown"]["heat"],
            "Equity Points": res["score_breakdown"]["equity"],
            "Infra Points": res["score_breakdown"]["infrastructure"],
        })
    scenario_df = pd.DataFrame(scenario_rows)
    scenario_csv_str = scenario_df.to_csv(index=False)

    for preset_id in presets:
        scenario_key = f"{preset_id}_{budget}cr"
        current_res = solve_portfolio(projects_df, budget, preset_id)
        explanation = generate_portfolio_explanation(current_res, zones_df, projects_df)
        selected_df = current_res["selected_projects"]

        # Portfolio CSV
        if not selected_df.empty:
            table_df = selected_df[[
                "project_id", "zone_id", "project_name", "intervention_type",
                "cost_crore", "flood_benefit_score", "heat_benefit_score",
                "equity_benefit_score", "infrastructure_benefit_score", "urgency_score",
                "evidence_quality", "data_status", "source_note"
            ]].copy()
            table_df.columns = [
                "Project ID", "Zone ID", "Project Package", "Type",
                "Cost (₹ Cr)", "Flood Pts", "Heat Pts", "Equity Pts",
                "Infra Pts", "Urgency", "Evidence", "Status", "Source Note"
            ]
            portfolio_csv_str = table_df.to_csv(index=False)
        else:
            portfolio_csv_str = ""

        # Unselected explanations mapping
        unselected_reasons = {
            item["project_id"]: item["reason_type"]
            for item in explanation["unselected_explanations"]
        }
        unselected_texts = {
            item["project_id"]: item["reason"]
            for item in explanation["unselected_explanations"]
        }

        oracle[scenario_key] = {
            "preset_id": preset_id,
            "budget_crore": budget,
            "selected_project_ids": current_res["selected_project_ids"],
            "total_cost_crore": current_res["total_cost_crore"],
            "budget_remaining_crore": current_res["budget_remaining_crore"],
            "total_score": current_res["total_score"],
            "score_breakdown": current_res["score_breakdown"],
            "summary_narrative": explanation["summary"],
            "unselected_reasons": unselected_reasons,
            "unselected_texts": unselected_texts,
            "portfolio_csv": portfolio_csv_str,
            "scenario_csv": scenario_csv_str,
        }

with open("tests/fixtures/m4_baseline_oracle.json", "w", encoding="utf-8") as f:
    json.dump(oracle, f, indent=2)

print(f"Successfully generated baseline oracle for {len(oracle)} scenarios.")
