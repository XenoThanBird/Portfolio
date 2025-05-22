# This tool includes: confidence score distribution histogram; fallback trigger rate via pie chart; and top misclassified intent pairs.
# To run it:
```bash
# streamlit run llm_analytics_dashboard.py

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="LLM Analytics Dashboard", layout="wide")
st.title("LLM Performance Analytics Dashboard")

# Upload CSV
uploaded_file = st.file_uploader("Upload LLM Output Log CSV", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Raw Data Preview")
    st.dataframe(df.head())

    # Plot: Confidence Score Distribution
    st.subheader("Confidence Score Distribution")
    if 'confidence_score' in df.columns:
        fig, ax = plt.subplots()
        sns.histplot(df['confidence_score'], bins=20, kde=True, ax=ax)
        ax.set_title("Distribution of Confidence Scores")
        ax.set_xlabel("Confidence Score")
        ax.set_ylabel("Frequency")
        st.pyplot(fig)
    else:
        st.warning("Column 'confidence_score' not found in uploaded file.")

    # Plot: Fallback vs. Success
    st.subheader("Fallback Trigger Rate")
    if 'status' in df.columns:
        fallback_counts = df['status'].value_counts()
        fig, ax = plt.subplots()
        fallback_counts.plot.pie(autopct='%1.1f%%', ax=ax)
        ax.set_ylabel('')
        ax.set_title("Routing Status Breakdown")
        st.pyplot(fig)

    # Top Misclassified Intents
    st.subheader("Top Intent Failures")
    if 'intent_label' in df.columns and 'expected_intent' in df.columns:
        df_errors = df[df['intent_label'] != df['expected_intent']]
        top_mistakes = df_errors.groupby(['expected_intent', 'intent_label']).size().reset_index(name='count')
        st.dataframe(top_mistakes.sort_values('count', ascending=False).head(10))
    else:
        st.warning("Expected columns 'intent_label' and/or 'expected_intent' not found.")
