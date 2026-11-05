"""Data loader module for Climate Adaptation Investment Prioritization.

Loads and validates zone and project CSV fixtures according to the authoritative
data contract defined in CONTEXT.md.
"""

from pathlib import Path
from typing import Tuple, Set
import pandas as pd


class DataValidationError(ValueError):
    """Raised when data fixture violates schema, integrity, or value bounds."""
    pass


REQUIRED_ZONE_COLUMNS = [
    "zone_id",
    "label",
    "latitude",
    "longitude",
    "flood_risk_index",
    "heat_risk_index",
    "exposure_index",
    "vulnerability_index",
    "critical_infrastructure_index",
    "data_status",
    "source_note",
]

REQUIRED_PROJECT_COLUMNS = [
    "project_id",
    "zone_id",
    "project_name",
    "intervention_type",
    "cost_crore",
    "feasible",
    "flood_benefit_score",
    "heat_benefit_score",
    "equity_benefit_score",
    "infrastructure_benefit_score",
    "urgency_score",
    "evidence_quality",
    "data_status",
    "source_note",
]

ALLOWED_DATA_STATUSES: Set[str] = {"verified", "derived", "simulated"}
ALLOWED_EVIDENCE_QUALITIES: Set[str] = {"low", "medium", "high"}

ZONE_SCORE_COLUMNS = [
    "flood_risk_index",
    "heat_risk_index",
    "exposure_index",
    "vulnerability_index",
    "critical_infrastructure_index",
]

PROJECT_SCORE_COLUMNS = [
    "flood_benefit_score",
    "heat_benefit_score",
    "equity_benefit_score",
    "infrastructure_benefit_score",
    "urgency_score",
]


def validate_zones_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validates the zones dataframe against the schema and value bounds."""
    # Check column presence
    missing_cols = [c for c in REQUIRED_ZONE_COLUMNS if c not in df.columns]
    if missing_cols:
        raise DataValidationError(f"zones.csv missing required column(s): {missing_cols}")

    # Check row count (exactly 6 zones)
    if len(df) != 6:
        raise DataValidationError(f"zones.csv must contain exactly 6 zones, found {len(df)}")

    # Check unique zone_id
    if df["zone_id"].duplicated().any():
        dups = df["zone_id"][df["zone_id"].duplicated()].tolist()
        raise DataValidationError(f"Duplicate zone_id(s) found in zones.csv: {dups}")

    # Check non-empty text fields
    for col in ["zone_id", "label", "source_note"]:
        if df[col].astype(str).str.strip().eq("").any() or df[col].isna().any():
            raise DataValidationError(f"zones.csv contains empty or null values in column '{col}'")

    # Check coordinates
    try:
        latitudes = pd.to_numeric(df["latitude"], errors="raise")
        longitudes = pd.to_numeric(df["longitude"], errors="raise")
    except Exception as exc:
        raise DataValidationError(f"Invalid coordinate format in zones.csv: {exc}") from exc

    if not latitudes.between(-90.0, 90.0).all():
        raise DataValidationError("zones.csv latitude values must be between -90 and 90")
    if not longitudes.between(-180.0, 180.0).all():
        raise DataValidationError("zones.csv longitude values must be between -180 and 180")

    # Check score bounds (0-100 integer)
    for col in ZONE_SCORE_COLUMNS:
        try:
            scores = pd.to_numeric(df[col], errors="raise")
        except Exception as exc:
            raise DataValidationError(f"Non-numeric values in zones.csv column '{col}': {exc}") from exc

        if not scores.apply(lambda x: float(x).is_integer()).all():
            raise DataValidationError(f"Score column '{col}' in zones.csv must contain integer values")
        if not scores.between(0, 100).all():
            raise DataValidationError(f"Score column '{col}' in zones.csv contains values outside range [0, 100]")

    # Check allowed data statuses
    invalid_statuses = set(df["data_status"].dropna().unique()) - ALLOWED_DATA_STATUSES
    if invalid_statuses:
        raise DataValidationError(
            f"Invalid data_status in zones.csv: {invalid_statuses}. Allowed: {ALLOWED_DATA_STATUSES}"
        )

    return df


def validate_projects_dataframe(df: pd.DataFrame, valid_zone_ids: Set[str]) -> pd.DataFrame:
    """Validates the projects dataframe against the schema and value bounds."""
    # Check column presence
    missing_cols = [c for c in REQUIRED_PROJECT_COLUMNS if c not in df.columns]
    if missing_cols:
        raise DataValidationError(f"projects.csv missing required column(s): {missing_cols}")

    # Check row count (exactly 12 projects)
    if len(df) != 12:
        raise DataValidationError(f"projects.csv must contain exactly 12 projects, found {len(df)}")

    # Check unique project_id
    if df["project_id"].duplicated().any():
        dups = df["project_id"][df["project_id"].duplicated()].tolist()
        raise DataValidationError(f"Duplicate project_id(s) found in projects.csv: {dups}")

    # Check non-empty text fields
    for col in ["project_id", "zone_id", "project_name", "intervention_type", "source_note"]:
        if df[col].astype(str).str.strip().eq("").any() or df[col].isna().any():
            raise DataValidationError(f"projects.csv contains empty or null values in column '{col}'")

    # Check foreign keys to zones
    invalid_zones = set(df["zone_id"]) - valid_zone_ids
    if invalid_zones:
        raise DataValidationError(f"projects.csv references unknown zone_id(s): {invalid_zones}")

    # Check exactly two projects per zone
    zone_counts = df["zone_id"].value_counts().to_dict()
    for zid in valid_zone_ids:
        cnt = zone_counts.get(zid, 0)
        if cnt != 2:
            raise DataValidationError(f"Zone '{zid}' has {cnt} projects in projects.csv; expected exactly 2")

    # Check positive finite cost
    try:
        costs = pd.to_numeric(df["cost_crore"], errors="raise")
    except Exception as exc:
        raise DataValidationError(f"Invalid cost_crore format in projects.csv: {exc}") from exc

    if (costs <= 0).any() or costs.isna().any():
        raise DataValidationError("projects.csv contains non-positive or missing cost_crore values")

    # Check feasible column boolean
    if not df["feasible"].isin([True, False, "True", "False", "true", "false", 1, 0]).all():
        raise DataValidationError("projects.csv 'feasible' column must be boolean")

    # Check score bounds (0-100 integer)
    for col in PROJECT_SCORE_COLUMNS:
        try:
            scores = pd.to_numeric(df[col], errors="raise")
        except Exception as exc:
            raise DataValidationError(f"Non-numeric values in projects.csv column '{col}': {exc}") from exc

        if not scores.apply(lambda x: float(x).is_integer()).all():
            raise DataValidationError(f"Score column '{col}' in projects.csv must contain integer values")
        if not scores.between(0, 100).all():
            raise DataValidationError(f"Score column '{col}' in projects.csv contains values outside range [0, 100]")

    # Check allowed evidence quality
    invalid_evidence = set(df["evidence_quality"].dropna().unique()) - ALLOWED_EVIDENCE_QUALITIES
    if invalid_evidence:
        raise DataValidationError(
            f"Invalid evidence_quality in projects.csv: {invalid_evidence}. Allowed: {ALLOWED_EVIDENCE_QUALITIES}"
        )

    # Check allowed data status
    invalid_statuses = set(df["data_status"].dropna().unique()) - ALLOWED_DATA_STATUSES
    if invalid_statuses:
        raise DataValidationError(
            f"Invalid data_status in projects.csv: {invalid_statuses}. Allowed: {ALLOWED_DATA_STATUSES}"
        )

    return df


def load_inputs(data_dir: str = "data") -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Loads and strictly validates both zones.csv and projects.csv from data_dir.

    Args:
        data_dir: Path to directory containing zones.csv and projects.csv.

    Returns:
        Tuple of (zones_df, projects_df).

    Raises:
        DataValidationError: If files are missing, malformed, or violate constraints.
    """
    path = Path(data_dir)
    zones_file = path / "zones.csv"
    projects_file = path / "projects.csv"

    if not zones_file.exists():
        raise DataValidationError(f"Required file not found: {zones_file}")
    if not projects_file.exists():
        raise DataValidationError(f"Required file not found: {projects_file}")

    try:
        zones_df = pd.read_csv(zones_file)
    except Exception as exc:
        raise DataValidationError(f"Failed to parse {zones_file}: {exc}") from exc

    try:
        projects_df = pd.read_csv(projects_file)
    except Exception as exc:
        raise DataValidationError(f"Failed to parse {projects_file}: {exc}") from exc

    # Validate zones
    validated_zones = validate_zones_dataframe(zones_df)
    valid_zone_ids = set(validated_zones["zone_id"])

    # Validate projects
    # Ensure boolean conversion for feasible
    if projects_df["feasible"].dtype != bool:
        projects_df["feasible"] = projects_df["feasible"].astype(str).str.strip().str.lower().isin(["true", "1"])

    validated_projects = validate_projects_dataframe(projects_df, valid_zone_ids)

    return validated_zones, validated_projects
