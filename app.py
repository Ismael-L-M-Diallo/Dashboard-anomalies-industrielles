import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

st.set_page_config(layout="wide")
st.title("Dashboard Détection Anomalies Énergie France")

contamination = st.sidebar.slider("Sensibilité (%)", 0.5, 5.0, 1.5, 0.1) / 100

@st.cache_data
def load_data():
    df = pd.read_csv('hourly_sample.csv')
    df['datetime_hour'] = pd.to_datetime(df['datetime_hour'])
    return df.sort_values('datetime_hour')

df = load_data()
st.info(f" {len(df):,} lignes | {df['datetime_hour'].min().date()} → {df['datetime_hour'].max().date()}")

data = df['conso_elec_mw'].dropna()
scaler = StandardScaler()
model = IsolationForest(contamination=contamination, random_state=42)
df['is_anomaly'] = model.fit_predict(scaler.fit_transform(data.values.reshape(-1,1))) == -1

fig = go.Figure()
fig.add_trace(go.Scatter(x=df['datetime_hour'], y=df['conso_elec_mw'], mode='lines', name='Conso'))
fig.add_trace(go.Scatter(x=df[df['is_anomaly']]['datetime_hour'], y=df[df['is_anomaly']]['conso_elec_mw'], 
                        mode='markers', name='Anomalies', marker=dict(color='red', size=8)))
st.plotly_chart(fig, height=500)

col1, col2 = st.columns(2)
col1.metric("Points", f"{len(df):,}")
col2.metric("Anomalies", df['is_anomaly'].sum())
