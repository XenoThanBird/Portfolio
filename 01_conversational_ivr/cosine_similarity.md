*Utterance Clustering Using Cosine Similarity

*This script groups semantically similar utterances using sentence embeddings and cosine similarity. It’s designed to assist with:
	-	Cleaning up NLU utterances
	-	Reducing intent conflicts in conversational bots
	-	Preprocessing data for Kore.ai and other LLM/NLP platforms

 *Features
	-	Generates sentence embeddings using sentence-transformers (all-MiniLM-L6-v2)
	-	Computes cosine similarity matrix
	-	Visualizes similarity with a heatmap
	-	Performs Agglomerative Clustering to identify semantic groups

 *Sample Utterances Clustered
 ```python
[
    "I need to pay my bill",
    "How much do I owe?",
    "My internet is not working",
    "Can you reset my router?",
    "I want to schedule a technician"
]

*Requirements

*Install dependencies:
```bash
pip install pandas scikit-learn sentence-transformers matplotlib seaborn

*How to Run
```bash
python utterance_clustering_cosine_similarity.py

 The script outputs a dataframe of utterances and their assigned cluster, and generates a cosine similarity heatmap for visual inspection.

*Example Output:

| Utterance | Cluster |
| I need to pay my bill | 0 |
| How much do I owe? | 0 |
|My internet is not working | 1 |
| Can you reset my router? | 1 |
| I want to schedule a technician | 2 |


*Use Cases
	-	Create new intent groupings for IVR systems
	-	Detect overlapping utterances across multiple bots
	-	Optimize training data for Few-Shot or Zero-Shot NLU models
