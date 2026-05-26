# 🎓 RTU Study Programme AI Recommender

> **An intelligent Streamlit application that helps high-school students discover
> the most suitable RTU (Riga Technical University) bachelor study programmes
> using AI-powered personalised matching.**

---

## 📸 Screenshots

| Student Profile Form | Top-3 Results with AI Explanation |
|---|---|
| *(screenshot placeholder)* | *(screenshot placeholder)* |

| Score Breakdown | Programme Comparison |
|---|---|
| *(screenshot placeholder)* | *(screenshot placeholder)* |

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd rtu-study-recommender

# 2. Create a virtual environment (recommended)
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up your Gemini API key
copy .env.example .env
# Open .env and add your GEMINI_API_KEY
# Get a free key at: https://aistudio.google.com/app/apikey

# 5. Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`.

---

## 🏗️ Architecture

```
rtu-study-recommender/
│
├── app.py                 ← Main Streamlit application (UI orchestrator)
├── data_loader.py         ← Multi-format JSON loader & normaliser
├── scoring.py             ← Weighted matching / recommendation engine
├── ai_explanations.py     ← Gemini API integration + local fallback
├── ui_components.py       ← Reusable Streamlit UI building blocks
├── utils.py               ← Universal taxonomy, tag mappings, helpers
│
├── datasets/              ← RTU JSON programme datasets (auto-loaded)
│   ├── rtu_programs.json
│   ├── rtu_bmf_programs.json
│   ├── rtu_programs_DITEF_IVF_prof.json
│   └── rtu_programs_rezekne_liepaja_jura.json
│
├── assets/                ← Optional static files (logos, CSS)
├── .streamlit/
│   └── config.toml        ← Streamlit theme (RTU red + clean light)
│
├── test_profiles.json     ← 6 pre-built test student profiles
├── requirements.txt
├── .env.example
└── README.md
```

### Data Flow

```
JSON Files (4 formats)
        ↓
  data_loader.py
  (detect format → normalise → canonical tags)
        ↓
  Universal Programme List (64 programmes)
        ↓
  Student Profile Form (app.py)
        ↓
  scoring.py
  (weighted matching → score 0–100% + breakdown)
        ↓
  ai_explanations.py
  (Gemini API → personalised explanation per programme)
        ↓
  ui_components.py
  (result cards, comparison table, all-programmes view)
```

---

## 📊 Scoring System

The recommendation engine uses **13 weighted factors**:

| Factor | Weight | Notes |
|--------|--------|-------|
| Interest domain match | +4 per match | From canonical taxonomy |
| Strength / subject match | +3 per match | Mapped from all 4 formats |
| Personality trait match | +2 per match | 13 canonical traits |
| Industry sector match | +3 per match | 16 canonical sectors |
| Language availability | +2 | −20% penalty if preferred lang unavailable |
| Difficulty preference | +2 | −10% penalty if programme is too hard |
| Research orientation | +2 | Bonus if both student & programme are research-oriented |
| International potential | +2 | Bonus if both value international |
| Creative component | +2 | Bonus if student likes creativity AND programme has it |
| Math intensity | +2 | +2 if both match, −8% penalty if student dislikes math but programme is intensive |
| Entrance exam | +2 | −15% penalty if student avoids exams but programme requires one |
| Teamwork compatibility | +1 | Minor bonus |

**Score normalisation:**
```
base_pct = (positive_points_scored / max_possible_positive_points) × 100
final_pct = max(0, min(100, base_pct - sum_of_penalties))
```

---

## 🤖 AI Explanation System

Uses **Google Gemini 1.5 Flash** (free tier, ~1500 requests/day).

### Grounding Rules
The prompt explicitly instructs Gemini to:
- ✅ Use **only** the provided programme data
- ❌ **Never** invent study courses, fees, or career paths
- ❌ **Never** reference RTU programmes not in the dataset
- ⚠️ Say "information not available" if a fact is missing

### Explanation Structure (5 sections)
1. **Kāpēc šī programma der tev** — Why this programme fits you
2. **Kuras stiprās puses palīdz** — Which strengths support success
3. **Iespējamie izaicinājumi** — Possible challenges
4. **Ko uzlabot pirms iestāšanās** — What to improve before applying
5. **Karjeras iespējas** — Career opportunities

### Failsafe
If the Gemini API is unavailable (missing key, rate limit, network error):
- The app **never crashes**
- A high-quality **local explanation** is generated from the scoring breakdown
- The UI clearly labels whether the explanation is AI-generated or local

---

## 📁 Dataset System

### Supported Formats
The loader automatically handles 4 different JSON schemas:

| File | Format | Programmes | Description |
|------|--------|-----------|-------------|
| `rtu_programs.json` | Academic A | 20 | Main RTU academic bachelor programmes |
| `rtu_bmf_programs.json` | BMF Professional | 11 | Building & Mechanical Engineering faculty |
| `rtu_programs_DITEF_IVF_prof.json` | DITEF/IVF Professional | 15 | Computer Science, IT & Energy faculty |
| `rtu_programs_rezekne_liepaja_jura.json` | RTU Academies | 18 | Rēzekne, Liepāja, Maritime Academy |

**Total: 64 programmes across all RTU faculties and campuses**

### Adding New Programmes
1. Create a new JSON file with programme data
2. Place it in the `datasets/` folder
3. Restart the app — it auto-discovers all `.json` files
4. Supported schemas are auto-detected; the normaliser handles variations gracefully

---

## 🔧 Configuration

### Environment Variables (`.env`)
```env
GEMINI_API_KEY=AIzaSy...     # Required for AI explanations
RTU_DATASET_DIR=./datasets   # Optional: custom dataset path
```

### Streamlit Theme (`.streamlit/config.toml`)
RTU red (`#c8102e`) primary colour with clean light background.
Toggle dark mode via Streamlit's built-in theme settings.

---

## 🧪 Testing

Use the **"📋 Ielādēt testa profilu"** button in the UI to load one of 6 pre-built profiles:

| Profile | Recommended Programmes |
|---------|----------------------|
| Math/Physics/IT Student | Datorzinātne, AI, Robotika |
| Creative Designer | Industrijālais dizains, Arhitektūra |
| Business-oriented | Uzņēmējdarbība, Ekonomika |
| Environment/Biology | Vides inženierija, Ķīmija |
| Robotics/Engineering | Robotika, Mašīnbūve |
| International English Student | Civil Engineering (EN), Aviation |

---

## ⚠️ Known Limitations

1. **Data freshness** — Dataset reflects 2026 RTU programme offerings; always verify at [rtu.lv](https://www.rtu.lv)
2. **Tag vocabulary** — 4 different source schemas use different tag vocabularies; mapping covers ~95% of cases
3. **AI accuracy** — Gemini explanations are grounded in provided data but may occasionally miss nuance
4. **Score relativity** — Scores are relative to the student's own profile, not absolute programme quality rankings
5. **Language** — UI is primarily in Latvian; English partial support exists for English-programme filtering

---

## 🔮 Future Improvements

- [ ] User accounts and persistent saved profiles
- [ ] Admission statistics integration (CE exam score requirements)
- [ ] RTU live API integration for real-time programme data
- [ ] Mobile-optimised layout
- [ ] Export recommendations as PDF
- [ ] Multi-language full UI (LV / EN)
- [ ] Alumni career outcome data integration
- [ ] Masters programme recommendations after bachelor

---

## 👨‍💻 Technical Notes

- **Python** 3.10+
- **Streamlit** 1.35+ (native session state, tabs, form widgets)
- **Gemini 1.5 Flash** — optimised for speed on free tier
- **No database** — fully stateless; all state in `st.session_state`
- **Caching** — programme data cached for 1 hour via `@st.cache_data`

---

## 📄 Licence

MIT — Free to use, modify, and distribute.

---

*Built as an MVP portfolio project demonstrating AI-powered recommendation systems,
multi-format data normalisation, and production-quality Streamlit UI engineering.*
