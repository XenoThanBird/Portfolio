# What it does: 
### Accepts income_sources.csv and monthly_expenses.csv
### Plots income vs expenses over time
### Highlights surplus visually
### Outputs surplus summary table

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Passive Income Dashboard", layout="wide")
st.title("Passive Income Tracker")

# Upload income and expense files
col1, col2 = st.columns(2)
with col1:
    income_file = st.file_uploader("Upload Income Sources CSV", type="csv", key="income")
with col2:
    expense_file = st.file_uploader("Upload Monthly Expenses CSV", type="csv", key="expenses")

if income_file and expense_file:
    df_income = pd.read_csv(income_file)
    df_expenses = pd.read_csv(expense_file)

    st.subheader("Monthly Passive Income")
    st.dataframe(df_income)
    st.subheader("Monthly Expenses")
    st.dataframe(df_expenses)

    # Merge on 'month'
    df_income['month'] = pd.to_datetime(df_income['month'])
    df_expenses['month'] = pd.to_datetime(df_expenses['month'])
    df_merged = pd.merge(df_income, df_expenses, on="month", how="inner")

    # Calculate surplus
    df_merged["surplus"] = df_merged["total_income"] - df_merged["total_expenses"]

    st.subheader("Income vs. Expenses Over Time")
    fig, ax = plt.subplots()
    ax.plot(df_merged["month"], df_merged["total_income"], label="Income", marker="o")
    ax.plot(df_merged["month"], df_merged["total_expenses"], label="Expenses", marker="x")
    ax.fill_between(df_merged["month"], df_merged["total_income"], df_merged["total_expenses"],
                    where=(df_merged["total_income"] > df_merged["total_expenses"]),
                    interpolate=True, color="green", alpha=0.3, label="Surplus")
    ax.legend()
    ax.set_title("Monthly Financial Overview")
    ax.set_ylabel("USD")
    st.pyplot(fig)

    st.subheader("Surplus Summary")
    st.dataframe(df_merged[["month", "surplus"]].set_index("month"))

else:
    st.info("Upload both income and expense files to generate dashboard.")
