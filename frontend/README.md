# CardioXAI Classic — React Frontend

A complete replacement React/Vite frontend for your **existing** CardioXAI Flask backend. Inspired by the uploaded presentation's dark editorial aesthetic, with a different midnight-navy / royal-purple / champagne-gold palette.

## Installation

1. **Back up your existing `frontend` folder** (rename it `frontend_backup`).
2. Extract this ZIP, and rename the extracted `cardioxai_frontend` folder to `frontend` inside `Explainable_CVD_Prediction`.
3. Keep your original `app/app.py`, `models/cvd_website_bundle.joblib`, and virtual environment **unchanged**.
4. Terminal 1 (project root): `python app/app.py` (activate your `.venv` first).
5. Terminal 2 (inside `frontend`): `npm install` then `npm run dev`.
6. Open the URL printed by Vite (typically `http://localhost:5173`).

## Backend compatibility

The Vite dev proxy sends `/api/*` requests to `http://127.0.0.1:5000`, avoiding hardcoded browser CORS dependencies. It expects your existing:
- `GET /api/health`
- `POST /api/predict` with 13 numeric features and response fields `prediction`, `label`, `disease_probability`, `shap`, `lime`, `disclaimer`.

This frontend does not modify or retrain your model. SHAP/LIME charts display the API's returned feature contributions.

## Notes

- Model performance cards use the previously reported held-out evaluation: accuracy 83.61%, ROC-AUC 0.9048, sensitivity 84.85%, specificity 82.14%. These are **static historical metrics** and should be updated if the saved model changes.
- Clinical code meanings for several encoded categorical variables need verification against the specific `heart.csv` dataset's codebook. For these, the UI deliberately displays code numbers rather than inventing clinical labels.
- The interface is an educational research prototype, not a diagnostic system.
- Do not run `npm install` in the project root; run it inside `frontend`.
