# FraudLens — System Architecture

**Status:** Approved Day 2 design. Source of truth alongside PRD and Implementation Blueprint.
**Scope note:** This is a static-artifact, no-backend architecture. There is no server process handling requests other than Streamlit's own script-rerun model. There is no database. This is intentional per the PRD (no auth, no persistence, no real-time streaming).

---

## 1. Component Diagram

```mermaid
flowchart TB
    subgraph Offline["Offline / One-Time (Days 2-5)"]
        DS[("Bank Account Fraud\nDataset (Base.csv)")]
        NB["Jupyter Notebooks\n(cleaning + training)"]
        MODEL[["fraud_model.pkl\nscaler.pkl\nfeature_columns.pkl"]]
        DS --> NB --> MODEL
    end

    subgraph Streamlit["Streamlit Web App (Live)"]
        UI["Browser UI\n(file uploader, tables, charts)"]
        APP["app.py\n(Streamlit script)"]
        PRE["utils/preprocessing.py"]
        EXP["utils/explain.py"]
        UI <--> APP
        APP --> PRE
        APP --> EXP
        APP --> MODEL
    end

    subgraph PowerBI["Power BI (Desktop Artifact)"]
        PBIX[["FraudLens_Report.pbix"]]
        PBIDATA["cleaned_base.csv"]
        PBIDATA --> PBIX
    end

    subgraph GitHub["GitHub Repository"]
        REPO[("uroojey/fraudlens")]
    end

    MODEL --> REPO
    PBIX --> REPO
    APP --> REPO
    REPO --> CLOUD["Streamlit Community Cloud"]
    CLOUD --> UI

    style Offline fill:#F2F6F6,stroke:#2F5B5E
    style Streamlit fill:#E8F7F2,stroke:#02C39A
    style PowerBI fill:#FDECEC,stroke:#F96167
    style GitHub fill:#EFEFEF,stroke:#333
```

**Key point:** MODEL (the trained model + scaler + feature list) is produced once, offline, in Days 4-5. It is committed to the repo and loaded read-only by the Streamlit app at runtime. It is never retrained inside the live app.

---

## 2. Data Flow

```mermaid
flowchart LR
    A["User's CSV\n(transactions)"] -->|"1. Upload via\nst.file_uploader"| B["Streamlit App"]
    B -->|"2. Same preprocessing\nas training"| C["preprocessing.py"]
    C -->|"3. Cleaned + scaled\nfeatures"| D["Loaded Model\n(fraud_model.pkl)"]
    D -->|"4. Predictions +\nprobabilities"| E["explain.py\n(rule-based reasons)"]
    E -->|"5. Results table +\ncharts + explanations"| F["Browser Display"]
```

**Critical constraint carried over from the blueprint (Day 6 debugging notes):** step 2 must use the *exact same* preprocessing function used during model training (Day 3/4). This is why `utils/preprocessing.py` is a shared module imported by both the training notebook and `app.py` — not duplicated logic in two places.

---

## 3. Request Lifecycle (Streamlit App)

Streamlit does not have traditional HTTP request/response endpoints — the entire script re-runs top to bottom on every user interaction. This lifecycle replaces a typical "API request" sequence:

```mermaid
sequenceDiagram
    participant U as User (Browser)
    participant S as Streamlit Runtime
    participant P as preprocessing.py
    participant M as fraud_model.pkl
    participant E as explain.py

    U->>S: Opens app URL
    S->>U: Renders empty upload page
    U->>S: Uploads CSV via file_uploader
    S->>S: Re-runs app.py script top to bottom
    S->>P: Pass raw uploaded dataframe
    P->>S: Return cleaned/encoded/scaled dataframe
    S->>M: model.predict() + model.predict_proba()
    M->>S: Return predictions + probabilities
    S->>E: Pass row + feature importances
    E->>S: Return plain-language explanation string
    S->>U: Render summary metric, chart, ranked table, explanations
```

Because there's no persistent session on a server beyond Streamlit's own in-memory session state, nothing is saved between visits — this matches the PRD's explicit exclusion of persistence/accounts.

---

## 4. AI/Model Interaction

There is no external AI API call in this project (no LLM, no third-party ML API). "AI interaction" here refers purely to loading a **locally trained Scikit-learn model** at runtime:

```mermaid
flowchart TB
    A["App startup"] --> B{"Model files\npresent in /models?"}
    B -->|Yes| C["joblib.load() the 3 files:\nfraud_model.pkl\nscaler.pkl\nfeature_columns.pkl"]
    B -->|No| D["Show friendly error:\n'Model not found — contact repo owner'"]
    C --> E["Model held in memory\nfor this session"]
    E --> F["Used for every prediction\nuntil app restarts/sleeps"]
```

## 5. External Services

| Service | Role | Cost | Auth Required? |
|---|---|---|---|
| GitHub | Source control + deployment source | Free | Yes (your existing account) |
| Streamlit Community Cloud | Hosts the live app, auto-redeploys on git push | Free | Sign in with GitHub |
| Power BI Desktop | Builds the report file locally | Free | No (Desktop app itself doesn't require sign-in to build/save a `.pbix`) |
| Kaggle | One-time dataset download | Free | Yes (to download the dataset in Day 2) |

**Note on the Day 2 scope change:** Power BI service (the cloud publish/share step) is **not used** in this architecture, per today's decision to avoid Microsoft account setup. The `.pbix` file is a static artifact stored in the GitHub repo and demonstrated via screen recording, not a live hosted service.
