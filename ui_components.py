"""
RTU Study Programme AI Recommender
ui_components.py — Reusable Streamlit UI building blocks.

All card rendering, metric displays, badges, and visual helpers live here.
"""

import streamlit as st
from typing import Optional

from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS, get_label,
)

# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILITY BAR
# ─────────────────────────────────────────────────────────────────────────────

def render_compatibility_bar(score: float, rank: int = 1):
    """Render a styled compatibility percentage bar."""
    if score >= 75:
        color = "#22c55e"   # green
        emoji = "🟢"
    elif score >= 55:
        color = "#f59e0b"   # amber
        emoji = "🟡"
    elif score >= 35:
        color = "#f97316"   # orange
        emoji = "🟠"
    else:
        color = "#ef4444"   # red
        emoji = "🔴"

    st.markdown(
        f"""
        <div style="margin-bottom:8px;">
          <div style="display:flex; align-items:center; gap:10px;">
            <span style="font-size:0.85rem; color:#6b7280; min-width:110px;">
              {emoji} Atbilstība
            </span>
            <div style="
              flex:1; height:14px; background:#e5e7eb; border-radius:7px; overflow:hidden;
            ">
              <div style="
                width:{score:.1f}%; height:100%; background:{color};
                border-radius:7px; transition:width 0.4s ease;
              "></div>
            </div>
            <span style="
              font-size:1.1rem; font-weight:700; color:{color}; min-width:52px;
            ">{score:.0f}%</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────────────────────────────────────
# BADGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _badge(text: str, color: str = "#3b82f6", text_color: str = "white") -> str:
    return (
        f'<span style="'
        f'background:{color}; color:{text_color}; padding:2px 8px; border-radius:12px;'
        f'font-size:0.75rem; font-weight:600; margin:2px; display:inline-block;">'
        f"{text}</span>"
    )


def render_tags(items: list[str], mapping: dict, color: str = "#3b82f6"):
    """Render a row of coloured tag badges from canonical keys."""
    if not items:
        st.caption("—")
        return
    labels = [get_label(mapping, k) for k in items if k]
    html = " ".join(_badge(lbl, color) for lbl in labels[:8])
    st.markdown(html, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RESULT CARD
# ─────────────────────────────────────────────────────────────────────────────

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
RANK_COLORS = {1: "#fbbf24", 2: "#9ca3af", 3: "#d97706"}


def render_result_card(
    rank: int,
    programme: dict,
    score: float,
    breakdown: dict,
    ai_explanation: str,
    is_ai: bool,
    summary: dict,
    on_save=None,
):
    """
    Render a full recommendation result card.

    Args:
        rank:           1, 2, or 3
        programme:      Normalised programme dict
        score:          Compatibility float 0–100
        breakdown:      Raw scoring breakdown
        ai_explanation: Generated explanation text (markdown)
        is_ai:          True if Gemini-generated
        summary:        Human-readable breakdown from scoring.breakdown_summary()
        on_save:        Callback when 'Save' clicked (optional)
    """
    medal = RANK_MEDALS.get(rank, f"#{rank}")
    m_color = RANK_COLORS.get(rank, "#6b7280")

    prog_id = programme.get("id", str(rank))
    is_saved = prog_id in st.session_state.get("saved_programmes", set())

    with st.container():
        st.markdown(
            f"""
            <div style="
              border:2px solid {m_color}20;
              border-left: 5px solid {m_color};
              border-radius:12px; padding:4px 16px 4px 16px;
              background: {'#fffbeb' if rank == 1 else 'var(--background-color)'};
              margin-bottom:8px;
            ">
              <h3 style="margin:8px 0 4px 0; font-size:1.05rem; color:{m_color};">
                {medal} #{rank} — {programme.get('name', 'Nezināma programma')}
              </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_title, col_save = st.columns([5, 1])
        with col_title:
            if programme.get("name_en"):
                st.caption(f"🌐 {programme['name_en']}")
        with col_save:
            saved_label = "❤️ Saglabāts" if is_saved else "🤍 Saglabāt"
            if st.button(saved_label, key=f"save_{prog_id}_{rank}", use_container_width=True):
                if on_save:
                    on_save(prog_id, programme)

        # ── Compatibility bar ──────────────────────────────────────────────
        render_compatibility_bar(score, rank)

        # ── Quick info pills ───────────────────────────────────────────────
        _render_info_pills(programme)

        # ── AI Explanation ─────────────────────────────────────────────────
        ai_label = "🤖 AI Paskaidrojums (Gemini)" if is_ai else "📝 Automātisks Paskaidrojums"
        with st.expander(ai_label, expanded=(rank == 1)):
            st.markdown(ai_explanation)

        # ── Why this score? ────────────────────────────────────────────────
        with st.expander("📊 Kāpēc šis rezultāts? (Sīkāk)"):
            _render_breakdown_details(summary, breakdown)

        # ── Programme details ──────────────────────────────────────────────
        with st.expander("📋 Pilnīga programmas informācija"):
            _render_programme_details(programme)

        st.divider()


def _render_info_pills(programme: dict):
    """Render quick-info metric row."""
    cols = st.columns(5)
    items = [
        ("🏛️", programme.get("faculty", "—"), "Fakultāte"),
        ("📍", ", ".join(programme.get("locations", ["Rīga"])), "Atrašanās vieta"),
        ("🕐", f"{programme.get('duration_years', 4)} gadi", "Ilgums"),
        (
            "💰",
            (f"€{programme.get('annual_fee_eur', 0):,.0f}/gadā" if programme.get("annual_fee_eur") else "Nav norādīts"),
            "Maksa",
        ),
        (
            "🎓",
            (f"{programme.get('budget_places', 0)} vietas" if programme.get("budget_places", 0) > 0 else "Nav budžeta"),
            "Budžets",
        ),
    ]
    for col, (icon, val, label) in zip(cols, items):
        with col:
            st.metric(label=f"{icon} {label}", value=val)

    # Language & exam row
    lang_badges = " ".join(
        _badge(LANG_LABELS.get(l, l), "#6366f1")
        for l in programme.get("languages", ["lv"])
    )
    exam_badge = (
        _badge("⚠️ Iestājpārbaudījums", "#ef4444")
        if programme.get("entry_exam")
        else _badge("✅ Nav iestājpārbaudījuma", "#22c55e")
    )
    prog_type = programme.get("program_type", "")
    type_short = (
        "🎓 Akadēmiskais" if "akadēm" in prog_type.lower()
        else "🔧 Profesionālais" if "profesion" in prog_type.lower()
        else prog_type[:30]
    )
    type_badge = _badge(type_short, "#8b5cf6")

    st.markdown(
        f"<div style='margin:8px 0;'>{lang_badges} &nbsp; {exam_badge} &nbsp; {type_badge}</div>",
        unsafe_allow_html=True,
    )


def _render_breakdown_details(summary: dict, breakdown: dict):
    """Render the detailed scoring breakdown."""
    c1, c2 = st.columns(2)

    with c1:
        if summary.get("matched_interests"):
            st.markdown("**✅ Sakrītošās intereses:**")
            for item in summary["matched_interests"]:
                st.markdown(f"  - {item}")
        else:
            st.info("Nav sakrītošu interešu jomu.")

        if summary.get("matched_strengths"):
            st.markdown("**✅ Sakrītošās stiprās puses:**")
            for item in summary["matched_strengths"]:
                st.markdown(f"  - {item}")

        if summary.get("matched_personality"):
            st.markdown("**✅ Personības atbilstība:**")
            for item in summary["matched_personality"]:
                st.markdown(f"  - {item}")

    with c2:
        if summary.get("matched_sectors"):
            st.markdown("**✅ Nozares atbilstība:**")
            for item in summary["matched_sectors"]:
                st.markdown(f"  - {item}")

        if summary.get("missed_interests"):
            st.markdown("**⬜ Nesakrītošas intereses:**")
            for item in summary["missed_interests"][:4]:
                st.markdown(f"  - {item}")

        if summary.get("penalties"):
            st.markdown("**⚠️ Sodu faktori:**")
            for p in summary["penalties"]:
                st.warning(p)

    # Mini score chart
    st.markdown("**📊 Vērtēšanas sadalījums:**")
    score_items = [
        ("Intereses", breakdown.get("interests", {}).get("points", 0), breakdown.get("interests", {}).get("max", 1)),
        ("Stiprās puses", breakdown.get("strengths", {}).get("points", 0), breakdown.get("strengths", {}).get("max", 1)),
        ("Personība", breakdown.get("personality", {}).get("points", 0), breakdown.get("personality", {}).get("max", 1)),
        ("Nozares", breakdown.get("sectors", {}).get("points", 0), breakdown.get("sectors", {}).get("max", 1)),
        ("Valoda", breakdown.get("language", {}).get("points", 0), breakdown.get("language", {}).get("max", 1)),
    ]
    for label, pts, max_pts in score_items:
        if max_pts and max_pts > 0:
            pct = (pts / max_pts) * 100
            st.markdown(
                f"""
                <div style="margin:4px 0;">
                  <span style="font-size:0.8rem; color:#6b7280; min-width:100px;
                               display:inline-block;">{label}</span>
                  <div style="display:inline-flex; align-items:center; gap:6px; width:70%;">
                    <div style="flex:1; height:8px; background:#e5e7eb; border-radius:4px;">
                      <div style="width:{pct:.0f}%; height:100%; background:#6366f1;
                                  border-radius:4px;"></div>
                    </div>
                    <span style="font-size:0.75rem; color:#374151;">
                      {pts}/{max_pts}
                    </span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _render_programme_details(programme: dict):
    """Render full programme details section."""
    c1, c2 = st.columns(2)
    m = programme.get("matching", {}) or {}
    career = programme.get("career", {}) or {}
    degree = programme.get("degree", {}) or {}

    with c1:
        st.markdown("**📌 Pamatinformācija**")
        info_items = {
            "Nosaukums": programme.get("name", "—"),
            "Angļu nosaukums": programme.get("name_en") or "—",
            "Fakultāte": programme.get("faculty", "—"),
            "Tips": programme.get("program_type", "—"),
            "Studiju virziens": programme.get("study_direction") or "—",
            "Studiju nozare": programme.get("study_field") or "—",
        }
        for k, v in info_items.items():
            if v and v != "—":
                st.markdown(f"**{k}:** {v}")

        st.markdown("**🎓 Grāds**")
        st.markdown(f"{degree.get('title', '—')}")
        if degree.get("title_en"):
            st.caption(degree["title_en"])
        if degree.get("professional_qualification"):
            st.caption(f"Kvalifikācija: {degree['professional_qualification']}")

    with c2:
        st.markdown("**🔧 Loģistika**")
        log_items = {
            "Ilgums": f"{programme.get('duration_years', 4)} gadi",
            "Kredītpunkti": str(programme.get("credits", 240)),
            "Studiju forma": programme.get("format", "Pilna laika"),
            "Valodas": ", ".join(LANG_LABELS.get(l, l) for l in programme.get("languages", [])),
            "Atrašanās vietas": ", ".join(programme.get("locations", [])),
        }
        for k, v in log_items.items():
            st.markdown(f"**{k}:** {v}")

        st.markdown("**💰 Finanses**")
        fee = programme.get("annual_fee_eur")
        budget = programme.get("budget_places", 0)
        st.markdown(f"**Gada maksa:** {'€' + str(int(fee)) if fee else 'Nav norādīts'}")
        st.markdown(f"**Budžeta vietas:** {budget if budget > 0 else 'Nav budžeta vietu'}")

        exam = programme.get("entry_exam", False)
        st.markdown(f"**Iestājpārbaudījums:** {'⚠️ Jā' if exam else '✅ Nē'}")
        if exam and programme.get("entry_exam_details"):
            st.caption(programme["entry_exam_details"])

    # Description
    if programme.get("description"):
        st.markdown("**📖 Apraksts**")
        st.markdown(programme["description"][:600] + ("..." if len(programme.get("description", "")) > 600 else ""))

    # Career
    if career.get("description") or career.get("job_titles"):
        st.markdown("**💼 Karjera**")
        if career.get("description"):
            st.caption(career["description"][:300])
        if career.get("job_titles"):
            jobs = career["job_titles"][:6]
            st.markdown("*Amati:* " + " · ".join(f"`{j}`" for j in jobs))

    # URL
    if programme.get("url"):
        st.markdown(f"🔗 [Atvērt RTU mājas lapā]({programme['url']})")


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON TABLE
# ─────────────────────────────────────────────────────────────────────────────

def render_comparison_table(saved_progs: list[dict], scores: dict[str, float]):
    """Render a side-by-side comparison of saved programmes."""
    if not saved_progs:
        st.info("Nav saglabātu programmu. Saglabā kādu programmu no rezultātiem!")
        return

    # Build comparison data
    fields = [
        ("Nosaukums", lambda p: p.get("name", "—")),
        ("Angļu nosaukums", lambda p: p.get("name_en") or "—"),
        ("Atbilstība", lambda p: f"{scores.get(p.get('id', ''), 0):.0f}%"),
        ("Fakultāte", lambda p: p.get("faculty", "—")),
        ("Ilgums", lambda p: f"{p.get('duration_years', 4)} gadi"),
        ("Valodas", lambda p: ", ".join(p.get("languages", []))),
        ("Gada maksa", lambda p: f"€{int(p['annual_fee_eur'])}" if p.get("annual_fee_eur") else "—"),
        ("Budžeta vietas", lambda p: str(p.get("budget_places", 0)) if p.get("budget_places", 0) > 0 else "Nav"),
        ("Iestājpārbaudījums", lambda p: "⚠️ Jā" if p.get("entry_exam") else "✅ Nē"),
        ("Matemātika intensīva", lambda p: "✅ Jā" if p.get("matching", {}).get("math_intensive") else "—"),
        ("Pētnieciskā", lambda p: "✅ Jā" if p.get("matching", {}).get("research_oriented") else "—"),
        ("Starptautisks", lambda p: "✅ Jā" if p.get("matching", {}).get("international_potential") else "—"),
    ]

    cols = st.columns(len(saved_progs))
    for col, prog in zip(cols, saved_progs):
        with col:
            score = scores.get(prog.get("id", ""), 0)
            color = "#22c55e" if score >= 75 else "#f59e0b" if score >= 55 else "#ef4444"
            st.markdown(
                f"""<div style="border:2px solid {color}; border-radius:8px; padding:8px;
                text-align:center; margin-bottom:8px;">
                <div style="font-weight:700; font-size:0.85rem;">{prog.get('name', '—')[:40]}</div>
                <div style="font-size:1.5rem; color:{color}; font-weight:700;">{score:.0f}%</div>
                </div>""",
                unsafe_allow_html=True,
            )
            for label, fn in fields[3:]:  # skip name/en/score since already shown
                val = fn(prog)
                st.markdown(f"**{label}:** {val}")


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMME TABLE (All Programmes view)
# ─────────────────────────────────────────────────────────────────────────────

def render_programme_table(programmes: list[dict], scores: dict[str, float] | None = None):
    """Render a searchable/filterable table of all programmes."""
    import pandas as pd

    rows = []
    for p in programmes:
        m = p.get("matching", {}) or {}
        rows.append(
            {
                "Nosaukums": p.get("name", "—"),
                "English": p.get("name_en", "—"),
                "Fakultāte": (p.get("faculty", "—") or "—")[:50],
                "Tips": (
                    "Akadēmiskais"
                    if "akadēm" in (p.get("program_type") or "").lower()
                    else "Profesionālais"
                ),
                "Ilgums": f"{p.get('duration_years', 4)}g",
                "Valoda": "/".join(p.get("languages", ["lv"])).upper(),
                "Atrašanās vieta": ", ".join(p.get("locations", ["Rīga"])),
                "Maksa €/gadā": int(p["annual_fee_eur"]) if p.get("annual_fee_eur") else 0,
                "Budžeta vietas": p.get("budget_places", 0),
                "Iest. pārb.": "Jā" if p.get("entry_exam") else "Nē",
                "Matemātika": "✓" if m.get("math_intensive") else "",
                "Pētnieciskā": "✓" if m.get("research_oriented") else "",
                "Atbilstība %": round(scores.get(p.get("id", ""), 0), 0) if scores else "—",
            }
        )

    df = pd.DataFrame(rows)
    if scores:
        df = df.sort_values("Atbilstība %", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(500, 50 + len(df) * 38),
    )


# ─────────────────────────────────────────────────────────────────────────────
# HERO / STATS BANNER
# ─────────────────────────────────────────────────────────────────────────────

def render_hero():
    """Render the app hero/header section."""
    st.markdown(
        """
        <div style="
          background: linear-gradient(135deg, #c8102e 0%, #9b0022 50%, #6d0019 100%);
          border-radius: 16px; padding: 28px 32px; margin-bottom: 20px; color: white;
        ">
          <h1 style="margin:0; font-size:2rem; font-weight:800;">
            🎓 RTU Studiju Programmu AI Ieteicējs
          </h1>
          <p style="margin:8px 0 0 0; opacity:0.9; font-size:1rem;">
            Atklāj savai personībai piemērotākās RTU bakalaura studiju programmas
            ar AI palīdzību
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_stats_bar(stats: dict, n_programmes: int):
    """Render dataset statistics."""
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📚 Kopā programmas", n_programmes)
    c2.metric("📁 Ielādēti faili", stats.get("files_loaded", 0))
    c3.metric("❌ Kļūdaini faili", stats.get("files_failed", 0))
    c4.metric("📊 Versija", "1.0 MVP")


# ─────────────────────────────────────────────────────────────────────────────
# LOADING SPINNER WRAPPER
# ─────────────────────────────────────────────────────────────────────────────

def loading_spinner_context(message: str = "Aprēķina atbilstību..."):
    """Return a Streamlit spinner context manager."""
    return st.spinner(message)


# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────

def render_empty_results():
    """Render a friendly empty state."""
    st.markdown(
        """
        <div style="text-align:center; padding:40px 20px; color:#9ca3af;">
          <div style="font-size:3rem;">🔍</div>
          <h3 style="color:#6b7280;">Aizpildi savu profilu un noklikšķini uz "Atrast programmu"!</h3>
          <p>Jo vairāk informācijas sniedzat, jo precīzāki būs ieteikumi.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
