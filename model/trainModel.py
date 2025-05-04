"""
sentiment_model.py  —— 2025‑05‑04 完整修正版
依赖: pandas numpy scikit-learn matplotlib seaborn joblib
可选: imbalanced‑learn (若需 SMOTE 等过采样)
"""
from __future__ import annotations
import warnings
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from collections import Counter

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_validate,
)
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    classification_report,
    RocCurveDisplay,
    f1_score,
    balanced_accuracy_score,
)
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight

# -------------------------------------------------------------------
# Matplotlib 中文支持
# -------------------------------------------------------------------
import matplotlib
matplotlib.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "SimSun"]
matplotlib.rcParams["axes.unicode_minus"] = False


# -------------------------------------------------------------------
# 数据加载
# -------------------------------------------------------------------
def load_data(csv_path: str | Path) -> pd.DataFrame:
    """读取 csv 为 DataFrame，并做基本清洗"""
    return (
        pd.read_csv(csv_path, header=None, names=["text", "label"])
        .dropna(subset=["text", "label"])
        .drop_duplicates()
        .reset_index(drop=True)
    )


# -------------------------------------------------------------------
# 朴素贝叶斯加权版（解决类别不平衡）
# -------------------------------------------------------------------
class WeightedMultinomialNB(MultinomialNB):
    """在 fit 时对少数类自动加权"""

    def fit(self, X, y):
        classes = np.unique(y)
        weights = compute_class_weight("balanced", classes=classes, y=y)
        sample_weight = np.array([dict(zip(classes, weights))[label] for label in y])
        return super().fit(X, y, sample_weight=sample_weight)


# -------------------------------------------------------------------
# 模型列表
# -------------------------------------------------------------------
MODELS = {
    "NaiveBayes": WeightedMultinomialNB(),
    "LogReg": LogisticRegression(max_iter=1000, class_weight="balanced"),
    "LinearSVM": LinearSVC(class_weight="balanced"),
    "RandomForest": RandomForestClassifier(
        n_estimators=300, n_jobs=-1, random_state=42, class_weight="balanced"
    ),
}


def build_pipeline(estimator):
    """统一的 TF‑IDF + 分类器流水线"""
    return Pipeline(
        steps=[
            ("tfidf", TfidfVectorizer(max_features=5000, ngram_range=(1, 2))),
            ("clf", estimator),
        ]
    )


# -------------------------------------------------------------------
# 交叉验证 + 可视化
# -------------------------------------------------------------------
def evaluate_models(
    df: pd.DataFrame,
    k_folds: int | None = None,
    scoring: str = "macro_f1",
) -> dict[str, np.ndarray]:
    """
    交叉验证比较各模型。
    scoring 取值：'macro_f1' | 'bal_acc' | 'accuracy'
    """
    X, y = df["text"], df["label"]

    # 动态决定 n_splits，避免最小类别 < n_splits
    min_class = y.value_counts().min()
    n_splits = k_folds or max(2, min(5, min_class))
    if min_class < 10:
        warnings.warn(
            f"⚠️ 最小类别样本数只有 {min_class}，已自动将 n_splits 设为 {n_splits}。",
            UserWarning,
        )

    skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)

    # 多指标
    cv_metrics = {
        "accuracy": "accuracy",
        "macro_f1": "f1_macro",
        "bal_acc": "balanced_accuracy",
    }

    results = {}

    for name, est in MODELS.items():
        pipe = build_pipeline(est)
        cv_res = cross_validate(
            pipe,
            X,
            y,
            cv=skf,
            scoring=cv_metrics,
            n_jobs=-1,
            return_train_score=False,
        )
        key = f"test_{scoring}"      # 自动加前缀
        results[name] = cv_res[key]
        print(
            f"{name:<12} | {scoring}={cv_res[key].mean():.4f}±{cv_res[key].std():.4f} "
            f"| acc={cv_res['test_accuracy'].mean():.4f}"
        )

    # 箱线图
    plt.figure(figsize=(8, 5))
    sns.boxplot(data=pd.DataFrame(results))
    plt.title(f"{n_splits}-Fold {scoring} Comparison")
    plt.ylabel(scoring)
    plt.tight_layout()
    plt.show()

    return results


# -------------------------------------------------------------------
# 训练最终模型 + 混淆矩阵 / ROC
# -------------------------------------------------------------------
def train_best_model(
    df: pd.DataFrame, model_name: str = "NaiveBayes"
):
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["label"],
        test_size=0.2,
        stratify=df["label"],
        random_state=42,
    )
    pipe = build_pipeline(MODELS[model_name])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_test)

    print("\n🎯 Classification Report")
    print(classification_report(y_test, y_pred, digits=4))

    # 混淆矩阵
    cm = confusion_matrix(y_test, y_pred, labels=np.unique(y_test))
    ConfusionMatrixDisplay(cm, display_labels=np.unique(y_test)).plot(
        cmap="Blues", xticks_rotation=45
    )
    plt.title(f"{model_name} Confusion Matrix")
    plt.tight_layout()
    plt.show()

    # ROC（仅二分类且支持 decision_function）
    if len(np.unique(y_test)) == 2 and hasattr(pipe, "decision_function"):
        RocCurveDisplay.from_predictions(y_test, pipe.decision_function(X_test))
        plt.title(f"{model_name} ROC Curve")
        plt.tight_layout()
        plt.show()

    # 保存模型
    joblib.dump(pipe, "best_sentiment_model.pkl")
    print("✅ 模型已保存为 best_sentiment_model.pkl")
    return pipe


# -------------------------------------------------------------------
# 推理接口（单例）
# -------------------------------------------------------------------
class SentimentPredictor:
    _model = None

    @classmethod
    def load(cls, path: str = "best_sentiment_model.pkl"):
        if cls._model is None:
            cls._model = joblib.load(path)
        return cls._model

    @classmethod
    def predict(cls, text: str):
        return cls.load().predict([text])[0]


# -------------------------------------------------------------------
# 主流程
# -------------------------------------------------------------------
if __name__ == "__main__":
    df = load_data("target.csv")
    print("📊 标签分布:", Counter(df["label"]))

    # ① 交叉验证比较
    evaluate_models(df, scoring="macro_f1")

    # ② 训练最优模型（看上一步结果手动改名即可）
    trained_pipe = train_best_model(df, model_name="NaiveBayes")

    # ③ 推理示例
    demo = "糟糕透了"
    print("⛅ 预测结果:", SentimentPredictor.predict(demo))
