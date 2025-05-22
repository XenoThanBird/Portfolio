# This tool uses libpostal to normalize address inputs, and includes: 
### Streamlit UI for address viewing and preprocessing; 
### Machine learning pipeline with TfidfVectorizer + LogisticRegression;
### Outputs classification report and accuracy
### Be sure to install libpostal before using this tool:
```bash
# brew install libpostal   # macOS
# sudo apt install libpostal-dev   # Debian/Ubuntu
# pip install postal 

import pandas as pd
import streamlit as st
import numpy as np
from postal.parser import parse_address
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

st.set_page_config(page_title="Address Training Pipeline", layout="wide")
st.title("Address Recognition & Training Pipeline (IVR + libpostal + ML)")

# Upload data
uploaded_file = st.file_uploader("Upload address samples (CSV with 'raw_address' and 'label')", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("Raw Address Data")
    st.dataframe(df.head())

    # Normalize using libpostal
    st.subheader("libpostal Normalization")
    def normalize_address(addr):
        try:
            parsed = parse_address(addr)
            return " ".join([token for token, label in parsed])
        except:
            return addr

    df["normalized"] = df["raw_address"].apply(normalize_address)
    st.dataframe(df[["raw_address", "normalized"]].head())

    # TF-IDF and ML classification (e.g., predict region, service area, zip type)
    st.subheader("ML Classification Example")

    if "label" in df.columns:
        X_train, X_test, y_train, y_test = train_test_split(df["normalized"], df["label"], test_size=0.2, random_state=42)

        vectorizer = TfidfVectorizer(ngram_range=(1, 2), max_features=1000)
        X_train_vec = vectorizer.fit_transform(X_train)
        X_test_vec = vectorizer.transform(X_test)

        clf = LogisticRegression(max_iter=200)
        clf.fit(X_train_vec, y_train)
        y_pred = clf.predict(X_test_vec)

        st.text("Classification Report")
        st.text(classification_report(y_test, y_pred))
        st.text(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")
    else:
        st.warning("Please include a 'label' column in your CSV for classification.")
