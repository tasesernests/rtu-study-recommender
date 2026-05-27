"""
RTU Study Programme AI Recommender
ui_components.py — Reusable Streamlit UI building blocks.
"""

import streamlit as st
from typing import Optional

from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS, get_label,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

RANK_MEDALS  = {1: "🥇", 2: "🥈", 3: "🥉"}
RANK_ACCENTS = {1: "#f59e0b", 2: "#94a3b8", 3: "#d97706"}


# ─────────────────────────────────────────────────────────────────────────────
# BADGE HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _badge(text: str, bg: str = "#e0e7ff", color: str = "#3730a3") -> str:
    return (
        f'<span style="background:{bg};color:{color};padding:3px 10px;'
        f'border-radius:20px;font-size:0.74rem;font-weight:600;'
        f'margin:2px 2px;display:inline-block;white-space:nowrap;">{text}</span>'
    )


def render_tags(items: list, mapping: dict, bg: str = "#e0e7ff", color: str = "#3730a3"):
    if not items:
        st.caption("—")
        return
    labels = [get_label(mapping, k) for k in items if k]
    st.html(" ".join(_badge(lbl, bg, color) for lbl in labels[:8]))


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────

def render_hero(stats: dict, n_programmes: int):
    files_ok = stats.get("files_loaded", 0)

    feature_pills = " ".join(
        f'<span style="background:rgba(255,255,255,0.18);color:rgba(255,255,255,0.95);'
        f'border:1px solid rgba(255,255,255,0.28);border-radius:20px;'
        f'padding:5px 14px;font-size:0.78rem;font-weight:600;display:inline-block;'
        f'letter-spacing:0.01em;">{icon} {label}</span>'
        for icon, label in [
            ("✨", "AI-assisted"), ("🔍", "Explainable"), ("📊", "RTU dataset"),
        ]
    )

    steps_html = "".join(
        f'<div style="background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.15);'
        f'border-radius:8px;padding:5px 14px;font-size:0.75rem;color:rgba(255,255,255,0.88);'
        f'font-weight:500;display:inline-flex;align-items:center;gap:6px;">'
        f'<span style="background:rgba(255,255,255,0.22);border-radius:50%;width:20px;height:20px;'
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:0.68rem;font-weight:800;color:white;flex-shrink:0;">{n}</span>'
        f'{step}</div>'
        for n, step in [
            (1, "Fill profile"), (2, "Get AI recommendations"),
            (3, "Compare programmes"), (4, "Apply to RTU"),
        ]
    )

    stat_cards = "".join(
        f'<div style="background:rgba(255,255,255,0.12);border:1px solid rgba(255,255,255,0.18);'
        f'border-radius:12px;padding:10px 18px;text-align:center;min-width:72px;">'
        f'<div style="font-size:1.5rem;font-weight:900;color:{nc};letter-spacing:-0.03em;">{num}</div>'
        f'<div style="font-size:0.61rem;color:rgba(255,255,255,0.62);text-transform:uppercase;'
        f'letter-spacing:0.08em;margin-top:2px;">{lbl}</div>'
        f'</div>'
        for num, nc, lbl in [
            (n_programmes, "white", "Programmes"),
            (files_ok, "white", "Datasets"),
            ("AI", "#fbbf24", "Gemini 2.5"),
        ]
    )

    st.html(f"""
    <div style="
      background:linear-gradient(135deg,#c8102e 0%,#9b0022 45%,#6d0019 100%);
      border-radius:20px;padding:32px 36px 26px;margin-bottom:28px;
      position:relative;overflow:hidden;">
      <div style="position:absolute;top:-40px;right:-40px;width:200px;height:200px;
                  border-radius:50%;background:rgba(255,255,255,0.04);pointer-events:none;"></div>
      <div style="position:absolute;bottom:-30px;right:100px;width:100px;height:100px;
                  border-radius:50%;background:rgba(255,255,255,0.05);pointer-events:none;"></div>

      <div style="position:relative;z-index:1;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;
                    gap:24px;flex-wrap:wrap;">

          <div style="flex:1;min-width:260px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
              <span style="font-size:2.4rem;line-height:1;flex-shrink:0;">🎓</span>
              <div>
                <h1 style="margin:0;font-size:1.65rem;font-weight:900;color:white;
                           letter-spacing:-0.03em;line-height:1.15;">
                  RTU Study Programme Recommender
                </h1>
                <p style="margin:7px 0 0;font-size:0.875rem;color:rgba(255,255,255,0.78);
                          font-weight:400;line-height:1.5;">
                  Find the bachelor programme that fits your interests,
                  strengths and future goals.
                </p>
              </div>
            </div>
            <div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px;">
              {feature_pills}
            </div>
          </div>

          <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center;flex-shrink:0;">
            {stat_cards}
          </div>
        </div>

        <div style="display:flex;gap:8px;margin-top:22px;flex-wrap:wrap;">
          {steps_html}
        </div>
      </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# RESULT CARD  (major redesign — description + matched tags always visible)
# ─────────────────────────────────────────────────────────────────────────────

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
    medal  = RANK_MEDALS.get(rank, f"#{rank}")
    accent = RANK_ACCENTS.get(rank, "#64748b")
    prog_id = programme.get("id", str(rank))
    is_saved = prog_id in st.session_state.get("saved_programmes", set())

    m      = programme.get("matching", {}) or {}
    career = programme.get("career", {})   or {}

    # ── Score colour ──────────────────────────────────────────────────────
    if score >= 75:
        score_color = "#059669"
    elif score >= 55:
        score_color = "#d97706"
    else:
        score_color = "#dc2626"

    # ── Short description (always visible) ────────────────────────────────
    desc_raw = (programme.get("description") or "").strip()
    desc     = (desc_raw[:220] + "…") if len(desc_raw) > 220 else desc_raw

    # ── Matched tags (always visible) ─────────────────────────────────────
    matched_interests = summary.get("matched_interests", [])
    matched_strengths = summary.get("matched_strengths", [])
    matched_html = (
        " ".join(_badge(f"💡 {t}", "#ecfdf5", "#059669") for t in matched_interests[:4])
        + " "
        + " ".join(_badge(f"💪 {t}", "#eff6ff", "#1d4ed8") for t in matched_strengths[:3])
    ).strip()

    # ── Info pills ────────────────────────────────────────────────────────
    fee    = programme.get("annual_fee_eur")
    fee_str   = f"€{int(fee):,}".replace(",", " ") if fee else "—"
    budget    = programme.get("budget_places", 0)
    budget_str = f"{budget} b.v." if budget > 0 else "Nav budžeta"
    diff_label = DIFFICULTY_LEVELS.get(m.get("difficulty_level", "medium"), "Vidēja")

    # ── Language + exam badges ────────────────────────────────────────────
    lang_badges = " ".join(
        _badge(
            LANG_LABELS.get(l, l).replace("🇱🇻 ", "").replace("🇬🇧 ", "").replace("🇷🇺 ", ""),
            "#dbeafe", "#1d4ed8",
        )
        for l in programme.get("languages", ["lv"])
    )
    exam_badge = (
        _badge("⚠️ Iestājpārb.", "#fee2e2", "#dc2626")
        if programme.get("entry_exam")
        else _badge("✅ Bez pārb.", "#dcfce7", "#16a34a")
    )

    # ── Programme type badge ──────────────────────────────────────────────
    pt = programme.get("program_type", "")
    if "akadēm" in pt.lower():
        type_badge = _badge("🎓 Akadēmiskais", "#ede9fe", "#7c3aed")
    elif "profesion" in pt.lower():
        type_badge = _badge("🔧 Profesionālais", "#fef3c7", "#b45309")
    else:
        type_badge = _badge(pt[:25], "#f1f5f9", "#475569") if pt else ""

    # ── Feature badges ────────────────────────────────────────────────────
    feature_parts = []
    if m.get("math_intensive"):
        feature_parts.append(_badge("📐 Intensīva matemātika", "#fef3c7", "#92400e"))
    if m.get("research_oriented"):
        feature_parts.append(_badge("🔬 Pētnieciskā", "#f0fdf4", "#166534"))
    if m.get("international_potential"):
        feature_parts.append(_badge("🌍 Starptautiskā", "#eff6ff", "#1d4ed8"))
    if m.get("creative_component"):
        feature_parts.append(_badge("🎨 Radošā", "#fdf4ff", "#7e22ce"))
    feature_badges = " ".join(feature_parts)

    # ── Optional HTML blocks ──────────────────────────────────────────────
    name_en_html = (
        f'<div style="font-size:0.78rem;color:#94a3b8;font-style:italic;margin-top:3px;">'
        f'{programme.get("name_en")}</div>'
    ) if programme.get("name_en") else ""

    desc_html = (
        f'<p style="font-size:0.85rem;color:#475569;line-height:1.65;'
        f'margin:0 0 0 0;padding:14px 0;border-top:1px solid #f1f5f9;'
        f'border-bottom:1px solid #f1f5f9;">{desc}</p>'
    ) if desc else ""

    matched_section_html = (
        f'<div style="margin:14px 0 4px;">'
        f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.08em;color:#94a3b8;margin-bottom:7px;">✅ Matched strengths & interests</div>'
        f'<div style="display:flex;gap:4px;flex-wrap:wrap;">{matched_html}</div>'
        f'</div>'
    ) if matched_html else ""

    feature_html = (
        f'<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px;">{feature_badges}</div>'
    ) if feature_badges else ""

    # ── Card HTML ─────────────────────────────────────────────────────────
    st.html(f"""
    <div style="
      background:white;
      border:1.5px solid #e8ecf0;
      border-left:5px solid {accent};
      border-radius:16px;
      padding:24px 24px 20px;
      box-shadow:0 2px 16px rgba(0,0,0,0.055);
    ">
      <!-- ── Header row: medal + name + score ── -->
      <div style="display:flex;align-items:flex-start;justify-content:space-between;
                  gap:16px;margin-bottom:14px;">

        <div style="display:flex;align-items:flex-start;gap:12px;flex:1;min-width:0;">
          <span style="font-size:2.2rem;line-height:1;flex-shrink:0;">{medal}</span>
          <div style="min-width:0;flex:1;">
            <div style="font-size:1.15rem;font-weight:800;color:#0f172a;
                        letter-spacing:-0.02em;line-height:1.25;">
              {programme.get('name', '—')}
            </div>
            {name_en_html}
            <div style="font-size:0.78rem;color:#64748b;margin-top:6px;
                        display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span>🏛️ {programme.get('faculty', '—')}</span>
              <span style="color:#e2e8f0;">·</span>
              <span>📍 {', '.join(programme.get('locations', ['Rīga']))}</span>
              <span style="color:#e2e8f0;">·</span>
              <span>🕐 {programme.get('duration_years', 4)} gadi</span>
            </div>
          </div>
        </div>

        <!-- Score -->
        <div style="text-align:right;flex-shrink:0;">
          <div style="font-size:2.8rem;font-weight:900;color:{score_color};
                      letter-spacing:-0.04em;line-height:1;">
            {score:.0f}<span style="font-size:1.3rem;">%</span>
          </div>
          <div style="font-size:0.63rem;color:#94a3b8;text-transform:uppercase;
                      letter-spacing:0.08em;margin-top:1px;">match</div>
        </div>
      </div>

      <!-- ── Progress bar ── -->
      <div style="height:8px;background:#f1f5f9;border-radius:6px;
                  overflow:hidden;margin-bottom:18px;">
        <div style="width:{score:.1f}%;height:100%;
                    background:linear-gradient(90deg,{score_color}99,{score_color});
                    border-radius:6px;"></div>
      </div>

      {desc_html}
      {matched_section_html}

      <!-- ── Info pills ── -->
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;
                  margin-top:14px;margin-bottom:8px;">
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:4px 12px;font-size:0.78rem;color:#374151;font-weight:500;">
          💰 {fee_str}/g
        </div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:4px 12px;font-size:0.78rem;color:#374151;font-weight:500;">
          🎓 {budget_str}
        </div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:4px 12px;font-size:0.78rem;color:#374151;font-weight:500;">
          📊 {diff_label}
        </div>
        {lang_badges} {exam_badge} {type_badge}
      </div>

      {feature_html}
    </div>
    """)

    # ── Save button ───────────────────────────────────────────────────────
    col_sp, col_save = st.columns([4, 1])
    with col_save:
        save_label = "❤️ Saglabāts" if is_saved else "🤍 Saglabāt"
        if st.button(save_label, key=f"save_{prog_id}_{rank}", use_container_width=True):
            if on_save:
                on_save(prog_id, programme)

    # ── Expanders ─────────────────────────────────────────────────────────
    ai_label = (
        "🤖 AI Explanation — Gemini 2.5 Flash"
        if is_ai else "📝 Automatic Explanation"
    )
    with st.expander(ai_label, expanded=(rank == 1)):
        if is_ai:
            st.caption("✨ Generated with Gemini 2.5 Flash · Based only on programme data")
        st.markdown(ai_explanation)

    with st.expander("📊 Why this score? — Scoring breakdown"):
        _render_breakdown_details(summary, breakdown)

    with st.expander("📋 Full programme details"):
        _render_programme_details(programme)

    st.write("")


# ─────────────────────────────────────────────────────────────────────────────
# SCORE BREAKDOWN DETAILS  (all HTML/Markdown bugs fixed)
# ─────────────────────────────────────────────────────────────────────────────

def _render_breakdown_details(summary: dict, breakdown: dict):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📊 Base score", f"{breakdown.get('base_pct', 0):.0f}%")
    with c2:
        penalty = breakdown.get("penalty_pct", 0)
        st.metric("⚠️ Penalties", f"−{penalty:.0f}%" if penalty else "0%")
    with c3:
        st.metric("🏆 Final", f"{breakdown.get('final_pct', 0):.0f}%")

    col_l, col_r = st.columns(2)

    with col_l:
        for section, items, icon in [
            ("Matched interests",  summary.get("matched_interests",  []), "✅"),
            ("Matched strengths",  summary.get("matched_strengths",  []), "💪"),
            ("Personality match",  summary.get("matched_personality",[]), "🧠"),
            ("Sector match",       summary.get("matched_sectors",    []), "🏭"),
        ]:
            if items:
                st.markdown(
                    f"**{icon} {section}**  \n" +
                    "  ·  ".join(f"`{i}`" for i in items)
                )

        # Related-domain / related-strength affinity partial credit
        aff_i = summary.get("affinity_interests", [])
        aff_s = summary.get("affinity_strengths", [])
        if aff_i or aff_s:
            combined = [f"~{x}" for x in (aff_i + aff_s)[:6]]
            st.markdown(
                "**🔗 Related field bonus**  \n" +
                "  ·  ".join(f"`{x}`" for x in combined)
            )

        # Career goal + deep-match bonus indicators
        if summary.get("career_bonus", 0) > 0:
            st.caption(f"✍️ Career goal match: +{summary['career_bonus']:.1f} pts")
        if summary.get("deep_bonus", 0) > 0:
            st.caption(f"🎯 Strong multi-match bonus: +{summary['deep_bonus']} pts")

    with col_r:
        missed = summary.get("missed_interests", [])
        if missed:
            st.markdown(
                "**⬜ Unmatched interests**  \n" +
                "  ·  ".join(f"`{i}`" for i in missed[:5])
            )

        if summary.get("penalties"):
            st.markdown("**⚠️ Score penalties**")
            for p in summary["penalties"]:
                st.warning(p)
        elif not missed:
            st.success("✨ No penalties — great match!")

    st.markdown("---")
    st.markdown("**📊 Factor breakdown:**")
    for label, key in [
        ("💡 Interests",  "interests"),
        ("💪 Strengths",  "strengths"),
        ("🧠 Personality","personality"),
        ("🏭 Sectors",    "sectors"),
        ("🌐 Language",   "language"),
    ]:
        pts     = breakdown.get(key, {}).get("points", 0)
        max_pts = breakdown.get(key, {}).get("max", 0)
        if max_pts and max_pts > 0:
            pct = pts / max_pts
            b1, b2, b3 = st.columns([3, 7, 1])
            b1.caption(label)
            b2.progress(pct)
            b3.caption(f"{pts}/{max_pts}")


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMME FULL DETAILS  (all HTML/Markdown bugs fixed)
# ─────────────────────────────────────────────────────────────────────────────

def _render_programme_details(programme: dict):
    career = programme.get("career", {}) or {}
    degree = programme.get("degree", {}) or {}

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**📌 Basic information**")
        lines = []
        for label, val in [
            ("Name (LV)",  programme.get("name")),
            ("Name (EN)",  programme.get("name_en")),
            ("Faculty",    programme.get("faculty")),
            ("Type",       programme.get("program_type")),
            ("Direction",  programme.get("study_direction")),
            ("Field",      programme.get("study_field")),
        ]:
            if val:
                lines.append(f"- **{label}:** {val}")
        if lines:
            st.markdown("\n".join(lines))

        st.markdown("**🎓 Degree awarded**")
        if degree.get("title"):
            st.markdown(f"*{degree['title']}*")
        if degree.get("title_en"):
            st.caption(degree["title_en"])
        if degree.get("professional_qualification"):
            st.caption(f"Qualification: {degree['professional_qualification']}")

    with c2:
        st.markdown("**📋 Logistics & Finances**")
        fee    = programme.get("annual_fee_eur")
        budget = programme.get("budget_places", 0)
        exam   = programme.get("entry_exam", False)
        lines2 = []
        for label, val in [
            ("Duration",       f"{programme.get('duration_years', 4)} years"),
            ("Credits",        str(programme.get("credits", 240))),
            ("Format",         programme.get("format", "Full-time")),
            ("Languages",      ", ".join(LANG_LABELS.get(l, l) for l in programme.get("languages", []))),
            ("Location",       ", ".join(programme.get("locations", []))),
            ("Annual fee",     f"€{int(fee)}" if fee else "—"),
            ("Budget places",  str(budget) if budget > 0 else "None"),
            ("Entry exam",     "⚠️ Yes" if exam else "✅ No"),
        ]:
            lines2.append(f"- **{label}:** {val}")
        st.markdown("\n".join(lines2))

        if exam and programme.get("entry_exam_details"):
            details = programme["entry_exam_details"]
            if isinstance(details, dict):
                subjects = details.get("subjects", [])
                dates    = details.get("exam_dates_2026", [])
                if subjects:
                    st.caption(f"📝 Exam subjects: {', '.join(subjects)}")
                if dates:
                    st.caption(f"📅 2026 exam dates: {', '.join(dates)}")
            else:
                st.caption(str(details))

    if programme.get("description"):
        st.markdown("**📖 Description**")
        st.info(
            programme["description"][:600] +
            ("…" if len(programme["description"]) > 600 else "")
        )

    if career.get("job_titles"):
        st.markdown("**💼 Career paths**")
        st.markdown("  ·  ".join(f"→ {j}" for j in career["job_titles"][:7]))
        if career.get("description"):
            st.caption(career["description"][:250])

    if programme.get("url"):
        st.link_button("🔗 Open on RTU website ↗", programme["url"])


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON TABLE
# ─────────────────────────────────────────────────────────────────────────────

def render_comparison_table(saved_progs: list[dict], scores: dict[str, float]):
    if not saved_progs:
        st.info("No saved programmes.")
        return

    n    = len(saved_progs)
    cols = st.columns(n, gap="medium")

    for col, prog in zip(cols, saved_progs):
        score = scores.get(prog.get("id", ""), 0)
        if score >= 75:
            s_color, s_bg = "#059669", "#dcfce7"
        elif score >= 55:
            s_color, s_bg = "#d97706", "#fef3c7"
        else:
            s_color, s_bg = "#dc2626", "#fee2e2"

        m      = prog.get("matching", {}) or {}
        fee    = prog.get("annual_fee_eur")
        budget = prog.get("budget_places", 0)

        with col:
            st.html(f"""
            <div style="border:1.5px solid {s_color}30;border-top:4px solid {s_color};
                        border-radius:14px;padding:16px;background:white;
                        box-shadow:0 2px 10px rgba(0,0,0,0.05);">
              <div style="font-size:0.9rem;font-weight:700;color:#0f172a;
                          line-height:1.3;margin-bottom:10px;">
                {prog.get('name', '—')}
              </div>
              <div style="font-size:2.2rem;font-weight:900;color:{s_color};
                          letter-spacing:-0.03em;line-height:1;">{score:.0f}%</div>
              <div style="height:6px;background:#f1f5f9;border-radius:4px;
                          overflow:hidden;margin:8px 0 14px;">
                <div style="width:{score:.0f}%;height:100%;background:{s_color};
                            border-radius:4px;"></div>
              </div>
              <hr style="border:none;border-top:1px solid #f1f5f9;margin:8px 0 12px;">
            </div>
            """)

            def _row(icon, label, val):
                st.html(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:4px 0;border-bottom:1px solid #f8fafc;">'
                    f'<span style="font-size:0.77rem;color:#64748b;">{icon} {label}</span>'
                    f'<span style="font-size:0.77rem;font-weight:600;color:#0f172a;">{val}</span>'
                    f'</div>',
                )

            _row("🏛️", "Faculty",   (prog.get("faculty", "—") or "—")[:28])
            _row("🕐", "Duration",  f"{prog.get('duration_years', 4)} yr")
            _row("🌐", "Language",  "/".join(prog.get("languages", ["lv"])).upper())
            _row("💰", "Fee/yr",    f"€{int(fee)}" if fee else "—")
            _row("🎓", "Budget",    f"{budget} pl." if budget > 0 else "None")
            _row("📝", "Exam",      "⚠️ Yes" if prog.get("entry_exam") else "✅ No")
            _row("📐", "Math",      "✓ Intensive" if m.get("math_intensive") else "Standard")
            _row("🔬", "Research",  "✓ Yes" if m.get("research_oriented") else "—")
            _row("🌍", "Intl.",     "✓ Yes" if m.get("international_potential") else "—")


# ─────────────────────────────────────────────────────────────────────────────
# ALL PROGRAMMES TABLE
# ─────────────────────────────────────────────────────────────────────────────

def render_programme_table(programmes: list[dict], scores: dict[str, float] | None = None):
    import pandas as pd

    rows = []
    for p in programmes:
        m = p.get("matching", {}) or {}
        score_val = round(scores.get(p.get("id", ""), 0)) if scores else None
        rows.append({
            "Programme":  p.get("name", "—"),
            "English":    p.get("name_en") or "—",
            "Faculty":    (p.get("faculty") or "—")[:40],
            "Type":       "Acad." if "akadēm" in (p.get("program_type") or "").lower() else "Prof.",
            "Dur.":       f"{p.get('duration_years', 4)}y",
            "Lang.":      "/".join(p.get("languages", ["lv"])).upper(),
            "Location":   ", ".join(p.get("locations", ["Rīga"])),
            "Fee €/yr":   int(p["annual_fee_eur"]) if p.get("annual_fee_eur") else 0,
            "Budget pl.": p.get("budget_places", 0),
            "Exam":       "Yes" if p.get("entry_exam") else "No",
            "Math":       "✓" if m.get("math_intensive") else "",
            "Research":   "✓" if m.get("research_oriented") else "",
            **({"Match %": score_val} if scores else {}),
        })

    df = pd.DataFrame(rows)
    if scores and "Match %" in df.columns:
        df = df.sort_values("Match %", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(520, 55 + len(df) * 38),
        column_config={
            "Programme": st.column_config.TextColumn("Programme", width="large"),
            "Match %":   st.column_config.ProgressColumn(
                "Match %", min_value=0, max_value=100, format="%d%%",
            ) if scores else None,
            "Fee €/yr":  st.column_config.NumberColumn("Fee €/yr", format="€%d"),
            "Budget pl.":st.column_config.NumberColumn("Budget"),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────

def render_empty_results():
    st.html("""
    <div style="text-align:center;padding:52px 24px 44px;">
      <div style="font-size:3.5rem;line-height:1;margin-bottom:16px;">🎓</div>
      <h3 style="color:#0f172a;font-weight:800;font-size:1.2rem;
                 letter-spacing:-0.02em;margin:0 0 10px 0;">
        Fill in your profile to get personalised recommendations
      </h3>
      <p style="color:#64748b;font-size:0.875rem;max-width:480px;
                margin:0 auto 32px;line-height:1.65;">
        Our AI compares your profile against all RTU bachelor programmes
        and explains — in plain language — why each one fits your goals.
      </p>
      <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;
                  max-width:580px;margin:0 auto;">
    """ + "".join(
        f'<div style="background:white;border:1.5px solid #e2e8f0;border-radius:14px;'
        f'padding:18px 20px;flex:1;min-width:120px;max-width:155px;text-align:center;'
        f'box-shadow:0 1px 4px rgba(0,0,0,0.04);">'
        f'<div style="font-size:1.7rem;margin-bottom:8px;">{icon}</div>'
        f'<div style="font-size:0.82rem;font-weight:700;color:#0f172a;margin-bottom:4px;">{title}</div>'
        f'<div style="font-size:0.72rem;color:#94a3b8;line-height:1.45;">{desc}</div>'
        f'</div>'
        for icon, title, desc in [
            ("💡", "Interests", "What topics excite you"),
            ("💪", "Strengths", "Your best subjects"),
            ("🧠", "Personality", "How you work best"),
            ("🚀", "Goals", "Where you want to go"),
        ]
    ) + """
      </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# LOADING SPINNER CONTEXT
# ─────────────────────────────────────────────────────────────────────────────

def loading_spinner_context(message: str = "Calculating compatibility…"):
    return st.spinner(message)
