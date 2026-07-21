#!/bin/bash
set -e

# ==============================================================================
# Polymarket Intelligence Lab - MLOps Self-Learning Loop
# ==============================================================================
# Runs once a day to:
# 1. Fetch Ground Truth (Closed Markets)
# 2. Merge with historical features
# 3. Train the Supervised XGBoost Classifier
# 4. Log the new "Brain" to MLflow
# ==============================================================================

echo "================================================================="
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] Starting MLOps Self-Learning Loop"
echo "================================================================="

cd "$(dirname "$0")/.."

# Build the training dataset (Downloads closed markets and merges with history)
echo "1. Building MLOps Dataset..."
~/.local/bin/poetry run python -m src.storage.mlops_dataset

# Train the supervised model and register in MLflow
echo "2. Training Supervised Model..."
~/.local/bin/poetry run python -m src.models.train_supervised

echo "================================================================="
echo "[$(date -u +"%Y-%m-%dT%H:%M:%SZ")] MLOps Loop Completed Successfully"
echo "================================================================="
