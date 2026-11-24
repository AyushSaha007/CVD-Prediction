
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap

from flask import Flask, request, jsonify
from flask_cors import CORS
from lime.lime_tabular import LimeTabularExplainer


# ==================================================
# 1. FLASK APPLICATION SETUP
# ==================================================

app = Flask(__name__)
CORS(app)

ROOT_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = ROOT_DIR / "models" / "cvd_website_bundle.joblib"

# Load saved model bundle
bundle = joblib.load(MODEL_PATH)

pipeline = bundle["pipeline"]
X_train_transformed = np.asarray(bundle["X_train_transformed"])
feature_names = list(bundle["feature_names"])
transformed_feature_names = list(bundle["transformed_feature_names"])

preprocessor = pipeline.named_steps["preprocessor"]
classifier = pipeline.named_steps["classifier"]

MODEL_NAME = "Logistic Regression"

# ==================================================
# 2. SHAP EXPLAINER
# ==================================================

shap_explainer = shap.LinearExplainer(
    classifier,
    X_train_transformed
)

# ==================================================
# 3. LIME EXPLAINER
# ==================================================

lime_explainer = LimeTabularExplainer(
    training_data=X_train_transformed,
    feature_names=transformed_feature_names,
    class_names=["No Disease", "Disease"],
    mode="classification",
    random_state=42
)


# ==================================================
# 4. HOME ROUTE
# ==================================================

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "success",
        "message": "Welcome to CardioXAI API",
        "project": "Explainable ML for Cardiovascular Disease",
        "model": MODEL_NAME,
        "version": "2.0"
    })


# ==================================================
# 5. HEALTH CHECK ROUTE
# ==================================================

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "success",
        "message": "Cardiovascular Disease Prediction API is running",
        "model": MODEL_NAME,
        "shap": "available",
        "lime": "available"
    })


# ==================================================
# 6. MODEL INFORMATION ROUTE
# ==================================================

@app.route("/api/model-info", methods=["GET"])
def model_info():
    return jsonify({
        "status": "success",
        "model_name": MODEL_NAME,
        "input_features": feature_names,
        "total_input_features": len(feature_names),
        "total_transformed_features": len(transformed_feature_names),
        "explanation_methods": ["SHAP", "LIME"],
        "classes": {
            "0": "No Disease",
            "1": "Disease"
        },
        "disclaimer": "Research model, not clinically validated."
    })


# ==================================================
# 7. PATIENT INPUT VALIDATION
# ==================================================

def validate_patient_input(data):

    if not isinstance(data, dict):
        raise ValueError("Please send patient data as a JSON object.")

    missing = [
        feature for feature in feature_names
        if feature not in data
    ]

    if missing:
        raise ValueError(
            "Missing required features: " + ", ".join(missing)
        )

    patient_data = {}

    for feature in feature_names:
        value = data[feature]

        if value is None or isinstance(value, bool):
            raise ValueError(
                f"Invalid value for {feature}."
            )

        try:
            numeric_value = float(value)
        except (TypeError, ValueError):
            raise ValueError(
                f"{feature} must be a valid number."
            )

        if not np.isfinite(numeric_value):
            raise ValueError(
                f"{feature} must be a finite number."
            )

        patient_data[feature] = numeric_value

    patient_df = pd.DataFrame(
        [patient_data],
        columns=feature_names
    )

    return patient_df


# ==================================================
# 8. SHAP EXPLANATION
# ==================================================

def generate_shap_explanation(processed_data):

    shap_result = shap_explainer(processed_data)
    shap_values = np.asarray(shap_result.values)

    if shap_values.ndim == 3:
        shap_values = shap_values[0, :, 1]

    elif shap_values.ndim == 2:
        shap_values = shap_values[0]

    else:
        shap_values = shap_values.reshape(-1)

    if len(shap_values) != len(transformed_feature_names):
        raise ValueError(
            "SHAP feature count does not match model features."
        )

    explanation = [
        {
            "feature": str(name),
            "value": float(value)
        }
        for name, value in zip(
            transformed_feature_names,
            shap_values
        )
    ]

    explanation.sort(
        key=lambda item: abs(item["value"]),
        reverse=True
    )

    return explanation[:10]


# ==================================================
# 9. LIME EXPLANATION
# ==================================================

def generate_lime_explanation(processed_data):

    lime_result = lime_explainer.explain_instance(
        data_row=processed_data[0],
        predict_fn=classifier.predict_proba,
        num_features=10,
        labels=(1,)
    )

    explanation = [
        {
            "feature": str(name),
            "weight": float(weight)
        }
        for name, weight in lime_result.as_list(label=1)
    ]

    return explanation


# ==================================================
# 10. PREDICTION API
# ==================================================

@app.route("/api/predict", methods=["POST"])
def predict():

    try:
        data = request.get_json(silent=True)

        # Validate patient inputs
        patient_df = validate_patient_input(data)

        # Transform patient data using saved preprocessor
        processed_data = np.asarray(
            preprocessor.transform(patient_df)
        )

        # Predict using saved pipeline
        prediction = int(
            pipeline.predict(patient_df)[0]
        )

        probabilities = pipeline.predict_proba(
            patient_df
        )[0]

        class_index = list(pipeline.classes_).index(1)

        disease_probability = float(
            probabilities[class_index]
        )

        # Generate explanations
        shap_explanation = generate_shap_explanation(
            processed_data
        )

        lime_explanation = generate_lime_explanation(
            processed_data
        )

        # API response
        return jsonify({
            "status": "success",
            "model_name": MODEL_NAME,

            "prediction": prediction,
            "label": (
                "Disease"
                if prediction == 1
                else "No Disease"
            ),

            "disease_probability": disease_probability,
            "no_disease_probability": 1 - disease_probability,

            "shap": shap_explanation,
            "lime": lime_explanation,

            "shap_unit": "log_odds",
            "lime_unit": "local_surrogate_weight",

            "explanation_info": {
                "shap": (
                    "SHAP explains feature contributions "
                    "to the Logistic Regression log-odds "
                    "of the disease class."
                ),
                "lime": (
                    "LIME approximates the model locally "
                    "and reports feature weights for "
                    "the disease class."
                )
            },

            "disclaimer": (
                "This is an experimental machine-learning "
                "result, not a medical diagnosis. "
                "Consult a qualified doctor."
            )
        })

    except ValueError as error:
        return jsonify({
            "status": "error",
            "error": str(error)
        }), 400

    except Exception:
        app.logger.exception("Prediction failed")

        return jsonify({
            "status": "error",
            "error": (
                "Prediction failed. "
                "Check the Flask backend terminal."
            )
        }), 500


# ==================================================
# 11. START FLASK SERVER
# ==================================================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
