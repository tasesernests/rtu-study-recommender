"""
RTU Study Programme AI Recommender
ai_explanations.py — Gemini AI explanation generator with local fallback.

Uses Google's Gemini API (google-genai SDK, free tier) to produce
personalised programme explanations.  If the API is unavailable a
high-quality local explanation is generated instead.
"""

import logging
import os
from typing import Optional

logger = logging.getLogger("ai_explanations")

# ── Lazy-import the new google-genai SDK ─────────────────────────────────────
try:
    from google import genai
    from google.genai import types as genai_types
    _GENAI_AVAILABLE = True
except ImportError:
    _GENAI_AVAILABLE = False
    logger.warning("google-genai not installed — AI explanations disabled.")

_client: Optional[object] = None
_api_key_loaded = False
_MODEL = "gemini-2.5-flash"   # best free-tier model as of 2026-05


def _init_genai() -> bool:
    """Initialise Gemini client (once). Returns True if ready."""
    global _client, _api_key_loaded
    if _api_key_loaded:
        return _client is not None
    _api_key_loaded = True

    if not _GENAI_AVAILABLE:
        return False

    # Check env var first, then Streamlit secrets (for cloud deployment)
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        try:
            import streamlit as st
            api_key = st.secrets.get("GEMINI_API_KEY", "")
        except Exception:
            pass
    if not api_key:
        logger.warning("GEMINI_API_KEY not set — using local fallback explanations.")
        return False

    try:
        _client = genai.Client(api_key=api_key)
        logger.info(f"Gemini client initialised — model: {_MODEL}")
        return True
    except Exception as e:
        logger.warning(f"Failed to initialise Gemini client: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
# PUBLIC API
# ─────────────────────────────────────────────────────────────────────────────

def generate_ai_explanation(
    student_profile: dict,
    programme: dict,
    scoring_breakdown: dict,
    language: str = "lv",
) -> tuple[str, bool]:
    """
    Generate an AI explanation for why this programme fits the student.

    Args:
        student_profile:   Student form data dict
        programme:         Normalised programme dict
        scoring_breakdown: Full breakdown from scoring.py
        language:          "lv" (Latvian) or "en" (English output)

    Returns:
        (explanation_text, is_ai_generated)
        - explanation_text: Formatted markdown string
        - is_ai_generated:  True if Gemini was used, False if local fallback
    """
    if _init_genai() and _client is not None:
        try:
            text = _call_gemini(student_profile, programme, scoring_breakdown, language)
            if text and len(text.strip()) > 50:
                return text.strip(), True
        except Exception as e:
            logger.warning(f"Gemini call failed for {programme.get('id')}: {e}")

    # Local fallback — always works, no API required
    return _local_explanation(student_profile, programme, scoring_breakdown), False


# ─────────────────────────────────────────────────────────────────────────────
# GEMINI PROMPT BUILDER
# ─────────────────────────────────────────────────────────────────────────────

def _call_gemini(
    student: dict, programme: dict, breakdown: dict, language: str
) -> Optional[str]:
    """Build a grounded prompt and call the Gemini API (new SDK)."""
    m = programme.get("matching", {}) or {}
    career = programme.get("career", {}) or {}

    # ── Compact programme fact sheet ──────────────────────────────────────────
    fact_sheet = f"""
PROGRAMME DATA (use ONLY this data — do NOT invent facts):
Name: {programme.get('name', 'N/A')}
English name: {programme.get('name_en', 'N/A')}
Faculty: {programme.get('faculty', 'N/A')}
Type: {programme.get('program_type', 'N/A')}
Duration: {programme.get('duration_years', 'N/A')} years
Languages: {', '.join(programme.get('languages', []))}
Locations: {', '.join(programme.get('locations', ['Rīga']))}
Budget places: {programme.get('budget_places', 0)}
Annual fee: €{programme.get('annual_fee_eur', 'N/A')}
Entry exam required: {programme.get('entry_exam', False)}
Description: {(programme.get('description', '') or '')[:400]}
Career roles: {', '.join((career.get('job_titles') or [])[:5])}
Career description: {(career.get('description', '') or '')[:200]}
Math intensive: {m.get('math_intensive', False)}
Research oriented: {m.get('research_oriented', False)}
International potential: {m.get('international_potential', False)}
Creative component: {m.get('creative_component', False)}
Difficulty: {m.get('difficulty_level', 'medium')}
""".strip()

    # ── Student profile summary ───────────────────────────────────────────────
    student_summary = f"""
STUDENT PROFILE:
Interests: {', '.join(student.get('interests', []))}
Strengths: {', '.join(student.get('strengths', []))}
Personality: {', '.join(student.get('personality', []))}
Preferred sectors: {', '.join(student.get('sectors', []))}
Preferred language: {student.get('preferred_language', 'lv')}
Likes math: {student.get('math_friendly', False)}
Wants research: {student.get('research_oriented', False)}
Wants international: {student.get('international', False)}
Likes creative work: {student.get('creative', False)}
Career interests: {student.get('career_text', '')}
""".strip()

    score_pct = breakdown.get("final_pct", 0)
    matched_interests = breakdown.get("interests", {}).get("matched", [])
    matched_strengths = breakdown.get("strengths", {}).get("matched", [])
    penalties = breakdown.get("penalties", [])

    lang_instruction = (
        "Write the explanation in English."
        if language == "en"
        else "Write the explanation in Latvian (use natural, friendly Latvian)."
    )

    prompt = f"""You are an RTU (Riga Technical University) admissions advisor.
Your task: Write a personalised programme recommendation explanation for a high-school student.

{lang_instruction}

STRICT RULES — NEVER BREAK THESE:
1. Use ONLY the programme data provided below. Do NOT invent study courses, fees, or facts.
2. Do NOT mention RTU programmes that are not in the data provided.
3. If information is missing, say "information not available" — do not guess.
4. Be encouraging but honest about challenges.
5. Keep the response under 380 words total.
6. Use clean Markdown: ### for section headers, bullet points (- item) for lists, **bold** for key terms.

{fact_sheet}

{student_summary}

SCORING SUMMARY:
Overall compatibility: {score_pct:.0f}%
Matched interests: {', '.join(matched_interests) if matched_interests else 'none'}
Matched strengths: {', '.join(matched_strengths) if matched_strengths else 'none'}
Warnings: {', '.join(penalties) if penalties else 'none'}

Use EXACTLY these 5 Markdown sections (### header + 2-4 sentences or a short bullet list each):

### 🎯 Kāpēc šī programma der tev
### 💪 Tavās stiprajās pusēs, kas palīdz
### ⚡ Iespējamie izaicinājumi
### 📚 Ko uzlabot pirms iestāšanās
### 💼 Karjeras iespējas
(list job titles from the data ONLY; if none — say so)
"""

    response = _client.models.generate_content(
        model=_MODEL,
        contents=prompt,
        config=genai_types.GenerateContentConfig(
            temperature=0.4,
            max_output_tokens=2000,
            top_p=0.9,
            # Disable thinking tokens — explanation task doesn't need deep reasoning
            # and thinking consumes the output budget on gemini-2.5-flash
            thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
        ),
    )
    return response.text


# ─────────────────────────────────────────────────────────────────────────────
# LOCAL FALLBACK EXPLANATION GENERATOR
# ─────────────────────────────────────────────────────────────────────────────

def _local_explanation(student: dict, programme: dict, breakdown: dict) -> str:
    """
    Generate a structured local explanation without the AI API.
    Produces clean, readable Markdown using ### headers and bullet lists.
    """
    m      = programme.get("matching", {}) or {}
    career = programme.get("career", {}) or {}
    score  = breakdown.get("final_pct", 0)

    name    = programme.get("name", "šī programma")
    faculty = programme.get("faculty", "RTU")

    matched_interests = breakdown.get("interests", {}).get("matched", [])
    matched_strengths = breakdown.get("strengths", {}).get("matched", [])
    penalties         = breakdown.get("penalties", [])
    job_titles        = (career.get("job_titles") or [])[:5]

    # ── Section 1: Why it fits ────────────────────────────────────────────────
    if matched_interests:
        from utils import get_label, INTEREST_DOMAINS
        interest_labels = [get_label(INTEREST_DOMAINS, k) for k in matched_interests[:3]]
        sec1 = (
            f"Tava interese par **{', '.join(interest_labels)}** tieši sakrīt ar "
            f"**{name}** mācību saturu. "
            f"Programma ({faculty}) nodrošina augsta līmeņa izglītību šajā jomā, "
            f"kas kopā ar tavu profilu dod **{score:.0f}% atbilstību**."
        )
    else:
        sec1 = (
            f"**{name}** var atbilst taviem karjeras mērķiem, lai gan tiešas interešu "
            f"sakritības netika konstatētas. Atbilstība pašlaik ir **{score:.0f}%** — "
            f"papildini profilu, lai iegūtu precīzāku novērtējumu."
        )

    # ── Section 2: Strengths ──────────────────────────────────────────────────
    if matched_strengths:
        from utils import get_label, STRENGTH_TAGS
        s_labels = [get_label(STRENGTH_TAGS, k) for k in matched_strengths[:3]]
        sec2_items = [f"- **{lbl}** atbilst programmas prasībām" for lbl in s_labels]
        sec2 = "\n".join(sec2_items)
    else:
        sec2 = (
            "- Tiešu sakritību starp stiprajām pusēm un programmas prasībām nav konstatēts\n"
            "- Nepieciešamās prasmes var apgūt studiju laikā — tas nav šķērslis iestājam"
        )

    # ── Section 3: Challenges ─────────────────────────────────────────────────
    ch = []
    if m.get("math_intensive") and not student.get("math_friendly"):
        ch.append("- **Matemātika** ir intensīva — var būt izaicinājums")
    if programme.get("entry_exam") and not student.get("exam_ok", True):
        ch.append("- Nepieciešams **iestājpārbaudījums** — svarīgi sagatavoties laicīgi")
    if m.get("difficulty_level") in ("high", "medium_high"):
        ch.append("- Programma ir **pieprasīta** — nepieciešama augsta motivācija")
    if not matched_interests:
        ch.append("- Interešu atbilstība ir **daļēja** — vēlams pārskatīt profilu")
    sec3 = "\n".join(ch) if ch else "- Nav nopietnu izaicinājumu — tavs profils labi atbilst programmai ✅"

    # ── Section 4: What to improve ────────────────────────────────────────────
    imp = []
    if m.get("math_intensive") and not student.get("math_friendly"):
        imp.append("- Nostiprināt **matemātikas** zināšanas (algebra, analīze)")
    if programme.get("entry_exam"):
        imp.append("- Sagatavoties **iestājpārbaudījumam** savlaicīgi")
    lang_ok = breakdown.get("language", {}).get("match", True)
    if not lang_ok:
        pref = student.get("preferred_language", "lv")
        imp.append(f"- Uzlabot **{'angļu' if pref == 'en' else 'latviešu'} valodas** prasmes")
    if not imp:
        imp = [
            "- Turpināt attīstīt esošās stiprās puses",
            "- Iepazīties ar nozares jaunumiem un tendencēm",
        ]
    sec4 = "\n".join(imp)

    # ── Section 5: Career ─────────────────────────────────────────────────────
    if job_titles:
        sec5 = "\n".join(f"- {j}" for j in job_titles)
        if career.get("description"):
            sec5 += f"\n\n{career['description'][:180]}"
    else:
        sec5 = career.get("description", "")[:250] or "Plašas iespējas nozares uzņēmumos un organizācijās."

    parts = [
        f"### 🎯 Kāpēc šī programma der tev\n{sec1}",
        f"### 💪 Tavās stiprajās pusēs, kas palīdz\n{sec2}",
        f"### ⚡ Iespējamie izaicinājumi\n{sec3}",
        f"### 📚 Ko uzlabot pirms iestāšanās\n{sec4}",
        f"### 💼 Karjeras iespējas\n{sec5}",
    ]

    footer = (
        "\n\n---\n"
        "*ℹ️ Lokāls paskaidrojums (Gemini API nav aktīva). "
        "Aktivizē GEMINI\\_API\\_KEY pilnīgākam AI paskaidrojumam.*"
    )
    return "\n\n".join(parts) + footer


# ─────────────────────────────────────────────────────────────────────────────
# AI SEMANTIC RERANKING
# ─────────────────────────────────────────────────────────────────────────────

def ai_rerank_programmes(
    student: dict,
    scored_programmes: list[dict],
) -> tuple[list[dict], bool]:
    """
    Optionally rerank top programmes using Gemini based on the student's
    free-text career goal.

    Only active when:
      • student["career_text"] is ≥ 15 characters
      • Gemini API is reachable (GEMINI_API_KEY set)

    Args:
        student:           Student profile dict
        scored_programmes: [{programme, score, breakdown}, ...] sorted desc

    Returns:
        (result_list, was_reranked)
        - result_list:  same items, possibly reordered
        - was_reranked: True when Gemini changed the top-3 order
    """
    career_text = (student.get("career_text") or "").strip()
    if len(career_text) < 15:
        return scored_programmes, False

    if not _init_genai() or _client is None:
        return scored_programmes, False

    # Only send top-10 to keep the prompt small and latency low
    to_rerank = scored_programmes[:10]
    rest      = scored_programmes[10:]

    lines = []
    for i, r in enumerate(to_rerank, 1):
        p    = r["programme"]
        c    = p.get("career", {}) or {}
        jobs = ", ".join((c.get("job_titles") or [])[:4])
        lines.append(
            f'{i}. ID="{p.get("id")}" | '
            f'{p.get("name_en") or p.get("name")} '
            f'({p.get("faculty", "")}) | '
            f'Jobs: {jobs or "—"} | '
            f'Score: {r["score"]:.0f}%'
        )

    prompt = (
        "You are an RTU (Riga Technical University) admissions advisor.\n"
        f'Student career goal: "{career_text}"\n\n'
        "Programmes sorted by algorithmic compatibility score:\n"
        + "\n".join(lines)
        + "\n\nTask: Reorder these programmes so the one whose job roles BEST "
        "match the student's stated career goal comes first.\n"
        "Keep ALL programme IDs — do not drop any.\n"
        "Return ONLY a valid JSON array of IDs in your preferred order. "
        'No explanation. Example: ["CS","EE","ME"]'
    )

    try:
        response = _client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.1,
                max_output_tokens=400,
                thinking_config=genai_types.ThinkingConfig(thinking_budget=0),
            ),
        )
        import json, re
        text  = (response.text or "").strip()
        m     = re.search(r'\[.*?\]', text, re.DOTALL)
        if not m:
            return scored_programmes, False

        ids = json.loads(m.group())
        if not isinstance(ids, list) or len(ids) < 2:
            return scored_programmes, False

        id_map: dict[str, dict] = {r["programme"].get("id"): r for r in to_rerank}
        reranked: list[dict]    = []
        seen: set[str]          = set()
        for pid in ids:
            if pid in id_map and pid not in seen:
                reranked.append(id_map[pid])
                seen.add(pid)
        # Append any programmes the AI dropped (shouldn't happen, defensive)
        for r in to_rerank:
            if r["programme"].get("id") not in seen:
                reranked.append(r)

        reranked += rest

        top3_before = [r["programme"].get("id") for r in scored_programmes[:3]]
        top3_after  = [r["programme"].get("id") for r in reranked[:3]]
        return reranked, top3_before != top3_after

    except Exception as e:
        logger.warning(f"AI reranking failed: {e}")
        return scored_programmes, False
