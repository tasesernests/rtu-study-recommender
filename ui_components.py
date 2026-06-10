"""
RTU Study Programme AI Recommender
ui_components.py — Reusable Streamlit UI building blocks.
"""

import streamlit as st

from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS, get_label,
)

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

RANK_MEDALS  = {1: "1", 2: "2", 3: "3"}
RANK_ACCENTS = {1: "#9f1d2f", 2: "#374151", 3: "#6b7280"}


# ─────────────────────────────────────────────────────────────────────────────
# BADGE HELPER
# ─────────────────────────────────────────────────────────────────────────────

def _badge(text: str, bg: str = "#e0e7ff", color: str = "#3730a3") -> str:
    return (
        f'<span style="background:{bg};color:{color};padding:3px 10px;'
        f'border-radius:8px;font-size:0.74rem;font-weight:600;'
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
        f'<span style="background:#f3f4f6;color:#374151;'
        f'border:1px solid #e5e7eb;border-radius:8px;'
        f'padding:5px 12px;font-size:0.78rem;font-weight:600;display:inline-block;'
        f'letter-spacing:0;">{label}</span>'
        for label in ["AI assisted", "Explainable", "RTU dataset"]
    )

    steps_html = "".join(
        f'<div style="background:#ffffff;border:1px solid #e5e7eb;'
        f'border-radius:8px;padding:5px 12px;font-size:0.75rem;color:#4b5563;'
        f'font-weight:500;display:inline-flex;align-items:center;gap:6px;">'
        f'<span style="background:#f3f4f6;border-radius:6px;width:20px;height:20px;'
        f'display:inline-flex;align-items:center;justify-content:center;'
        f'font-size:0.68rem;font-weight:800;color:#374151;flex-shrink:0;">{n}</span>'
        f'{step}</div>'
        for n, step in [
            (1, "Fill profile"), (2, "Get recommendations"),
            (3, "Compare programmes"), (4, "Apply to RTU"),
        ]
    )

    stat_cards = "".join(
        f'<div style="background:#ffffff;border:1px solid #e5e7eb;'
        f'border-radius:8px;padding:10px 16px;text-align:center;min-width:76px;">'
        f'<div style="font-size:1.35rem;font-weight:800;color:{nc};letter-spacing:0;">{num}</div>'
        f'<div style="font-size:0.68rem;color:#6b7280;text-transform:uppercase;'
        f'letter-spacing:0;margin-top:2px;">{lbl}</div>'
        f'</div>'
        for num, nc, lbl in [
            (n_programmes, "#111827", "Programmes"),
            (files_ok, "#111827", "Datasets"),
            ("AI", "#9f1d2f", "Gemini"),
        ]
    )

    st.html(f"""
    <div style="
      background:#ffffff;border:1px solid #e5e7eb;border-left:4px solid #9f1d2f;
      border-radius:8px;padding:24px 28px 22px;margin-bottom:24px;">
        <div style="display:flex;align-items:flex-start;justify-content:space-between;
                    gap:24px;flex-wrap:wrap;">

          <div style="flex:1;min-width:260px;">
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
              <span style="width:40px;height:40px;border-radius:8px;background:#111827;
                           color:#ffffff;display:inline-flex;align-items:center;justify-content:center;
                           font-size:0.8rem;font-weight:800;line-height:1;flex-shrink:0;">RTU</span>
              <div>
                <h1 style="margin:0;font-size:1.55rem;font-weight:800;color:#111827;
                           letter-spacing:0;line-height:1.2;">
                  RTU Study Programme Recommender
                </h1>
                <p style="margin:7px 0 0;font-size:0.875rem;color:#6b7280;
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
    """)


# ─────────────────────────────────────────────────────────────────────────────
# RESULT CARD  (major redesign — description + matched tags always visible)
# ─────────────────────────────────────────────────────────────────────────────

def render_result_card(
    rank: int,
    programme: dict,
    score: float,
    breakdown: dict,
    ai_explanation: str | None,
    is_ai: bool,
    summary: dict,
    on_save=None,
) -> bool:
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
        " ".join(_badge(t, "#f0fdf4", "#047857") for t in matched_interests[:4])
        + " "
        + " ".join(_badge(t, "#eff6ff", "#1d4ed8") for t in matched_strengths[:3])
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
        _badge("Entry exam", "#fee2e2", "#b91c1c")
        if programme.get("entry_exam")
        else _badge("No entry exam", "#dcfce7", "#15803d")
    )

    # ── Programme type badge ──────────────────────────────────────────────
    pt = programme.get("program_type", "")
    if "akadēm" in pt.lower():
        type_badge = _badge("Academic", "#f3f4f6", "#374151")
    elif "profesion" in pt.lower():
        type_badge = _badge("Professional", "#fef3c7", "#92400e")
    else:
        type_badge = _badge(pt[:25], "#f1f5f9", "#475569") if pt else ""

    # ── Feature badges ────────────────────────────────────────────────────
    feature_parts = []
    if m.get("math_intensive"):
        feature_parts.append(_badge("Math intensive", "#fef3c7", "#92400e"))
    if m.get("research_oriented"):
        feature_parts.append(_badge("Research oriented", "#f0fdf4", "#166534"))
    if m.get("international_potential"):
        feature_parts.append(_badge("International", "#eff6ff", "#1d4ed8"))
    if m.get("creative_component"):
        feature_parts.append(_badge("Creative component", "#f5f3ff", "#6d28d9"))
    feature_badges = " ".join(feature_parts)

    # ── Optional HTML blocks ──────────────────────────────────────────────
    name_en_html = (
        f'<div style="font-size:0.78rem;color:#6b7280;font-style:italic;margin-top:3px;">'
        f'{programme.get("name_en")}</div>'
    ) if programme.get("name_en") else ""

    desc_html = (
        f'<p style="font-size:0.85rem;color:#4b5563;line-height:1.65;'
        f'margin:0 0 0 0;padding:14px 0;border-top:1px solid #e5e7eb;'
        f'border-bottom:1px solid #e5e7eb;">{desc}</p>'
    ) if desc else ""

    matched_section_html = (
        f'<div style="margin:14px 0 4px;">'
        f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0;color:#6b7280;margin-bottom:7px;">Matched strengths & interests</div>'
        f'<div style="display:flex;gap:4px;flex-wrap:wrap;">{matched_html}</div>'
        f'</div>'
    ) if matched_html else ""

    feature_html = (
        f'<div style="display:flex;gap:4px;flex-wrap:wrap;margin-top:8px;">{feature_badges}</div>'
    ) if feature_badges else ""

    # ── Card HTML ─────────────────────────────────────────────────────────
    st.html(f"""
    <div style="
      background:#ffffff;
      border:1px solid #e5e7eb;
      border-left:4px solid {accent};
      border-radius:8px;
      padding:22px 22px 18px;
      box-shadow:none;
    ">
      <!-- ── Header row: medal + name + score ── -->
      <div style="display:flex;align-items:flex-start;justify-content:space-between;
                  gap:16px;margin-bottom:14px;">

        <div style="display:flex;align-items:flex-start;gap:12px;flex:1;min-width:0;">
          <span style="width:34px;height:34px;border-radius:8px;background:#f3f4f6;
                       color:#374151;border:1px solid #e5e7eb;display:inline-flex;
                       align-items:center;justify-content:center;font-size:0.95rem;
                       font-weight:800;line-height:1;flex-shrink:0;">{medal}</span>
          <div style="min-width:0;flex:1;">
            <div style="font-size:1.12rem;font-weight:800;color:#111827;
                        letter-spacing:0;line-height:1.3;">
              {programme.get('name', '—')}
            </div>
            {name_en_html}
            <div style="font-size:0.78rem;color:#6b7280;margin-top:6px;
                        display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span>{programme.get('faculty', '—')}</span>
              <span style="color:#e2e8f0;">·</span>
              <span>{', '.join(programme.get('locations', ['Rīga']))}</span>
              <span style="color:#e2e8f0;">·</span>
              <span>{programme.get('duration_years', 4)} gadi</span>
            </div>
          </div>
        </div>

        <!-- Score -->
        <div style="text-align:right;flex-shrink:0;">
          <div style="font-size:2.35rem;font-weight:800;color:{score_color};
                      letter-spacing:0;line-height:1;">
            {score:.0f}<span style="font-size:1.3rem;">%</span>
          </div>
          <div style="font-size:0.68rem;color:#6b7280;text-transform:uppercase;
                      letter-spacing:0;margin-top:1px;">match</div>
        </div>
      </div>

      <!-- ── Progress bar ── -->
      <div style="height:8px;background:#f3f4f6;border-radius:6px;
                  overflow:hidden;margin-bottom:18px;">
        <div style="width:{score:.1f}%;height:100%;
                    background:{score_color};
                    border-radius:6px;"></div>
      </div>

      {desc_html}
      {matched_section_html}

      <!-- ── Info pills ── -->
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;
                  margin-top:14px;margin-bottom:8px;">
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:4px 12px;font-size:0.78rem;color:#374151;font-weight:500;">
          Fee {fee_str}/g
        </div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:4px 12px;font-size:0.78rem;color:#374151;font-weight:500;">
          Budget {budget_str}
        </div>
        <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;
                    padding:4px 12px;font-size:0.78rem;color:#374151;font-weight:500;">
          Difficulty {diff_label}
        </div>
        {lang_badges} {exam_badge} {type_badge}
      </div>

      {feature_html}
    </div>
    """)

    # ── Save button ───────────────────────────────────────────────────────
    col_sp, col_save = st.columns([4, 1])
    with col_save:
        save_label = "Saved" if is_saved else "Save"
        if st.button(save_label, key=f"save_{prog_id}_{rank}", use_container_width=True):
            if on_save:
                on_save(prog_id, programme)

    # ── Expanders ─────────────────────────────────────────────────────────
    explanation_requested = False
    ai_label = (
        "AI Explanation"
        if is_ai else "Automatic Explanation" if ai_explanation else "Programme Explanation"
    )
    with st.expander(ai_label, expanded=bool(ai_explanation and rank == 1)):
        if ai_explanation:
            if is_ai:
                st.caption("Generated with Gemini 2.5 Flash · Based only on programme data")
            st.markdown(ai_explanation)
        else:
            st.caption(
                "Generate a detailed explanation only when you need it. "
                "This keeps the recommendations screen fast."
            )
            explanation_requested = st.button(
                "Generate explanation",
                key=f"explain_{prog_id}_{rank}",
                use_container_width=True,
            )

    with st.expander("Why this score?"):
        _render_breakdown_details(summary, breakdown)

    with st.expander("Full programme details"):
        _render_programme_details(programme)

    st.write("")
    return explanation_requested


# ─────────────────────────────────────────────────────────────────────────────
# SCORE BREAKDOWN DETAILS  (all HTML/Markdown bugs fixed)
# ─────────────────────────────────────────────────────────────────────────────

def _render_breakdown_details(summary: dict, breakdown: dict):
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Base score", f"{breakdown.get('base_pct', 0):.0f}%")
    with c2:
        penalty = breakdown.get("penalty_pct", 0)
        st.metric("Penalties", f"−{penalty:.0f}%" if penalty else "0%")
    with c3:
        st.metric("Final", f"{breakdown.get('final_pct', 0):.0f}%")

    col_l, col_r = st.columns(2)

    with col_l:
        for section, items in [
            ("Matched interests",  summary.get("matched_interests",  [])),
            ("Matched strengths",  summary.get("matched_strengths",  [])),
            ("Personality match",  summary.get("matched_personality",[])),
            ("Sector match",       summary.get("matched_sectors",    [])),
        ]:
            if items:
                st.markdown(
                    f"**{section}**  \n" +
                    "  ·  ".join(f"`{i}`" for i in items)
                )

        # Related-domain / related-strength affinity partial credit
        aff_i = summary.get("affinity_interests", [])
        aff_s = summary.get("affinity_strengths", [])
        if aff_i or aff_s:
            combined = [f"~{x}" for x in (aff_i + aff_s)[:6]]
            st.markdown(
                "**Related field bonus**  \n" +
                "  ·  ".join(f"`{x}`" for x in combined)
            )

        # Career goal + deep-match bonus indicators
        if summary.get("career_bonus", 0) > 0:
            st.caption(f"Career goal match: +{summary['career_bonus']:.1f} pts")
        if summary.get("deep_bonus", 0) > 0:
            st.caption(f"Strong multi-match bonus: +{summary['deep_bonus']} pts")

    with col_r:
        missed = summary.get("missed_interests", [])
        if missed:
            st.markdown(
                "**⬜ Unmatched interests**  \n" +
                "  ·  ".join(f"`{i}`" for i in missed[:5])
            )

        if summary.get("penalties"):
            st.markdown("**Score penalties**")
            for p in summary["penalties"]:
                st.warning(p)
        elif not missed:
            st.success("No penalties - great match.")

    st.markdown("---")
    st.markdown("**Factor breakdown:**")
    for label, key in [
        ("Interests",  "interests"),
        ("Strengths",  "strengths"),
        ("Personality","personality"),
        ("Sectors",    "sectors"),
        ("Language",   "language"),
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

        st.markdown("**Degree awarded**")
        if degree.get("title"):
            st.markdown(f"*{degree['title']}*")
        if degree.get("title_en"):
            st.caption(degree["title_en"])
        if degree.get("professional_qualification"):
            st.caption(f"Qualification: {degree['professional_qualification']}")

    with c2:
        st.markdown("**Logistics & Finances**")
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
            ("Entry exam",     "Yes" if exam else "No"),
        ]:
            lines2.append(f"- **{label}:** {val}")
        st.markdown("\n".join(lines2))

        if exam and programme.get("entry_exam_details"):
            details = programme["entry_exam_details"]
            if isinstance(details, dict):
                subjects = details.get("subjects", [])
                dates    = details.get("exam_dates_2026", [])
                if subjects:
                    st.caption(f"Exam subjects: {', '.join(subjects)}")
                if dates:
                    st.caption(f"2026 exam dates: {', '.join(dates)}")
            else:
                st.caption(str(details))

    if programme.get("description"):
        st.markdown("**Description**")
        st.info(
            programme["description"][:600] +
            ("…" if len(programme["description"]) > 600 else "")
        )

    if career.get("job_titles"):
        st.markdown("**Career paths**")
        st.markdown("  ·  ".join(f"→ {j}" for j in career["job_titles"][:7]))
        if career.get("description"):
            st.caption(career["description"][:250])

    if programme.get("url"):
        st.link_button("Open on RTU website", programme["url"])


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
            <div style="border:1px solid #e5e7eb;border-top:4px solid {s_color};
                        border-radius:8px;padding:16px;background:#ffffff;
                        box-shadow:none;">
              <div style="font-size:0.9rem;font-weight:700;color:#111827;
                          line-height:1.3;margin-bottom:10px;">
                {prog.get('name', '—')}
              </div>
              <div style="font-size:2rem;font-weight:800;color:{s_color};
                          letter-spacing:0;line-height:1;">{score:.0f}%</div>
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
                    f'padding:4px 0;border-bottom:1px solid #f3f4f6;">'
                    f'<span style="font-size:0.77rem;color:#6b7280;">{label}</span>'
                    f'<span style="font-size:0.77rem;font-weight:600;color:#111827;">{val}</span>'
                    f'</div>',
                )

            _row("", "Faculty",   (prog.get("faculty", "—") or "—")[:28])
            _row("", "Duration",  f"{prog.get('duration_years', 4)} yr")
            _row("", "Language",  "/".join(prog.get("languages", ["lv"])).upper())
            _row("", "Fee/yr",    f"€{int(fee)}" if fee else "—")
            _row("", "Budget",    f"{budget} pl." if budget > 0 else "None")
            _row("", "Exam",      "Yes" if prog.get("entry_exam") else "No")
            _row("", "Math",      "Intensive" if m.get("math_intensive") else "Standard")
            _row("", "Research",  "Yes" if m.get("research_oriented") else "—")
            _row("", "Intl.",     "Yes" if m.get("international_potential") else "—")


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
    <div style="text-align:center;padding:46px 24px 40px;">
      <h3 style="color:#111827;font-weight:800;font-size:1.2rem;
                 letter-spacing:0;margin:0 0 10px 0;">
        Fill in your profile to get personalised recommendations
      </h3>
      <p style="color:#6b7280;font-size:0.875rem;max-width:480px;
                margin:0 auto 32px;line-height:1.65;">
        Our AI compares your profile against all RTU bachelor programmes
        and can explain in plain language why each one fits your goals.
      </p>
      <div style="display:flex;gap:12px;justify-content:center;flex-wrap:wrap;
                  max-width:580px;margin:0 auto;">
    """ + "".join(
        f'<div style="background:#ffffff;border:1px solid #e5e7eb;border-radius:8px;'
        f'padding:18px 20px;flex:1;min-width:120px;max-width:155px;text-align:center;'
        f'box-shadow:none;">'
        f'<div style="font-size:0.82rem;font-weight:700;color:#111827;margin-bottom:4px;">{title}</div>'
        f'<div style="font-size:0.72rem;color:#6b7280;line-height:1.45;">{desc}</div>'
        f'</div>'
        for title, desc in [
            ("Interests", "What topics excite you"),
            ("Strengths", "Your best subjects"),
            ("Personality", "How you work best"),
            ("Goals", "Where you want to go"),
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
