from .i18n import t

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:wght@400;500;700;900&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{--ink:#0C1411;--panel:#131E19;--panel2:#182721;--line:rgba(231,237,233,.10);--text:#E7EDE9;--muted:#8FA69A;
--up:#3FD68C;--down:#FF6E5E;--warn:#F4B942;--data:#79D4E8;--mono:'IBM Plex Mono',monospace;--disp:'Archivo',sans-serif}
.stApp{background:
 radial-gradient(1100px 480px at 85% -10%,rgba(121,212,232,.06),transparent 60%),
 radial-gradient(900px 480px at -10% 110%,rgba(63,214,140,.05),transparent 60%),
 repeating-linear-gradient(0deg,transparent 0 39px,rgba(231,237,233,.03) 39px 40px),
 repeating-linear-gradient(90deg,transparent 0 39px,rgba(231,237,233,.03) 39px 40px),var(--ink)}
#MainMenu,footer{visibility:hidden}
html,body,.stMarkdown,.stButton{font-family:var(--disp)}
section[data-testid="stSidebar"]{background:rgba(12,20,17,.78);border-right:1px solid var(--line)}
section[data-testid="stSidebar"] label{font-family:var(--mono);font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;color:var(--muted)}
.masthead{padding:1.4rem 0 1rem;border-bottom:1px solid var(--line);margin-bottom:.6rem}
.eyebrow{font-family:var(--mono);font-size:.7rem;letter-spacing:.22em;text-transform:uppercase;color:var(--muted);margin-bottom:.5rem}
.desk-title{font-weight:900;text-transform:uppercase;font-size:clamp(2.2rem,5vw,3.6rem);line-height:.95;letter-spacing:-.02em;margin:0}
.desk-title span{color:var(--data)}
.statusline{display:flex;flex-wrap:wrap;gap:1.1rem;margin-top:.9rem;font-family:var(--mono);font-size:.7rem;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:6px;animation:pulse 2.2s infinite}
.dot-ok{background:var(--up);box-shadow:0 0 0 0 rgba(63,214,140,.5)}
.dot-warn{background:var(--warn);box-shadow:0 0 0 0 rgba(244,185,66,.5)}
@keyframes pulse{0%{box-shadow:0 0 0 0 rgba(255,255,255,.22)}70%{box-shadow:0 0 0 7px rgba(255,255,255,0)}100%{box-shadow:0 0 0 0 rgba(255,255,255,0)}}
.coverage{font-family:var(--mono);font-size:.7rem;color:var(--muted);letter-spacing:.12em;text-transform:uppercase;margin-top:.5rem}
.ticker{overflow:hidden;border-bottom:1px solid var(--line);margin-bottom:1.4rem;padding:.45rem 0}
.ticker-track{display:inline-block;white-space:nowrap;font-family:var(--mono);font-size:.72rem;letter-spacing:.18em;color:var(--muted);animation:scroll 30s linear infinite}
.ticker:hover .ticker-track{animation-play-state:paused}
.ticker b{color:var(--data);font-weight:600}
@keyframes scroll{from{transform:translateX(0)}to{transform:translateX(-50%)}}
.stButton>button{font-family:var(--mono);font-weight:600;text-transform:uppercase;letter-spacing:.14em;font-size:.78rem;
 background:var(--up);color:#07130C;border:none;border-radius:4px;padding:.85rem 1.6rem;width:100%;
 transition:transform .18s,box-shadow .18s,background .18s;box-shadow:0 0 0 1px rgba(63,214,140,.35),0 8px 24px rgba(63,214,140,.12)}
.stButton>button:hover{transform:translateY(-2px);background:#63E6A6;box-shadow:0 0 0 1px rgba(63,214,140,.6),0 12px 30px rgba(63,214,140,.22)}
.brief{background:linear-gradient(180deg,var(--panel2),var(--panel));border:1px solid var(--line);border-radius:6px;
 padding:1.1rem 1.3rem;margin-bottom:1rem;transition:transform .2s,border-color .2s,box-shadow .2s;animation:rise .55s ease both}
.brief:hover{transform:translateY(-3px);border-color:rgba(231,237,233,.22);box-shadow:0 14px 34px rgba(0,0,0,.35)}
.brief:nth-of-type(1){animation-delay:.05s}.brief:nth-of-type(2){animation-delay:.15s}
.brief:nth-of-type(3){animation-delay:.25s}.brief:nth-of-type(4){animation-delay:.35s}.brief:nth-of-type(5){animation-delay:.45s}
.brief:nth-of-type(6){animation-delay:.55s}
@keyframes rise{from{transform:translateY(14px)}to{transform:none}}
.brief h3{font-family:var(--mono);font-size:.7rem;font-weight:600;letter-spacing:.2em;text-transform:uppercase;color:var(--muted);
 margin:0 0 .8rem;padding-bottom:.5rem;border-bottom:1px solid var(--line)}
.brief.data{border-left:3px solid var(--data)}.brief.ctx{border-left:3px solid var(--warn)}
.brief.risk{border-left:3px solid var(--down)}.brief.opp{border-left:3px solid var(--up)}
.bignum{font-family:var(--mono);font-size:2.4rem;font-weight:600;color:var(--data);line-height:1.1}
.deltaline{font-family:var(--mono);font-size:.8rem;color:var(--muted);margin-top:.35rem}
.kv{font-size:.92rem;margin:.4rem 0}
.evidence{border-left:2px solid var(--warn);background:rgba(244,185,66,.06);padding:.45rem .8rem;margin:.45rem 0;
 font-family:var(--mono);font-size:.76rem;color:var(--muted);font-style:italic}
.chip{display:inline-block;font-family:var(--mono);font-size:.64rem;letter-spacing:.1em;padding:2px 8px;border-radius:3px;border:1px solid var(--line);color:var(--muted);margin-right:6px}
.chip.risk{color:var(--down);border-color:rgba(255,110,94,.4)}.chip.opp{color:var(--up);border-color:rgba(63,214,140,.4)}
.src a{color:var(--data);text-decoration:none;font-family:var(--mono);font-size:.78rem;
 background:linear-gradient(currentColor,currentColor) no-repeat 0 100%/0 1px;transition:background-size .25s}
.src a:hover{background-size:100% 1px}
.insufficient{border:1px dashed rgba(244,185,66,.45);border-radius:4px;color:var(--warn);font-family:var(--mono);
 font-size:.74rem;letter-spacing:.12em;text-transform:uppercase;padding:.8rem 1rem;margin:.5rem 0}
::-webkit-scrollbar{width:8px}::-webkit-scrollbar-track{background:var(--ink)}
::-webkit-scrollbar-thumb{background:#2A3A33;border-radius:4px}::-webkit-scrollbar-thumb:hover{background:#3A4F45}
</style>"""

def masthead(n_c, n_i, date_str, model, lang, ticker_items):
    tick = " &nbsp;·&nbsp; ".join(ticker_items)
    return f"""<div class="masthead">
<div class="eyebrow">{t('eyebrow', lang)} {date_str}</div>
<h1 class="desk-title">{t('title_a', lang)} <span>{t('title_b', lang)}</span></h1>
<div class="statusline">
<span><span class="dot dot-ok"></span>{t('st_llm', lang)} · {model}</span>
<span><span class="dot dot-ok"></span>{t('st_search', lang)} · Tavily</span>
<span><span class="dot dot-ok"></span>{t('st_data', lang)} · WB + IMF WEO + WGI</span>
<span><span class="dot dot-warn"></span>{t('st_mode', lang)}</span></div>
<div class="coverage">{t('coverage', lang)} : {n_c} {t('countries_w', lang)} · {t('official_only', lang)}</div>
</div>
<div class="ticker"><div class="ticker-track">{tick} &nbsp;·&nbsp; {tick}</div></div>
"""
