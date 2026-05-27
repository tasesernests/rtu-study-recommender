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
    page_title="RTU Studiju Ieteicējs",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": "https://www.rtu.lv",
        "Report a bug": None,
        "About": "RTU Study Programme AI Recommender — v1.0",
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
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,300;0,14..32,400;0,14..32,500;0,14..32,600;0,14..32,700;0,14..32,800;0,14..32,900&display=swap');

/* ── BASE ─────────────────────────────────────────────────── */
*, html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
}
.main .block-container {
    padding-top: 1rem !important;
    padding-bottom: 3rem !important;
    max-width: 1140px !important;
}

/* ── SIDEBAR ─────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #0f172a 0%, #1e293b 60%, #0f172a 100%) !important;
}
[data-testid="stSidebar"] section > div { padding-top: 0.5rem; }
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption { color: #94a3b8 !important; }
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 { color: #e2e8f0 !important; }
[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
    margin: 0.8rem 0 !important;
}
/* Sidebar multiselect tags */
[data-testid="stSidebar"] [data-baseweb="tag"] {
    background: #1e3a5f !important;
    border: 1px solid #2563eb40 !important;
    border-radius: 20px !important;
}
[data-testid="stSidebar"] [data-baseweb="tag"] span { color: #93c5fd !important; }

/* ── TABS ────────────────────────────────────────────────── */
.stTabs [data-baseweb="tab-list"] {
    background: #f1f5f9 !important;
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

/* ── BUTTONS ─────────────────────────────────────────────── */
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
    box-shadow: 0 4px 14px rgba(200,16,46,0.30) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 22px rgba(200,16,46,0.45) !important;
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

/* ── METRICS ─────────────────────────────────────────────── */
[data-testid="stMetric"] {
    background: white !important;
    border: 1px solid #f0f4f8 !important;
    border-radius: 14px !important;
    padding: 14px 18px !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
    transition: box-shadow 0.2s !important;
}
[data-testid="stMetric"]:hover {
    box-shadow: 0 4px 14px rgba(0,0,0,0.09) !important;
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

/* ── EXPANDERS ───────────────────────────────────────────── */
[data-testid="stExpander"] {
    border: 1px solid #e8ecf0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    margin-bottom: 8px !important;
    background: white !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}
[data-testid="stExpander"] summary {
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    color: #374151 !important;
    padding: 12px 16px !important;
    background: #fafafa !important;
}
[data-testid="stExpander"] summary:hover { background: #f5f8fa !important; }
[data-testid="stExpander"] [data-testid="stExpanderDetails"] {
    padding: 16px !important;
}

/* ── FORM ────────────────────────────────────────────────── */
[data-testid="stForm"] {
    background: white !important;
    border: 1px solid #e8ecf0 !important;
    border-radius: 20px !important;
    padding: 4px 2px !important;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05) !important;
}

/* ── MULTISELECT TAGS ────────────────────────────────────── */
[data-testid="stMultiSelect"] [data-baseweb="tag"] {
    background: #fef1f3 !important;
    border: 1px solid #fecdd3 !important;
    border-radius: 20px !important;
}
[data-testid="stMultiSelect"] [data-baseweb="tag"] span { color: #be123c !important; }

/* ── SELECT SLIDER ───────────────────────────────────────── */
[data-testid="stSlider"] [role="slider"] { background: #c8102e !important; }

/* ── ALERTS ──────────────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; border: none !important; }

/* ── HR ──────────────────────────────────────────────────── */
hr {
    border: none !important;
    border-top: 1px solid #e8ecf0 !important;
    margin: 1rem 0 !important;
}

/* ── INPUTS ──────────────────────────────────────────────── */
[data-baseweb="input"] > div,
[data-baseweb="textarea"] > div { border-radius: 10px !important; }

/* ── MISC ────────────────────────────────────────────────── */
footer { visibility: hidden; }
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

@st.cache_data(ttl=3600, show_spinner="⏳ Ielādē RTU programmu datu bāzi…")
def _load_data() -> tuple[list, dict, dict]:
    programmes, stats = load_all_programmes()
    taxonomy = extract_taxonomy(programmes)
    return programmes, stats, taxonomy


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

def _section_label(icon: str, text: str):
    st.html(
        f'<div style="font-size:0.7rem;font-weight:700;text-transform:uppercase;'
        f'letter-spacing:0.08em;color:#475569;margin:12px 0 6px 0;">{icon} {text}</div>',
        )


def render_sidebar(programmes: list[dict], taxonomy: dict) -> dict:
    with st.sidebar:
        # Brand header
        st.html("""
        <div style="padding:16px 8px 20px 8px; text-align:center;">
          <div style="font-size:2.8rem; line-height:1;">🎓</div>
          <div style="font-size:1rem; font-weight:800; color:white; margin-top:8px;
                      letter-spacing:-0.02em;">RTU Ieteicējs</div>
          <div style="font-size:0.72rem; color:#64748b; margin-top:3px;
                      text-transform:uppercase; letter-spacing:0.08em;">
            Riga Technical University</div>
        </div>
        """)

        st.markdown("---")
        _section_label("⚡", "Ātrie filtri")

        no_exam = st.toggle("✅ Bez iestājpārbaudījuma", value=False, key="f_no_exam")
        budget_only = st.toggle("🎓 Tikai budžeta vietas", value=False, key="f_budget")

        st.markdown("---")
        _section_label("🏛️", "Fakultāte")
        faculties = sorted({p.get("faculty", "") for p in programmes if p.get("faculty")})
        selected_faculties = st.multiselect(
            "Fakultāte", options=faculties, default=[],
            placeholder="Visas…", key="filter_faculties", label_visibility="collapsed",
        )

        _section_label("🌐", "Studiju valoda")
        lang_opts = {"lv": "🇱🇻 Latviešu", "en": "🇬🇧 Angļu", "ru": "🇷🇺 Krievu"}
        selected_langs = st.multiselect(
            "Valoda", options=list(lang_opts.keys()),
            format_func=lambda k: lang_opts[k],
            default=[], placeholder="Visas…",
            key="filter_langs", label_visibility="collapsed",
        )

        _section_label("📍", "Atrašanās vieta")
        all_locations = sorted({loc for p in programmes for loc in (p.get("locations") or [])})
        selected_locations = st.multiselect(
            "Vieta", options=all_locations, default=[],
            placeholder="Visas…", key="filter_locations", label_visibility="collapsed",
        )

        _section_label("📚", "Programmas tips")
        prog_types = sorted({p.get("program_type", "") for p in programmes if p.get("program_type")})
        selected_types = st.multiselect(
            "Tips", options=prog_types, default=[],
            placeholder="Visi…", key="filter_types", label_visibility="collapsed",
        )

        st.markdown("---")

        n_saved = len(st.session_state.get("saved_programmes", set()))
        if n_saved > 0:
            st.html(
                f'<div style="background:#0d3b2e;border:1px solid #065f46;border-radius:10px;'
                f'padding:10px 12px;margin-bottom:8px;">'
                f'<div style="color:#34d399;font-weight:700;font-size:0.85rem;">'
                f'❤️ {n_saved} saglabāta programma{"s" if n_saved != 1 else ""}</div></div>',
                )
            if st.button("🗑️ Notīrīt saglabātās", key="clear_saved", use_container_width=True):
                st.session_state["saved_programmes"] = set()
                st.session_state["saved_programme_data"] = {}
                st.rerun()

        st.markdown("---")
        st.html(
            f'<div style="color:#475569;font-size:0.72rem;text-align:center;line-height:1.8;">'
            f'📦 {len(programmes)} programmas ielādētas<br>'
            f'🗓️ Dati: RTU 2026</div>',
            )

    return {
        "faculties": selected_faculties or None,
        "languages": selected_langs or None,
        "locations": selected_locations or None,
        "program_types": selected_types or None,
        "no_exam_only": no_exam,
        "budget_only": budget_only,
    }


# ─────────────────────────────────────────────────────────────────────────────
# STUDENT PROFILE FORM
# ─────────────────────────────────────────────────────────────────────────────

def _form_section(icon: str, title: str, subtitle: str):
    """Render a styled section header inside the form."""
    st.html(
        f"""<div style="
          display:flex; align-items:center; gap:12px;
          padding:14px 4px 10px 4px;
          border-bottom:1.5px solid #f1f5f9;
          margin-bottom:4px;
        ">
          <div style="
            background:linear-gradient(135deg,#c8102e,#9b0022);
            color:white; border-radius:10px;
            width:36px; height:36px;
            display:flex; align-items:center; justify-content:center;
            font-size:1.1rem; flex-shrink:0;
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
    <div style="margin-bottom:16px;">
      <h2 style="margin:0;font-size:1.4rem;font-weight:800;color:#0f172a;
                 letter-spacing:-0.02em;">📝 Mans Profils</h2>
      <p style="margin:4px 0 0 0;color:#64748b;font-size:0.875rem;">
        Jo precīzāk aizpildi, jo personalizētāki ieteikumi. Visi lauki ir brīvprātīgi.</p>
    </div>
    """)

    with st.form("student_profile_form", clear_on_submit=False):

        # ── SECTION 1: Interests & Skills ────────────────────────────────
        _form_section("🎯", "Intereses & Spējas",
                      "Ko tev patīk un kādās jomās esi stiprāks")

        col1, col2 = st.columns(2, gap="medium")
        with col1:
            st.markdown("**💡 Interešu jomas** *(līdz 5)*")
            interests = st.multiselect(
                "Intereses", options=list(INTEREST_DOMAINS.keys()),
                format_func=lambda k: INTEREST_DOMAINS[k]["label"],
                max_selections=5, key="form_interests",
                label_visibility="collapsed",
                placeholder="Izvēlies, kas tevi interesē...",
            )
            st.markdown("**💪 Stiprās puses & Priekšmeti** *(līdz 6)*")
            strengths = st.multiselect(
                "Stiprās puses", options=list(STRENGTH_TAGS.keys()),
                format_func=lambda k: STRENGTH_TAGS[k]["label"],
                max_selections=6, key="form_strengths",
                label_visibility="collapsed",
                placeholder="Kuros priekšmetos esi stiprāks...",
            )
        with col2:
            st.markdown("**🧠 Personības tips** *(līdz 4)*")
            personality = st.multiselect(
                "Personība", options=list(PERSONALITY_TRAITS.keys()),
                format_func=lambda k: PERSONALITY_TRAITS[k]["label"],
                max_selections=4, key="form_personality",
                label_visibility="collapsed",
                placeholder="Kā tu raksturotu sevi...",
            )
            st.markdown("**🏭 Vēlamās nozares** *(līdz 5)*")
            sectors = st.multiselect(
                "Nozares", options=list(INDUSTRY_SECTORS.keys()),
                format_func=lambda k: INDUSTRY_SECTORS[k]["label"],
                max_selections=5, key="form_sectors",
                label_visibility="collapsed",
                placeholder="Kurā nozarē vēlies strādāt...",
            )

        # ── SECTION 2: Study Preferences ─────────────────────────────────
        _form_section("⚙️", "Studiju Preferences",
                      "Valoda, grūtības pakāpe un citas vēlmes")

        col3, col4 = st.columns(2, gap="medium")
        with col3:
            st.markdown("**🌐 Studiju valoda**")
            preferred_language = st.selectbox(
                "Valoda", options=["lv", "en", "ru", "any"],
                format_func=lambda k: {
                    "lv": "🇱🇻 Latviešu",
                    "en": "🇬🇧 Angļu",
                    "ru": "🇷🇺 Krievu",
                    "any": "🌍 Jebkura",
                }[k],
                key="form_language", label_visibility="collapsed",
            )
            st.markdown("**📊 Grūtības pakāpe**")
            preferred_difficulty = st.select_slider(
                "Grūtība",
                options=["low", "medium", "medium_high", "high"],
                value="medium",
                format_func=lambda k: DIFFICULTY_LEVELS.get(k, k),
                key="form_difficulty", label_visibility="collapsed",
            )
            st.markdown("**🤝 Darba stils**")
            teamwork = st.select_slider(
                "Teamwork",
                options=["team", "both", "independent"],
                value="both",
                format_func=lambda k: {
                    "team": "👥 Komandas darbs",
                    "both": "🔄 Abos labi",
                    "independent": "🦅 Patstāvīgs",
                }[k],
                key="form_teamwork", label_visibility="collapsed",
            )

        with col4:
            st.markdown("**Personīgās Preferences**")
            st.html("<div style='height:4px'></div>")

            math_friendly = st.toggle(
                "📐 Matemātika ir mana stiprā puse",
                key="form_math", value=False
            )
            creative = st.toggle(
                "🎨 Man patīk radošs / dizaina darbs",
                key="form_creative", value=False
            )
            research = st.toggle(
                "🔬 Interesē pētnieciskās studijas",
                key="form_research", value=False
            )
            international = st.toggle(
                "🌍 Vēlos studēt vai strādāt ārzemēs",
                key="form_intl", value=False
            )
            exam_ok = st.toggle(
                "📝 Esmu gatavs iestājpārbaudījumam",
                key="form_exam", value=True
            )

        # ── SECTION 3: Career Goals ───────────────────────────────────────
        _form_section("🚀", "Karjeras Mērķi",
                      "Apraksti savus nākotnes plānus (brīvi, neobligāti)")

        career_text = st.text_area(
            "Karjera",
            placeholder=(
                "Piemēram: \"Vēlos kļūt par datorsistēmu inženieri un strādāt AI jomā\" "
                "vai \"Interesē arhitektūra un ilgtspējīga būvniecība\"…"
            ),
            max_chars=300, height=90,
            key="form_career_text", label_visibility="collapsed",
        )

        # ── Submit area ───────────────────────────────────────────────────
        st.html("<div style='height:8px'></div>")
        c1, c2, c3 = st.columns([1, 3, 1])
        with c2:
            submitted = st.form_submit_button(
                "🔍  Atrast Manai Personībai Atbilstošās Programmas",
                use_container_width=True,
                type="primary",
            )
        with c3:
            load_test = st.form_submit_button(
                "📋 Testa profils",
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
            chosen = random.choice(profiles)
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
            st.toast(f"✅ Testa profils ielādēts: **{chosen.get('name', 'Nezināms')}**")
    except Exception as e:
        st.toast(f"⚠️ Neizdevās ielādēt testa profilu: {e}", icon="⚠️")


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS RENDERER
# ─────────────────────────────────────────────────────────────────────────────

def render_results(student: dict, programmes: list[dict], filters: dict):
    with loading_spinner_context("🔍 Aprēķina atbilstību visām programmām…"):
        top_results = rank_programmes(student, programmes, top_n=3, filters=filters)
        all_scored = score_all_programmes(student, programmes, filters=filters)

    scores_map = {r["programme"].get("id", ""): r["score"] for r in all_scored}
    st.session_state["last_scores"] = scores_map

    if not top_results:
        st.warning(
            "⚠️ Nav atrasta neviena programma ar šādiem filtriem. "
            "Mēģini mainīt filtrus sānjoslā vai papildināt savu profilu."
        )
        return

    top_score = top_results[0]["score"]
    avg_score = sum(r["score"] for r in top_results) / len(top_results)

    # Result summary banner
    if top_score >= 75:
        badge_color, badge_bg, badge_text = "#059669", "#ecfdf5", "Augsta pārliecība"
        badge_icon = "🟢"
    elif top_score >= 50:
        badge_color, badge_bg, badge_text = "#d97706", "#fffbeb", "Vidēja pārliecība"
        badge_icon = "🟡"
    else:
        badge_color, badge_bg, badge_text = "#dc2626", "#fef2f2", "Zema pārliecība"
        badge_icon = "🟠"

    st.html(f"""
    <div style="
      background:{badge_bg};
      border:1.5px solid {badge_color}30;
      border-left:5px solid {badge_color};
      border-radius:14px;
      padding:14px 20px;
      margin-bottom:24px;
      display:flex; align-items:center; gap:16px;
    ">
      <div style="font-size:2rem;">{badge_icon}</div>
      <div>
        <div style="font-size:1rem;font-weight:700;color:{badge_color};">
          {badge_text} — labākā atbilstība: {top_score:.0f}%
        </div>
        <div style="font-size:0.8rem;color:#64748b;margin-top:2px;">
          Top-3 vidēji: {avg_score:.0f}% ·
          {"Profils lieliski atbilst šīm programmām." if top_score >= 75
           else "Laba atbilstība ar dažiem kompromisiem." if top_score >= 50
           else "Apsver papildināt profilu vai pielāgot filtrus."}
        </div>
      </div>
    </div>
    """)

    for rank_i, result in enumerate(top_results, start=1):
        prog = result["programme"]
        score = result["score"]
        breakdown = result["breakdown"]
        bd_summary = breakdown_summary(breakdown)

        with st.spinner(f"✨ Ģenerē AI paskaidrojumu programmai #{rank_i}…"):
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
    saved = st.session_state.get("saved_programmes", set())
    saved_data = st.session_state.get("saved_programme_data", {})
    if prog_id in saved:
        saved.discard(prog_id)
        saved_data.pop(prog_id, None)
        st.toast("Programma noņemta no saglabātajām.", icon="🗑️")
    else:
        saved.add(prog_id)
        saved_data[prog_id] = programme
        st.toast(f"Saglabāts: **{programme.get('name', prog_id)}**", icon="❤️")
    st.session_state["saved_programmes"] = saved
    st.session_state["saved_programme_data"] = saved_data
    st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
# COMPARE TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_compare_tab():
    saved_data = st.session_state.get("saved_programme_data", {})
    scores = st.session_state.get("last_scores", {})
    saved_list = list(saved_data.values())

    if not saved_list:
        st.html("""
        <div style="text-align:center;padding:48px 24px;color:#94a3b8;">
          <div style="font-size:3.5rem;">⚖️</div>
          <h3 style="color:#64748b;font-weight:700;margin:12px 0 8px 0;">
            Nav saglabātu programmu</h3>
          <p style="max-width:400px;margin:0 auto;font-size:0.9rem;line-height:1.6;">
            Atrod savai personībai atbilstošas programmas cilnē <strong>🔍 Atrast</strong>,
            tad nospied <strong>🤍 Saglabāt</strong> pie katra interesējošā rezultāta.
          </p>
        </div>
        """)
        return

    st.html(
        f'<h3 style="margin:0 0 20px 0;font-size:1.2rem;font-weight:700;color:#0f172a;">'
        f'⚖️ Salīdzinājums — {len(saved_list)} programmas</h3>',
        )
    render_comparison_table(saved_list, scores)


# ─────────────────────────────────────────────────────────────────────────────
# ALL PROGRAMMES TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_all_programmes_tab(programmes: list[dict]):
    col_title, col_search = st.columns([2, 3])
    with col_title:
        st.html(
            '<h3 style="margin:0 0 4px 0;font-size:1.1rem;font-weight:700;color:#0f172a;">'
            '📋 Visas RTU Programmas</h3>',
            )
    with col_search:
        search = st.text_input(
            "Meklēt",
            placeholder="🔍  Meklēt pēc nosaukuma, fakultātes, atslēgvārdiem…",
            key="search_bar", label_visibility="collapsed",
        )

    filtered = programmes
    if search:
        sl = search.lower()
        filtered = [
            p for p in programmes if (
                sl in (p.get("name") or "").lower()
                or sl in (p.get("name_en") or "").lower()
                or sl in (p.get("description") or "").lower()
                or sl in (p.get("faculty") or "").lower()
                or any(sl in kw.lower() for kw in p.get("keywords", []))
            )
        ]

    scores = st.session_state.get("last_scores", {})

    col_info, col_sort = st.columns([3, 2])
    with col_info:
        st.caption(f"Rāda **{len(filtered)}** no {len(programmes)} programmām"
                   + (f" · kārtots pēc Tavas atbilstības" if scores else ""))
    with col_sort:
        sort_by = st.selectbox(
            "Kārtot pēc:",
            ["Atbilstība %", "Nosaukums A–Z", "Gada maksa ↑", "Budžeta vietas ↓"],
            key="sort_by", label_visibility="collapsed",
        )

    if sort_by == "Atbilstība %" and scores:
        filtered = sorted(filtered, key=lambda p: scores.get(p.get("id", ""), 0), reverse=True)
    elif sort_by == "Nosaukums A–Z":
        filtered = sorted(filtered, key=lambda p: p.get("name", ""))
    elif sort_by == "Gada maksa ↑":
        filtered = sorted(filtered, key=lambda p: p.get("annual_fee_eur") or 0)
    elif sort_by == "Budžeta vietas ↓":
        filtered = sorted(filtered, key=lambda p: p.get("budget_places", 0), reverse=True)

    render_programme_table(filtered, scores if scores else None)


# ─────────────────────────────────────────────────────────────────────────────
# ABOUT TAB
# ─────────────────────────────────────────────────────────────────────────────

def render_about_tab():
    col1, col2 = st.columns([3, 2])
    with col1:
        st.markdown("""
## ℹ️ Par šo rīku

**RTU Studiju Programmu AI Ieteicējs** palīdz vidusskolas skolēniem izvēlēties
piemērotākās RTU bakalaura studiju programmas, pamatojoties uz personīgo profilu.

---

### 🏗️ Kā tas strādā?

**1. Profila aizpildīšana**
Norādi savas intereses, stiprās puses, personības tipu un preferences.

**2. Svērtā vērtēšana (13 faktori)**
Katra programma saņem punktus par atbilstību Tavam profilam:

| Faktors | Svars | Sods |
|---|---|---|
| Interešu jomas | +4/sakritību | — |
| Stiprās puses | +3/sakritību | — |
| Personība | +2/sakritību | — |
| Nozares | +3/sakritību | — |
| Studiju valoda | +2 | −20% (nav pieejama) |
| Grūtības pakāpe | +2 | −10% (par grūtu) |
| Matemātika | +2 | −8% (nemīl, bet intensīva) |
| Iestājpārbaudījums | +2 | −15% (neatbilst) |
| Pētnieciskā, Starptautisks, Radošais, Komandas darbs | +1–2 | — |

**3. AI Paskaidrojums (Gemini 2.5 Flash)**
Personalizēts paskaidrojums katrai top-3 programmai, pamatojoties uz Tavu profilu.

---

### ⚠️ Ierobežojumi
- Ieteikumi ir orientējoši — galīgo izvēli veic Students
- Dati balstīti uz 2026. gada RTU programmu aprakstiem
- Vienmēr pārbaudi aktuālo info: [rtu.lv](https://www.rtu.lv)
        """)
    with col2:
        st.markdown("""
### 🚀 Ātrā palaišana

```bash
pip install -r requirements.txt
streamlit run app.py
```

### 📁 Struktūra
```
rtu-study-recommender/
├── app.py           ← Galvenā UI
├── data_loader.py   ← JSON ielāde
├── scoring.py       ← Vērtēšana
├── ai_explanations.py ← Gemini AI
├── ui_components.py ← UI bloki
├── utils.py         ← Taksonomija
└── datasets/        ← 64 programmas
```

### 🔮 Nākotnes plāni
- [ ] PDF eksports
- [ ] CE eksāmena prasību integrācija
- [ ] RTU live API
- [ ] Pilns EN/LV UI
- [ ] Lietotāju profili
        """)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    _init_session()
    programmes, stats, taxonomy = _load_data()

    if not programmes:
        st.error("❌ Nav atrasta neviena programma! Pārliecinies, ka `datasets/` mapē ir RTU JSON datnes.")
        st.stop()

    render_hero(stats, len(programmes))
    filters = render_sidebar(programmes, taxonomy)

    tab_search, tab_compare, tab_all, tab_about = st.tabs([
        "🔍  Atrast Programmu",
        "⚖️  Salīdzināt",
        "📋  Visas Programmas",
        "ℹ️  Par Rīku",
    ])

    with tab_search:
        st.html("<div style='height:4px'></div>")
        profile = render_student_form(programmes, taxonomy)

        if profile:
            st.session_state["student_profile"] = profile
            st.session_state["search_done"] = True

        if st.session_state.get("search_done") and st.session_state.get("student_profile"):
            st.markdown("---")
            st.html("""
            <h2 style="margin:0 0 4px 0;font-size:1.4rem;font-weight:800;
                       color:#0f172a;letter-spacing:-0.02em;">
              🏆 Tavai personībai atbilstošākās programmas
            </h2>
            <p style="margin:0 0 20px 0;color:#64748b;font-size:0.875rem;">
              Trīs labākās atbilstības ar detalizētu AI analīzi
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
