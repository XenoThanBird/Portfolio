# 1. Toolkit & Notebook Starter Template
# Purpose: Gives a clear structure for every Python mini-project or production script. Clean, readable, team-ready.
#python

# --------------------------------------
# Project: [Insert Project Name]
# Author: Matthan Bird
# Date: [Insert Date]
# Description: [Short project description]
# --------------------------------------

# === Imports ===
import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# === Global Variables ===
DATA_DIR = "data/"
OUTPUT_DIR = "outputs/"

# === Functions ===
def load_data(filepath):
    """Loads data from a CSV file."""
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def clean_data(df):
    """Cleans and preprocesses the dataframe."""
    # TODO: Add data cleaning steps
    return df

def main():
    """Main execution function."""
    data_path = os.path.join(DATA_DIR, "your_file.csv")
    df = load_data(data_path)
    
    if df is not None:
        df = clean_data(df)
        # TODO: Add analysis or modeling steps
        print(df.head())
    else:
        print("Data load failed. Exiting program.")

# === Run Script ===
if __name__ == "__main__":
    main()

2. SQL Query Boilerplate Template
Purpose: Keeps everyone's SQL organized and readable.
sql

-- --------------------------------------
-- Purpose: [Short description of what this query does]
-- Author: Matthan Bird
-- Date: [Insert Date]
-- --------------------------------------

-- Parameters
-- DECLARE @StartDate DATE = '2024-01-01';
-- DECLARE @EndDate DATE = '2024-12-31';

WITH BaseData AS (
    SELECT
        user_id,
        transaction_date,
        amount
    FROM transactions
    WHERE transaction_date BETWEEN '2024-01-01' AND '2024-12-31'
)

, AggregatedData AS (
    SELECT
        user_id,
        SUM(amount) AS total_spent
    FROM BaseData
    GROUP BY user_id
)

SELECT *
FROM AggregatedData
ORDER BY total_spent DESC;

#3. Jupyter Notebook Boilerplate
#Purpose: Keeps all team notebooks structured and easier to review/share.
markdown

# Project Title

## Purpose
Brief overview of the project's goals.

---

## 1. Setup

#python
# Imports
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Settings
%matplotlib inline
pd.set_option('display.max_columns', None)

#2. Data Load
#python

# Load the dataset
df = pd.read_csv("path/to/data.csv")
df.head()

3. Exploratory Data Analysis (EDA)
#python

# Summary statistics
df.describe()

# Missing values
df.isnull().sum()

4. Data Cleaning
#python

# Cleaning steps (dropping missing values, fixing types, etc.)
df.dropna(inplace=True)


#4. Cosine Similarity Starter Template (Python)
#Purpose: Template for text similarity, semantic clustering, or search ranking tasks.
#python

# --------------------------------------
# Project: Text Cosine Similarity Analysis
# Author: Matthan Bird
# --------------------------------------

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

# === Sample Text Data ===
texts = [
    "How to reset my password?",
    "I forgot my password, how can I change it?",
    "What is the refund policy?",
    "Can I return a product after 30 days?"
]

# === Vectorization ===
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(texts)

# === Cosine Similarity Calculation ===
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

# === Cosine Similarity Matrix Display ===
cosine_df = pd.DataFrame(cosine_sim, index=texts, columns=texts)
print(cosine_df)

# === Find Most Similar Texts (Optional) ===
def find_most_similar(text_index, similarity_matrix):
    similarities = similarity_matrix[text_index]
    most_similar = similarities.argsort()[::-1][1]  # Skipping itself
    return most_similar

index = 0  # Compare first question
most_similar_index = find_most_similar(index, cosine_sim)
print(f"Text most similar to '{texts[index]}' is '{texts[most_similar_index]}'")

#5. LLM/NLP Experiment Boilerplate
#Purpose: Sets up quick experiments using HuggingFace, OpenAI, or any GenAI model.
#python

# --------------------------------------
# Project: Quick LLM Experiment Template
# Author: Matthan Bird
# --------------------------------------

from transformers import pipeline

# === Model Initialization ===
generator = pipeline("text-generation", model="gpt2")

# === Input Prompt ===
prompt = "Once upon a time, there was a programmer who"

# === Generate Text ===
outputs = generator(prompt, max_length=100, num_return_sequences=1)

# === Display Result ===
for i, output in enumerate(outputs):
    print(f"Generated Text {i+1}:\n{output['generated_text']}")

#Switch "gpt2" to "openai-gpt" or "facebook/opt-1.3b" or whatever easily.

#6. Data Cleaning Universal Script
#Purpose: Standardizes a starting point for new datasets.
#python

# --------------------------------------
# Project: Universal Data Cleaner
# Author: Matthan Bird
# --------------------------------------

import pandas as pd

def load_data(filepath):
    return pd.read_csv(filepath)

def clean_data(df):
    # === Drop completely empty rows
    df.dropna(how='all', inplace=True)

    # === Fill missing numerical values with 0
    num_cols = df.select_dtypes(include=['float64', 'int64']).columns
    df[num_cols] = df[num_cols].fillna(0)

    # === Fill missing categorical values with 'Unknown'
    cat_cols = df.select_dtypes(include=['object']).columns
    df[cat_cols] = df[cat_cols].fillna('Unknown')

    # === Lowercase all column names
    df.columns = [col.lower() for col in df.columns]
    
    return df

def save_clean_data(df, output_path):
    df.to_csv(output_path, index=False)

# === Example Usage ===
if __name__ == "__main__":
    df = load_data("path/to/raw_data.csv")
    df_cleaned = clean_data(df)
    save_clean_data(df_cleaned, "path/to/cleaned_data.csv")

#Now you have one cleaning script to rule them all!

#7. Folder Structure Auto-Generator (Python Script)
Purpose: Quickly make clean project folders.
#python

# --------------------------------------
# Project: Folder Structure Generator
# Author: Matthan Bird
# --------------------------------------

import os

def create_project_structure(project_name):
    folders = [
        "data/raw",
        "data/processed",
        "scripts",
        "notebooks",
        "outputs/figures",
        "outputs/models",
        "tests",
        "docs"
    ]
    for folder in folders:
        path = os.path.join(project_name, folder)
        os.makedirs(path, exist_ok=True)
    print(f"Project '{project_name}' structure created successfully.")

# === Example Usage ===
if __name__ == "__main__":
    create_project_structure("my_new_project")

#8. Matplotlib Quick Plot Template
#Purpose: Gives your team a ready-to-go plotting script, so no one struggles setting up basic visualizations.
#python

# --------------------------------------
# Project: Quick Plot Template
# Author: Matthan Bird
# --------------------------------------

import matplotlib.pyplot as plt
import pandas as pd

# === Sample Data ===
data = {'Category': ['A', 'B', 'C', 'D'],
        'Values': [23, 45, 12, 30]}

df = pd.DataFrame(data)

# === Bar Plot ===
plt.figure(figsize=(8, 5))
plt.bar(df['Category'], df['Values'])
plt.xlabel('Category')
plt.ylabel('Values')
plt.title('Simple Bar Plot')
plt.grid(True)
plt.tight_layout()
plt.show()

# === Save the plot ===
plt.savefig("outputs/figures/bar_plot.png")

#9. Pandas EDA Fast Report Template
#Purpose: Auto-generate quick statistical profiles of any dataset — no more wasting time doing it manually.
#python

# --------------------------------------
# Project: EDA Fast Report
# Author: Matthan Bird
# --------------------------------------

import pandas as pd

def generate_eda_report(df):
    print("=== Data Info ===")
    print(df.info())
    print("\n=== Data Head ===")
    print(df.head())
    print("\n=== Data Describe ===")
    print(df.describe())
    print("\n=== Missing Values ===")
    print(df.isnull().sum())
    print("\n=== Value Counts ===")
    for col in df.select_dtypes(include='object').columns:
        print(f"\nValue counts for {col}:\n{df[col].value_counts()}")

# === Example Usage ===
if __name__ == "__main__":
    df = pd.read_csv("path/to/your/data.csv")
    generate_eda_report(df)

#10. Task Automation Boilerplate (Command Line Tool Basics)
#Purpose: Gives you the ability to automate repetitive tasks with CLI tools.
#python

# --------------------------------------
# Project: Simple CLI Tool Template
# Author: Matthan Bird
# --------------------------------------

import argparse

def main(input_file, output_file):
    # === Placeholder functionality: Copy file contents
    with open(input_file, 'r') as f:
        content = f.read()

    with open(output_file, 'w') as f:
        f.write(content)

    print(f"Copied content from {input_file} to {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple file copier CLI tool.")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--output", required=True, help="Output file path")
    
    args = parser.parse_args()
    
    main(args.input, args.output)

python cli_tool.py --input data.txt --output copy_data.txt

#11. Plotly Dashboard Boilerplate (Interactive Web Dashboards)
#Purpose: Builds interactive dashboards right using Python.
#python

# --------------------------------------
# Project: Interactive Plotly Dashboard Starter
# Author: Matthan Bird
# --------------------------------------

import pandas as pd
import plotly.express as px
import plotly.io as pio

# === Sample Data ===
df = pd.DataFrame({
    "Category": ["A", "B", "C", "D"],
    "Sales": [100, 200, 150, 300]
})

# === Create Interactive Bar Chart ===
fig = px.bar(df, x="Category", y="Sales", title="Sales by Category")

# === Show in Browser ===
fig.show()

# === Save as HTML file ===
pio.write_html(fig, file="outputs/figures/sales_dashboard.html", auto_open=True)
# === You can share the HTML dashboard with anyone — no server needed. # === Fully interactive (hover, zoom, filter, etc.,). === #

# 12. SQLite Local Database Template (No server needed)
# Purpose: Gives a quick way to persist project data without needing real backend infrastructure.
# python

# --------------------------------------
# Project: SQLite Database Starter
# Author: Matthan Bird
# --------------------------------------

import sqlite3
import pandas as pd

# === Connect to Database (creates if not exists) ===
conn = sqlite3.connect('data/project_data.db')
cursor = conn.cursor()

# === Create a Table ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    amount REAL,
    description TEXT
)
''')

# === Insert Sample Data ===
sample_data = [
    (749.17, "Investment Return"),
    (-11.54, "Utilities")
]
cursor.executemany('INSERT INTO transactions (amount, description) VALUES (?, ?)', sample_data)

conn.commit()

# === Query Data ===
df = pd.read_sql_query('SELECT * FROM transactions', conn)
print(df)

conn.close()
# === Instantly save data across script runs — without needing PostgreSQL, AWS, etc. # ===

# 13. FastAPI Server Starter Template (Create Web APIs easily)
# Purpose: Allows you to quickly turn any Python script into an API endpoint.
# python

# --------------------------------------
# Project: FastAPI Starter
# Author: Matthan Bird
# --------------------------------------

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to Matthan's Starter API!"}

@app.get("/echo/{text}")
def echo_text(text: str):
    return {"you_said": text}

# Run this server by typing:
# uvicorn filename:app --reload
# === Launches a full web server in 30 seconds. # === Great for building microservices or internal tools.

# 14. GitHub Actions Starter (Automated Workflow)
# Purpose: Automatically run code checks, tests, or deploys when you push to GitHub — no human babysitting needed.
# yaml

# .github/workflows/python-app.yml

name: Python application

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Lint with flake8
      run: |
        pip install flake8
        flake8 .
# === Every time you push code Git will automatically run checks.

# 15. Secrets Management Template (Environment Variables)
# Purpose: Keep API keys, passwords, and sensitive info safe — not hardcoded in scripts.
# python

# --------------------------------------
# Project: Environment Variable Loader
# Author: Matthan Bird
# --------------------------------------

import os
from dotenv import load_dotenv

# === Load environment variables from .env file ===
load_dotenv()

API_KEY = os.getenv('API_KEY')
DB_PASSWORD = os.getenv('DB_PASSWORD')

print(f"My API Key is: {API_KEY}")
# === Create a .env file (NOT pushed to GitHub): # ===
dotenv

# .env
API_KEY="your-api-key-here"
DB_PASSWORD="your-db-password-here"

# do not post the script to any team Gits
