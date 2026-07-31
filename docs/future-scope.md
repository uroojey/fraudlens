# FraudLens — Future Scope

## Next 3 Months: Deepen What Already Works

**Explainability upgrade.** Replace the rule-based "why flagged" logic with real SHAP values. The current explanation approach was a deliberate v1.0 simplification (documented in the PRD's exclusions), but SHAP would give per-transaction, mathematically grounded attribution instead of a coefficient-times-scaled-value heuristic — directly building on the scaling bug we found and fixed during Day 8's QA pass.

**Fairness study using the dataset's other 5 variants.** The Bank Account Fraud dataset was originally published for fairness research across 6 variants — we deliberately used only "Base" for v1.0 scope control. A natural next step: compare model performance and fraud-flagging rates across demographic-sensitive variants, and publish findings as a dedicated analysis. This turns a scope exclusion into a genuine second project.

**Threshold as a user-facing control.** Day 5 taught us that threshold tuning matters more than model choice on imbalanced data. Right now the threshold is fixed at training time. Exposing a slider in the Streamlit app ("show me fraud flags at X% confidence") would let a fraud analyst tune the precision/recall trade-off live, based on their own team's review capacity.

## Next 6 Months: Real-Time & Broader Model Coverage

**Real-time single-transaction scoring API.** Currently batch-CSV-only (an explicit v1.0 exclusion). A lightweight FastAPI endpoint wrapping the same saved model would let this plug into a real transaction pipeline instead of requiring manual CSV exports — the natural evolution once batch screening proves useful.

**Model retraining pipeline.** Right now the model is trained once, statically, in a notebook. A scheduled retraining job (using new labeled data as it becomes available) would keep the model from drifting — directly relevant since Day 4/5 showed fraud rate itself drifts over the 8 simulated months in this very dataset.

**Ensemble revisit.** Day 5's finding — Logistic Regression beat Random Forest even after fair threshold tuning — was legitimate for this dataset and sample size. Worth revisiting with the full 1M rows (not the 200K sample used for speed) and additional techniques (XGBoost, gradient boosting) to see if the finding holds at scale.

## Next 12 Months: Product Maturity

**User accounts and case management.** A fraud analyst reviewing flagged transactions currently has no way to mark "reviewed," "confirmed fraud," or "false positive" and have that persist. Adding lightweight accounts + a database (explicitly excluded from v1.0) would turn this from a scoring tool into a real workflow tool.

**Multi-tenant deployment.** Currently a single shared instance. A bank or fintech evaluating this seriously would need isolated deployments per organization, with their own uploaded data never touching another tenant's.

**Power BI live publishing.** Day 2's decision to skip Power BI service (avoiding Microsoft account setup) was the right v1.0 call, but a mature product would publish live, filterable reports rather than a static file + recording — worth revisiting once the underlying data pipeline supports scheduled refresh.

**Automated model monitoring.** Track precision/recall drift over time in production, alert when the model's real-world performance diverges from its Day 5 baseline — closing the loop between "we validated this once" and "we know it still works."