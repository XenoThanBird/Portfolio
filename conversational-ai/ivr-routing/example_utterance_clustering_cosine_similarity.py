

# Utterance Clustering Using Cosine Similarity
# This notebook demonstrates how to use sentence embeddings and cosine similarity to cluster similar utterances, useful for NLU optimization, intent cleanup, and conflict detection in IVR systems.
# Note: This can be converted into a .ipynb for use in jupyter or colab.

# In[ ]:


# Step 1: Install & Import Libraries
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import AgglomerativeClustering
from sentence_transformers import SentenceTransformer
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np


# In[ ]:


# Step 2: Load Utterances
utterances = [
    "I need to pay my bill",
    "How much do I owe?",
    "What's the amount due?",
    "Please tell me my balance",
    "My internet is not working",
    "The WiFi is down",
    "Can you reset my router?",
    "I want to schedule a technician",
    "Book a repair appointment"
]
df = pd.DataFrame(utterances, columns=["utterance"])
df.head()


# In[ ]:


# Step 3: Generate Embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(df['utterance'].tolist())


# In[ ]:


# Step 4: Compute Cosine Similarity Matrix
similarity_matrix = cosine_similarity(embeddings)
sns.heatmap(similarity_matrix, annot=True, xticklabels=df['utterance'], yticklabels=df['utterance'], cmap="coolwarm")
plt.xticks(rotation=90)
plt.title("Cosine Similarity Between Utterances")
plt.show()


# In[ ]:


# Step 5: Cluster Utterances
clustering = AgglomerativeClustering(n_clusters=None, distance_threshold=0.4, affinity='cosine', linkage='average')
labels = clustering.fit_predict(embeddings)
df['cluster'] = labels
df.sort_values(by='cluster')
