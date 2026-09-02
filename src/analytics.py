# -*- coding: utf-8 -*-
"""Analyses avancees, deterministes et factuelles :
1. Analyse de scenarios  : what-if sur les regles de seuils (brief pays).
2. Analyse temporelle    : franchissements de seuils sur 12 mois (vue globale).
3. Lecture croisee       : divergences S&P / Moody's / Fitch (vue globale).
Aucun score agregé : uniquement des regles documentees et des donnees publiees.
"""
import pandas as pd
import streamlit as st

from .i18n import cname


# ------------------------------------------------------------ 1. Scenarios
def render_scenario(df, country, indicator, stats, lang):
    from .alerts import generate_outlook
    if not stats.get("available"):
        return
    series = df[(df.country == country) & (df.indicator == indicator)]["value"]
    series = pd.to_numeric(series, errors="coerce").dropna()
    if series.empty:
        return
    lo, hi = float(series.min()), float(series.max())
    cur = float(stats["latest_value"])
    lo, hi = min(lo, cur), max(hi, cur)

    with st.expander(
            "Analyse de scenarios : que se passerait-il si la valeur changeait ?"
            if lang == "fr" else
            "Scenario analysis: what if the value changed?", expanded=False):
        v = st.slider(
            "Valeur hypothetique" if lang == "fr" else "Hypothetical value",
            min_value=lo, max_value=hi, value=cur,
            format="%.2f", key=f"scen_{country}_{indicator}")
        if abs(v - cur) < 1e-9:
            st.caption("Deplacez le curseur pour tester une valeur hypothetique."
                       if lang == "fr" else
                       "Move the slider to test a hypothetical value.")
            return
        base = generate_outlook(stats)
        scen_stats = dict(stats)
        scen_stats["latest_value"] = v
        scen = generate_outlook(scen_stats)

        def _ids(o, k):
            return {i.get("rule_id") for i in o.get(k, [])}

        def _txt(i):
            return (i.get("text_fr") if lang == "fr" else i.get("text_en")) or ""

        new_r = [i for i in scen.get("risks", []) if i.get("rule_id") not in _ids(base, "risks")]
        gone_r = [i for i in base.get("risks", []) if i.get("rule_id") not in _ids(scen, "risks")]
        new_o = [i for i in scen.get("opportunities", []) if i.get("rule_id") not in _ids(base, "opportunities")]
        gone_o = [i for i in base.get("opportunities", []) if i.get("rule_id") not in _ids(scen, "opportunities")]

        st.markdown(f"**{cur:.2f} \u2192 {v:.2f}**")
        cols = st.columns(2)
        with cols[0]:
            st.markdown("**Nouveaux risques**" if lang == "fr" else "**New risks**")
            for i in new_r:
                st.markdown(f"- {_txt(i)}")
            if not new_r:
                st.caption("Aucun." if lang == "fr" else "None.")
            st.markdown("**Risques leves**" if lang == "fr" else "**Risks cleared**")
            for i in gone_r:
                st.markdown(f"- {_txt(i)}")
            if not gone_r:
                st.caption("Aucun." if lang == "fr" else "None.")
        with cols[1]:
            st.markdown("**Nouvelles opportunites**" if lang == "fr" else "**New opportunities**")
            for i in new_o:
                st.markdown(f"- {_txt(i)}")
            if not new_o:
                st.caption("Aucune." if lang == "fr" else "None.")
            st.markdown("**Opportunites perdues**" if lang == "fr" else "**Opportunities lost**")
            for i in gone_o:
                st.markdown(f"- {_txt(i)}")
            if not gone_o:
                st.caption("Aucune." if lang == "fr" else "None.")


# ------------------------------------------------------------ 2. Temporel
def render_temporal(df, lang):
    from .alerts import RULES
    d = df.assign(date=pd.to_datetime(df["date"], errors="coerce")).dropna(subset=["date"])
    if d.empty:
        st.caption("Historique insuffisant." if lang == "fr" else "Insufficient history.")
        return
    latest = d.sort_values("date").groupby(["country", "indicator"], as_index=False).tail(1)
    cut = d["date"].max() - pd.DateOffset(months=12)
    past = d[d["date"] <= cut].sort_values("date").groupby(["country", "indicator"], as_index=False).tail(1)

    entered, exited = [], []
    for rule in RULES:
        ind = rule["indicator"]
        l = pd.to_numeric(latest[latest.indicator == ind].set_index("country")["value"], errors="coerce")
        p = pd.to_numeric(past[past.indicator == ind].set_index("country")["value"], errors="coerce")
        common = l.dropna().index.intersection(p.dropna().index)
        if len(common) == 0:
            continue
        now_t = l[common].map(rule["cond"]).fillna(False).astype(bool)
        then_t = p[common].map(rule["cond"]).fillna(False).astype(bool)
        for iso in now_t.index[(now_t & ~then_t).values]:
            entered.append((iso, rule, float(p[iso]), float(l[iso])))
        for iso in now_t.index[(~now_t & then_t).values]:
            exited.append((iso, rule, float(p[iso]), float(l[iso])))

    # Diversite : 3 signaux max par regle, pour ne pas etre domine par 1-2 regles
    def _diverse(items):
        by_rule = {}
        for it in items:
            by_rule.setdefault(it[1]["id"], []).append(it)
        out = []
        for its in by_rule.values():
            its.sort(key=lambda x: abs(x[3] - x[2]), reverse=True)
            out.extend(its[:3])
        out.sort(key=lambda x: abs(x[3] - x[2]), reverse=True)
        return out

    entered, exited = _diverse(entered), _diverse(exited)
    n_in = len({it[1]["id"] for it in entered})
    n_out = len({it[1]["id"] for it in exited})

    st.caption(
        f"Comparaison de l'etat des seuils a 12 mois d'intervalle \u00b7 "
        f"{n_in} regle(s) avec signaux apparus \u00b7 {n_out} avec signaux leves (3 max par regle)."
        if lang == "fr" else
        f"Threshold states compared at a 12-month interval \u00b7 "
        f"{n_in} rule(s) with emerged signals \u00b7 {n_out} with cleared signals (3 max per rule).")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Signaux apparus (12 mois)**" if lang == "fr" else "**Signals emerged (12 m)**")
        if not entered:
            st.caption("Aucun." if lang == "fr" else "None.")
        for iso, rule, pv, nv in entered[:15]:
            lab = rule["fr"] if lang == "fr" else rule["en"]
            st.markdown(f"- {cname(iso, lang)} \u00b7 {lab} \u00b7 {pv:.1f} \u2192 {nv:.1f}")
    with c2:
        st.markdown("**Signaux leves (12 mois)**" if lang == "fr" else "**Signals cleared (12 m)**")
        if not exited:
            st.caption("Aucun." if lang == "fr" else "None.")
        for iso, rule, pv, nv in exited[:15]:
            lab = rule["fr"] if lang == "fr" else rule["en"]
            st.markdown(f"- {cname(iso, lang)} \u00b7 {lab} \u00b7 {pv:.1f} \u2192 {nv:.1f}")



# ------------------------------------------------------------ 3. Lecture croisee
_ORD = {
    "AAA": 0, "AA+": 1, "AA": 2, "AA-": 3, "A+": 4, "A": 5, "A-": 6,
    "BBB+": 7, "BBB": 8, "BBB-": 9, "BB+": 10, "BB": 11, "BB-": 12,
    "B+": 13, "B": 14, "B-": 15, "CCC+": 16, "CCC": 17, "CCC-": 18,
    "CC": 19, "C": 20, "D": 21, "SD": 21, "RD": 21,
    "Aaa": 0, "Aa1": 1, "Aa2": 2, "Aa3": 3, "A1": 4, "A2": 5, "A3": 6,
    "Baa1": 7, "Baa2": 8, "Baa3": 9, "Ba1": 10, "Ba2": 11, "Ba3": 12,
    "B1": 13, "B2": 14, "B3": 15, "Caa1": 16, "Caa2": 17, "Caa3": 18,
    "Ca": 19,
}


def render_divergences(lang):
    from . import ratings as rat
    rows = rat._load()
    out = []

    def _cell(rt, rd):
        rt = (rt or "").strip()
        rd = (rd or "").strip()
        if not rt:
            return "-"
        if rd:
            d = pd.to_datetime(rd, errors="coerce")
            rd = d.strftime("%Y-%m-%d") if pd.notna(d) else rd
        return f"{rt} \u00b7 {rd}"
    for iso, r in rows.items():
        sp = (r.get("sp_r") or "").strip()
        mo = (r.get("mo_r") or "").strip()
        fi = (r.get("fi_r") or "").strip()
        ords = {k: _ORD.get(v) for k, v in (("S&P", sp), ("Moody's", mo), ("Fitch", fi)) if v and _ORD.get(v) is not None and _ORD.get(v) < 21}
        if len(ords) < 2:
            continue
        kinds = []
        ig = {k: (v <= 9) for k, v in ords.items()}
        if len(set(ig.values())) > 1:
            kinds.append("Investment vs speculatif" if lang == "fr" else "Investment vs speculative")
        elif (max(ords.values()) - min(ords.values())) >= 2:
            kinds.append("Ecart >= 2 crans" if lang == "fr" else "Gap >= 2 notches")
        outs = {o for o in (r.get("sp_o"), r.get("mo_o"), r.get("fi_o")) if o}
        if "Positive" in outs and "Negative" in outs:
            kinds.append("Perspectives opposees" if lang == "fr" else "Opposite outlooks")
        if kinds:
            out.append({
                ("Pays" if lang == "fr" else "Country"): cname(iso, lang),
                "S&P": _cell(sp, r.get("sp_d")), "Moody's": _cell(mo, r.get("mo_d")), "Fitch": _cell(fi, r.get("fi_d")),
                ("Divergence" if lang == "fr" else "Divergence"): " + ".join(kinds),
            })
    if not out:
        st.caption("Aucune divergence majeure detectee." if lang == "fr" else "No major divergence detected.")
        return
    st.caption(
        "Pays sur lesquels les agences publient des lectures structurellement differentes "
        "(classification, ecart de crans ou perspectives). Aucune aggregation : simple comparaison."
        if lang == "fr" else
        "Countries on which agencies publish structurally different readings "
        "(classification, notch gap or outlooks). No aggregation: plain comparison.")
    st.dataframe(pd.DataFrame(out), hide_index=True, width="stretch")
