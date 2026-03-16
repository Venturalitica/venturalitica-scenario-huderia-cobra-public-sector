#!/usr/bin/env python3
"""
HUDERIA Fundamental Rights Impact Assessment Demo
Public Sector Coverage Prediction using ACSPublicCoverage Dataset

This script demonstrates the Venturalitica SDK's HUDERIA support for evaluating
AI system impact on fundamental rights (privacy, non-discrimination) in public sector
deployments. The assessment follows the Council of Europe HUDERIA COBRA methodology
with two gates: G2 (design/dev) and G3 (pre-release/deployment).

Usage:
    uv run python main.py

Outputs:
    .venturalitica/
        trace_<session>.json        # Execution trace with metrics
        results.json                # HUDERIA gate results (PASS/FAIL per control)
        Annex_IV.md                 # Technical documentation
"""

import logging

import pandas as pd
from folktables import ACSDataSource, ACSPublicCoverage
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

import venturalitica as vl

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_data():
    """Load ACSPublicCoverage dataset from folktables."""
    logger.info("Loading ACSPublicCoverage dataset from Census Bureau...")

    source = ACSDataSource(
        survey_year='2018',
        horizon='1-Year',
        survey='person'
    )

    # Fetch data for California (smaller subset for demo)
    data = source.get_data(states=['CA'], download=True)
    df, labels, _ = ACSPublicCoverage.df_to_pandas(data)

    logger.info(f"Dataset shape: {df.shape}")
    logger.info(f"Columns: {list(df.columns)[:10]}...")  # First 10 columns
    logger.info(f"Target variable (PUBCOV): {labels.value_counts().to_dict()}")

    return df, labels


def train_model(X_train, y_train):
    """Train a simple RandomForest model for coverage prediction."""
    logger.info("Training RandomForest model...")

    model = RandomForestClassifier(
        n_estimators=50,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    logger.info(f"Model trained. Features: {X_train.shape[1]}")
    return model


def gate_g2_design_eval(df, labels, model, X_test):
    """
    Gate G2: Post-Training Evaluation (Design & Development)

    Evaluates:
    - Data quality (completeness, class balance, privacy)
    - Model fairness across protected attributes (race, gender)
    - Model performance metrics
    """
    logger.info("\n" + "="*60)
    logger.info("GATE G2: Post-Training Evaluation (Design & Development)")
    logger.info("="*60)

    # Generate predictions for fairness evaluation
    y_pred = model.predict(X_test)
    y_test = labels.iloc[X_test.index]

    # Create evaluation dataframe with predictions
    eval_df = X_test.copy()
    eval_df['target'] = y_test.values
    eval_df['prediction'] = y_pred

    # Enforce HUDERIA COBRA B controls (design phase)
    logger.info("Enforcing HUDERIA COBRA Resource B controls...")

    g2_results = vl.enforce(
        data=eval_df,
        policy="policies/huderia-cobra-design.oscal.yaml",
        target="target",
        prediction="prediction",
        dimension="RAC1P",  # Race dimension for fairness analysis
        strict=False  # Warnings, not exceptions (for demo)
    )

    logger.info(f"G2 Results: {str(g2_results)}")
    return g2_results, eval_df


def gate_g3_prerelease_eval(eval_df):
    """
    Gate G3: Pre-Release Evaluation (Deployment Readiness)

    Enforces stricter privacy and fairness controls before model promotion
    in production model registries (SageMaker, MLflow).
    """
    logger.info("\n" + "="*60)
    logger.info("GATE G3: Pre-Release Evaluation (Deployment Readiness)")
    logger.info("="*60)

    # Enforce HUDERIA COBRA C controls (prerelease/deployment)
    logger.info("Enforcing HUDERIA COBRA Resource C controls...")

    g3_results = vl.enforce(
        data=eval_df,
        policy="policies/huderia-cobra-prerelease.oscal.yaml",
        target="target",
        prediction="prediction",
        dimension="RAC1P",
        strict=False
    )

    logger.info(f"G3 Results: {str(g3_results)}")
    return g3_results


def main():
    """Main HUDERIA assessment pipeline."""
    logger.info("Starting HUDERIA Fundamental Rights Assessment...")
    logger.info("Scenario: Public Sector Coverage Prediction (ACSPublicCoverage)")

    # Step 1: Load data
    df, labels = load_data()

    # Step 2: Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        df, labels, test_size=0.3, random_state=42, stratify=labels
    )
    logger.info(f"Train/test split: {X_train.shape[0]} / {X_test.shape[0]}")

    # Step 3: Train model
    model = train_model(X_train, y_train)

    # Step 4: Gate G2 (Design & Development)
    g2_results, eval_df = gate_g2_design_eval(df, labels, model, X_test)

    # Step 5: Gate G3 (Pre-Release / Deployment)
    g3_results = gate_g3_prerelease_eval(eval_df)

    # Summary
    logger.info("\n" + "="*60)
    logger.info("HUDERIA ASSESSMENT SUMMARY")
    logger.info("="*60)

    # Count passed controls
    g2_passed = sum(1 for r in g2_results if r.passed)
    g2_total = len(g2_results)
    g3_passed = sum(1 for r in g3_results if r.passed)
    g3_total = len(g3_results)

    logger.info(f"G2 (Design): {g2_passed}/{g2_total} controls passed")
    logger.info(f"G3 (Deployment): {g3_passed}/{g3_total} controls passed")
    logger.info(f"Evidence vault: .venturalitica/")
    logger.info("="*60)

    # Results are automatically collected in .venturalitica/ via SDK's Evidence Vault
    # Follow the SDK's transparent artifact pattern - artifacts generated automatically
    # The SDK generates:
    # - trace_<session>.json (execution trace with metrics, AST analysis, probes)
    # - results.json (compliance control results per gate)
    # - .venturalitica/ directory (evidence vault)
    # Do NOT save explicit JSON - this is the SDK's responsibility

    logger.info("Assessment complete. Artifacts stored in .venturalitica/")
    logger.info("View compliance results: cat .venturalitica/results.json")
    logger.info("View execution trace: cat .venturalitica/trace_*.json")
    logger.info("View dashboard: uv run venturalitica ui")


if __name__ == "__main__":
    main()
