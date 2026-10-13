<!-- README-R26-IT-152-v2 -->
# Tour Ceylon - SafeJourney AI (R26-IT-152)

**Tourism Risk and Context Intelligence System: an AI-based tourism risk prediction and advisory platform for Sri Lanka**

Final Year Research Project - BSc (Hons) in Information Technology, Department of Information Technology, Sri Lanka Institute of Information Technology (SLIIT), Malabe. Module: IT4010 Research Project.

---

## 1. Project Overview

Tourists in Sri Lanka often plan trips without reliable, combined information on crowding, safety, travel planning and wellness options. Information is scattered across many sources, and help in an emergency can be slow to reach.

Tour Ceylon brings four AI-supported components into one platform: a crowd and risk prediction service, an emergency (SOS) service, an itinerary planner and a wellness recommender. Together they help tourists choose where and when to travel, plan a trip, find wellness options and get help quickly when something goes wrong.

## 2. Research Objectives

**Main objective:** To design and build an integrated, AI-based advisory platform that improves the safety, planning and experience of tourists in Sri Lanka.

**Sub-objectives (one per component):**
- Crowd and risk prediction: predict crowd levels and risk for tourist sites across Sri Lanka and validate the model on unseen sites.
- SOS: provide one-tap emergency reporting with location capture and routing to the nearest responding station.
- Itinerary: generate day-by-day travel plans from the traveller's mood, budget and selected attractions.
- Wellness: recommend Ayurveda and spiritual/meditation centres matched to the traveller's needs.

## 3. Team and Supervisors

| Member | Student ID | Component |
|--------|-----------|-----------|
| De Silva D.S.K (group leader) | IT22108654 | SOS and emergency response |
| Wanniarachchi P.M.R | IT22225092 | Itinerary planning |
| De Silva D.C.M | IT22108586 | Wellness / Ayurveda recommendation |
| Abinaya Rajasekara | IT22090058 | Crowd and risk prediction |

- **Supervisor:** Mr. Buddika Harshanath
- **Co-supervisor:** Prof. Samantha Rajapaksha

## 4. System Architecture

The platform has a React front end for each component and Flask back ends. A shared Flask back end (port 5002) serves the travel, SOS, wellness and risk APIs from one PostgreSQL database. The crowd and risk component can also run on its own (port 5000).

<!-- ![System Architecture](docs/architecture.png) -->

## 5. Components

- **Crowd and risk prediction:** Random Forest pipeline trained on a 197-site dataset. Evaluated with site-holdout (primary), random-split and cross-validation results, reported separately and labelled by split.
- **SOS:** one-tap SOS with GPS capture, incident triage, routing to the nearest station, officer dashboards and an offline queue.
- **Itinerary:** step-by-step wizard (attractions, budget, accommodation, itinerary, recommendations, export) with rule-based scheduling and PDF export.
- **Wellness:** dual-path wizard (Ayurveda and spiritual/meditation) with a dosha classifier and a weighted matching score.

## 6. Tech Stack

- **Back end:** Python, Flask, Flask-SocketIO
- **ML/AI:** scikit-learn (Random Forest), pandas, NumPy
- **Front end:** React, Vite
- **Database:** PostgreSQL, SQLite
- **Other:** JWT authentication, WeasyPrint / ReportLab (PDF export)

## 7. Folder Structure

```
R26-IT152/
  backend/
    data/
    models/
    outputs/
    scripts/
  components/
    scripts/
    shared/
  frontend/
    src/
  tourism_risk_system (1)/
    tourism_risk_system/
  tourism-unified/
    public/
    scripts/
    src/
  README.md
```

## 8. Setup and Installation

**Requirements:** Python 3.10+, Node.js 18+, PostgreSQL, Git.

```
git clone https://github.com/SavinDeSilva/R26-IT152.git
cd R26-IT152
python -m venv .venv
.venv\Scripts\activate
```

Install the Python packages for each component you want to run:

```
pip install -r components\<component>\backend\requirements.txt
```

Configuration: create a `.env` file in `components\shared\backend` with your own `DATABASE_URL` and secret keys. The `.env` file is not stored in the repository.

## 9. How to Run

**Shared back end (port 5002):**

```
cd components\shared\backend
python run.py
```

Check it at `http://127.0.0.1:5002/api/health`.

**Crowd and risk back end on its own (port 5000):**

```
cd components\risk-management\backend
python app.py
```

**Front ends** (run `npm install` once, then `npm run dev` inside each folder):

| Front end | Folder | Port |
|-----------|--------|------|
| SOS (tourist) | components\sos\frontend\tourist | 5175 |
| SOS (police) | components\sos\frontend\police | 5176 |
| Itinerary | components\itinerary\frontend | 5180 |
| Wellness | components\wellness\frontend | 5181 |
| Crowd and risk | components\risk-management\frontend | 5182 |

## 10. Project Status

Final-year research project, submission stage. All four components are implemented and run on the shared back end. Known limitations are documented in the individual theses and the group report.

## 11. License

Academic project, SLIIT. Not licensed for commercial use.
