"""
RTU Study Programme AI Recommender
app.py — Main Streamlit application entry point.
"""

import os
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="RTU Study Programme Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.rtu.lv",
        "Report a bug": None,
        "About": "RTU Study Programme AI Recommender — v1.1",
    },
)

sys.path.insert(0, str(Path(__file__).parent))

from data_loader import load_all_programmes, extract_taxonomy
from scoring import rank_programmes, score_all_programmes, breakdown_summary
from ai_explanations import generate_ai_explanation
from ui_components import (
    render_hero, render_result_card,
    render_comparison_table, render_programme_table,
    render_empty_results, loading_spinner_context,
)
from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS,
)

# ─────────────────────────────────────────────────────────────────────────────
# DESIGN SYSTEM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.html("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

/* ── BASE ─────────────────────────────────────────────────────── */
*, html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.stApp {
    background: #f0f4f8 !important;
}
.main .block-container {
    padding-top: 1.25rem !important;
    padding-bottom: 3rem !important;
    max-width: 1160px !important;
}

/* ── SIDEBAR ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0f172a 0%, #1e293b 60%, #0f172a 100%) !important;
}
[data-testid="stSidebar"] section > div { padding-top: 0.25rem; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
    margin: 0.75rem 0 !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #1e3a5f !important;
    border: 1px solid #2563eb40 !important;
    border-radius: 20px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #93c5fd !important; }

/* ── TABS ─────────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #e8edf2 !important;
    padding: 4px !important;
    border-radius: 14px !important;
    gap: 2px !important;
    border-bottom: none !important;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 8px 20px !important;
    color: #64748b !important;
    background: transparent !important;
    border: none !important;
    transition: all 0.15s ease !important;
}
.stTabs [aria-selected="true"] {
    background: white !important;
    color: #c8102e !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── BUTTONS ──────────────────────────────────────────────────── */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    transition: all 0.2s ease !important;
    padding: 0.5rem 1.2rem !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #c8102e 0%, #9b0022 100%) !important;
    color: white !important;
    border: none !important;
    box-shadow: 0 4px 14px rgba(200,16,46,0.28) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(200,16,46,0.42) !important;
    transform: translateY(-1px) !important;
}
.stButton > button[kind="secondary"],
.stButton > button:not([kind]) {
    background: white !important;
    color: #475569 !important;
    border: 1.5px solid #e2e8f0 !important;
}
.stButton > button[kind="secondary"]:hover,
.stButton > button:not([kind]):hover {
    background: #fef1f3 !important;
    border-color: #c8102e !important;
    color: #c8102e !important;
}

/* ── METRICS ──────────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #e8ecf0 !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.68rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: #94a3b8 !important;
}
[data-testid="stMetricValue"] {
    font-size: 1rem !important;
    font-weight: 800 !important;
    color: #0f172a !important;
    letter-spacing: -0.02em !important;
}

/* ── EXPANDERS ────────────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    margin-bottom: 6px !important;
    background: white !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
/* Only style background — never override padding on summary (it houses the icon) */
[data-testid="stExpander"] summary {
    background: #fafafa !important;
}
[data-testid="stExpander"] summary:hover { background: #f5f8fa !important; }
/* Style the label text inside summary without touching the icon layout */
[data-testid="stExpander"] summary p,
[data-testid="stExpander"] summary span {
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #374151 !important;
}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 16px !important;
}

/* ── FORM ─────────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: white !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 20px !important;
    padding: 4px 2px !important;
    box-shadow: 0 2px 16px rgba(0,0,0,0.06) !important;
}

/* ── MULTISELECT TAGS ─────────────────────────────────────────── */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #fef1f3 !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 20px !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span { color: #be123c !important; }

/* ── SELECT SLIDER ────────────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] { background: #c8102e !important; }

/* ── ALERTS ───────────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }

/* ── HR ───────────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid #e2e8f0 !important;
    margin: 1rem 0 !important;
}

/* ── INPUTS ───────────────────────────────────────────────────── */
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div { border-radius: 10px !important; }

/* ── MISC ─────────────────────────────────────────────────────── */
footer    { visibility: hidden; }
#MainMenu { visibility: hidden; }
</style>
""")


# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────

def _init_session():
    defaults = {
        "programmes": [], "load_stats": {}, "taxonomy": {},
        "results": [], "saved_programmes": set(), "saved_programme_data": {},
        "last_scores": {}, "search_done": False, "student_profile": {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADING
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner="⏳ Loading RTU programme database…")
def _load_data() -> tuple[list, dict, dict]:
    programmes, stats = load_all_programmes()
    taxonomy = extract_taxonomy(programmes)
    return programmes, stats, taxonomy


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def _section_label(icon: str, text: str):
    st.html(
        f'<div style="font-size:0.68rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.09em;color:#475569;margin:14px 0 6px 0;">{icon} {text}</div>',
    )


def render_sidebar(programmes: list[dict], taxonomy: dict) -> dict:
    with st.sidebar:
        # Brand header
        st.html("""
        <div style="padding:20px 8px 22px;text-align:center;">
          <div style="font-size:2.8rem;line-height:1;">🎓</div>
          <div style="font-size:1rem;font-weight:800;color:white;margin-top:8px;
                      letter-spacing:-0.02em;">RTU Recommender</div>
          <div style="font-size:0.68rem;color:#475569;margin-top:3px;
                      text-transform:uppercase;letter-spacing:0.09em;">
            Riga Technical University</div>
        </div>
        """)

        st.markdown("---")
        _section_label("⚡", "Quick filters")

        no_exam     = st.toggle("✅ No entrance exam",    value=False, key="f_no_exam")
        budget_only = st.toggle("🎓 Budget places only", value=False, key="f_budget")

        st.markdown("---")
        _section_label("🏛️", "Faculty")
        faculties = sorted({p.get("faculty", "") for p in programmes if p.get("faculty")})
        selected_faculties = st.multiselect(
            "Faculty", options=faculties, default=[],
            placeholder="All…", key="filter_faculties", label_visibility="collapsed",
        )

        _section_label("🌐", "Language of instruction")
        lang_opts = {"lv": "🇱🇻 Latvian", "en": "🇬🇧 English", "ru": "🇷🇺 Russian"}
        selected_langs = st.multiselect(
            "Language", options=list(lang_opts.keys()),
            format_func=lambda k: lang_opts[k],
            default=[], placeholder="All…",
            key="filter_langs", label_visibility="collapsed",
        )

        _section_label("📍", "Location")
        all_locations = sorted({loc for p in programmes for loc in (p.get("locations") or [])})
        selected_locations = st.multiselect(
            "Location", options=all_locations, default=[],
            placeholder="All…", key="filter_locations", label_visibility="collapsed",
        )

        _section_label("📚", "Programme type")
        prog_types = sorted({p.get("program_type", "") for p in programmes if p.get("program_type")})
        selected_types = st.multiselect(
            "Type", options=prog_types, default=[],
            placeholder="All…", key="filter_types", label_visibility="collapsed",
        )

        st.markdown("---")

        n_saved = len(st.session_state.get("saved_programmes", set()))
        if n_saved > 0:
            st.html(
                f'<div style="background:#0d3b2e;border:1px solid #065f46;border-radius:10px;'
                f'padding:10px 12px;margin-bottom:8px;">'
                f'<div style="color:#34d399;font-weight:700;font-size:0.85rem;">'
                f'❤️ {n_saved} saved programme{"s" if n_saved != 1 else ""}</div></div>',
            )
            if st.button("🗑️ Clear saved", key="clear_saved", use_container_width=True):
                st.session_state["saved_programmes"]    = set()
                st.session_state["saved_programme_data"] = {}
                st.rerun()

        st.markdown("---")
        st.html(
            f'<div style="color:#475569;font-size:0.7rem;text-align:center;line-height:1.9;">'
            f'📦 {len(programmes)} programmes loaded<br>'
            f'🗓️ Data: RTU 2026</div>',
        )

    return {
        "faculties":    selected_faculties or None,
        "languages":    selected_langs     or None,
        "locations":    selected_locations or None,
        "program_types":selected_types     or None,
        "no_exam_only": no_exam,
        "budget_only":  budget_only,
    }


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT PROFILE FORM
# ─────────────────────────────────────────────────────────────────────────────

def _form_section(icon: str, title: str, subtitle: str):
    """Render a styled section divider inside the form."""
    st.html(
        f"""<div style="
          display:flex;align-items:center;gap:12px;
          padding:16px 4px 12px;
          border-bottom:1.5px solid #f1f5f9;
          margin-bottom:4px;
        ">
          <div style="
            background:linear-gradient(135deg,#c8102e,#9b0022);
            color:white;border-radius:10px;
            width:36px;height:36px;
            display:flex;align-items:center;justify-content:center;
            font-size:1.1rem;flex-shrink:0;
            box-shadow:0 3px 8px rgba(200,16,46,0.25);
          ">{icon}</div>
          <div>
            <div style="font-size:0.95rem;font-weight:700;color:#0f172a;
                        letter-spacing:-0.01em;">{title}</div>
            <div style="font-size:0.75rem;color:#94a3b8;margin-top:1px;">{subtitle}</div>
          </div>
        </div>""",
    )


def render_student_form(programmes: list[dict], taxonomy: dict) -> dict | None:
    st.html("""
    <div style="margin-bottom:18px;">
      <h2 style="margin:0;font-size:1.4rem;font-weight:800;color:#0f172a;
                 letter-spacing:-0.02em;">📝 My Profile</h2>
      <p style="margin:5px 0 0;color:#64748b;font-size:0.875rem;">
        The more you fill in, the better your matches. All fields are optional.</p>
    </div>
    """)

    with st.form("student_profile_form", clear_on_submit=False):

        # ── SECTION 1: Interests & Skills ────────────────────────────────
        _form_section("🎯", "Interests & Strengths",
                      "What you enjoy and what you're good at")

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown("**💡 Interest areas** *(up to 5)*")
            interests = st.multiselect(
                "Interests", options=list(INTEREST_DOMAINS.keys()),
                format_func=lambda k: INTEREST_DOMAINS[k]["label"],
                max_selections=5, key="form_interests",
                label_visibility="collapsed",
                placeholder="Choose what interests you…",
            )
            st.markdown("**💪 Strengths & Subjects** *(up to 6)*")
            strengths = st.multiselect(
                "Strengths", options=list(STRENGTH_TAGS.keys()),
                format_func=lambda k: STRENGTH_TAGS[k]["label"],
                max_selections=6, key="form_strengths",
                label_visibility="collapsed",
                placeholder="Which subjects are you strongest in…",
            )
        with col2:
            st.markdown("**🧠 Personality type** *(up to 4)*")
            personality = st.multiselect(
                "Personality", options=list(PERSONALITY_TRAITS.keys()),
                format_func=lambda k: PERSONALITY_TRAITS[k]["label"],
                max_selections=4, key="form_personality",
                label_visibility="collapsed",
                placeholder="How would you describe yourself…",
            )
            st.markdown("**🏭 Preferred industry sectors** *(up to 5)*")
            sectors = st.multiselect(
                "Sectors", options=list(INDUSTRY_SECTORS.keys()),
                format_func=lambda k: INDUSTRY_SECTORS[k]["label"],
                max_selections=5, key="form_sectors",
                label_visibility="collapsed",
                placeholder="Which sector do you want to work in…",
            )

        # ── SECTION 2: Study Preferences ─────────────────────────────────
        _form_section("⚙️", "Study Preferences",
                      "Language, difficulty level and personal preferences")

        col3, col4 = st.columns(2, gap="medium")
        with col3:
            st.markdown("**🌐 Language of instruction**")
            preferred_language = st.selectbox(
                "Language", options=["lv", "en", "ru", "any"],
                format_func=lambda k: {
                    "lv": "🇱🇻 Latvian",
                    "en": "🇬🇧 English",
                    "ru": "🇷🇺 Russian",
                    "any": "🌍 Any language",
                }[k],
                key="form_language", label_visibility="collapsed",
            )
            st.markdown("**📊 Difficulty level**")
            preferred_difficulty = st.select_slider(
                "Difficulty",
                options=["low", "medium", "medium_high", "high"],
                value="medium",
                format_func=lambda k: DIFFICULTY_LEVELS.get(k, k),
                key="form_difficulty", label_visibility="collapsed",
            )
            st.markdown("**🤝 Work style**")
            teamwork = st.select_slider(
                "Teamwork",
                options=["team", "both", "independent"],
                value="both",
                format_func=lambda k: {
                    "team": "👥 Team work",
                    "both": "🔄 Both",
                    "independent": "🦅 Independent",
                }[k],
                key="form_teamwork", label_visibility="collapsed",
            )

        with col4:
            st.markdown("**Personal preferences**")
            st.html("<div style='height:4px'></div>")

            math_friendly = st.toggle(
                "📐 Maths is one of my strengths",
                key="form_math", value=False,
            )
            creative = st.toggle(
                "🎨 I enjoy creative / design work",
                key="form_creative", value=False,
            )
            research = st.toggle(
                "🔬 I'm interested in research-oriented studies",
                key="form_research", value=False,
            )
            international = st.toggle(
                "🌍 I want to study or work abroad",
                key="form_intl", value=False,
            )
            exam_ok = st.toggle(
                "📝 I'm willing to sit an entrance exam",
                key="form_exam", value=True,
            )

        # ── SECTION 3: Career Goals ───────────────────────────────────────
        _form_section("🚀", "Career Goals",
                      "Describe your future plans in your own words (optional)")

        career_text = st.text_area(
            "Career goals",
            placeholder=(
                'e.g. "I want to become a software engineer working in AI" '
                'or "Interested in architecture and sustainable construction"...'
            ),
            max_chars=300, height=90,
            key="form_career_text", label_visibility="collapsed",
        )

        # ── Submit ────────────────────────────────────────────────────────
        st.html("<div style='height:8px'></div>")
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            submitted = st.form_submit_button(
                "🔍  Find My Best-Matching Programmes",
                use_container_width=True,
                type="primary",
            )
        with c3:
            load_test = st.form_submit_button(
                "📋 Load test profile",
                use_container_width=True,
            )

    if load_test:
        _load_test_profile()
        st.rerun()

    if submitted:
        return {
            "interests": interests, "strengths": strengths,
            "personality": personality, "sectors": sectors,
            "preferred_language": preferred_language,
            "preferred_difficulty": preferred_difficulty,
            "math_friendly": math_friendly, "creative": creative,
            "research_oriented": research, "international": international,
            "exam_ok": exam_ok, "teamwork": teamwork,
            "career_text": career_text,
        }
    return None


def _load_test_profile():
    import json, random
    test_file = Path(__file__).parent / "test_profiles.json"
    try:
        with open(test_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        profiles = data.get("profiles", [])
        if profiles:
            chosen  = random.choice(profiles)
            profile = chosen.get("profile", {})
            mapping = {
                "form_interests": "interests", "form_strengths": "strengths",
                "form_personality": "personality", "form_sectors": "sectors",
                "form_language": "preferred_language", "form_difficulty": "preferred_difficulty",
                "form_math": "math_friendly", "form_creative": "creative",
                "form_research": "research_oriented", "form_intl": "international",
                "form_exam": "exam_ok", "form_teamwork": "teamwork",
                "form_career_text": "career_text",
            }
            for form_key, profile_key in mapping.items():
                if profile_key in profile:
                    st.session_state[form_key] = profile[profile_key]
            st.toast(f"✅ Test profile loaded: **{chosen.get('name', 'Unknown')}**")
    except Exception as e:
        st.toast(f"⚠️ Could not load test profile: {e}", icon="⚠️")


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def render_results(student: dict, programmes: list[dict], filters: dict):
    with loading_spinner_context("🔍 Calculating compatibility for all programmes…"):
        top_results = rank_programmes(student, programmes, top_n=3, filters=filters)
        all_scored  = score_all_programmes(student, programmes, filters=filters)

    scores_map = {r["programme"].get("id", ""): r["score"] for r in all_scored}
    st.session_state["last_scores"] = scores_map

    if not top_results:
        st.warning(
            "⚠️ No programmes found with the current filters. "
            "Try adjusting the sidebar filters or adding more profile details."
        )
        return

    top_score = top_results[0]["score"]
    avg_score = sum(r["score"] for r in top_results) / len(top_results)

    # Confidence banner
    if top_score >= 75:
        b_color, b_bg, b_text, b_icon = "#059669", "#ecfdf5", "High confidence", "🟢"
    elif top_score >= 50:
        b_color, b_bg, b_text, b_icon = "#d97706", "#fffbeb", "Good match", "🟡"
    else:
        b_color, b_bg, b_text, b_icon = "#dc2626", "#fef2f2", "Partial match", "🟠"

    st.html(f"""
    <div style="
      background:{b_bg};border:1.5px solid {b_color}30;
      border-left:5px solid {b_color};border-radius:14px;
      padding:14px 20px;margin-bottom:24px;
      display:flex;align-items:center;gap:16px;">
      <div style="font-size:2rem;">{b_icon}</div>
      <div>
        <div style="font-size:1rem;font-weight:700;color:{b_color};">
          {b_text} — best match: {top_score:.0f}%
        </div>
        <div style="font-size:0.8rem;color:#64748b;margin-top:2px;">
          Top-3 average: {avg_score:.0f}% ·
          {"Your profile is a great fit for these programmes." if top_score >= 75
           else "Good match with some trade-offs." if top_score >= 50
           else "Consider adding more profile details or adjusting filters."}
        </div>
      </div>
    </div>
    """)

    for rank_i, result in enumerate(top_results, start=1):
        prog      = result["programme"]
        score     = result["score"]
        breakdown = result["breakdown"]
        bd_summary = breakdown_summary(breakdown)

        with st.spinner(f"✨ Generating AI explanation for programme #{rank_i}…"):
            explanation, is_ai = generate_ai_explanation(
                student_profile=student,
                programme=prog,
                scoring_breakdown=breakdown,
            )

        render_result_card(
            rank=rank_i, programme=prog, score=score,
            breakdown=breakdown, ai_explanation=explanation,
            is_ai=is_ai, summary=bd_summary,
            on_save=_save_programme,
        )


def _save_programme(prog_id: str, programme: dict):
    saved      = st.session_state.get("saved_programmes", set())
    saved_data = st.session_state.get("saved_programme_data", {})
    if prog_id in saved:
        saved.discard(prog_id)
        saved_data.pop(prog_id, None)
        st.toast("Programme removed from saved.", icon="🗑️")
    else:
        saved.add(prog_id)
        saved_data[prog_id] = programme
        st.toast(f"Saved: **{programme.get('name', prog_id)}**", icon="❤️")
    st.session_state["saved_programmes"]     = saved
    st.session_state["saved_programme_data"] = saved_data
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# COMPARE TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_compare_tab():
    saved_data = st.session_state.get("saved_programme_data", {})
    scores     = st.session_state.get("last_scores", {})
    saved_list = list(saved_data.values())

    if not saved_list:
        st.html("""
        <div style="text-align:center;padding:52px 24px;color:#94a3b8;">
          <div style="font-size:3.5rem;">⚖️</div>
          <h3 style="color:#64748b;font-weight:700;margin:12px 0 8px;">No saved programmes</h3>
          <p style="max-width:400px;margin:0 auto;font-size:0.9rem;line-height:1.6;">
            Find matching programmes in the <strong>🔍 Recommendations</strong> tab,
            then click <strong>🤍 Save</strong> on any result.
          </p>
        </div>
        """)
        return

    st.html(
        f'<h3 style="margin:0 0 20px;font-size:1.2rem;font-weight:700;color:#0f172a;">'
        f'⚖️ Comparison — {len(saved_list)} programme{"s" if len(saved_list) != 1 else ""}</h3>',
    )
    render_comparison_table(saved_list, scores)


# ─────────────────────────────────────────────────────────────────────────────
# ALL PROGRAMMES TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_all_programmes_tab(programmes: list[dict]):
    col_title, col_search = st.columns([2, 3])
    with col_title:
        st.html(
            '<h3 style="margin:0 0 4px;font-size:1.1rem;font-weight:700;color:#0f172a;">'
            '📋 All RTU Programmes</h3>',
        )
    with col_search:
        search = st.text_input(
            "Search",
            placeholder="🔍  Search by name, faculty, keywords…",
            key="search_bar", label_visibility="collapsed",
        )

    filtered = programmes
    if search:
        sl = search.lower()
        filtered = [
            p for p in programmes if (
                sl in (p.get("name")    or "").lower()
                or sl in (p.get("name_en")  or "").lower()
                or sl in (p.get("description") or "").lower()
                or sl in (p.get("faculty") or "").lower()
                or any(sl in kw.lower() for kw in p.get("keywords", []))
            )
        ]

    scores = st.session_state.get("last_scores", {})

    col_info, col_sort = st.columns([3, 2])
    with col_info:
        st.caption(
            f"Showing **{len(filtered)}** of {len(programmes)} programmes"
            + (" · sorted by your match %" if scores else "")
        )
    with col_sort:
        sort_by = st.selectbox(
            "Sort by:",
            ["Match %", "Name A–Z", "Annual fee ↑", "Budget places ↓"],
            key="sort_by", label_visibility="collapsed",
        )

    if sort_by == "Match %" and scores:
        filtered = sorted(filtered, key=lambda p: scores.get(p.get("id", ""), 0), reverse=True)
    elif sort_by == "Name A–Z":
        filtered = sorted(filtered, key=lambda p: p.get("name", ""))
    elif sort_by == "Annual fee ↑":
        filtered = sorted(filtered, key=lambda p: p.get("annual_fee_eur") or 0)
    elif sort_by == "Budget places ↓":
        filtered = sorted(filtered, key=lambda p: p.get("budget_places", 0), reverse=True)

    render_programme_table(filtered, scores if scores else None)


# ─────────────────────────────────────────────────────────────────────────────
# ABOUT TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_about_tab():
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
## ℹ️ About this tool

**RTU Study Programme AI Recommender** helps high-school students choose the
best-fitting RTU bachelor programmes based on their personal profile.

---

### 🏗️ How it works

**1. Fill in your profile**
Add your interests, strengths, personality type and preferences.

**2. Weighted scoring (13 factors)**
Each programme receives points based on how well it matches your profile:

| Factor | Weight | Penalty |
|---|---|---|
| Interest areas | +4/match | — |
| Strengths | +3/match | — |
| Personality | +2/match | — |
| Industry sectors | +3/match | — |
| Study language | +2 | −20% (not available) |
| Difficulty | +2 | −10% (too hard) |
| Maths | +2 | −8% (dislikes, but intensive) |
| Entrance exam | +2 | −15% (mismatch) |
| Research, International, Creative, Teamwork | +1–2 | — |

**3. AI Explanation (Gemini 2.5 Flash)**
A personalised explanation for each top-3 programme, based on your profile.

---

### ⚠️ Limitations
- Recommendations are indicative — the final choice is always yours
- Data is based on RTU 2026 programme descriptions
- Always verify current info at [rtu.lv](https://www.rtu.lv)
        """)
    with col2:
        st.markdown("""
### 🚀 Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 📁 Project structure
```
rtu-study-recommender/
├── app.py              ← Main UI
├── data_loader.py      ← JSON loader
├── scoring.py          ← Match engine
├── ai_explanations.py  ← Gemini AI
├── ui_components.py    ← UI blocks
├── utils.py            ← Taxonomy
└── datasets/           ← 64 programmes
```

### 🔮 Planned improvements
- [ ] CE exam requirement integration
- [ ] PDF export of results
- [ ] Top-10 results view
- [ ] Score a minimum profile threshold
- [ ] RTU live data API
        """)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    _init_session()
    programmes, stats, taxonomy = _load_data()

    if not programmes:
        st.error("❌ No programmes found! Make sure the `datasets/` folder contains RTU JSON files.")
        st.stop()

    render_hero(stats, len(programmes))
    filters = render_sidebar(programmes, taxonomy)

    tab_search, tab_compare, tab_all, tab_about = st.tabs([
        "🔍  Recommendations",
        "⚖️  Compare",
        "📋  All Programmes",
        "ℹ️  About",
    ])

    with tab_search:
        st.html("<div style='height:4px'></div>")
        profile = render_student_form(programmes, taxonomy)

        if profile:
            st.session_state["student_profile"] = profile
            st.session_state["search_done"]     = True

        if st.session_state.get("search_done") and st.session_state.get("student_profile"):
            st.markdown("---")
            st.html("""
            <h2 style="margin:0 0 4px;font-size:1.4rem;font-weight:800;
                       color:#0f172a;letter-spacing:-0.02em;">
              🏆 Your top matching programmes
            </h2>
            <p style="margin:0 0 20px;color:#64748b;font-size:0.875rem;">
              The three best matches with detailed AI analysis
            </p>
            """)
            render_results(
                student=st.session_state["student_profile"],
                programmes=programmes,
                filters=filters,
            )
        elif not st.session_state.get("search_done"):
            render_empty_results()

    with tab_compare:
        render_compare_tab()

    with tab_all:
        render_all_programmes_tab(programmes)

    with tab_about:
        render_about_tab()


if __name__ == "__main__":
    main()
