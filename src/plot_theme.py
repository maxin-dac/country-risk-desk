"""Theme centralise pour tous les graphiques Plotly.

- Fond transparent, sans contour
- Unites affichees dans le titre du visuel (pas de titres d'axes)
"""

# Unites par indicateur (en, fr) - source de verite unique
UNITS = {
    "Reserves": ("months of imports", "mois d'importations"),
    "Current account": ("% GDP", "% PIB"),
    "External debt": ("% GNI", "% RNB"),
    "Debt service": ("% exports", "% exports"),
    "GDP growth": ("%", "%"),
    "Inflation": ("%", "%"),
    "Fiscal balance": ("% GDP", "% PIB"),
    "Gen gov debt": ("% GDP", "% PIB"),
    "Gov debt": ("% GDP", "% PIB"),
    "Unemployment": ("%", "%"),
    "Youth unemployment": ("%", "%"),
    "Political stability": ("index -2.5 to 2.5", "indice -2,5 a 2,5"),
    "Control of corruption": ("index -2.5 to 2.5", "indice -2,5 a 2,5"),
    "Rule of law": ("index -2.5 to 2.5", "indice -2,5 a 2,5"),
    "Regulatory quality": ("index -2.5 to 2.5", "indice -2,5 a 2,5"),
    "Gini": ("index 0-100", "indice 0-100"),
    "Dependency ratio": ("%", "%"),
    "Commodity dependence": ("% exports", "% exports"),
    "Risk score": ("/100", "/100"),
}


def unit_suffix(indicator, lang="en"):
    u = UNITS.get(indicator)
    if not u:
        return ""
    return "(" + u[1 if lang == "fr" else 0] + ")"


def apply_theme(fig, title="", unit=None, y_indicator=None, y_label=None,
                x_label=None, x_indicator=None):
    """Theme transparent + unite dans le titre. Les anciens kwargs
    (y_label, x_label, x_indicator) sont acceptes mais ignores."""
    if unit is None and y_indicator:
        unit = unit_suffix(y_indicator)
    if unit:
        if not title:
            title = unit
        elif not title.endswith(unit):
            title = f"{title} {unit}"
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#d7e2ec", size=11),
        title=dict(text=title, font=dict(size=13, color="#9fb3c8"), x=0.02),
        margin=dict(l=50, r=20, t=40, b=40),
        showlegend=False,
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(159,179,200,.08)",
                     zeroline=False, tickfont=dict(color="#9fb3c8", size=10))
    fig.update_yaxes(showgrid=True, gridcolor="rgba(159,179,200,.08)",
                     zeroline=False, tickfont=dict(color="#9fb3c8", size=10))
    return fig
