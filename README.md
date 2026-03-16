# venturalitica-scenario-huderia-cobra-public-sector

**HUDERIA COBRA Fundamental Rights Impact Assessment for Public Sector AI Systems**

A 5-minute demo of the Venturalitica SDK's native **HUDERIA COBRA** support, implementing the Council of Europe Framework Convention on Artificial Intelligence for evaluating AI impact on human rights, democracy, and rule of law in public sector deployments.

## What is HUDERIA?

**HUDERIA** (Human Rights, Democracy and Rule of Law Impact Assessment) is a non-binding Council of Europe methodology published in February 2026 for evaluating AI systems' impact on fundamental rights. It complements the EU AI Act and GDPR with a human rights lens.

This scenario demonstrates how to operationalize **HUDERIA's COBRA** (Context-Based Risk Analysis) methodology using automated compliance gates. HUDERIA prescribes *what* to evaluate; Venturalitica implements *how* to measure it operationally:

- **Development Gate** (HUDERIA Resource B): Post-training evaluation of fairness, privacy, and data quality
- **Deployment Gate** (HUDERIA Resource C): Stricter pre-deployment controls before model release to production

## Scenario: Public Sector Coverage Prediction

This demo uses the **ACSPublicCoverage** dataset (US Census Bureau American Community Survey) to predict public health insurance coverage. The scenario implements:

- **Context**: EU public sector (GDPR + Equal Treatment Directive)
- **Protected attributes**: Race (RAC1P), Gender (SEX)
- **Regulatory constraints**:
  - k-anonymity ≥ 20 (design), l-diversity ≥ 5 (deployment)
  - Demographic parity difference < 0.05 (strict fairness)
  - Data completeness ≥ 0.95

## Quick Start

### Installation

```bash
# Clone and enter the scenario directory
git clone <repo> && cd venturalitica-scenario-huderia-cobra-public-sector

# Install dependencies
uv sync
```

### Run the Demo

```bash
# Execute the full HUDERIA assessment (G2 + G3 gates)
uv run python main.py
```

**Output** (2-3 minutes):

```
Loading ACSPublicCoverage dataset from Census Bureau...
Dataset shape: (150000, 104)
Training RandomForest model...
============================================================
GATE G2: Post-Training Evaluation (Design & Development)
============================================================
Enforcing HUDERIA COBRA Resource B controls...
G2 Results: {"passed": true, "controls": {...}, ...}

============================================================
GATE G3: Pre-Release Evaluation (Deployment Readiness)
============================================================
Enforcing HUDERIA COBRA Resource C controls...
G3 Results: {"passed": true, "controls": {...}, ...}

============================================================
HUDERIA ASSESSMENT SUMMARY
============================================================
G2 (Design) Status: PASS
G3 (Deployment) Status: PASS
Evidence vault: .venturalitica/
============================================================
```

### Inspect Results

```bash
# View the assessment results
cat .venturalitica/huderia_assessment.json

# View detailed execution traces
cat .venturalitica/trace_*.json
```

## HUDERIA Controls Implemented

**Note**: HUDERIA defines what to evaluate (Resources A, B, C); Venturalitica operationalizes this through automated gates. The development gate below implements HUDERIA Resource B controls.

### Development Gate: Design & Development Controls (HUDERIA Resource B)

| Control | Metric | Threshold | Purpose |
|---------|--------|-----------|---------|
| **B.5.1** Data Completeness | `data_completeness` | ≥ 0.95 | High-integrity datasets |
| **B.5.1** Class Balance | `class_imbalance` | < 0.70 | Avoid representation bias |
| **B.5.2** Privacy | `k_anonymity` | ≥ 20 | Quasi-identifier protection |
| **B.5.3** Data Integrity | `provenance_completeness` | ≥ 0.90 | Audit trail tracking |
| **B.6.1** Causal Fairness | `causal_fairness_diagnostic` | ≥ 0.75 | Causal independence |
| **B.6.1** Output Parity | `disparate_impact` | ≥ 0.90 | Selection rate fairness |
| **B.6.1** Counterfactual | `counterfactual_fairness` | ≥ 0.80 | Protected attribute independence |
| **B.6.3** Demographic Parity | `demographic_parity_diff` | < 0.05 | Equal opportunity |
| **B.6.3** Equal Opportunity | `equal_opportunity_diff` | < 0.05 | True positive rate parity |
| **B.6.3** Equalized Odds | `equalized_odds_ratio` | ≥ 0.90 | TPR + FPR equalization |
| **B.6.3** Predictive Parity | `predictive_parity` | ≥ 0.85 | Precision parity |
| **B.6.5** Model Performance | `f1_score` | ≥ 0.70 | Minimum effectiveness |

### Deployment Gate: Pre-Release / Deployment Controls (HUDERIA Resource C)

| Control | Metric | Threshold | Purpose |
|---------|--------|-----------|---------|
| **C.1.1** L-Diversity | `l_diversity` | ≥ 5 | Sensitive outcome diversity per QI group |
| **C.1.1** T-Closeness | `t_closeness` | < 0.15 | Distribution divergence limit |
| **C.1.2** Data Minimization | `data_minimization` | ≥ 0.60 | Minimize sensitive attributes |
| **C.2.1** Equalized Odds | `equalized_odds_ratio` | ≥ 0.95 | Strict deployment fairness |
| **C.2.1** Disparate Impact | `disparate_impact` | ≥ 0.95 | Strict 95% rule |
| **C.2.1** Counterfactual | `counterfactual_fairness` | ≥ 0.90 | Causal fairness at deployment |

## Policy Files

Two OSCAL YAML policies are pre-configured with sector-specific thresholds:

- **`policies/huderia-cobra-design.oscal.yaml`** — Development gate (HUDERIA Resource B: post-training evaluation)
- **`policies/huderia-cobra-prerelease.oscal.yaml`** — Deployment gate (HUDERIA Resource C: pre-deployment evaluation)

Both policies include detailed comments explaining threshold selection for public sector context (GDPR, Equal Treatment Directive).

### Customize Thresholds

Edit the `threshold` field in either policy to adjust for your risk tolerance:

```yaml
- control-id: B.6.3-eval-demographic-parity
  props:
    - name: threshold
      value: "0.10"  # Relax from 0.05 to 0.10
```

## Regulatory Alignment

This scenario demonstrates compliance with:

- **EU AI Act**: Art 6 (high-risk), Art 9 (risk management), Art 10 (data), Art 15 (fairness)
- **GDPR**: Art 6 (lawfulness), Art 9 (special categories), Art 22 (automated decisions)
- **Equal Treatment Directive**: Non-discrimination on grounds of race, nationality, gender
- **Council of Europe Convention on AI**: HUDERIA COBRA methodology

## Documentation

- **SDK HUDERIA Mapping**: [compliance-mapping.md](../packages/venturalitica-sdk/docs/compliance-mapping.md#huderia-council-of-europe-framework-convention-on-ai)
- **HUDERIA Templates**: [SDK policies/templates/](../packages/venturalitica-sdk/src/venturalitica/policies/templates/)
- **HUDERIA Spec**: [Council of Europe Framework Convention on Artificial Intelligence](https://www.coe.int/en/web/artificial-intelligence/coe-ai-convention)

## CI/CD Integration

To integrate HUDERIA compliance gates into a production pipeline:

```bash
# Block model promotion if development gate fails
VENTURALITICA_STRICT=true uv run python main.py

# Or run gates independently:
VENTURALITICA_STRICT=true python -c "
import venturalitica as vl
results = vl.enforce(
    data=eval_df,
    policy='policies/huderia-cobra-design.oscal.yaml',
    target='target',
    prediction='prediction',
    strict=True  # Raises exception on failure
)
"
```

## License

This scenario is part of Venturalitica and follows the same license terms.

## Next Steps

1. **Customize thresholds** for your regulatory context
2. **Integrate into CI/CD** using `VENTURALITICA_STRICT=true`
3. **Add your own metrics** via custom policy extensions
4. **Report** to governance dashboards via the SDK's evidence collection

Questions? Open an issue or visit the [Venturalitica docs](../packages/venturalitica-sdk/docs/).
