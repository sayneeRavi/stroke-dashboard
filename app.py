# app.py

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Medical Stats Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("healthcare-dataset-stroke-data.csv")
    df['bmi'].fillna(df['bmi'].median(), inplace=True)

    # Feature engineering
    bins = [0, 18, 30, 45, 60, 75, 100]
    labels = ['0–17', '18–30', '31–45', '46–60', '61–75', '76+']
    df['age_group'] = pd.cut(df['age'], bins=bins, labels=labels)

    def bmi_category(bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif 18.5 <= bmi < 25:
            return 'Normal'
        elif 25 <= bmi < 30:
            return 'Overweight'
        else:
            return 'Obese'

    df['bmi_category'] = df['bmi'].apply(bmi_category)

    return df

df = load_data()

# -------------------- Sidebar Filters --------------------
st.sidebar.title("🧪 Filter Data")
gender = st.sidebar.multiselect("Gender", df['gender'].unique(), default=df['gender'].unique())
hypertension = st.sidebar.multiselect("Hypertension", df['hypertension'].unique(), default=df['hypertension'].unique())
heart_disease = st.sidebar.multiselect("Heart Disease", df['heart_disease'].unique(), default=df['heart_disease'].unique())

df_filtered = df[
    (df['gender'].isin(gender)) &
    (df['hypertension'].isin(hypertension)) &
    (df['heart_disease'].isin(heart_disease))
]

# -------------------- KPIs --------------------
st.title("📊 Stroke & Medical Insights Dashboard")

col1, col2, col3 = st.columns(3)
stroke_rate = df_filtered['stroke'].mean() * 100
col1.metric("🧠 Stroke Rate", f"{stroke_rate:.2f} %")

col2.metric("💉 Avg Glucose", f"{df_filtered['avg_glucose_level'].mean():.2f}")
col3.metric("⚖️ Avg BMI", f"{df_filtered['bmi'].mean():.2f}")

# Insight Summary Section
st.markdown("### 📝 Insight Summary")

# Calculate stroke rate for filtered group
group_stroke_rate = df_filtered['stroke'].mean() * 100
overall_stroke_rate = df['stroke'].mean() * 100
rate_diff = group_stroke_rate - overall_stroke_rate

# Glucose level interpretation
avg_glucose = df_filtered['avg_glucose_level'].mean()
if avg_glucose < 100:
    glucose_status = "normal"
elif avg_glucose < 126:
    glucose_status = "prediabetic"
else:
    glucose_status = "diabetic"

# Compose paragraph
summary = f"""
Among patients with selected conditions — gender: {', '.join(gender)}, hypertension: {', '.join(map(str, hypertension))}, and heart disease: {', '.join(map(str, heart_disease))} — the stroke rate is **{group_stroke_rate:.2f}%**.

This is {'higher' if rate_diff > 0 else 'lower'} than the overall average stroke rate of **{overall_stroke_rate:.2f}%**.  
The average glucose level for this group is **{avg_glucose:.2f} mg/dL**, which falls into the **{glucose_status}** range.

These insights suggest that stroke risk may be influenced by metabolic factors like glucose, even in the absence of hypertension or heart disease. Age remains a strong predictive feature based on trends observed in age group comparisons.
"""

st.markdown(summary)


# -------------------- Charts --------------------

st.subheader("🧬 Stroke Distribution")
fig_pie = px.pie(df_filtered, names='stroke', title='Stroke (0 = No, 1 = Yes)', color_discrete_sequence=px.colors.sequential.RdBu)
st.plotly_chart(fig_pie, use_container_width=True)

st.subheader("📈 Stroke by Age Group")
fig_bar = px.bar(df_filtered.groupby('age_group')['stroke'].mean().reset_index(),
                 x='age_group', y='stroke', title="Stroke Rate by Age Group")
st.plotly_chart(fig_bar, use_container_width=True)

st.subheader("📊 Glucose Level by Stroke")
fig_box = px.box(df_filtered, x='stroke', y='avg_glucose_level', color='stroke',
                 title="Avg Glucose by Stroke")
st.plotly_chart(fig_box, use_container_width=True)

