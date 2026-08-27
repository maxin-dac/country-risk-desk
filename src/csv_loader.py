import pandas as pd

REQUIRED = {"country", "indicator", "category", "date", "value", "unit", "region"}

def load_csv(path):
    df = pd.read_csv(path, dtype={"region": str, "country": str, "indicator": str, "unit": str, "source": str})
    missing = REQUIRED - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    for c in ("country", "indicator", "category", "region", "unit", "source"):
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    return df

def _closest(df, target, days):
    if df.empty:
        return None
    d = (df["date"] - target).abs()
    i = d.idxmin()
    return df.loc[i] if d[i] <= pd.Timedelta(days=days) else None

def _pct(cur, prev):
    return (cur - prev) / abs(prev) * 100 if prev else None

def get_stats(df, country, indicator):
    s = df[(df.country == country) & (df.indicator == indicator)] \
        .dropna(subset=["date", "value"]).sort_values("date")
    if s.empty:
        return {"available": False, "country": country, "indicator": indicator}
    last = s.iloc[-1]
    p3 = _closest(s, last.date - pd.DateOffset(months=3), 75)
    p12 = _closest(s, last.date - pd.DateOffset(months=12), 120)
    out = {
        "available": True, "country": country, "indicator": indicator,
        "category": last.get("category", ""), "unit": last.get("unit", ""),
        "region": last.get("region", ""), "source": last.get("source", ""),
        "latest_date": last.date.date().isoformat(), "latest_value": float(last.value),
        "prev3_value": float(p3.value) if p3 is not None else None,
        "prev12_value": float(p12.value) if p12 is not None else None,
        "change_3m_pct": _pct(last.value, p3.value) if p3 is not None else None,
        "change_12m_pct": _pct(last.value, p12.value) if p12 is not None else None,
    }
    reg = df[(df.indicator == indicator) & (df.region == out["region"])].dropna(subset=["date", "value"])
    reg = reg[reg.date >= last.date - pd.Timedelta(days=730)]
    if not reg.empty:
        per = reg.sort_values("date").groupby("country").tail(1)
        med = float(per.value.median())
        out.update(
            regional_median=med,
            regional_countries=int(per.country.nunique()),
            regional_position="above" if last.value > med * 1.02 else "below" if last.value < med * 0.98 else "near",
        )
    return out

def format_stats(st_):
    if not st_.get("available"):
        return "No CSV data for this country/indicator."
    lines = [
        f"Indicator: {st_['indicator']} ({st_['category']})",
        f"Country: {st_['country']} ({st_['region']})",
        f"Latest: {st_['latest_value']:.2f} {st_['unit']} on {st_['latest_date']} (source: {st_['source']})",
    ]
    if st_.get("change_3m_pct") is not None:
        lines.append(f"3-month change: {st_['change_3m_pct']:+.1f}%")
    if st_.get("change_12m_pct") is not None:
        lines.append(f"12-month change: {st_['change_12m_pct']:+.1f}%")
    if st_.get("regional_median") is not None:
        lines.append(f"Regional median ({st_['region']}, {st_['regional_countries']} countries): "
                     f"{st_['regional_median']:.2f} {st_['unit']} - position: {st_['regional_position']}")
    return "\n".join(lines)