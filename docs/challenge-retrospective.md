# FraudLens — Challenge Retrospective
**#60DayClaudeChallenge Capstone, Days 1–10**

## Timeline

**Day 1 — Discovery.** Started with a rough idea ("fraud detection, classification, anomaly detection") and no dataset. A structured interview narrowed scope against real constraints: 1-2 hours/day, beginner Scikit-learn comfort, "some exposure" to dashboards. The first real decision was the dataset itself — rejecting the overused Kaggle credit card dataset in favor of the Bank Account Fraud Dataset (NeurIPS 2022, feedzai), chosen specifically for industry credibility over convenience. PRD, 10-Day Blueprint, and Pitch Deck approved before any code was written.

**Day 2 — System Design.** Architecture, schema, API (interface) design, and wireframes — all before touching code. The first scope negotiation happened here: rejecting Power BI service publishing to avoid Microsoft account setup, choosing a `.pbix` file + recording instead. This decision rippled through the PRD, blueprint, and every later day's plan — a small early call with real downstream consequences.

**Day 3 — Foundation.** Environment setup turned into real debugging: three separate Python installations on one machine, a venv that inherited 300+ Anaconda packages, file-lock errors from a running debugger, an incomplete venv from an interrupted creation. None of this was in any tutorial — it was genuine "why doesn't this work" troubleshooting, resolved methodically rather than by trial and error alone.

**Day 4 — First Model.** Baseline Logistic Regression: 82.3% recall, 4.5% precision on a ~1.1% fraud rate. The key lesson here wasn't the model — it was learning why accuracy is meaningless on imbalanced data, and reading a confusion matrix correctly for the first time in a real project rather than a tutorial.

**Day 5 — The Random Forest Detour.** This was the hardest technical day. Random Forest with `class_weight='balanced'` caught only 5 of 441 fraud cases — a near-total failure. Switching to `class_weight='balanced_subsample'` helped marginally (13 caught). The real fix was realizing the problem wasn't the model — it was the default 0.5 decision threshold, wrong for a ~1% positive class. Threshold tuning via precision-recall curves closed the gap, but even then, Logistic Regression's F1 (0.086) beat tuned Random Forest's (0.065). The simpler model won, honestly, after a fair fight — not a fallback, a real finding.

**Day 6 — First Working App.** Streamlit core build: upload, preprocess, predict, display. Required building `save_imputation_values.py` to solve a real problem — new uploads needed the exact same imputation values used in training, which only existed inside a notebook until then.

**Day 7 — Polish, Deploy, First Production Bug.** Merged UX polish with deployment (a deliberate schedule compression, approved explicitly rather than assumed). Deployed live via Streamlit Community Cloud on the first attempt — then discovered the live app's explanations were silently falling back to generic text. Root cause: a `.gitignore` rule (`*.csv`) meant to exclude the large raw dataset was also blocking the small `feature_importance.csv` the app needed. First real "works on my machine, broken in production" debugging experience.

**Day 8 — QA Deep Dive.** A dedicated release-readiness review caught a subtler bug than Day 7's: the explanation feature was technically working, but computing feature contributions using raw unscaled values against coefficients trained on scaled data — a dimensional mismatch that produced plausible-looking but not-quite-correct explanations. Fixed by passing properly scaled values through instead. Also added encoding-safe CSV reading, numeric-type validation, and matplotlib figure cleanup to prevent memory buildup.

**Day 9 — The Power BI Sprint.** Built the entire Power BI report in one session after it had been deferred twice. Reconstructed one-hot-encoded categories back into readable single columns using DAX `SWITCH` formulas (since the model-ready data had split "payment type" into 5 separate binary columns). Applied full dark-theme styling to match the Streamlit app's aesthetic. Then hit a genuine production snag: the `.pbix` file was 117MB, over GitHub's 100MB limit — traced to Power BI internally storing all ~52 columns even though only ~12 were used by any visual. Removing unused columns dropped the file to 56KB.

**Day 10 — Graduation.** Final review, documentation, and release.

## Major Technical Decisions & Pivots

1. **Dataset choice over convenience** (Day 1) — chose industry credibility over the "easy" well-known dataset.
2. **Power BI Desktop-only, no cloud publish** (Day 2) — a real constraint (avoiding account setup) reshaping architecture and three separate documents.
3. **Simpler model wins** (Day 5) — Logistic Regression beat Random Forest after a fair, threshold-tuned comparison. Resisting the urge to assume "more complex = better."
4. **Schedule compression by explicit approval, twice** (Days 6+7 merged; Power BI deferred then caught up in one sprint) — deliberate trade-offs, not silent scope creep.

## Debugging Moments Worth Remembering

- Multi-Python-install venv contamination (Day 3)
- Random Forest's catastrophic recall failure and its real cause: bootstrap sampling diluting an already-rare class (Day 5)
- `.gitignore` silently blocking a needed file in production (Day 7)
- A scaling unit-mismatch bug that "looked" fine but wasn't (Day 8)
- A 117MB file traced to unused columns (Day 9)

## Skills Demonstrated

Data cleaning and leakage-checking, imbalanced classification, threshold tuning via precision-recall curves, model comparison methodology, Streamlit app development, shared preprocessing architecture (train/serve consistency), Power BI DAX and data modeling, git/GitHub troubleshooting, production debugging across two completely different deployment surfaces (Streamlit Cloud, GitHub file limits), and honest technical documentation throughout.

## Final Project Summary

FraudLens is a two-tool fraud detection system — a live Streamlit app for transaction-level screening and a Power BI report for business-level trend analysis — sharing one trained Logistic Regression model. Built in 10 days at 1-2 hours/day, it went from an undefined idea to a publicly deployed, professionally documented v1.0 product, with every major technical decision documented and every production bug found through genuine testing rather than luck.

## Lessons Learned

- Scoping the dataset matters as much as scoping the code.
- The simplest model that wins a fair comparison is the right model — complexity isn't a proxy for quality.
- Bugs that "look right" are more dangerous than bugs that crash loudly.
- Production environments (a live server, a git repository's file limits) surface problems no local test will ever catch.
- Real documentation, written honestly (including what doesn't work and why), is worth more than a polished README hiding the messy parts.

## Farewell

We started this on Day 1 with a vague idea and a blank repository, and I want you to notice what actually got you here — not luck, and not me. It was the willingness to stop and debug the Random Forest failure properly instead of accepting a bad number. It was catching your own footer decision reversal and asking for confirmation instead of just changing it silently. It was the instinct to ask "is this safe?" before authorizing GitHub access, and to push back on "built with Claude" when you decided you didn't want it there. Those are the habits of someone who builds real things, not just someone who follows a tutorial.

FraudLens works. It's live, it's documented, and the model comparison you ran on Day 5 is more rigorous than plenty of published tutorials I've seen. Take that confidence into whatever you build next — on Day 61 and beyond, you won't have a daily prompt template to follow, and that's exactly when this kind of judgment starts to matter most.