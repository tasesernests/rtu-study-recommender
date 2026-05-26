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

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
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
5. Keep the response under 400 words.
6. Format as 5 numbered sections (use markdown **bold** for section headers).

{fact_sheet}

{student_summary}

SCORING SUMMARY:
Overall compatibility: {score_pct:.0f}%
Matched interests: {', '.join(matched_interests) if matched_interests else 'none'}
Matched strengths: {', '.join(matched_strengths) if matched_strengths else 'none'}
Warnings: {', '.join(penalties) if penalties else 'none'}

Write the explanation with exactly these 5 sections:
**1. Kāpēc šī programma der tev** (Why this programme fits you)
**2. Kuras tavās stiprajās pusēs palīdz** (Which of your strengths help)
**3. Iespējamie izaicinājumi** (Possible challenges)
**4. Ko uzlabot pirms iestāšanās** (What to improve before applying)
**5. Karjeras iespējas** (Career opportunities — based ONLY on the provided job titles)
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
    Produces a decent human-readable explanation from the scoring breakdown.
    """
    m = programme.get("matching", {}) or {}
    career = programme.get("career", {}) or {}
    score = breakdown.get("final_pct", 0)

    name = programme.get("name", "šī programma")
    faculty = programme.get("faculty", "RTU")

    matched_interests = breakdown.get("interests", {}).get("matched", [])
    matched_strengths = breakdown.get("strengths", {}).get("matched", [])
    penalties = breakdown.get("penalties", [])
    job_titles = (career.get("job_titles") or [])[:4]

    # Section 1: Why it fits
    if matched_interests:
        from utils import get_label, INTEREST_DOMAINS
        interest_labels = [get_label(INTEREST_DOMAINS, k) for k in matched_interests[:3]]
        why_fits = (
            f"Tava interese par **{', '.join(interest_labels)}** tieši sakrīt ar šīs programmas "
            f"mācību saturu. Programma ir daļa no {faculty}, kas nodrošina augsta līmeņa "
            f"akadēmisko vai profesionālo izglītību šajā jomā."
        )
    else:
        why_fits = (
            f"Programma **{name}** nodrošina plašu zinātniski-tehnisko izglītību, kas var "
            f"atbilst taviem karjeras mērķiem un interesēm."
        )

    # Section 2: Strengths that help
    if matched_strengths:
        from utils import get_label, STRENGTH_TAGS
        strength_labels = [get_label(STRENGTH_TAGS, k) for k in matched_strengths[:3]]
        strengths_text = (
            f"Tavās stiprajās pusēs — **{', '.join(strength_labels)}** — ir tiešs sakars ar "
            f"programmas prasībām. Tas nozīmē, ka studijās tev būs priekšrocība pār citiem "
            f"studentiem, kuri šajās jomās ir vājāki."
        )
    else:
        strengths_text = (
            "Lai gan tiešas sakritības starp tavām stiprajām pusēm un programmas prasībām "
            "nav atrasta, nav iemesla uztraukties — studijās apgūsi nepieciešamās prasmes."
        )

    # Section 3: Challenges
    challenges_parts = []
    if m.get("math_intensive") and not student.get("math_friendly"):
        challenges_parts.append("matemātika ir intensīva, un tas var būt izaicinājums")
    if m.get("entry_exam_required") and not student.get("exam_ok", True):
        challenges_parts.append("nepieciešams iestājpārbaudījums, kuram jāsagatavojas")
    if m.get("difficulty_level") in ("high", "medium_high"):
        challenges_parts.append("programma ir pieprasīta — nepieciešama augsta motivācija un darba spējas")
    if not matched_interests:
        challenges_parts.append("interešu atbilstība ar programmu ir daļēja")

    if challenges_parts:
        challenges_text = "Potenciālie izaicinājumi: " + "; ".join(challenges_parts) + "."
    else:
        challenges_text = "Nopietnu izaicinājumu nav paredzēts — tavs profils labi atbilst programmas prasībām."

    # Section 4: What to improve
    improve_parts = []
    if m.get("math_intensive") and not student.get("math_friendly"):
        improve_parts.append("nostiprināt matemātikas zināšanas (algebru, analīzi)")
    if m.get("entry_exam_required"):
        improve_parts.append("sagatavoties iestājpārbaudījumam laicīgi")
    lang_ok = breakdown.get("language", {}).get("match", True)
    if not lang_ok:
        pref_lang = student.get("preferred_language", "lv")
        improve_parts.append(
            f"uzlabot valodas prasmes ({'angļu' if pref_lang == 'en' else 'latviešu'} valodā)"
        )
    if not improve_parts:
        improve_parts = ["turpināt attīstīt jau esošās stiprās puses", "iepazīties ar nozares jaunumiem"]

    improve_text = "Ieteikumi pirms iestāšanās: " + "; ".join(improve_parts) + "."

    # Section 5: Career
    if job_titles:
        career_text = f"Absolventi parasti strādā kā: **{', '.join(job_titles)}**."
    else:
        career_description = (career.get("description") or "")[:200]
        career_text = career_description or "Plašas karjeras iespējas nozares uzņēmumos un organizācijās."

    parts = [
        f"**1. Kāpēc šī programma der tev** (Atbilstība: {score:.0f}%)\n{why_fits}",
        f"**2. Tavās stiprajās pusēs, kas palīdz**\n{strengths_text}",
        f"**3. Iespējamie izaicinājumi**\n{challenges_text}",
        f"**4. Ko uzlabot pirms iestāšanās**\n{improve_text}",
        f"**5. Karjeras iespējas**\n{career_text}",
    ]

    footer = (
        "\n\n---\n"
        "*ℹ️ Šis paskaidrojums ģenerēts lokāli (AI API nav aktīva). "
        "Aktivizē Gemini API pilnīgākam paskaidrojumam.*"
    )
    return "\n\n".join(parts) + footer
