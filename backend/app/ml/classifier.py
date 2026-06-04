"""
Career Classifier using Scikit-learn.
Maps Holland Code (RIASEC) assessment scores to career recommendations.
Includes SHAP-based explainability (XAI).
"""
import numpy as np
import joblib
import os
from pathlib import Path
from typing import List, Dict, Optional

MODEL_PATH = Path(__file__).parent / "models" / "career_classifier.joblib"
ENCODER_PATH = Path(__file__).parent / "models" / "label_encoder.joblib"


class CareerClassifier:
    def __init__(self):
        self.model = None
        self.label_encoder = None
        self.feature_names = [
            "realistic", "investigative", "artistic",
            "social", "enterprising", "conventional",
            "math_score", "science_score", "literature_score",
            "financial_level",  # 1=low, 2=medium, 3=high
        ]

    def load(self):
        """Load pre-trained model or initialize a default rule-based fallback."""
        if MODEL_PATH.exists():
            self.model = joblib.load(MODEL_PATH)
            self.label_encoder = joblib.load(ENCODER_PATH)
        else:
            self._init_rule_based_fallback()

    def _init_rule_based_fallback(self):
        """
        Rule-based fallback when ML model is not available.
        Implements Robustness requirement: system stays functional without trained model.
        """
        self.model = None
        self.label_encoder = None

    def predict(self, features: Dict[str, float]) -> List[Dict]:
        """
        Returns top-3 career recommendations with confidence scores.
        Falls back to rule-based if ML model unavailable.
        """
        if self.model is None:
            return self._rule_based_predict(features)

        X = np.array([[features.get(f, 0) for f in self.feature_names]])
        probas = self.model.predict_proba(X)[0]
        top_3_idx = np.argsort(probas)[::-1][:3]

        return [
            {
                "career_code": self.label_encoder.inverse_transform([idx])[0],
                "confidence": float(probas[idx]),
                "explanation": self._explain(X, idx),
            }
            for idx in top_3_idx
        ]

    def _rule_based_predict(self, features: Dict[str, float]) -> List[Dict]:
        """Deterministic fallback using Holland RIASEC rules."""
        scores = {
            "CNTT": features.get("investigative", 0) * 0.4 + features.get("realistic", 0) * 0.3 + features.get("math_score", 0) / 10 * 0.3,
            "Kinh_te": features.get("enterprising", 0) * 0.4 + features.get("conventional", 0) * 0.3 + features.get("math_score", 0) / 10 * 0.3,
            "Su_pham": features.get("social", 0) * 0.5 + features.get("artistic", 0) * 0.3 + features.get("literature_score", 0) / 10 * 0.2,
            "Y_khoa": features.get("investigative", 0) * 0.4 + features.get("social", 0) * 0.4 + features.get("science_score", 0) / 10 * 0.2,
            "Nghe_thuat": features.get("artistic", 0) * 0.6 + features.get("social", 0) * 0.2 + features.get("literature_score", 0) / 10 * 0.2,
        }
        sorted_careers = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        return [
            {"career_code": code, "confidence": round(score, 3), "explanation": "Dựa trên trắc nghiệm Holland (rule-based)"}
            for code, score in sorted_careers[:3]
        ]

    def _explain(self, X: np.ndarray, class_idx: int) -> str:
        """Generate SHAP-based explanation (requires shap library)."""
        try:
            import shap
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)
            values = shap_values[class_idx][0]
            top_features = sorted(
                zip(self.feature_names, values),
                key=lambda x: abs(x[1]), reverse=True
            )[:3]
            parts = [f"{feat} ({'+' if val > 0 else ''}{val:.2f})" for feat, val in top_features]
            return "Yếu tố chính: " + ", ".join(parts)
        except Exception:
            return "Dựa trên điểm số và sở thích nghề nghiệp của bạn"


career_classifier = CareerClassifier()
