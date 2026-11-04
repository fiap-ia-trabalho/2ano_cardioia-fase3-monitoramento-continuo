import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, f1_score, precision_score, recall_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def generate_window(length=128, label=0, rng=None):
    if rng is None:
        rng = np.random.default_rng(42)

    t = np.linspace(0, 1, length)
    if label == 0:
        signal = np.sin(2 * np.pi * 3 * t)
        signal += 0.05 * np.sin(2 * np.pi * 9 * t)
        signal += rng.normal(0, 0.08, size=length)
    else:
        signal = np.sin(2 * np.pi * 3 * t + 0.6)
        signal += 0.60 * np.sin(2 * np.pi * 12 * t)
        signal += rng.normal(0, 0.18, size=length)
        signal += np.linspace(0.0, 0.8, length)
        signal = np.clip(signal, -2.0, 2.0)
    return signal.astype(float)


def generate_dataset(n_samples=600, window_length=128, seed=42):
    rng = np.random.default_rng(seed)
    windows = []
    labels = []

    for _ in range(n_samples):
        label = int(rng.random() < 0.5)
        window = generate_window(window_length, label=label, rng=rng)
        windows.append(window)
        labels.append(label)

    X = np.vstack(windows)
    y = np.asarray(labels, dtype=int)
    return X, y


def statistical_features(window):
    values = np.asarray(window, dtype=float)
    return np.array([
        values.mean(),
        values.std(),
        values.min(),
        values.max(),
        np.sqrt(np.mean(np.square(values))),
        np.mean(np.abs(np.diff(values))),
        np.abs(np.diff(values)).mean(),
        np.ptp(values),
    ], dtype=float)


def lif_feature_extractor(window, threshold=0.75, decay=0.85):
    signal = np.asarray(window, dtype=float)
    membrane = 0.0
    spikes = 0
    spike_times = []
    max_membrane = 0.0

    for value in signal:
        membrane = decay * membrane + value
        max_membrane = max(max_membrane, membrane)
        if membrane > threshold:
            spikes += 1
            spike_times.append(1)
            membrane = 0.0
        else:
            spike_times.append(0)

    firing_rate = spikes / len(signal)
    return np.array([
        spikes,
        firing_rate,
        np.mean(spike_times),
        max_membrane,
        np.abs(signal).mean(),
        np.std(signal),
    ], dtype=float)


def build_feature_matrix(X, mode="statistical"):
    features = []
    for sample in X:
        if mode == "statistical":
            features.append(statistical_features(sample))
        elif mode == "lif":
            features.append(lif_feature_extractor(sample))
        else:
            raise ValueError(f"Modo inválido: {mode}")
    return np.vstack(features)


def fit_and_score(X_train, y_train, X_test, y_test, mode):
    model = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42))
    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    proba = model.predict_proba(X_test)[:, 1]

    metrics = {
        "mode": mode,
        "accuracy": accuracy_score(y_test, pred),
        "precision": precision_score(y_test, pred, zero_division=0),
        "recall": recall_score(y_test, pred, zero_division=0),
        "f1": f1_score(y_test, pred, zero_division=0),
        "cm": confusion_matrix(y_test, pred).tolist(),
    }
    return model, pred, proba, metrics


def plot_signal_examples(X, y, path):
    sample_idx = [0, 1, 10, 20]
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), sharex=True)
    for ax, idx in zip(axes.flat, sample_idx):
        label = y[idx]
        ax.plot(X[idx], color="#1f77b4" if label == 0 else "#d62728")
        ax.set_title(f"Classe {label}")
        ax.set_xlabel("Tempo")
        ax.set_ylabel("Amplitude")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_confusion_matrix(cm, title, path):
    fig, ax = plt.subplots(figsize=(5, 4))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False, ax=ax)
    ax.set_title(title)
    ax.set_xlabel("Predição")
    ax.set_ylabel("Real")
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def plot_model_comparison(metrics, path):
    labels = ["Logística", "LIF"]
    acc = [metrics["logistic"]["accuracy"], metrics["lif"]["accuracy"]]
    f1 = [metrics["logistic"]["f1"], metrics["lif"]["f1"]]

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(labels))
    ax.bar(x - 0.2, acc, width=0.35, label="Acurácia")
    ax.bar(x + 0.2, f1, width=0.35, label="F1")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 1.1)
    ax.set_ylabel("Métrica")
    ax.set_title("Comparação de desempenho")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main():
    X, y = generate_dataset(n_samples=800, window_length=128, seed=42)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=42
    )

    X_train_stat = build_feature_matrix(X_train, mode="statistical")
    X_test_stat = build_feature_matrix(X_test, mode="statistical")
    X_train_lif = build_feature_matrix(X_train, mode="lif")
    X_test_lif = build_feature_matrix(X_test, mode="lif")

    _, _, _, logistic_metrics = fit_and_score(X_train_stat, y_train, X_test_stat, y_test, mode="logistic")
    _, _, _, lif_metrics = fit_and_score(X_train_lif, y_train, X_test_lif, y_test, mode="lif")

    metrics = {"logistic": logistic_metrics, "lif": lif_metrics}

    plot_signal_examples(X_test, y_test, RESULTS_DIR / "series_examples.png")
    plot_confusion_matrix(np.array(logistic_metrics["cm"]), "Matriz de confusão - logística", RESULTS_DIR / "cm_logistic.png")
    plot_confusion_matrix(np.array(lif_metrics["cm"]), "Matriz de confusão - LIF", RESULTS_DIR / "cm_lif.png")
    plot_model_comparison(metrics, RESULTS_DIR / "comparacao_modelos.png")

    with (RESULTS_DIR / "metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("=== Comparação de modelos ===")
    for name in ["logistic", "lif"]:
        print(f"{name.upper()}: acc={metrics[name]['accuracy']:.3f}, precision={metrics[name]['precision']:.3f}, recall={metrics[name]['recall']:.3f}, f1={metrics[name]['f1']:.3f}")

    print(f"\nArquivos salvos em: {RESULTS_DIR}")


if __name__ == "__main__":
    sns.set_theme(style="whitegrid")
    main()
