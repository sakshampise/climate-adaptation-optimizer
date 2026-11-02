"""Unit tests for data loader and schema validation."""

import pytest
import pandas as pd
from pathlib import Path
from src.data_loader import load_inputs, DataValidationError


def test_load_inputs_success():
    """Verify that the baseline data directory loads cleanly with expected shapes."""
    zones_df, projects_df = load_inputs("data")

    assert len(zones_df) == 6
    assert len(projects_df) == 12

    # Check that each zone has exactly 2 projects
    counts = projects_df["zone_id"].value_counts()
    for zid in zones_df["zone_id"]:
        assert counts[zid] == 2

    # Check all costs positive
    assert (projects_df["cost_crore"] > 0).all()

    # Check all data_status valid
    assert set(zones_df["data_status"]).issubset({"verified", "derived", "simulated"})
    assert set(projects_df["data_status"]).issubset({"verified", "derived", "simulated"})


def test_missing_file_raises_error(tmp_path):
    """Verify that a missing CSV raises DataValidationError."""
    with pytest.raises(DataValidationError, match="Required file not found"):
        load_inputs(str(tmp_path))


def test_missing_column_raises_error(tmp_path):
    """Verify that a missing column triggers a validation error."""
    # Write incomplete zones
    bad_zones = pd.DataFrame({
        "zone_id": ["Z01"],
        "label": ["Zone 1"],
    })
    bad_zones.to_csv(tmp_path / "zones.csv", index=False)
    (tmp_path / "projects.csv").write_text("dummy")

    with pytest.raises(DataValidationError, match="missing required column"):
        load_inputs(str(tmp_path))


def test_invalid_zone_count_raises_error(tmp_path):
    """Verify that anything other than exactly 6 zones triggers an error."""
    zones_df, projects_df = load_inputs("data")
    # Drop one zone to make it 5
    bad_zones = zones_df.iloc[:5]
    bad_zones.to_csv(tmp_path / "zones.csv", index=False)
    projects_df.to_csv(tmp_path / "projects.csv", index=False)

    with pytest.raises(DataValidationError, match="must contain exactly 6 zones"):
        load_inputs(str(tmp_path))


def test_duplicate_zone_id_raises_error(tmp_path):
    """Verify duplicate zone_id triggers an error."""
    zones_df, projects_df = load_inputs("data")
    bad_zones = zones_df.copy()
    bad_zones.loc[1, "zone_id"] = bad_zones.loc[0, "zone_id"]
    bad_zones.to_csv(tmp_path / "zones.csv", index=False)
    projects_df.to_csv(tmp_path / "projects.csv", index=False)

    with pytest.raises(DataValidationError, match="Duplicate zone_id"):
        load_inputs(str(tmp_path))


def test_unknown_zone_id_in_projects(tmp_path):
    """Verify project referencing unknown zone_id triggers an error."""
    zones_df, projects_df = load_inputs("data")
    bad_projects = projects_df.copy()
    bad_projects.loc[0, "zone_id"] = "Z99"
    zones_df.to_csv(tmp_path / "zones.csv", index=False)
    bad_projects.to_csv(tmp_path / "projects.csv", index=False)

    with pytest.raises(DataValidationError, match="references unknown zone_id"):
        load_inputs(str(tmp_path))


def test_negative_cost_raises_error(tmp_path):
    """Verify non-positive cost_crore triggers an error."""
    zones_df, projects_df = load_inputs("data")
    bad_projects = projects_df.copy()
    bad_projects.loc[0, "cost_crore"] = -1.5
    zones_df.to_csv(tmp_path / "zones.csv", index=False)
    bad_projects.to_csv(tmp_path / "projects.csv", index=False)

    with pytest.raises(DataValidationError, match="non-positive"):
        load_inputs(str(tmp_path))


def test_score_out_of_range_raises_error(tmp_path):
    """Verify scores outside 0-100 trigger an error."""
    zones_df, projects_df = load_inputs("data")
    bad_projects = projects_df.copy()
    bad_projects.loc[0, "flood_benefit_score"] = 150
    zones_df.to_csv(tmp_path / "zones.csv", index=False)
    bad_projects.to_csv(tmp_path / "projects.csv", index=False)

    with pytest.raises(DataValidationError, match="outside range"):
        load_inputs(str(tmp_path))


def test_invalid_coordinates_raises_error(tmp_path):
    """Verify invalid coordinates trigger an error."""
    zones_df, projects_df = load_inputs("data")
    bad_zones = zones_df.copy()
    bad_zones.loc[0, "latitude"] = 120.0  # Invalid latitude
    bad_zones.to_csv(tmp_path / "zones.csv", index=False)
    projects_df.to_csv(tmp_path / "projects.csv", index=False)

    with pytest.raises(DataValidationError, match="latitude"):
        load_inputs(str(tmp_path))
