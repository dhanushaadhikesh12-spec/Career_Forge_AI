"""
K-Means student grouping module for trainer analytics.
Groups students based on multi-dimensional performance vectors.
"""
from __future__ import annotations
import logging
from typing import Dict, Any, List
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


def cluster_students(student_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Cluster students based on:
    - aptitude_score (0-100)
    - coding_score (0-100)
    - avg_test_score (0-100)
    - completion_rate (0-100)
    - streak_days (integer)

    Returns:
    {
        "status": "SUCCESS" | "INSUFFICIENT_DATA",
        "clusters": [...],
        "students": [...]
    }
    """
    n_students = len(student_data)
    if n_students < 3:
        return {
            "status": "INSUFFICIENT_DATA",
            "message": f"K-Means clustering requires at least 3 students with performance history (current: {n_students}).",
            "min_required": 3,
            "current_count": n_students,
            "clusters": [],
            "students": [],
        }

    # Extract feature matrix
    features = []
    student_ids = []
    for s in student_data:
        apt = float(s.get("aptitude_score") or 0.0)
        cod = float(s.get("coding_score") or 0.0)
        test = float(s.get("avg_test_score") or 0.0)
        comp = float(s.get("completion_rate") or 0.0)
        streak = float(s.get("streak_days") or 0.0)
        features.append([apt, cod, test, comp, streak])
        student_ids.append(s.get("id"))

    X = np.array(features, dtype=float)

    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Determine k (up to 3 clusters, but at most n_students - 1)
    k = min(3, max(2, n_students // 2))

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)

    # Analyze cluster centroids on original scale to assign intelligent labels
    cluster_means = []
    for c in range(k):
        members_idx = np.where(labels == c)[0]
        if len(members_idx) > 0:
            c_data = X[members_idx]
            composite_score = float(np.mean(c_data[:, :3]))  # mean of apt, cod, test
            cluster_means.append((c, composite_score, len(members_idx), np.mean(c_data, axis=0)))
        else:
            cluster_means.append((c, 0.0, 0, np.zeros(5)))

    # Sort clusters descending by composite performance
    cluster_means.sort(key=lambda x: x[1], reverse=True)

    # Map cluster index to meaningful semantic labels
    label_map = {}
    if k == 3:
        semantic_labels = ["High Performer", "Developing", "Needs Attention"]
    elif k == 2:
        semantic_labels = ["Proficient", "Needs Attention"]
    else:
        semantic_labels = [f"Group {i+1}" for i in range(k)]

    cluster_summaries = []
    for rank, (cluster_idx, comp_score, count, means) in enumerate(cluster_means):
        sem_label = semantic_labels[rank]
        label_map[cluster_idx] = sem_label
        cluster_summaries.append({
            "cluster_id": cluster_idx,
            "label": sem_label,
            "student_count": count,
            "avg_aptitude": round(float(means[0]), 1),
            "avg_coding": round(float(means[1]), 1),
            "avg_test_score": round(float(means[2]), 1),
            "avg_completion": round(float(means[3]), 1),
            "avg_streak": round(float(means[4]), 1),
        })

    # Prepare per-student results
    assigned_students = []
    for i, s in enumerate(student_data):
        c_idx = int(labels[i])
        assigned_students.append({
            "student_id": s.get("id"),
            "full_name": s.get("full_name"),
            "email": s.get("email"),
            "cluster_id": c_idx,
            "performance_group": label_map.get(c_idx, "Developing"),
            "aptitude_score": s.get("aptitude_score"),
            "coding_score": s.get("coding_score"),
            "avg_test_score": s.get("avg_test_score"),
        })

    return {
        "status": "SUCCESS",
        "clusters": cluster_summaries,
        "students": assigned_students,
    }
