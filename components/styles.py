"""Design system and CSS theme definitions for the Pune Climate Optimizer dashboard.

Provides unified styling, responsive typography, custom KPI cards, animated elements,
color palettes, and dimension mappings across all application views.
"""

import streamlit as st

# Color palette constants — Premium Civic Design Identity
COLORS = {
    "primary": "#426B52",          # Forest Green Primary Accent
    "primary_dark": "#2E4B39",     # Deep Forest Green
    "accent": "#426B52",           # Primary Green for metrics
    "accent_light": "#E8EFE9",     # Soft Sage Tint
    "terracotta": "#C17C57",       # Muted Terracotta Accent
    "warning": "#D5A34A",          # Soft Amber for Risk/Alerts
    "danger": "#BD4F43",           # Editorial Brick/Crimson
    "text_primary": "#252B27",     # Charcoal Primary Typography
    "text_secondary": "#575F59",   # Muted Charcoal Secondary
    "text_muted": "#8A948C",       # Soft Grey Muted
    "bg_page": "#F6F5EF",          # Warm Ivory Background
    "bg_card": "#FFFFFF",          # Pure White Content Surface
    "bg_surface_warm": "#EFECE4",  # Warm Grey / Sand Surface
    "bg_sidebar": "#EFECE4",       # Warm Grey Sidebar Surface
    "border": "#DCD7CC",           # Subtle Warm Border
    "border_light": "#EAE6DC",     # Delicate Divider Border
}

# Dimension specific color assignments — Editorial & Earth-tone Palette
DIMENSION_COLORS = {
    "flood": "#3E6B89",            # Slate/Ocean Blue
    "heat": "#C17C57",             # Muted Terracotta
    "equity": "#426B52",           # Forest Green
    "infrastructure": "#6B5B7B",   # Soft Plum / Muted Violet
    "urgency": "#D5A34A",          # Soft Amber
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
    /* Google Fonts Import: Newsreader (Editorial Serif), Inter, & Material Symbols */
    @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=Inter:wght@400;500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap');

    /* Global typography and root font assignment */
    html, body, [class*="css"], [class*="st-"]:not([data-testid="stIconMaterial"]), .stApp {{
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        color: {COLORS["text_primary"]};
        background-color: {COLORS["bg_page"]};
    }}

    /* Editorial headings styling */
    h1, h2, h3, .editorial-heading {{
        font-family: 'Newsreader', Georgia, serif !important;
        font-weight: 500 !important;
        color: {COLORS["text_primary"]} !important;
        letter-spacing: -0.015em !important;
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

    /* Main container spacing and civic layout */
    .main .block-container {{
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 1240px;
    }}

    /* Executive KPI Card styling — Civic Architectural Refinement */
    .kpi-card {{
        background-color: {COLORS["bg_card"]};
        border-radius: 4px;
        border: 1px solid {COLORS["border"]};
        border-top: 3px solid {COLORS["primary"]};
        padding: 16px 18px;
        min-height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        box-sizing: border-box;
        box-shadow: none;
        transition: border-color 0.15s ease;
    }}

    .kpi-card:hover {{
        border-color: {COLORS["primary"]};
    }}

    .kpi-label {{
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: {COLORS["text_secondary"]};
        font-weight: 600;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }}

    .kpi-icon {{
        font-size: 17px;
        line-height: 1;
        margin-left: 8px;
        flex-shrink: 0;
        opacity: 0.85;
    }}

    .kpi-value {{
        font-family: 'Newsreader', Georgia, serif;
        font-size: 28px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        margin: 6px 0 2px;
        line-height: 1.15;
    }}

    .kpi-subtitle {{
        font-size: 11.5px;
        color: {COLORS["text_muted"]};
        line-height: 1.3;
    }}

    /* Section header styling — Editorial Divider */
    .section-header {{
        font-family: 'Newsreader', Georgia, serif;
        font-size: 22px;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        padding-bottom: 8px;
        border-bottom: 1px solid {COLORS["border"]};
        margin: 36px 0 18px;
        display: flex;
        align-items: center;
        gap: 10px;
        letter-spacing: -0.01em;
    }}

    /* Provenance advisory banner — Architectural Note Style */
    .provenance-banner {{
        background-color: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-left: 4px solid {COLORS["warning"]};
        border-radius: 4px;
        padding: 16px 20px;
        font-size: 13.5px;
        color: {COLORS["text_primary"]};
        display: flex;
        align-items: flex-start;
        gap: 14px;
        margin: 20px 0 28px;
        line-height: 1.55;
    }}

    .provenance-icon {{
        font-size: 18px;
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
        padding: 2px 8px;
        border-radius: 3px;
        font-size: 10.5px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        line-height: 1.3;
    }}

    .status-simulated {{
        background-color: #F7EFE2;
        color: #8C5E19;
        border: 1px solid #E8D3B0;
    }}

    .status-verified {{
        background-color: #E8EFE9;
        color: #2E4B39;
        border: 1px solid #C4D7C7;
    }}

    .status-derived {{
        background-color: #E7EDF1;
        color: #2D4C61;
        border: 1px solid #CAD7E0;
    }}

    /* Sidebar styling — Warm Grey Sand Surface */
    [data-testid='stSidebar'] {{
        background-color: {COLORS["bg_sidebar"]};
        border-right: 1px solid {COLORS["border"]};
    }}

    [data-testid='stSidebar'] > div:first-child {{
        padding-top: 2rem;
    }}

    [data-testid='stSidebar'] h1,
    [data-testid='stSidebar'] h2,
    [data-testid='stSidebar'] .sidebar-header {{
        font-family: 'Newsreader', Georgia, serif;
        font-size: 1.3rem;
        font-weight: 600;
        color: {COLORS["text_primary"]};
        letter-spacing: -0.01em;
    }}

    /* Metric comparison highlight cards */
    .comparison-highlight {{
        background-color: {COLORS["bg_card"]};
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        padding: 12px 16px;
        margin: 8px 0;
    }}

    /* Streamlit Tab styling — Understated Tab Bar */
    button[data-baseweb="tab"] {{
        font-size: 13.5px;
        font-weight: 500;
        color: {COLORS["text_secondary"]};
        padding: 8px 16px;
        border-radius: 0;
        background-color: transparent !important;
        border-bottom: 2px solid transparent !important;
        transition: color 0.15s ease;
    }}

    button[data-baseweb="tab"]:hover {{
        color: {COLORS["primary"]};
    }}

    button[data-baseweb="tab"][aria-selected="true"] {{
        color: {COLORS["primary"]} !important;
        font-weight: 600 !important;
        border-bottom: 2px solid {COLORS["primary"]} !important;
    }}

    /* Custom understated scrollbars */
    ::-webkit-scrollbar {{
        width: 6px;
        height: 6px;
    }}

    ::-webkit-scrollbar-track {{
        background: {COLORS["bg_page"]};
    }}

    ::-webkit-scrollbar-thumb {{
        background: #DCD7CC;
        border-radius: 3px;
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS["text_muted"]};
    }}

    /* Streamlit dataframe headers & container */
    [data-testid="stDataFrame"] {{
        border: 1px solid {COLORS["border"]};
        border-radius: 4px;
        overflow: hidden;
        background-color: {COLORS["bg_card"]};
    }}

    .stDataFrame table thead th {{
        background-color: {COLORS["bg_surface_warm"]} !important;
        color: {COLORS["text_primary"]} !important;
        font-weight: 600 !important;
        font-size: 12px !important;
        border-bottom: 1px solid {COLORS["border"]} !important;
        letter-spacing: 0.4px;
        text-transform: uppercase;
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
        color: CSS hex color for the accent border. Defaults to primary forest green.

    Returns:
        Rendered HTML string formatted with .kpi-card CSS classes.
    """
    icon_html = f'<span class="kpi-icon">{icon}</span>' if icon else ""
    return (
        f'<div class="kpi-card" style="border-left: 4px solid {color}; border-top: 2px solid {color};">\n'
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

