# This tool supports: semantic comparison of utterances; cosine similarity matrix display; and threshold-based similarity filtering.
# To run it:
```bash
# streamlit run streamlit_cosine_tool.py

import streamlit as st
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Title and description
st.set_page_config(page_title="Cosine Similarity Tool", layout="centered")
st.title("🔍 Streamlit Cosine Similarity Tool")
st.write("Compare the semantic similarity between two or more utterances using sentence-transformer embeddings.")

# Model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Input section
st.header("Enter Utterances")
utterances = st.text_area("Enter one utterance per line:", height=200)

if utterances:
    utterance_list = [u.strip() for u in utterances.strip().split("\n") if u.strip()]
    if len(utterance_list) < 2:
        st.warning("Please enter at least two utterances.")
    else:
        # Generate embeddings
        embeddings = model.encode(utterance_list)
        # Compute cosine similarity
        sim_matrix = cosine_similarity(embeddings)

        # Display results
        st.header("Cosine Similarity Matrix")
        df_sim = pd.DataFrame(sim_matrix, index=utterance_list, columns=utterance_list)
        st.dataframe(df_sim.style.background_gradient(cmap="coolwarm").format("{:.2f}"))

        # Find pairs above threshold
        st.header("Similar Utterance Pairs")
        threshold = st.slider("Similarity threshold", 0.5, 1.0, 0.85)
        results = []
        for i in range(len(utterance_list)):
            for j in range(i + 1, len(utterance_list)):
                if sim_matrix[i][j] >= threshold:
                    results.append({
                        "Utterance 1": utterance_list[i],
                        "Utterance 2": utterance_list[j],
                        "Similarity": round(sim_matrix[i][j], 2)
                    })

        if results:
            st.dataframe(pd.DataFrame(results))
        else:
            st.info("No utterance pairs found above the selected threshold.")
