#!/usr/bin/env python3
"""
manual_enrich.py — Hand-curated canonical enrichment for all 64 RTU programmes.
No API needed. Run:  python manual_enrich.py
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

DATASET_DIR = Path(__file__).parent / "datasets"

# ─────────────────────────────────────────────────────────────────────────────
# ENRICHMENT DATA  — canonical keys matching utils.py
# ─────────────────────────────────────────────────────────────────────────────

ENRICHMENTS: dict[str, dict] = {

    # ══════════════════════════════════════════════════════════════════════════
    # rtu_programs.json  —  20 academic bachelor programmes
    # ══════════════════════════════════════════════════════════════════════════

    "ATSI": {
        "interest_domains": ["transport_aviation", "mechanics_engineering", "robotics_automation"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "technical_thinking", "practical_skills"],
        "personality_fit": ["analytical", "technical", "practical"],
        "keywords": ["aeronautics", "transport engineer", "logistics", "UAV operator", "drone", "aviation technician", "transport systems", "fleet management", "CAD CAM", "aerospace", "air traffic"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "high",
    },
    "BUV_EN": {
        "interest_domains": ["construction_civil", "environment_sustainability"],
        "required_strengths": ["mathematics", "physics", "technical_thinking", "analytical_thinking", "languages"],
        "personality_fit": ["technical", "analytical", "international"],
        "keywords": ["civil engineer", "structural engineer", "construction manager", "infrastructure", "sustainable construction", "BIM", "project manager", "building design", "concrete structures"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "BTBI": {
        "interest_domains": ["chemistry_biotech", "medical_technology", "environment_sustainability"],
        "required_strengths": ["biology", "chemistry", "mathematics", "research", "analytical_thinking"],
        "personality_fit": ["scientific", "analytical", "independent"],
        "keywords": ["biotechnologist", "bioengineering", "lab scientist", "pharmaceutical", "bioreactor", "molecular biology", "biotech startup", "food technology", "genetic engineering", "bioproducts", "fermentation"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "high",
    },
    "MATI": {
        "interest_domains": ["chemistry_biotech", "mechanics_engineering"],
        "required_strengths": ["chemistry", "physics", "mathematics", "research", "practical_skills"],
        "personality_fit": ["scientific", "analytical", "technical"],
        "keywords": ["materials scientist", "materials engineer", "quality control", "nanomaterials", "composite materials", "polymer", "metallurgy", "surface engineering", "3D printing materials", "materials testing"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "high",
    },
    "VIDE": {
        "interest_domains": ["environment_sustainability", "chemistry_biotech", "energy_power"],
        "required_strengths": ["mathematics", "chemistry", "physics", "analytical_thinking", "research"],
        "personality_fit": ["analytical", "sustainability_conscious", "scientific"],
        "keywords": ["environmental engineer", "climate technology", "waste management", "water treatment", "pollution control", "renewable energy", "sustainability consultant", "environmental inspector", "green tech"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "medium_high",
    },
    "KKT": {
        "interest_domains": ["chemistry_biotech", "environment_sustainability"],
        "required_strengths": ["chemistry", "mathematics", "physics", "research", "analytical_thinking", "practical_skills"],
        "personality_fit": ["scientific", "analytical", "practical"],
        "keywords": ["chemical engineer", "process engineer", "quality analyst", "laboratory chemist", "chemical technologist", "pharmaceutical", "polymer", "petrochemical", "industrial chemistry"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "high",
    },
    "DS": {
        "interest_domains": ["it_programming", "software_engineering", "data_science_ai"],
        "required_strengths": ["mathematics", "programming", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["analytical", "technical", "independent"],
        "keywords": ["software developer", "programmer", "computer engineer", "systems analyst", "AI developer", "database engineer", "software testing", "DevOps", "backend developer", "computer science"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "IT": {
        "interest_domains": ["it_programming", "data_science_ai", "software_engineering"],
        "required_strengths": ["mathematics", "programming", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["analytical", "technical", "team_player"],
        "keywords": ["IT consultant", "software developer", "systems analyst", "data analyst", "IT manager", "project manager", "e-business", "enterprise software", "web developer", "IT solutions"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "IRS": {
        "interest_domains": ["robotics_automation", "it_programming", "electronics_telecom"],
        "required_strengths": ["mathematics", "physics", "programming", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["analytical", "technical", "team_player", "scientific"],
        "keywords": ["robotics engineer", "automation engineer", "AI programmer", "robot developer", "embedded systems", "control systems", "industrial automation", "machine learning", "mechatronics", "computer vision"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "high",
    },
    "TTDP": {
        "interest_domains": ["electronics_telecom", "it_programming"],
        "required_strengths": ["mathematics", "physics", "programming", "analytical_thinking"],
        "personality_fit": ["technical", "analytical", "international"],
        "keywords": ["telecom engineer", "network engineer", "wireless engineer", "data transmission", "signal processing", "5G networks", "IoT", "cybersecurity", "network administrator", "radio frequency"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "VDT": {
        "interest_domains": ["it_programming", "robotics_automation", "data_science_ai"],
        "required_strengths": ["mathematics", "programming", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["analytical", "technical", "creative"],
        "keywords": ["computer vision engineer", "3D graphics specialist", "IoT developer", "automation specialist", "image processing", "machine learning", "AR VR developer", "smart systems", "industrial IoT"],
        "math_intensive": True, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "RIND": {
        "interest_domains": ["art_design", "business_management", "education_research"],
        "required_strengths": ["creativity", "communication", "languages", "leadership"],
        "personality_fit": ["creative", "entrepreneurial", "social"],
        "keywords": ["creative industries manager", "cultural entrepreneur", "startup founder", "media production", "cultural organization", "event organizer", "marketing creative", "arts management", "content creator"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ARH": {
        "interest_domains": ["architecture", "art_design", "construction_civil"],
        "required_strengths": ["drawing_design", "creativity", "mathematics", "physics", "analytical_thinking"],
        "personality_fit": ["creative", "technical", "analytical"],
        "keywords": ["architect", "architectural designer", "urban planner", "CAD designer", "BIM specialist", "interior design", "structural design", "architectural visualization", "building design", "city planning"],
        "math_intensive": True, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": False, "difficulty_level": "high",
    },
    # Remaining 7 academic programmes
    "DZOT": {
        "interest_domains": ["it_programming", "data_science_ai", "business_management"],
        "required_strengths": ["mathematics", "programming", "analytical_thinking", "languages", "leadership"],
        "personality_fit": ["analytical", "technical", "entrepreneurial"],
        "keywords": ["IT manager", "information systems", "cybersecurity analyst", "system administrator", "network security", "data systems manager", "digital transformation", "IT governance"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "VSU": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["languages", "communication", "leadership", "analytical_thinking", "economics_finance"],
        "personality_fit": ["entrepreneurial", "international", "social"],
        "keywords": ["international business manager", "project manager", "marketing manager", "financial analyst", "business development", "export manager", "global business", "trade specialist"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "EVKS": {
        "interest_domains": ["education_research", "business_management"],
        "required_strengths": ["languages", "communication", "research", "analytical_thinking"],
        "personality_fit": ["analytical", "international", "social"],
        "keywords": ["translator", "interpreter", "language specialist", "teacher", "cultural studies", "European languages", "linguistics", "communication specialist", "foreign language teacher"],
        "math_intensive": False, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "medium",
    },
    "JMMD": {
        "interest_domains": ["art_design", "it_programming"],
        "required_strengths": ["creativity", "drawing_design", "programming", "analytical_thinking"],
        "personality_fit": ["creative", "technical", "analytical"],
        "keywords": ["media artist", "graphic designer", "web designer", "VR AR developer", "digital art", "motion graphics", "UI UX designer", "multimedia", "game designer", "visual artist"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ITMM": {
        "interest_domains": ["mechanics_engineering", "robotics_automation", "transport_aviation"],
        "required_strengths": ["mathematics", "physics", "technical_thinking", "analytical_thinking", "practical_skills"],
        "personality_fit": ["analytical", "technical", "practical"],
        "keywords": ["mechanical engineer", "machine engineer", "manufacturing engineer", "robotics engineer", "mechatronics", "CAD designer", "industrial engineering", "product design", "metal processing"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # rtu_bmf_programs.json  —  11 professional bachelor programmes
    # ══════════════════════════════════════════════════════════════════════════

    "ATI": {
        "interest_domains": ["transport_aviation", "mechanics_engineering"],
        "required_strengths": ["mathematics", "physics", "technical_thinking", "practical_skills", "analytical_thinking"],
        "personality_fit": ["technical", "practical", "analytical"],
        "keywords": ["automotive engineer", "vehicle technician", "transport engineer", "fleet manager", "car mechanic", "automobile design", "transport systems", "vehicle inspection", "powertrain", "chassis"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "AVT": {
        "interest_domains": ["transport_aviation", "mechanics_engineering", "electronics_telecom"],
        "required_strengths": ["mathematics", "physics", "technical_thinking", "practical_skills"],
        "personality_fit": ["technical", "practical", "precise"],
        "keywords": ["aviation technician", "aircraft maintenance engineer", "avionics specialist", "aeronautics", "flight engineer", "aircraft inspector", "aerospace maintenance", "aviation safety", "helicopter technician"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "high",
    },
    "BUV_PRO": {
        "interest_domains": ["construction_civil", "architecture"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "practical_skills", "technical_thinking"],
        "personality_fit": ["technical", "practical", "precise"],
        "keywords": ["civil engineer", "construction engineer", "building engineer", "project manager", "structural engineer", "construction site manager", "building regulations", "infrastructure", "BIM"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "IND": {
        "interest_domains": ["art_design", "mechanics_engineering"],
        "required_strengths": ["creativity", "drawing_design", "technical_thinking", "mathematics", "practical_skills"],
        "personality_fit": ["creative", "technical", "practical"],
        "keywords": ["industrial designer", "product designer", "design consultant", "prototype developer", "ergonomic design", "CAD designer", "manufacturing design", "3D modelling", "product development"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "MAB": {
        "interest_domains": ["mechanics_engineering", "robotics_automation"],
        "required_strengths": ["mathematics", "physics", "technical_thinking", "practical_skills", "analytical_thinking"],
        "personality_fit": ["technical", "practical", "precise"],
        "keywords": ["mechanical engineer", "machine engineer", "apparatus engineer", "manufacturing engineer", "factory equipment", "industrial machinery", "production engineer", "CAD modelling", "mechanical design"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "MIF": {
        "interest_domains": ["medical_technology", "electronics_telecom", "data_science_ai"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "practical_skills", "technical_thinking"],
        "personality_fit": ["scientific", "analytical", "precise"],
        "keywords": ["medical physicist", "biomedical engineer", "medical device engineer", "radiation safety", "medical equipment", "healthcare technology", "hospital technician", "medical imaging", "dosimetry"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "high",
    },
    "MEH": {
        "interest_domains": ["robotics_automation", "electronics_telecom", "mechanics_engineering"],
        "required_strengths": ["mathematics", "physics", "programming", "practical_skills", "technical_thinking"],
        "personality_fit": ["technical", "practical", "analytical"],
        "keywords": ["mechatronics engineer", "automation engineer", "robotics specialist", "industrial automation", "PLC programmer", "control systems", "embedded systems", "machine design", "servo drives"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "SGU": {
        "interest_domains": ["energy_power", "construction_civil", "environment_sustainability"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "practical_skills", "technical_thinking"],
        "personality_fit": ["technical", "practical", "analytical"],
        "keywords": ["HVAC engineer", "heating engineer", "plumbing engineer", "water supply engineer", "gas systems engineer", "building services", "energy efficiency", "district heating", "sustainable building"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "SET": {
        "interest_domains": ["energy_power", "mechanics_engineering"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "technical_thinking", "practical_skills"],
        "personality_fit": ["technical", "analytical", "practical"],
        "keywords": ["thermal engineer", "heat engineer", "energy engineer", "boiler engineer", "power plant engineer", "district heating", "steam technology", "energy efficiency", "thermal systems"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "TRB": {
        "interest_domains": ["construction_civil", "transport_aviation"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "technical_thinking", "practical_skills"],
        "personality_fit": ["technical", "analytical", "practical"],
        "keywords": ["transport structures engineer", "road engineer", "bridge engineer", "infrastructure engineer", "highway designer", "railway engineer", "structural engineer", "tunnel engineer", "road construction"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "GEO": {
        "interest_domains": ["construction_civil", "environment_sustainability"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "practical_skills", "technical_thinking"],
        "personality_fit": ["analytical", "technical", "practical"],
        "keywords": ["geodesist", "cartographer", "land surveyor", "GIS specialist", "geomatics engineer", "land registry", "cadastre", "spatial data", "remote sensing", "photogrammetry", "topography"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": False, "difficulty_level": "medium",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # rtu_programs_DITEF_IVF_prof.json  —  15 DITEF/IVF professional programmes
    # ══════════════════════════════════════════════════════════════════════════

    "ECV": {
        "interest_domains": ["electronics_telecom", "it_programming", "robotics_automation"],
        "required_strengths": ["mathematics", "physics", "programming", "technical_thinking", "analytical_thinking"],
        "personality_fit": ["technical", "analytical", "precise"],
        "keywords": ["electronics engineer", "embedded systems developer", "wireless engineer", "IoT engineer", "mobile app developer", "smart electronics", "circuit design", "firmware developer", "PCB design"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "ECR": {
        "interest_domains": ["energy_power", "electronics_telecom"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "technical_thinking", "practical_skills"],
        "personality_fit": ["technical", "analytical", "sustainability_conscious"],
        "keywords": ["power engineer", "smart grid engineer", "energy systems engineer", "electrical engineer", "renewable energy", "energy efficiency", "smart meters", "electricity networks", "EV charging", "solar power"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "ECS": {
        "interest_domains": ["electronics_telecom", "transport_aviation", "it_programming"],
        "required_strengths": ["mathematics", "physics", "programming", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["technical", "analytical", "precise"],
        "keywords": ["telematics engineer", "transport electronics engineer", "navigation systems", "vehicle electronics", "autonomous vehicles", "GPS systems", "fleet tracking", "transport IT", "ADAS systems"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "HCF": {
        "interest_domains": ["education_research", "business_management"],
        "required_strengths": ["languages", "communication", "analytical_thinking", "research"],
        "personality_fit": ["analytical", "international", "precise"],
        "keywords": ["technical translator", "interpreter", "conference interpreter", "audiovisual translator", "technical writer", "localization specialist", "language technology", "content creator", "subtitling"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": False, "difficulty_level": "medium",
    },
    "DCP": {
        "interest_domains": ["it_programming", "business_management", "data_science_ai"],
        "required_strengths": ["mathematics", "programming", "analytical_thinking", "economics_finance"],
        "personality_fit": ["analytical", "technical", "precise"],
        "keywords": ["fintech developer", "financial systems programmer", "banking IT", "financial analyst", "software engineer finance", "payment systems", "ERP developer", "accounting software", "financial data"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "DCM": {
        "interest_domains": ["data_science_ai", "business_management"],
        "required_strengths": ["mathematics", "analytical_thinking", "economics_finance", "research"],
        "personality_fit": ["analytical", "precise", "scientific"],
        "keywords": ["actuary", "financial engineer", "risk analyst", "quantitative analyst", "credit risk", "insurance analyst", "financial modeller", "statistics", "data scientist finance", "derivative pricing"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "high",
    },
    "ECO": {
        "interest_domains": ["energy_power", "robotics_automation", "electronics_telecom"],
        "required_strengths": ["mathematics", "physics", "analytical_thinking", "technical_thinking", "practical_skills"],
        "personality_fit": ["technical", "analytical", "practical"],
        "keywords": ["electrotechnology engineer", "power electronics engineer", "industrial electronics", "automation engineer", "electric drives", "frequency converters", "energy management", "EV technology", "welding technology"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "ICO": {
        "interest_domains": ["environment_sustainability", "education_research"],
        "required_strengths": ["chemistry", "physics", "analytical_thinking", "practical_skills"],
        "personality_fit": ["analytical", "practical", "precise"],
        "keywords": ["safety engineer", "occupational safety", "fire safety specialist", "civil protection", "risk manager", "work safety inspector", "emergency planning", "hazard assessment", "labour inspection"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ECA": {
        "interest_domains": ["robotics_automation", "electronics_telecom", "medical_technology"],
        "required_strengths": ["mathematics", "physics", "programming", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["scientific", "technical", "analytical"],
        "keywords": ["adaptronic engineer", "smart materials engineer", "biomedical engineer", "medical devices", "rehabilitation technology", "adaptive systems", "industrial automation", "smart actuators", "piezoelectric"],
        "math_intensive": True, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "high",
    },
    "ICM": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["analytical_thinking", "communication", "economics_finance", "social_sciences"],
        "personality_fit": ["analytical", "precise", "entrepreneurial"],
        "keywords": ["customs administrator", "tax administrator", "customs broker", "trade compliance", "state revenue officer", "border administration", "import export", "tax economist", "VAT specialist"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ICN": {
        "interest_domains": ["construction_civil", "business_management"],
        "required_strengths": ["mathematics", "economics_finance", "analytical_thinking", "communication"],
        "personality_fit": ["analytical", "entrepreneurial", "practical"],
        "keywords": ["real estate manager", "property valuator", "real estate economist", "property portfolio manager", "facilities manager", "construction economics", "real estate investment", "building management"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ICH": {
        "interest_domains": ["construction_civil", "environment_sustainability", "business_management"],
        "required_strengths": ["mathematics", "analytical_thinking", "economics_finance", "research"],
        "personality_fit": ["analytical", "sustainability_conscious", "entrepreneurial"],
        "keywords": ["urban planner", "regional development specialist", "city planner", "infrastructure planner", "spatial planning", "EU funds specialist", "economic development", "municipal manager", "territorial planning"],
        "math_intensive": False, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ICU": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["communication", "leadership", "economics_finance", "analytical_thinking"],
        "personality_fit": ["entrepreneurial", "social", "team_player"],
        "keywords": ["business manager", "entrepreneur", "HR manager", "marketing manager", "financial director", "startup founder", "operations manager", "business consultant", "SME owner"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ICL": {
        "interest_domains": ["transport_aviation", "business_management"],
        "required_strengths": ["mathematics", "economics_finance", "analytical_thinking", "practical_skills"],
        "personality_fit": ["analytical", "practical", "entrepreneurial"],
        "keywords": ["logistics manager", "supply chain manager", "transport economist", "warehouse manager", "freight manager", "customs logistics", "procurement specialist", "fleet coordinator", "distribution manager"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ICK": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["mathematics", "analytical_thinking", "economics_finance", "technical_thinking"],
        "personality_fit": ["analytical", "precise", "technical"],
        "keywords": ["quality manager", "process engineer", "compliance specialist", "ISO auditor", "quality systems", "risk manager", "six sigma", "lean manufacturing", "operations quality", "TQM"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },

    # ══════════════════════════════════════════════════════════════════════════
    # rtu_programs_rezekne_liepaja_jura.json  —  18 regional programmes
    # ══════════════════════════════════════════════════════════════════════════

    "JCD": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["communication", "leadership", "economics_finance", "analytical_thinking"],
        "personality_fit": ["entrepreneurial", "social", "team_player"],
        "keywords": ["entrepreneur", "business manager", "tourism manager", "hospitality manager", "marketing specialist", "small business owner", "restaurant manager", "hotel manager", "catering"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "ICE": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["mathematics", "economics_finance", "analytical_thinking", "research"],
        "personality_fit": ["analytical", "precise", "entrepreneurial"],
        "keywords": ["economist", "financial analyst", "accountant", "project manager", "budget planner", "tax specialist", "statistics analyst", "public sector economist", "macroeconomics"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": False, "difficulty_level": "medium",
    },
    "DCZ": {
        "interest_domains": ["software_engineering", "it_programming", "data_science_ai"],
        "required_strengths": ["programming", "mathematics", "analytical_thinking", "technical_thinking"],
        "personality_fit": ["analytical", "technical", "independent"],
        "keywords": ["software engineer", "programmer", "web developer", "database developer", "mobile developer", "AI developer", "software tester", "IT project manager", "backend developer", "full stack"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "MCE": {
        "interest_domains": ["robotics_automation", "mechanics_engineering", "electronics_telecom"],
        "required_strengths": ["mathematics", "physics", "technical_thinking", "practical_skills", "programming"],
        "personality_fit": ["technical", "practical", "analytical"],
        "keywords": ["mechatronics engineer", "robotics engineer", "CNC programmer", "automation engineer", "industrial robot", "machine design", "manufacturing engineer", "PLC programmer", "servo systems"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "WCU": {
        "interest_domains": ["art_design", "architecture"],
        "required_strengths": ["creativity", "drawing_design", "practical_skills", "analytical_thinking"],
        "personality_fit": ["creative", "practical", "precise"],
        "keywords": ["designer", "interior designer", "fashion designer", "textile designer", "product designer", "industrial design", "3D modelling", "visual design", "pattern design", "furniture design"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "WCH": {
        "interest_domains": ["art_design", "chemistry_biotech"],
        "required_strengths": ["creativity", "drawing_design", "practical_skills", "chemistry"],
        "personality_fit": ["creative", "practical", "precise"],
        "keywords": ["materials designer", "textile designer", "fashion designer", "wood technology", "metal craft", "interior designer", "product designer", "materials technology", "design engineer", "craft"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "JCR": {
        "interest_domains": ["education_research", "transport_aviation"],
        "required_strengths": ["analytical_thinking", "communication", "languages", "practical_skills"],
        "personality_fit": ["analytical", "precise", "adventurous"],
        "keywords": ["border guard officer", "customs officer", "immigration specialist", "Frontex officer", "security officer", "migration management", "border control", "law enforcement", "patrol officer"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "GCT-R": {
        "interest_domains": ["education_research"],
        "required_strengths": ["communication", "social_sciences", "creativity", "analytical_thinking"],
        "personality_fit": ["social", "practical", "team_player"],
        "keywords": ["primary school teacher", "elementary teacher", "classroom teacher", "pedagogy", "child education", "educational methodology", "special pedagogy", "tutor", "primary education"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "GCT-L": {
        "interest_domains": ["education_research"],
        "required_strengths": ["communication", "social_sciences", "creativity", "analytical_thinking"],
        "personality_fit": ["social", "practical", "team_player"],
        "keywords": ["primary school teacher", "elementary teacher", "classroom teacher", "pedagogy", "child education", "educational methodology", "special pedagogy", "tutor", "primary education"],
        "math_intensive": False, "creative_component": True, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "GCS-R": {
        "interest_domains": ["education_research"],
        "required_strengths": ["communication", "social_sciences", "analytical_thinking", "languages"],
        "personality_fit": ["social", "analytical", "team_player"],
        "keywords": ["secondary school teacher", "high school teacher", "subject teacher", "pedagogy", "curriculum development", "educational specialist", "mentor", "tutor", "teaching"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "GCS-L": {
        "interest_domains": ["education_research"],
        "required_strengths": ["communication", "social_sciences", "analytical_thinking", "languages"],
        "personality_fit": ["social", "analytical", "team_player"],
        "keywords": ["secondary school teacher", "high school teacher", "subject teacher", "pedagogy", "curriculum development", "educational specialist", "mentor", "tutor", "teaching"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "GCU": {
        "interest_domains": ["education_research", "medical_technology"],
        "required_strengths": ["communication", "social_sciences", "practical_skills", "analytical_thinking"],
        "personality_fit": ["social", "practical", "team_player"],
        "keywords": ["special education teacher", "special pedagogue", "inclusive education", "child rehabilitation", "sign language specialist", "correction pedagogue", "speech support", "learning disabilities"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "GCL": {
        "interest_domains": ["education_research", "medical_technology"],
        "required_strengths": ["communication", "social_sciences", "analytical_thinking", "research"],
        "personality_fit": ["social", "analytical", "precise"],
        "keywords": ["speech therapist", "logopedist", "speech language pathologist", "communication disorders", "rehabilitation", "clinical logopedics", "child speech development", "voice therapy", "dyslexia"],
        "math_intensive": False, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "SCE": {
        "interest_domains": ["education_research"],
        "required_strengths": ["communication", "social_sciences", "analytical_thinking", "practical_skills"],
        "personality_fit": ["social", "practical", "team_player"],
        "keywords": ["social worker", "social rehabilitologist", "social services specialist", "family support worker", "social care", "community worker", "crisis intervention", "social rehabilitation", "welfare"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "SCD": {
        "interest_domains": ["education_research"],
        "required_strengths": ["communication", "social_sciences", "analytical_thinking"],
        "personality_fit": ["social", "practical", "team_player"],
        "keywords": ["social worker", "municipal social worker", "NGO worker", "social policy", "child welfare", "community social worker", "social case manager", "human rights", "social protection"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "UCZ": {
        "interest_domains": ["maritime", "transport_aviation"],
        "required_strengths": ["mathematics", "physics", "practical_skills", "analytical_thinking", "languages"],
        "personality_fit": ["adventurous", "international", "precise"],
        "keywords": ["navigator", "ship captain", "deck officer", "helmsman", "maritime officer", "port operations", "STCW", "navigation officer", "maritime logistics", "sea voyage", "vessel routing"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "UCN": {
        "interest_domains": ["maritime", "mechanics_engineering", "energy_power"],
        "required_strengths": ["mathematics", "physics", "practical_skills", "technical_thinking", "analytical_thinking"],
        "personality_fit": ["technical", "practical", "adventurous"],
        "keywords": ["marine engineer", "ship engineer", "chief engineer", "engine room officer", "ship mechanic", "maritime engineering", "propulsion systems", "STCW", "vessel maintenance", "diesel engine"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },
    "UCE": {
        "interest_domains": ["maritime", "electronics_telecom", "energy_power"],
        "required_strengths": ["mathematics", "physics", "programming", "technical_thinking", "practical_skills"],
        "personality_fit": ["technical", "precise", "adventurous"],
        "keywords": ["marine electro engineer", "ship electrician", "electro automation engineer", "shipboard electronics", "marine automation systems", "vessel electrical systems", "STCW", "maritime electronics", "navigation electronics"],
        "math_intensive": True, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium_high",
    },

    # ── rtu_programs.json  (Rēzekne Academy programmes in academic file) ──────
    "BV": {
        "interest_domains": ["business_management", "education_research"],
        "required_strengths": ["communication", "leadership", "economics_finance", "analytical_thinking"],
        "personality_fit": ["entrepreneurial", "analytical", "social"],
        "keywords": ["business manager", "entrepreneur", "marketing manager", "HR manager", "financial manager", "operations manager", "business consultant", "SME owner", "startup founder", "management"],
        "math_intensive": False, "creative_component": False, "research_oriented": False,
        "teamwork_oriented": True, "difficulty_level": "medium",
    },
    "TZ": {
        "interest_domains": ["education_research", "business_management"],
        "required_strengths": ["analytical_thinking", "communication", "languages", "social_sciences"],
        "personality_fit": ["analytical", "precise", "social"],
        "keywords": ["lawyer", "jurist", "legal adviser", "legal consultant", "judge", "prosecutor", "notary", "legal analyst", "compliance officer", "contract law", "public law"],
        "math_intensive": False, "creative_component": False, "research_oriented": True,
        "teamwork_oriented": False, "difficulty_level": "medium_high",
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# FILE PROCESSOR
# ─────────────────────────────────────────────────────────────────────────────

def enrich_file(path: Path) -> tuple[int, int]:
    """Apply enrichments to one JSON file. Returns (enriched, skipped)."""
    with open(path, "r", encoding="utf-8-sig") as f:
        data = json.load(f)

    key = "programs" if "programs" in data else "programmes"
    programs = data.get(key, [])

    enriched = skipped = 0
    for prog in programs:
        pid = (prog.get("id") or prog.get("slug") or "").strip()
        if not pid:
            continue

        entry = ENRICHMENTS.get(pid)
        if entry is None:
            print(f"  SKIP  {pid:<14}  (no manual enrichment defined)")
            skipped += 1
            continue

        # Write matching block (merge so existing flags are preserved)
        existing = prog.get("matching", {}) or {}
        existing.update({
            "interest_domains":        entry["interest_domains"],
            "required_strengths":      entry["required_strengths"],
            "personality_fit":         entry["personality_fit"],
            "math_intensive":          entry["math_intensive"],
            "creative_component":      entry["creative_component"],
            "research_oriented":       entry["research_oriented"],
            "teamwork_oriented":       entry["teamwork_oriented"],
            "difficulty_level":        entry["difficulty_level"],
        })
        prog["matching"] = existing
        prog["keywords"] = entry["keywords"]

        print(f"  OK    {pid:<14}  domains={entry['interest_domains'][:2]}")
        enriched += 1

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return enriched, skipped


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    files = sorted(DATASET_DIR.glob("*.json"))
    if not files:
        print(f"ERROR: No JSON files in {DATASET_DIR}")
        sys.exit(1)

    total_enriched = total_skipped = 0
    for path in files:
        print(f"\n{'='*60}")
        print(f"  {path.name}")
        print(f"{'='*60}")
        e, s = enrich_file(path)
        total_enriched += e
        total_skipped  += s
        print(f"  → {e} enriched, {s} skipped")

    print(f"\n{'='*60}")
    print(f"DONE  {total_enriched} enriched  |  {total_skipped} skipped (no definition)")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
