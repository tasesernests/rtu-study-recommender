"""
RTU Study Programme AI Recommender
scoring.py — Weighted, explainable recommendation engine.

Scoring philosophy:
  - Every student input dimension has a corresponding programme dimension
  - Points are awarded for matches, penalties for incompatibilities
  - Score is normalised to 0–100% based on what the student selected
  - A full scoring_breakdown is returned alongside the score for AI explainability
"""

from typing import Any
from utils import (
    INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS,
    LANG_LABELS, DIFFICULTY_LEVELS,
    get_label, normalize_difficulty,
)

# ─────────────────────────────────────────────────────────────────────────────
# SCORING WEIGHTS
# ─────────────────────────────────────────────────────────────────────────────
W_INTEREST = 4        # per matched interest domain
W_STRENGTH = 3        # per matched strength / subject
W_SKILL = 3           # per matched skill (reuses strength bucket)
W_PERSONALITY = 2     # per matched personality trait
W_SECTOR = 3          # per matched industry sector
W_LANGUAGE = 2        # language available match
W_DIFFICULTY = 2      # difficulty preference match
W_RESEARCH = 2        # research-orientation match
W_INTERNATIONAL = 2   # international opportunity match
W_CREATIVE = 2        # creative component match
W_MATH = 2            # math-intensity match
W_EXAM = 2            # entrance exam compatibility
W_TEAMWORK = 1        # teamwork preference match

# Penalties (applied after normalisation, as percentage-point deductions)
P_LANGUAGE = 20       # preferred language not offered (large — deal-breaker)
P_EXAM = 15           # student avoids exams but programme requires one
P_DIFFICULTY_HARD = 10  # student wants easy but programme is hard
P_MATH = 8            # student dislikes maths but programme is math-intensive


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SCORING FUNCTION
# ─────────────────────────────────────────────────────────────────────────────

def score_programme(student: dict, programme: dict) -> tuple[float, dict]:
    """
    Calculate compatibility between a student profile and a programme.

    Args:
        student:   Normalised student profile dict (from UI form)
        programme: Normalised programme dict (from data_loader)

    Returns:
        (compatibility_pct, breakdown_dict)
        - compatibility_pct: float 0.0–100.0
        - breakdown_dict: detailed scoring explanation for display + AI prompt
    """
    m = programme.get("matching", {}) or {}
    breakdown: dict[str, Any] = {}
    raw_score = 0
    max_positive = 0

    # ── 1. INTEREST DOMAINS ──────────────────────────────────────────────────
    s_interests = set(student.get("interests", []))
    p_interests = set(m.get("interest_domains", []))
    matched_interests = s_interests & p_interests
    pts = len(matched_interests) * W_INTEREST
    max_i = len(s_interests) * W_INTEREST
    raw_score += pts
    max_positive += max_i
    breakdown["interests"] = {
        "student": list(s_interests),
        "programme": list(p_interests),
        "matched": list(matched_interests),
        "points": pts,
        "max": max_i,
        "weight": W_INTEREST,
        "label": "Interešu jomas",
    }

    # ── 2. STRENGTHS / SUBJECTS ───────────────────────────────────────────────
    s_strengths = set(student.get("strengths", []))
    p_strengths = set(m.get("required_strengths", []))
    matched_strengths = s_strengths & p_strengths
    pts = len(matched_strengths) * W_STRENGTH
    max_s = len(s_strengths) * W_STRENGTH
    raw_score += pts
    max_positive += max_s
    breakdown["strengths"] = {
        "student": list(s_strengths),
        "programme": list(p_strengths),
        "matched": list(matched_strengths),
        "points": pts,
        "max": max_s,
        "weight": W_STRENGTH,
        "label": "Stiprās puses & Priekšmeti",
    }

    # ── 3. PERSONALITY TRAITS ────────────────────────────────────────────────
    s_personality = set(student.get("personality", []))
    p_personality = set(m.get("personality_fit", []))
    matched_personality = s_personality & p_personality
    pts = len(matched_personality) * W_PERSONALITY
    max_p = len(s_personality) * W_PERSONALITY
    raw_score += pts
    max_positive += max_p
    breakdown["personality"] = {
        "student": list(s_personality),
        "programme": list(p_personality),
        "matched": list(matched_personality),
        "points": pts,
        "max": max_p,
        "weight": W_PERSONALITY,
        "label": "Personības tipa atbilstība",
    }

    # ── 4. INDUSTRY SECTORS ───────────────────────────────────────────────────
    s_sectors = set(student.get("sectors", []))
    p_sectors = set(programme.get("career", {}).get("sectors_canonical", []))
    matched_sectors = s_sectors & p_sectors
    pts = len(matched_sectors) * W_SECTOR
    max_sec = len(s_sectors) * W_SECTOR
    raw_score += pts
    max_positive += max_sec
    breakdown["sectors"] = {
        "student": list(s_sectors),
        "programme": list(p_sectors),
        "matched": list(matched_sectors),
        "points": pts,
        "max": max_sec,
        "weight": W_SECTOR,
        "label": "Nozares preferences",
    }

    # ── 5. LANGUAGE ───────────────────────────────────────────────────────────
    s_lang = student.get("preferred_language", "lv")
    p_langs = set(m.get("language_codes", ["lv"]))
    lang_match = s_lang in p_langs
    breakdown["language"] = {
        "student_pref": s_lang,
        "programme_langs": list(p_langs),
        "match": lang_match,
        "points": W_LANGUAGE if lang_match else 0,
        "max": W_LANGUAGE,
        "weight": W_LANGUAGE,
        "label": "Studiju valoda",
    }
    raw_score += W_LANGUAGE if lang_match else 0
    max_positive += W_LANGUAGE

    # ── 6. DIFFICULTY ──────────────────────────────────────────────────────────
    s_difficulty = student.get("preferred_difficulty", "medium")
    p_difficulty = m.get("difficulty_level", "medium")
    diff_match = _difficulty_compatible(s_difficulty, p_difficulty)
    diff_pts = W_DIFFICULTY if diff_match else 0
    raw_score += diff_pts
    max_positive += W_DIFFICULTY
    breakdown["difficulty"] = {
        "student_pref": s_difficulty,
        "programme": p_difficulty,
        "compatible": diff_match,
        "points": diff_pts,
        "max": W_DIFFICULTY,
        "label": "Grūtības pakāpe",
    }

    # ── 7. RESEARCH ORIENTATION ───────────────────────────────────────────────
    s_research = bool(student.get("research_oriented", False))
    p_research = bool(m.get("research_oriented", False))
    research_match = (s_research == p_research) or (s_research and p_research)
    research_pts = W_RESEARCH if (s_research and p_research) else (W_RESEARCH // 2 if not s_research else 0)
    raw_score += research_pts
    max_positive += W_RESEARCH
    breakdown["research"] = {
        "student": s_research,
        "programme": p_research,
        "points": research_pts,
        "max": W_RESEARCH,
        "label": "Pētnieciskā orientācija",
    }

    # ── 8. INTERNATIONAL ──────────────────────────────────────────────────────
    s_intl = bool(student.get("international", False))
    p_intl = bool(m.get("international_potential", False))
    intl_pts = W_INTERNATIONAL if (s_intl and p_intl) else (W_INTERNATIONAL // 2 if not s_intl else 0)
    raw_score += intl_pts
    max_positive += W_INTERNATIONAL
    breakdown["international"] = {
        "student": s_intl,
        "programme": p_intl,
        "points": intl_pts,
        "max": W_INTERNATIONAL,
        "label": "Starptautiskās iespējas",
    }

    # ── 9. CREATIVE COMPONENT ────────────────────────────────────────────────
    s_creative = bool(student.get("creative", False))
    p_creative = bool(m.get("creative_component", False))
    creative_pts = W_CREATIVE if (s_creative and p_creative) else (W_CREATIVE // 2 if not s_creative else 0)
    raw_score += creative_pts
    max_positive += W_CREATIVE
    breakdown["creative"] = {
        "student": s_creative,
        "programme": p_creative,
        "points": creative_pts,
        "max": W_CREATIVE,
        "label": "Radošā / dizaina komponente",
    }

    # ── 10. MATH INTENSITY ────────────────────────────────────────────────────
    s_math = bool(student.get("math_friendly", False))
    p_math = bool(m.get("math_intensive", False))
    math_pts = W_MATH if (s_math and p_math) else (W_MATH if (not s_math and not p_math) else 0)
    raw_score += math_pts
    max_positive += W_MATH
    breakdown["math"] = {
        "student_likes_math": s_math,
        "programme_math_intensive": p_math,
        "points": math_pts,
        "max": W_MATH,
        "label": "Matemātikas intensitāte",
    }

    # ── 11. ENTRANCE EXAM ─────────────────────────────────────────────────────
    s_exam_ok = bool(student.get("exam_ok", True))
    p_exam_req = bool(m.get("entry_exam_required", False))
    if p_exam_req and s_exam_ok:
        exam_pts = W_EXAM
    elif not p_exam_req:
        exam_pts = W_EXAM
    else:
        exam_pts = 0  # student doesn't want exam, but it's required
    raw_score += exam_pts
    max_positive += W_EXAM
    breakdown["exam"] = {
        "student_ok_with_exam": s_exam_ok,
        "programme_requires_exam": p_exam_req,
        "compatible": exam_pts > 0,
        "points": exam_pts,
        "max": W_EXAM,
        "label": "Iestājpārbaudījums",
    }

    # ── 12. TEAMWORK ─────────────────────────────────────────────────────────
    s_team = student.get("teamwork", "both")
    p_team = bool(m.get("teamwork_oriented", True))
    team_match = s_team in ("team", "both") or not p_team
    team_pts = W_TEAMWORK if team_match else 0
    raw_score += team_pts
    max_positive += W_TEAMWORK
    breakdown["teamwork"] = {
        "student_pref": s_team,
        "programme_teamwork": p_team,
        "points": team_pts,
        "max": W_TEAMWORK,
        "label": "Komandas darbs",
    }

    # ── NORMALISE TO PERCENTAGE ───────────────────────────────────────────────
    if max_positive == 0:
        base_pct = 50.0
    else:
        base_pct = (raw_score / max_positive) * 100.0

    # ── PENALTIES ─────────────────────────────────────────────────────────────
    penalty = 0
    penalties_applied = []

    if not lang_match and s_lang != "any":
        penalty += P_LANGUAGE
        penalties_applied.append(f"Vēlamā valoda ({LANG_LABELS.get(s_lang, s_lang)}) nav pieejama (−{P_LANGUAGE}%)")

    if not s_exam_ok and p_exam_req:
        penalty += P_EXAM
        penalties_applied.append(f"Nepieciešams iestājpārbaudījums (−{P_EXAM}%)")

    if _difficulty_too_hard(s_difficulty, p_difficulty):
        penalty += P_DIFFICULTY_HARD
        penalties_applied.append(f"Programma ir grūtāka nekā vēlams (−{P_DIFFICULTY_HARD}%)")

    if not s_math and p_math:
        penalty += P_MATH
        penalties_applied.append(f"Matemātikas intensīvā programma neatbilst (−{P_MATH}%)")

    breakdown["penalties"] = penalties_applied
    breakdown["raw_score"] = round(raw_score, 2)
    breakdown["max_possible"] = round(max_positive, 2)
    breakdown["base_pct"] = round(base_pct, 1)
    breakdown["penalty_pct"] = penalty

    compatibility = max(0.0, min(100.0, base_pct - penalty))
    breakdown["final_pct"] = round(compatibility, 1)

    return compatibility, breakdown


# ─────────────────────────────────────────────────────────────────────────────
# RANK PROGRAMMES
# ─────────────────────────────────────────────────────────────────────────────

def rank_programmes(
    student: dict,
    programmes: list[dict],
    top_n: int = 3,
    filters: dict | None = None,
) -> list[dict]:
    """
    Score and rank all programmes for a given student profile.

    Args:
        student:    Student profile dict
        programmes: List of normalised programme dicts
        top_n:      Number of top results to return (default 3)
        filters:    Optional dict of UI filters to pre-filter programmes

    Returns:
        List of dicts: [{programme, score, breakdown}, ...] sorted by score desc
    """
    filtered = _apply_filters(programmes, filters or {})

    results = []
    for prog in filtered:
        score, breakdown = score_programme(student, prog)
        results.append({"programme": prog, "score": score, "breakdown": breakdown})

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_n]


def score_all_programmes(
    student: dict,
    programmes: list[dict],
    filters: dict | None = None,
) -> list[dict]:
    """Score ALL programmes (used for full results / comparison view)."""
    return rank_programmes(student, programmes, top_n=len(programmes), filters=filters)


# ─────────────────────────────────────────────────────────────────────────────
# FILTER HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _apply_filters(programmes: list[dict], filters: dict) -> list[dict]:
    """Pre-filter programmes based on sidebar filter selections."""
    result = programmes
    if faculties := filters.get("faculties"):
        result = [p for p in result if p.get("faculty") in faculties]
    if langs := filters.get("languages"):
        result = [
            p for p in result
            if set(p.get("languages", [])) & set(langs)
        ]
    if locations := filters.get("locations"):
        result = [
            p for p in result
            if set(p.get("locations", [])) & set(locations)
        ]
    if prog_types := filters.get("program_types"):
        result = [p for p in result if p.get("program_type") in prog_types]
    if filters.get("no_exam_only"):
        result = [p for p in result if not p.get("matching", {}).get("entry_exam_required", False)]
    if filters.get("budget_only"):
        result = [p for p in result if p.get("budget_places", 0) > 0]
    return result


# ─────────────────────────────────────────────────────────────────────────────
# COMPATIBILITY HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_DIFF_ORDER = {"low": 0, "medium": 1, "medium_high": 2, "high": 3}


def _difficulty_compatible(student_pref: str, programme_level: str) -> bool:
    """True if programme difficulty is within +1 level of student preference."""
    s = _DIFF_ORDER.get(student_pref, 1)
    p = _DIFF_ORDER.get(programme_level, 1)
    return abs(p - s) <= 1


def _difficulty_too_hard(student_pref: str, programme_level: str) -> bool:
    """True if programme is MORE than 1 difficulty tier above student preference."""
    s = _DIFF_ORDER.get(student_pref, 1)
    p = _DIFF_ORDER.get(programme_level, 1)
    return (p - s) > 1


# ─────────────────────────────────────────────────────────────────────────────
# HUMAN-READABLE BREAKDOWN SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def breakdown_summary(breakdown: dict) -> dict:
    """
    Convert raw breakdown dict to human-readable label lists.
    Used by the UI 'Why this score?' section.
    """
    from utils import INTEREST_DOMAINS, STRENGTH_TAGS, PERSONALITY_TRAITS, INDUSTRY_SECTORS

    def _labels(keys: list, mapping: dict) -> list[str]:
        return [get_label(mapping, k) for k in keys if k]

    return {
        "matched_interests": _labels(breakdown.get("interests", {}).get("matched", []), INTEREST_DOMAINS),
        "missed_interests": _labels(
            list(
                set(breakdown.get("interests", {}).get("student", []))
                - set(breakdown.get("interests", {}).get("matched", []))
            ),
            INTEREST_DOMAINS,
        ),
        "matched_strengths": _labels(breakdown.get("strengths", {}).get("matched", []), STRENGTH_TAGS),
        "matched_personality": _labels(breakdown.get("personality", {}).get("matched", []), PERSONALITY_TRAITS),
        "matched_sectors": _labels(breakdown.get("sectors", {}).get("matched", []), INDUSTRY_SECTORS),
        "language_ok": breakdown.get("language", {}).get("match", False),
        "exam_ok": breakdown.get("exam", {}).get("compatible", True),
        "penalties": breakdown.get("penalties", []),
        "final_pct": breakdown.get("final_pct", 0),
        "base_pct": breakdown.get("base_pct", 0),
    }
