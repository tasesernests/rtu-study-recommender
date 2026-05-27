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

RANK_MEDALS = {1: "🥇", 2: "🥈", 3: "🥉"}
RANK_COLORS = {1: "#f59e0b", 2: "#64748b", 3: "#b45309"}
RANK_GRADIENTS = {
    1: "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)",
    2: "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
    3: "linear-gradient(135deg, #fefce8 0%, #fef9c3 100%)",
}


# ─────────────────────────────────────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────────────────────────────────────

def render_hero(stats: dict, n_programmes: int):
    """Render the app hero section with statistics."""
    files_ok = stats.get("files_loaded", 0)

    # Pre-compute nested HTML to avoid f-string nesting issues
    steps_html = "".join(
        '<div style="background:rgba(255,255,255,0.12);border-radius:8px;'
        'padding:5px 12px;font-size:0.75rem;color:rgba(255,255,255,0.85);'
        'font-weight:500;display:flex;align-items:center;gap:5px;">'
        f'<span style="color:#fbbf24;font-weight:700;">{n}.</span> {step}</div>'
        for n, step in [
            (1, "Aizpildi profilu"), (2, "Saņem AI ieteikumus"),
            (3, "Salīdzini programmas"), (4, "Piesakies RTU"),
        ]
    )

    st.html(f"""
    <div style="
      background: linear-gradient(135deg, #c8102e 0%, #9b0022 45%, #6d0019 100%);
      border-radius: 20px;
      padding: 28px 36px;
      margin-bottom: 24px;
      position: relative;
      overflow: hidden;
    ">
      <!-- Decorative circles -->
      <div style="
        position:absolute; top:-30px; right:-30px;
        width:160px; height:160px; border-radius:50%;
        background:rgba(255,255,255,0.05);
      "></div>
      <div style="
        position:absolute; bottom:-20px; right:80px;
        width:80px; height:80px; border-radius:50%;
        background:rgba(255,255,255,0.06);
      "></div>

      <div style="position:relative; z-index:1;">
        <div style="display:flex; align-items:flex-start; justify-content:space-between;
                    flex-wrap:wrap; gap:16px;">
          <!-- Title area -->
          <div>
            <div style="display:flex; align-items:center; gap:10px; margin-bottom:8px;">
              <span style="font-size:2.2rem;">🎓</span>
              <div>
                <h1 style="margin:0; font-size:1.6rem; font-weight:900; color:white;
                           letter-spacing:-0.03em; line-height:1.1;">
                  RTU Studiju Programmu AI Ieteicējs
                </h1>
                <p style="margin:4px 0 0 0; font-size:0.85rem; color:rgba(255,255,255,0.75);
                          font-weight:400;">
                  Atklāj savai personībai piemērotākās RTU bakalaura studiju programmas
                </p>
              </div>
            </div>
          </div>

          <!-- Stats pills -->
          <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
            <div style="
              background:rgba(255,255,255,0.15); backdrop-filter:blur(8px);
              border:1px solid rgba(255,255,255,0.2);
              border-radius:12px; padding:8px 16px; text-align:center;
            ">
              <div style="font-size:1.4rem; font-weight:800; color:white;
                          letter-spacing:-0.02em;">{n_programmes}</div>
              <div style="font-size:0.65rem; color:rgba(255,255,255,0.7);
                          text-transform:uppercase; letter-spacing:0.08em; margin-top:1px;">
                Programmas</div>
            </div>
            <div style="
              background:rgba(255,255,255,0.15); backdrop-filter:blur(8px);
              border:1px solid rgba(255,255,255,0.2);
              border-radius:12px; padding:8px 16px; text-align:center;
            ">
              <div style="font-size:1.4rem; font-weight:800; color:white;
                          letter-spacing:-0.02em;">{files_ok}</div>
              <div style="font-size:0.65rem; color:rgba(255,255,255,0.7);
                          text-transform:uppercase; letter-spacing:0.08em; margin-top:1px;">
                Datu kopas</div>
            </div>
            <div style="
              background:rgba(255,255,255,0.15); backdrop-filter:blur(8px);
              border:1px solid rgba(255,255,255,0.2);
              border-radius:12px; padding:8px 16px; text-align:center;
            ">
              <div style="font-size:1.4rem; font-weight:800; color:#fbbf24;
                          letter-spacing:-0.02em;">AI</div>
              <div style="font-size:0.65rem; color:rgba(255,255,255,0.7);
                          text-transform:uppercase; letter-spacing:0.08em; margin-top:1px;">
                Gemini 2.5</div>
            </div>
          </div>
        </div>

        <!-- Step guide -->
        <div style="display:flex; gap:6px; margin-top:18px; flex-wrap:wrap;">
          {steps_html}
        </div>
      </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILITY BAR
# ─────────────────────────────────────────────────────────────────────────────

def render_compatibility_bar(score: float, rank: int = 1):
    """Render a styled compatibility percentage bar."""
    if score >= 75:
        color, label = "#059669", "Augsta"
    elif score >= 55:
        color, label = "#d97706", "Laba"
    elif score >= 35:
        color, label = "#ea580c", "Vidēja"
    else:
        color, label = "#dc2626", "Zema"

    st.html(f"""
    <div style="margin:10px 0 14px 0;">
      <div style="display:flex; align-items:center; gap:10px;">
        <div style="flex:1; height:10px; background:#f1f5f9;
                    border-radius:5px; overflow:hidden;">
          <div style="width:{score:.1f}%; height:100%; background:
                      linear-gradient(90deg, {color}cc, {color});
                      border-radius:5px; transition:width 0.5s ease;"></div>
        </div>
        <div style="min-width:90px; display:flex; align-items:center; gap:6px;">
          <span style="font-size:1.3rem; font-weight:800; color:{color};
                       letter-spacing:-0.03em;">{score:.0f}%</span>
          <span style="font-size:0.7rem; color:{color}; background:{color}15;
                       padding:2px 7px; border-radius:20px; font-weight:600;">
            {label}</span>
        </div>
      </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# BADGE HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _badge(text: str, bg: str = "#e0e7ff", color: str = "#3730a3") -> str:
    return (
        f'<span style="background:{bg};color:{color};padding:3px 10px;'
        f'border-radius:20px;font-size:0.74rem;font-weight:600;'
        f'margin:2px 2px;display:inline-block;white-space:nowrap;">{text}</span>'
    )


def render_tags(items: list[str], mapping: dict, bg: str = "#e0e7ff", color: str = "#3730a3"):
    if not items:
        st.caption("—")
        return
    labels = [get_label(mapping, k) for k in items if k]
    html = " ".join(_badge(lbl, bg, color) for lbl in labels[:8])
    st.html(html)


# ─────────────────────────────────────────────────────────────────────────────
# RESULT CARD
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
    medal = RANK_MEDALS.get(rank, f"#{rank}")
    accent = RANK_COLORS.get(rank, "#64748b")
    prog_id = programme.get("id", str(rank))
    is_saved = prog_id in st.session_state.get("saved_programmes", set())

    m = programme.get("matching", {}) or {}
    career = programme.get("career", {}) or {}

    # ── Score colour ──────────────────────────────────────────────────────
    if score >= 75:
        score_color = "#059669"
    elif score >= 55:
        score_color = "#d97706"
    else:
        score_color = "#dc2626"

    # ── Language badges HTML ───────────────────────────────────────────────
    lang_badges = "".join(
        _badge(LANG_LABELS.get(l, l).replace("🇱🇻 ", "").replace("🇬🇧 ", "").replace("🇷🇺 ", ""),
               "#dbeafe", "#1d4ed8")
        for l in programme.get("languages", ["lv"])
    )

    # ── Exam badge ─────────────────────────────────────────────────────────
    exam_badge = (
        _badge("⚠️ Iestājpārb.", "#fee2e2", "#dc2626")
        if programme.get("entry_exam")
        else _badge("✅ Bez pārb.", "#dcfce7", "#16a34a")
    )

    # ── Type badge ─────────────────────────────────────────────────────────
    pt = programme.get("program_type", "")
    if "akadēm" in pt.lower():
        type_badge = _badge("🎓 Akadēmiskais", "#ede9fe", "#7c3aed")
    elif "profesion" in pt.lower():
        type_badge = _badge("🔧 Profesionālais", "#fef3c7", "#b45309")
    else:
        type_badge = _badge(pt[:25], "#f1f5f9", "#475569") if pt else ""

    # ── Special feature badges ─────────────────────────────────────────────
    feature_badges = ""
    if m.get("math_intensive"):
        feature_badges += _badge("📐 Intensīva matemātika", "#fef3c7", "#92400e")
    if m.get("research_oriented"):
        feature_badges += _badge("🔬 Pētnieciskā", "#f0fdf4", "#166534")
    if m.get("international_potential"):
        feature_badges += _badge("🌍 Starptautiskā", "#eff6ff", "#1d4ed8")
    if m.get("creative_component"):
        feature_badges += _badge("🎨 Radošā", "#fdf4ff", "#7e22ce")

    # ── Card header HTML ───────────────────────────────────────────────────
    fee = programme.get("annual_fee_eur")
    fee_str = f"€{int(fee):,}".replace(",", " ") if fee else "Nav norādīts"
    budget = programme.get("budget_places", 0)
    budget_str = f"{budget} b.v." if budget > 0 else "Nav budžeta"
    difficulty_label = DIFFICULTY_LEVELS.get(m.get("difficulty_level", "medium"), "Vidēja")

    st.html(f"""
    <div style="
      background:{RANK_GRADIENTS.get(rank, '#f8fafc')};
      border:1.5px solid {accent}35;
      border-left:5px solid {accent};
      border-radius:16px;
      padding:20px 24px 16px 20px;
      margin-bottom:0px;
    ">
      <!-- Rank + Name row -->
      <div style="display:flex; align-items:flex-start;
                  justify-content:space-between; gap:12px; flex-wrap:wrap;">
        <div style="display:flex; align-items:center; gap:12px; min-width:0; flex:1;">
          <span style="font-size:2.4rem; line-height:1; flex-shrink:0;">{medal}</span>
          <div style="min-width:0;">
            <div style="font-size:1.15rem; font-weight:800; color:#0f172a;
                        letter-spacing:-0.02em; line-height:1.2;">
              {programme.get('name', '—')}
            </div>
            {f'<div style="font-size:0.78rem; color:#64748b; font-style:italic; margin-top:3px;">{programme.get("name_en")}</div>' if programme.get("name_en") else ""}
            <div style="font-size:0.78rem; color:#94a3b8; margin-top:4px;
                        display:flex; align-items:center; gap:6px; flex-wrap:wrap;">
              <span>🏛️ {programme.get('faculty', '—')}</span>
              <span style="color:#cbd5e1;">·</span>
              <span>📍 {', '.join(programme.get('locations', ['Rīga']))}</span>
              <span style="color:#cbd5e1;">·</span>
              <span>🕐 {programme.get('duration_years', 4)} gadi</span>
            </div>
          </div>
        </div>

        <!-- Score badge -->
        <div style="
          background:{score_color};
          color:white;
          border-radius:14px;
          padding:10px 18px;
          text-align:center;
          flex-shrink:0;
          box-shadow:0 4px 14px {score_color}40;
          min-width:80px;
        ">
          <div style="font-size:1.7rem; font-weight:900; line-height:1;
                      letter-spacing:-0.03em;">{score:.0f}%</div>
          <div style="font-size:0.62rem; opacity:0.85; text-transform:uppercase;
                      letter-spacing:0.08em; margin-top:2px;">atbilstība</div>
        </div>
      </div>

      <!-- Key info pills row -->
      <div style="display:flex; gap:8px; margin-top:14px; flex-wrap:wrap;">
        <div style="background:white; border:1px solid #e2e8f0; border-radius:8px;
                    padding:4px 12px; font-size:0.78rem; color:#374151; font-weight:500;">
          💰 {fee_str}/gadā
        </div>
        <div style="background:white; border:1px solid #e2e8f0; border-radius:8px;
                    padding:4px 12px; font-size:0.78rem; color:#374151; font-weight:500;">
          🎓 {budget_str}
        </div>
        <div style="background:white; border:1px solid #e2e8f0; border-radius:8px;
                    padding:4px 12px; font-size:0.78rem; color:#374151; font-weight:500;">
          📊 {difficulty_label}
        </div>
      </div>

      <!-- Badges row -->
      <div style="margin-top:10px; display:flex; gap:3px; flex-wrap:wrap;">
        {lang_badges} {exam_badge} {type_badge}
      </div>
      {f'<div style="margin-top:6px; display:flex; gap:3px; flex-wrap:wrap;">{feature_badges}</div>' if feature_badges else ""}
    </div>
    """)

    # ── Save button (outside HTML) ─────────────────────────────────────────
    col_sp, col_save = st.columns([4, 1])
    with col_save:
        save_label = "❤️ Saglabāts" if is_saved else "🤍 Saglabāt"
        if st.button(save_label, key=f"save_{prog_id}_{rank}",
                     use_container_width=True):
            if on_save:
                on_save(prog_id, programme)

    # ── Compatibility detail bar ───────────────────────────────────────────
    render_compatibility_bar(score, rank)

    # ── Content expanders ─────────────────────────────────────────────────
    ai_label = (
        "🤖 AI Paskaidrojums (Gemini 2.5 Flash)"
        if is_ai
        else "📝 Automātisks Paskaidrojums"
    )
    with st.expander(ai_label, expanded=(rank == 1)):
        if is_ai:
            st.html(
                '<div style="background:#eff6ff;border-left:3px solid #3b82f6;'
                'border-radius:0 6px 6px 0;padding:6px 12px;margin-bottom:12px;'
                'font-size:0.78rem;color:#1e40af;">✨ Ģenerēts ar Gemini 2.5 Flash · '
                'Pamatots tikai uz programmas datiem</div>',
                )
        st.html(ai_explanation)

    with st.expander("📊 Kāpēc šis rezultāts? — Vērtēšanas sadalījums"):
        _render_breakdown_details(summary, breakdown)

    with st.expander("📋 Pilnīga programmas informācija"):
        _render_programme_details(programme)

    st.markdown("<div style='height:16px'></div>")


# ─────────────────────────────────────────────────────────────────────────────
# SCORE BREAKDOWN DETAILS
# ─────────────────────────────────────────────────────────────────────────────

def _render_breakdown_details(summary: dict, breakdown: dict):
    # Top summary metrics
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("📊 Bāzes rezultāts", f"{breakdown.get('base_pct', 0):.0f}%")
    with c2:
        penalty = breakdown.get("penalty_pct", 0)
        st.metric("⚠️ Sodi", f"−{penalty:.0f}%" if penalty else "0%")
    with c3:
        st.metric("🏆 Galīgais", f"{breakdown.get('final_pct', 0):.0f}%")

    st.html("<div style='height:8px'></div>")

    col_l, col_r = st.columns(2)

    with col_l:
        # Matched items
        for section, items, color_bg, color_text, icon in [
            ("Sakrītošās intereses", summary.get("matched_interests", []), "#dcfce7", "#166534", "✅"),
            ("Sakrītošās stiprās puses", summary.get("matched_strengths", []), "#dbeafe", "#1d4ed8", "💪"),
            ("Personības atbilstība", summary.get("matched_personality", []), "#ede9fe", "#7c3aed", "🧠"),
            ("Nozares atbilstība", summary.get("matched_sectors", []), "#fef3c7", "#92400e", "🏭"),
        ]:
            if items:
                st.html(f"**{icon} {section}**")
                tags_html = " ".join(_badge(i, color_bg, color_text) for i in items)
                st.markdown(tags_html)
                st.html("<div style='height:6px'></div>")

    with col_r:
        # Missed interests
        missed = summary.get("missed_interests", [])
        if missed:
            st.html("**⬜ Nesakrītošas intereses**")
            tags_html = " ".join(_badge(i, "#f1f5f9", "#64748b") for i in missed[:5])
            st.markdown(tags_html)
            st.html("<div style='height:8px'></div>")

        # Penalties
        if summary.get("penalties"):
            st.html("**⚠️ Punktu sodi**")
            for p in summary["penalties"]:
                st.html(
                    f'<div style="background:#fef2f2;border-left:3px solid #dc2626;'
                    f'border-radius:0 6px 6px 0;padding:6px 10px;margin:4px 0;'
                    f'font-size:0.8rem;color:#991b1b;">{p}</div>',
                    )
        elif not missed:
            st.html(
                '<div style="background:#f0fdf4;border-radius:8px;padding:12px;'
                'text-align:center;color:#166534;font-size:0.85rem;">'
                '✨ Nav nekādu sodu — ideāla atbilstība!</div>',
                )

    # Mini bar chart
    st.markdown("---")
    st.markdown("**📊 Faktoru sadalījums:**")
    score_items = [
        ("💡 Intereses", "interests"),
        ("💪 Stiprās puses", "strengths"),
        ("🧠 Personība", "personality"),
        ("🏭 Nozares", "sectors"),
        ("🌐 Valoda", "language"),
    ]
    for label, key in score_items:
        pts = breakdown.get(key, {}).get("points", 0)
        max_pts = breakdown.get(key, {}).get("max", 0)
        if max_pts and max_pts > 0:
            pct = (pts / max_pts) * 100
            color = "#059669" if pct >= 75 else "#d97706" if pct >= 40 else "#dc2626"
            st.markdown(f"""
            <div style="display:flex;align-items:center;gap:8px;margin:5px 0;">
              <span style="font-size:0.78rem;color:#374151;min-width:130px;">{label}</span>
              <div style="flex:1;height:7px;background:#f1f5f9;border-radius:4px;overflow:hidden;">
                <div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:4px;"></div>
              </div>
              <span style="font-size:0.74rem;color:#94a3b8;min-width:40px;text-align:right;">
                {pts}/{max_pts}</span>
            </div>
            """)


# ─────────────────────────────────────────────────────────────────────────────
# PROGRAMME FULL DETAILS
# ─────────────────────────────────────────────────────────────────────────────

def _render_programme_details(programme: dict):
    m = programme.get("matching", {}) or {}
    career = programme.get("career", {}) or {}
    degree = programme.get("degree", {}) or {}

    c1, c2 = st.columns(2)
    with c1:
        st.html("**📌 Pamatinformācija**")
        for label, val in [
            ("Nosaukums (LV)", programme.get("name")),
            ("Nosaukums (EN)", programme.get("name_en")),
            ("Fakultāte", programme.get("faculty")),
            ("Programmas tips", programme.get("program_type")),
            ("Studiju virziens", programme.get("study_direction")),
            ("Nozare", programme.get("study_field")),
        ]:
            if val:
                st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{label}:</span> "
                            f"<span style='font-size:0.85rem;font-weight:500;'>{val}</span>")

        st.html("<div style='height:8px'></div>")
        st.html("**🎓 Iegūstamais grāds**")
        if degree.get("title"):
            st.markdown(f"*{degree['title']}*")
        if degree.get("title_en"):
            st.caption(degree["title_en"])
        if degree.get("professional_qualification"):
            st.caption(f"Kvalifikācija: {degree['professional_qualification']}")

    with c2:
        st.markdown("**📋 Loģistika & Finanses**")
        for label, val in [
            ("Ilgums", f"{programme.get('duration_years', 4)} gadi"),
            ("Kredītpunkti", str(programme.get("credits", 240))),
            ("Forma", programme.get("format", "Pilna laika")),
            ("Valodas", ", ".join(LANG_LABELS.get(l, l) for l in programme.get("languages", []))),
            ("Atrašanās vieta", ", ".join(programme.get("locations", []))),
        ]:
            st.markdown(f"<span style='color:#64748b;font-size:0.8rem;'>{label}:</span> "
                        f"<span style='font-size:0.85rem;font-weight:500;'>{val}</span>")

        fee = programme.get("annual_fee_eur")
        budget = programme.get("budget_places", 0)
        st.html("<div style='height:6px'></div>")
        st.html(
            f"<span style='color:#64748b;font-size:0.8rem;'>Gada maksa:</span> "
            f"<span style='font-size:0.85rem;font-weight:600;color:#0f172a;'>"
            f"{'€' + str(int(fee)) if fee else '—'}</span>",
            )
        st.html(
            f"<span style='color:#64748b;font-size:0.8rem;'>Budžeta vietas:</span> "
            f"<span style='font-size:0.85rem;font-weight:600;"
            f"color:{'#059669' if budget > 0 else '#dc2626'};'>"
            f"{budget if budget > 0 else 'Nav'}</span>",
            )
        exam = programme.get("entry_exam", False)
        st.html(
            f"<span style='color:#64748b;font-size:0.8rem;'>Iestājpārbaudījums:</span> "
            f"<span style='font-size:0.85rem;font-weight:600;"
            f"color:{'#dc2626' if exam else '#059669'};'>"
            f"{'⚠️ Jā' if exam else '✅ Nē'}</span>",
            )
        if exam and programme.get("entry_exam_details"):
            st.caption(programme["entry_exam_details"])

    if programme.get("description"):
        st.html("**📖 Apraksts**")
        desc = programme["description"]
        st.html(
            f'<div style="font-size:0.85rem;color:#374151;line-height:1.6;'
            f'background:#f8fafc;border-radius:8px;padding:12px;">'
            f'{desc[:600]}{"…" if len(desc) > 600 else ""}</div>',
            )

    if career.get("job_titles"):
        st.markdown("**💼 Karjeras iespējas**")
        jobs_html = " ".join(
            _badge(f"→ {j}", "#f0fdf4", "#166534")
            for j in career["job_titles"][:7]
        )
        st.markdown(jobs_html)
        if career.get("description"):
            st.caption(career["description"][:250])

    if programme.get("url"):
        st.html(
            f'<a href="{programme["url"]}" target="_blank" style="'
            f'display:inline-flex;align-items:center;gap:6px;margin-top:8px;'
            f'background:#c8102e;color:white;text-decoration:none;'
            f'border-radius:8px;padding:6px 14px;font-size:0.8rem;font-weight:600;">'
            f'🔗 Atvērt RTU mājas lapā ↗</a>',
            )


# ─────────────────────────────────────────────────────────────────────────────
# COMPARISON TABLE
# ─────────────────────────────────────────────────────────────────────────────

def render_comparison_table(saved_progs: list[dict], scores: dict[str, float]):
    if not saved_progs:
        st.info("Nav saglabātu programmu.")
        return

    n = len(saved_progs)
    cols = st.columns(n, gap="medium")

    for col, prog in zip(cols, saved_progs):
        score = scores.get(prog.get("id", ""), 0)
        if score >= 75:
            s_color, s_bg = "#059669", "#dcfce7"
        elif score >= 55:
            s_color, s_bg = "#d97706", "#fef3c7"
        else:
            s_color, s_bg = "#dc2626", "#fee2e2"

        m = prog.get("matching", {}) or {}
        fee = prog.get("annual_fee_eur")
        budget = prog.get("budget_places", 0)

        with col:
            st.html(f"""
            <div style="border:1.5px solid {s_color}30;border-top:4px solid {s_color};
                        border-radius:14px;padding:16px;background:white;">
              <div style="font-size:0.9rem;font-weight:700;color:#0f172a;
                          line-height:1.3;margin-bottom:8px;">
                {prog.get('name', '—')}
              </div>
              <div style="font-size:2rem;font-weight:900;color:{s_color};
                          letter-spacing:-0.03em;">{score:.0f}%</div>
              <div style="font-size:0.7rem;color:{s_color};background:{s_bg};
                          padding:2px 8px;border-radius:20px;display:inline-block;
                          margin-bottom:12px;font-weight:600;">atbilstība</div>
              <hr style="border:none;border-top:1px solid #f1f5f9;margin:8px 0;">
            </div>
            """)

            def row(icon, label, val):
                st.html(
                    f'<div style="display:flex;justify-content:space-between;'
                    f'padding:4px 0;border-bottom:1px solid #f8fafc;">'
                    f'<span style="font-size:0.77rem;color:#64748b;">{icon} {label}</span>'
                    f'<span style="font-size:0.77rem;font-weight:600;color:#0f172a;">{val}</span>'
                    f'</div>',
                    )

            row("🏛️", "Fakultāte", (prog.get("faculty", "—") or "—")[:30])
            row("🕐", "Ilgums", f"{prog.get('duration_years', 4)} gadi")
            row("🌐", "Valoda", "/".join(prog.get("languages", ["lv"])).upper())
            row("💰", "Maksa/gadā", f"€{int(fee)}" if fee else "—")
            row("🎓", "Budžets", f"{budget} vietas" if budget > 0 else "Nav")
            row("📝", "Iestājpārb.", "⚠️ Jā" if prog.get("entry_exam") else "✅ Nē")
            row("📐", "Matemātika", "✓ Intensīva" if m.get("math_intensive") else "Standarta")
            row("🔬", "Pētnieciskā", "✓ Jā" if m.get("research_oriented") else "—")
            row("🌍", "Starptautisks", "✓ Jā" if m.get("international_potential") else "—")


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
            "Nosaukums": p.get("name", "—"),
            "English": p.get("name_en") or "—",
            "Fakultāte": (p.get("faculty") or "—")[:45],
            "Tips": "Akad." if "akadēm" in (p.get("program_type") or "").lower() else "Prof.",
            "Ilg.": f"{p.get('duration_years', 4)}g",
            "Valoda": "/".join(p.get("languages", ["lv"])).upper(),
            "Vieta": ", ".join(p.get("locations", ["Rīga"])),
            "Maksa €/g": int(p["annual_fee_eur"]) if p.get("annual_fee_eur") else 0,
            "Budžets": p.get("budget_places", 0),
            "Pārb.": "Jā" if p.get("entry_exam") else "Nē",
            "Mat.": "✓" if m.get("math_intensive") else "",
            "Pētn.": "✓" if m.get("research_oriented") else "",
            **({"Atbilstība %": score_val} if scores else {}),
        })

    df = pd.DataFrame(rows)
    if scores and "Atbilstība %" in df.columns:
        df = df.sort_values("Atbilstība %", ascending=False)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        height=min(520, 55 + len(df) * 38),
        column_config={
            "Nosaukums": st.column_config.TextColumn("Nosaukums", width="large"),
            "Atbilstība %": st.column_config.ProgressColumn(
                "Atbilstība %", min_value=0, max_value=100, format="%d%%",
            ) if scores else None,
            "Maksa €/g": st.column_config.NumberColumn("Maksa €/g", format="€%d"),
            "Budžets": st.column_config.NumberColumn("Budžets"),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────

def render_empty_results():
    st.html("""
    <div style="text-align:center; padding:40px 20px 32px 20px;">
      <div style="font-size:3.5rem; line-height:1; margin-bottom:16px;">🎓</div>
      <h3 style="color:#0f172a; font-weight:800; font-size:1.2rem;
                 letter-spacing:-0.02em; margin:0 0 8px 0;">
        Aizpildi savu profilu un saņem personalizētus ieteikumus!
      </h3>
      <p style="color:#64748b; font-size:0.875rem; max-width:480px;
                margin:0 auto 28px auto; line-height:1.6;">
        Mūsu AI salīdzina Tavu profilu ar visām 64 RTU programmām un
        izskaidro, kāpēc katra programma der tieši Tev.
      </p>

      <div style="display:flex; gap:12px; justify-content:center; flex-wrap:wrap;
                  max-width:560px; margin:0 auto;">
    """ + "".join(f"""
        <div style="
          background:white; border:1.5px solid #e2e8f0;
          border-radius:14px; padding:14px 18px;
          flex:1; min-width:130px; max-width:160px;
          text-align:center;
        ">
          <div style="font-size:1.5rem; margin-bottom:6px;">{icon}</div>
          <div style="font-size:0.78rem; font-weight:700; color:#0f172a;
                      margin-bottom:3px;">{title}</div>
          <div style="font-size:0.71rem; color:#94a3b8; line-height:1.4;">{desc}</div>
        </div>
    """ for icon, title, desc in [
        ("💡", "Intereses", "Ko tev patīk un kas tevi aizrauj"),
        ("💪", "Spējas", "Kuros priekšmetos esi stiprāks"),
        ("🧠", "Personība", "Kā tu raksturotu sevi"),
        ("🚀", "Mērķi", "Kurp vēlies nokļūt karjerā"),
    ]) + """
      </div>
    </div>
    """)


# ─────────────────────────────────────────────────────────────────────────────
# LOADING SPINNER
# ─────────────────────────────────────────────────────────────────────────────

def loading_spinner_context(message: str = "Aprēķina atbilstību…"):
    return st.spinner(message)
