"""
Career Classifier using Scikit-learn.
Maps Holland Code (RIASEC) assessment scores to career recommendations.
Includes SHAP-based explainability (XAI).
"""
import numpy as np
import joblib
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple

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
        self.feature_labels = {
            "realistic": "Realistic (R)",
            "investigative": "Investigative (I)",
            "artistic": "Artistic (A)",
            "social": "Social (S)",
            "enterprising": "Enterprising (E)",
            "conventional": "Conventional (C)",
            "math_score": "Điểm Toán",
            "science_score": "Điểm KHTN",
            "literature_score": "Điểm Ngữ văn",
            "financial_level": "Điều kiện tài chính",
        }

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

        return [self._build_ml_result(X, probas, idx) for idx in top_3_idx]

    def _build_ml_result(self, X: np.ndarray, probas: np.ndarray, idx: int) -> Dict:
        explanation, shap_factors = self._explain_with_factors(X, idx)
        return {
            "career_code": self.label_encoder.inverse_transform([idx])[0],
            "confidence": float(probas[idx]),
            "explanation": explanation,
            "shap_factors": shap_factors,
        }

    def _rule_based_predict(self, features: Dict[str, float]) -> List[Dict]:
        """Deterministic fallback using Holland RIASEC rules."""
        weight_sets = {
            "CNTT": {"investigative": 0.4, "realistic": 0.3, "math_score": 0.3},
            "Kinh_te": {"enterprising": 0.4, "conventional": 0.3, "math_score": 0.3},
            "Su_pham": {"social": 0.5, "artistic": 0.3, "literature_score": 0.2},
            "Y_khoa": {"investigative": 0.4, "social": 0.4, "science_score": 0.2},
            "Nghe_thuat": {"artistic": 0.6, "social": 0.2, "literature_score": 0.2},
        }

        scored = []
        for career_code, weights in weight_sets.items():
            factors = self._fallback_factors(features, weights)
            score = sum(factors.values())
            top_features = sorted(factors.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
            explanation_parts = [f"{self.feature_labels.get(name, name)} ({value:.2f})" for name, value in top_features]
            scored.append(
                {
                    "career_code": career_code,
                    "confidence": round(score, 3),
                    "explanation": "Yếu tố chính (rule-based): " + ", ".join(explanation_parts),
                    "shap_factors": factors,
                }
            )

        scored.sort(key=lambda x: x["confidence"], reverse=True)
        return scored[:3]

    def _fallback_factors(self, features: Dict[str, float], weights: Dict[str, float]) -> Dict[str, float]:
        normalized_values = {
            "realistic": features.get("realistic", 0),
            "investigative": features.get("investigative", 0),
            "artistic": features.get("artistic", 0),
            "social": features.get("social", 0),
            "enterprising": features.get("enterprising", 0),
            "conventional": features.get("conventional", 0),
            "math_score": features.get("math_score", 0) / 10,
            "science_score": features.get("science_score", 0) / 10,
            "literature_score": features.get("literature_score", 0) / 10,
            "financial_level": features.get("financial_level", 0) / 3,
        }

        return {
            feature_name: round(normalized_values.get(feature_name, 0) * feature_weight, 4)
            for feature_name, feature_weight in weights.items()
        }

    def _explain_with_factors(self, X: np.ndarray, class_idx: int) -> Tuple[str, Optional[Dict[str, float]]]:
        """Generate SHAP-based explanation and factor values (requires shap library)."""
        try:
            import shap
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X)

            if isinstance(shap_values, list):
                values = shap_values[class_idx][0]
            else:
                values = shap_values[0, :, class_idx]

            top_features = sorted(
                zip(self.feature_names, values),
                key=lambda x: abs(x[1]), reverse=True
            )[:3]
            parts = [f"{feat} ({'+' if val > 0 else ''}{val:.2f})" for feat, val in top_features]
            factor_map = {
                feature_name: round(float(feature_value), 4)
                for feature_name, feature_value in zip(self.feature_names, values)
            }
            return "Yếu tố chính: " + ", ".join(parts), factor_map
        except Exception:
            return "Dựa trên điểm số và sở thích nghề nghiệp của bạn", None


career_classifier = CareerClassifier()
