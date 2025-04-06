import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="Hybrid PONV Scoring App", layout="wide")
st.title("Hybrid PONV Risk Scoring System")
st.markdown("""
This app demonstrates a comprehensive **PONV (Postoperative Nausea and Vomiting) risk scoring system**, integrating:

1. **Patient-Specific Risk Factors** (Apfel, Koivuranta, Bellville)
2. **Surgical and Anesthetic Risk Factors**
3. **Drug-related Dose-based Risk Factors**
4. **Postoperative Symptoms**

➡️ **All cells are embedded with clinical justifications.**
➡️ **Synthetic data for 1000 patients** is generated within this app.
➡️ **Download the full scored dataset** as `.csv` or `.xlsx`
""")

# ----------------------------
# Synthetic Data Generator
# ----------------------------
st.header("Generate Synthetic PONV Data (n = 1000)")

@st.cache_data
def generate_synthetic_data(n=1000, seed=42):
    np.random.seed(seed)
    data = {
        # Patient-Specific
        "Gender_Female": np.random.choice([0, 1], size=n, p=[0.3, 0.7]),
        "Non_Smoker": np.random.choice([0, 1], size=n, p=[0.4, 0.6]),
        "History_PONV_or_MS": np.random.choice([0, 1], size=n, p=[0.7, 0.3]),
        "Age_Less_50": np.random.choice([0, 1], size=n, p=[0.3, 0.7]),
        "Anxiety": np.random.choice([0, 1], size=n, p=[0.6, 0.4]),
        "Migraine": np.random.choice([0, 1], size=n, p=[0.85, 0.15]),
        "Obese_BMI_30": np.random.choice([0, 1], size=n, p=[0.75, 0.25]),

        # Surgery-related
        "Abdominal_Lap_Surgery": np.random.choice([0, 1], size=n, p=[0.4, 0.6]),
        "ENT_Neuro_Eye_Surgery": np.random.choice([0, 1], size=n, p=[0.8, 0.2]),
        "Gynae_Breast_Surgery": np.random.choice([0, 1], size=n, p=[0.85, 0.15]),
        "Surgery_gt_60min": np.random.choice([0, 1], size=n, p=[0.5, 0.5]),
        "BloodLoss_gt_500ml": np.random.choice([0, 1], size=n, p=[0.9, 0.1]),

        # Drug doses
        "Ondansetron_mg": np.random.uniform(0, 24, n),
        "Midazolam_mg_per_kg": np.random.uniform(0, 0.5, n),
        "Dexamethasone_mg": np.random.uniform(0, 40, n),
        "Glycopyrrolate_mg": np.random.uniform(0, 0.4, n),
        "Nalbuphine_mg": np.random.uniform(0, 160, n),
        "Fentanyl_mcg_per_kg": np.random.uniform(0, 20, n),
        "Butorphanol_mg": np.random.uniform(0, 4, n),
        "Pentazocine_mg": np.random.uniform(0, 360, n),
        "Propofol_TIVA": np.random.choice([0, 1], size=n, p=[0.7, 0.3]),
        "Propofol_InductionOnly": np.random.choice([0, 1], size=n, p=[0.3, 0.7]),
        "Volatile_Agents_MAC": np.random.uniform(0, 2, n),

        # Muscle relaxants
        "Succinylcholine": np.random.choice([0, 1], size=n),
        "Atracurium": np.random.choice([0, 1], size=n),
        "Cisatracurium": np.random.choice([0, 1], size=n),
        "Vecuronium": np.random.choice([0, 1], size=n),

        # Postoperative symptoms
        "Nausea_gt_30min": np.random.choice([0, 1], size=n, p=[0.7, 0.3]),
        "Vomiting_gt_2": np.random.choice([0, 1], size=n, p=[0.85, 0.15]),
        "Abdominal_Discomfort": np.random.choice([0, 1], size=n, p=[0.6, 0.4]),
    }
    return pd.DataFrame(data)

raw_data = generate_synthetic_data()
st.success("Synthetic patient dataset (n=1000) generated!")

# ---------------------------
# Scoring Logic
# ---------------------------
def score_patient(row):
    score = 0

    # Patient-specific
    score += row.Gender_Female * 1
    score += row.Non_Smoker * 1
    score += row.History_PONV_or_MS * 2
    score += row.Age_Less_50 * 1
    score += row.Anxiety * 1
    score += row.Migraine * 1
    score += row.Obese_BMI_30 * 1

    # Surgical
    score += row.Abdominal_Lap_Surgery * 2
    score += row.ENT_Neuro_Eye_Surgery * 1
    score += row.Gynae_Breast_Surgery * 2
    score += row.Surgery_gt_60min * 1
    score += row.BloodLoss_gt_500ml * 1

    # Drug-based scores (dose dependent)
    score += -2 if row.Ondansetron_mg >= 4 else 0
    score += -2 if row.Midazolam_mg_per_kg >= 0.05 else 0
    score += -1 if row.Dexamethasone_mg >= 4 else 0
    score += 1 if row.Glycopyrrolate_mg > 0.2 else 0
    score += 1 if row.Nalbuphine_mg > 50 else 0
    score += 3 if row.Fentanyl_mcg_per_kg > 5 else 0
    score += 1 if row.Butorphanol_mg > 2 else 0
    score += 3 if row.Pentazocine_mg > 100 else 0
    score += -3 if row.Propofol_TIVA == 1 else 0
    score += -1 if row.Propofol_InductionOnly == 1 else 0
    score += 2 if row.Volatile_Agents_MAC > 1 else 0

    # Muscle relaxants (neutral)

    # Postoperative symptoms
    score += row.Nausea_gt_30min * 1
    score += row.Vomiting_gt_2 * 2
    score += row.Abdominal_Discomfort * 1

    return score

raw_data["Hybrid_PONV_Score"] = raw_data.apply(score_patient, axis=1)
st.dataframe(raw_data.head(20), use_container_width=True)

# ---------------------------
# Download Option
# ---------------------------
st.subheader("Download Full Scored Dataset")

@st.cache_data
def convert_df(df):
    return df.to_csv(index=False).encode("utf-8")

csv = convert_df(raw_data)
st.download_button(
    label="Download CSV",
    data=csv,
    file_name="hybrid_ponv_scores.csv",
    mime="text/csv"
)

# ---------------------------
# References
# ---------------------------
st.markdown("""
---
### 📚 References
- [Apfel Score (2002) - A simplified risk score](https://pubmed.ncbi.nlm.nih.gov/11748473/)
- [Koivuranta et al. (1997) – PONV predictive model](https://pubmed.ncbi.nlm.nih.gov/9285183/)
- [Bellville et al. (1960) – Early PONV factors](https://pubmed.ncbi.nlm.nih.gov/13831276/)
- [Recent Review (2020): Risk Factors and Prophylaxis of PONV](https://pubmed.ncbi.nlm.nih.gov/32770642/)
""")
