"""Design system and CSS theme definitions for the Pune Climate Optimizer dashboard.

Provides unified styling, responsive typography, custom KPI cards, animated elements,
color palettes, and dimension mappings across all application views.
"""

import streamlit as st

# Color palette constants
COLORS = {
    "primary": "#0E7C7B",          # Teal
    "primary_dark": "#0A5F5E",     # Dark Teal
    "accent": "#17B890",           # Emerald
    "accent_light": "#D1FAE5",     # Light Emerald
    "warning": "#F59E0B",          # Amber
    "danger": "#EF4444",           # Red
    "text_primary": "#0F172A",     # Slate 900
    "text_secondary": "#475569",   # Slate 600
    "text_muted": "#94A3B8",       # Slate 400
    "bg_page": "#F8FAFC",          # Slate 50
    "bg_card": "#FFFFFF",          # Pure White
    "bg_sidebar": "#F1F5F9",       # Slate 100
    "border": "#E2E8F0",           # Slate 200
    "border_light": "#F1F5F9",     # Slate 100
}

# Dimension specific color assignments
DIMENSION_COLORS = {
    "flood": "#2563EB",            # Blue 600
    "heat": "#EA580C",             # Orange 600
    "equity": "#16A34A",           # Green 600
    "infrastructure": "#7C3AED",   # Violet 600
    "urgency": "#DC2626",          # Red 600
}

# Dimension display labels with emoji icons
DIMENSION_LABELS = {
    "flood": "🌊 Flood Mitigation",
    "heat": "☀️ Heat Abatement",
    "equity": "🤝 Social & Equity",
    "infrastructure": "🏗️ Critical Infrastructure",
    "urgency": "⚡ Urgency Priority",
}

# Dimension standalone emoji icons
DIMENSION_ICONS = {
    "flood": "🌊",
    "heat": "☀️",
    "equity": "🤝",
    "infrastructure": "🏗️",
    "urgency": "⚡",
}


def inject_custom_css() -> None:
    """Inject the global design system stylesheet into the Streamlit app.

    Applies typography rules, spacing adjustments, KPI card styles,
    section headers, provenance notices, badges, and scrollbars.
    """
    css_content = f"""
    <style>
    /* Google Fonts Import: Inter & Material Symbols Rounded */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

    /* Global typography and root font assignment (excluding Streamlit material icons) */
    html, body, [class*="css"], [class*="st-"]:not([data-testid="stIconMaterial"]), .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }}

    /* Ensure Material Icons font is preserved for expanders and buttons */
    [data-testid="stIconMaterial"], .material-symbols-rounded {{
        font-family: "Material Symbols Rounded", sans-serif !important;
        font-size: 20px !important;
        line-height: 1 !important;
        letter-spacing: normal !important;
        text-transform: none !important;
        white-space: nowrap !important;
        direction: ltr !important;
    }}

    /* Main container spacing and layout */
    .main .block-container {{
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1280px;
    }}

    /* Card entrance keyframe animation */
    @keyframes fadeInUp {{
        from {{
            opacity: 0;
            transform: translateY(10px);
        }}
        to {{
            opacity: 1;
            transform: translateY(0);
        }}
    }}

    /* KPI Card styling */
    .kpi-card {{
        background-color: {COLORS["bg_card"]};
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05), 0 1px 2px rgba(0, 0, 0, 0.03);
        padding: 16px 18px;
        border-left: 4px solid {COLORS["primary"]};
        min-height: 125px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        animation: fadeInUp 0.4s ease-out;
    }}

    .kpi-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.08), 0 2px 4px -1px rgba(0, 0, 0, 0.04);
    }}

    .kpi-label {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: {COLORS["text_muted"]};
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .kpi-icon {{
        font-size: 18px;
        line-height: 1;
        margin-left: 8px;
        flex-shrink: 0;
    }}

    .kpi-value {{
        font-size: 26px;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        margin: 6px 0 2px;
        line-height: 1.15;
    }}

    .kpi-subtitle {{
        font-size: 12px;
        color: {COLORS["text_secondary"]};
        line-height: 1.3;
    }}

    /* Section header styling */
    .section-header {{
        font-size: 20px;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        padding-bottom: 12px;
        border-bottom: 2px solid {COLORS["primary"]};
        margin: 32px 0 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }}

    /* Provenance advisory banner */
    .provenance-banner {{
        background: linear-gradient(135deg, #FEF3C7, #FDE68A);
        border: 1px solid {COLORS["warning"]};
        border-radius: 10px;
        padding: 16px 20px;
        font-size: 14px;
        color: #92400E;
        display: flex;
        align-items: flex-start;
        gap: 12px;
        margin: 16px 0 24px;
        line-height: 1.5;
    }}

    .provenance-icon {{
        font-size: 20px;
        flex-shrink: 0;
        line-height: 1.4;
    }}

    .provenance-content {{
        flex: 1;
    }}

    /* Status badges */
    .status-badge {{
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.3;
    }}

    .status-simulated {{
        background-color: #FEF3C7;
        color: #92400E;
        border: 1px solid #FDE68A;
    }}

    .status-verified {{
        background-color: #D1FAE5;
        color: #065F46;
        border: 1px solid #A7F3D0;
    }}

    .status-derived {{
        background-color: #DBEAFE;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
    }}

    /* Sidebar improvements */
    [data-testid='stSidebar'] > div:first-child {{
        padding-top: 2rem;
    }}

    [data-testid='stSidebar'] h1,
    [data-testid='stSidebar'] h2,
    [data-testid='stSidebar'] .sidebar-header {{
        font-size: 1.25rem;
        font-weight: 700;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.01em;
    }}

    /* Metric comparison highlight cards */
    .comparison-highlight {{
        background-color: {COLORS["bg_page"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        padding: 12px 16px;
        margin: 8px 0;
    }}

    /* Streamlit Tab styling */
    button[data-baseweb="tab"] {{
        font-size: 14px;
        font-weight: 500;
        color: {COLORS["text_secondary"]};
        padding: 8px 16px;
        border-radius: 6px 6px 0 0;
        transition: all 0.2s ease;
    }}

    button[data-baseweb="tab"]:hover {{
        color: {COLORS["primary"]};
        background-color: {COLORS["bg_sidebar"]};
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS["primary"]} !important;
        font-weight: 600 !important;
        border-bottom: 2px solid {COLORS["primary"]} !important;
    }}

    /* Custom smooth scrollbars */
    ::-webkit-scrollbar {{
        width: 8px;
        height: 8px;
    }}

    ::-webkit-scrollbar-track {{
        background: {COLORS["bg_sidebar"]};
    }}

    ::-webkit-scrollbar-thumb {{
        background: #CBD5E1;
        border-radius: 4px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS["text_muted"]};
    }}

    /* Streamlit dataframe headers & container */
    [data-testid="stDataFrame"] {{
        border: 1px solid {COLORS["border"]};
        border-radius: 8px;
        overflow: hidden;
    }}

    .stDataFrame table thead th {{
        background-color: {COLORS["bg_page"]} !important;
        color: {COLORS["text_primary"]} !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        border-bottom: 2px solid {COLORS["border"]} !important;
        letter-spacing: 0.3px;
    }}
    </style>
    """
    st.markdown(css_content, unsafe_allow_html=True)


def kpi_card_html(
    label: str,
    value: str,
    subtitle: str,
    icon: str = "",
    color: str = COLORS["primary"],
) -> str:
    """Generate HTML markup for a styled KPI card.

    Args:
        label: The metric label or name (e.g., 'Funded Planning Areas').
        value: The main displayed metric value (e.g., '4 / 6').
        subtitle: Secondary descriptive text (e.g., 'Zones receiving investment').
        icon: Optional emoji icon (e.g., '🏗️').
        color: CSS hex color for the left border accent. Defaults to primary teal.

    Returns:
        Rendered HTML string formatted with .kpi-card CSS classes.
    """
    icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ""
    return (
        f'<div class="kpi-card" style="border-left: 4px solid {color};">\n'
        f'    <div style="display: flex; justify-content: space-between; align-items: flex-start;">\n'
        f'        <span class="kpi-label">{label}</span>\n'
        f'        {icon_html}\n'
        f'    </div>\n'
        f'    <div class="kpi-value">{value}</div>\n'
        f'    <div class="kpi-subtitle">{subtitle}</div>\n'
        f'</div>'
    )


def section_header_html(icon: str, title: str) -> str:
    """Generate HTML markup for a styled section header.

    Args:
        icon: Emoji icon prefix (e.g., '📊').
        title: Header title text.

    Returns:
        Rendered HTML string formatted with .section-header CSS class.
    """
    icon_part = f"<span>{icon}</span> " if icon else ""
    return f'<div class="section-header">{icon_part}<span>{title}</span></div>'

