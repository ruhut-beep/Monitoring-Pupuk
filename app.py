import streamlit as st
import pandas as pd
import datetime

st.set_page_config(page_title="Aplikasi Realisasi Pupuk Region 4", layout="wide")

st.title("🌱 Aplikasi Monitoring Realisasi Pupuk - Region 4")
st.markdown("---")

@st.cache_data
def load_data():
    df = pd.read_excel('LHA Bahan 2026-01-01 - 2026-10-10.xlsx')
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
    df['Bulan_Nama'] = df['Tanggal'].dt.strftime('%B')
    df['Hari'] = df['Tanggal'].dt.day
    return df

df_raw = load_data()

# Sidebar Filters
st.sidebar.header("🔍 Filter Dashboard")

# 1. Estate Filter (7 Estate Options)
estate_options = ["SEMUA", "SDME", "SAGE", "SBHE", "SCME", "BKLE", "BHGE", "SMME"]
selected_estate = st.sidebar.selectbox("Pilih Estate:", estate_options)

# 2. Month Filter
bulan_dict = {
    "SEMUA": None,
    "Januari": 1, "Februari": 2, "Maret": 3, "April": 4,
    "Mei": 5, "Juni": 6, "Juli": 7, "Agustus": 8,
    "September": 9, "Oktober": 10, "November": 11, "Desember": 12
}
selected_month_name = st.sidebar.selectbox("Pilih Bulan:", list(bulan_dict.keys()))

# 3. Day Filter (1 - 31)
day_options = ["SEMUA"] + list(range(1, 32))
selected_day = st.sidebar.selectbox("Pilih Tanggal (1-31):", day_options)

# 4. Jenis Pupuk Filter
pupuk_list = ["SEMUA"] + sorted(list(df_raw[df_raw['Kelompok Pekerjaan']=='PEMUPUKAN KELAPA SAWIT']['Nama Bahan'].dropna().unique()))
selected_pupuk = st.sidebar.selectbox("Pilih Jenis Pupuk:", pupuk_list)

# Filter Data Logic
filtered_df = df_raw.copy()

if selected_estate != "SEMUA":
    filtered_df = filtered_df[filtered_df['Estate'] == selected_estate]

if selected_month_name != "SEMUA":
    m_num = bulan_dict[selected_month_name]
    filtered_df = filtered_df[filtered_df['Bulan'] == m_num]

if selected_day != "SEMUA":
    filtered_df = filtered_df[filtered_df['Hari'] == int(selected_day)]

if selected_pupuk != "SEMUA":
    filtered_df = filtered_df[filtered_df['Nama Bahan'] == selected_pupuk]

# KPI Metrics
st.subheader("📊 Key Performance Metrics")
col1, col2, col3, col4 = st.columns(4)
total_kg = filtered_df['Jumlah Bahan'].sum()
total_transaksi = len(filtered_df)
estate_count = filtered_df['Estate'].nunique()
pupuk_count = filtered_df['Nama Bahan'].nunique()

col1.metric("Total Pemakaian Pupuk", f"{total_kg:,.2f} Kg")
col2.metric("Jumlah Transaksi LHA", f"{total_transaksi:,}")
col3.metric("Estate Tercover", f"{estate_count} Estate")
col4.metric("Varian Pupuk", f"{pupuk_count} Jenis")

st.markdown("---")

# Tab Layout
tab1, tab2, tab3, tab4 = st.tabs(["📊 Rekapan Per Bulan", "📦 Rekapan Per Jenis Pupuk", "🏞️ Rekapan Per Estate", "📋 Update Data & Tabel Transaksi"])

with tab1:
    st.subheader("Rekapan Realisasi Pemupukan Per Bulan (Kg)")
    piv_month = pd.pivot_table(df_raw if selected_pupuk=="SEMUA" else df_raw[df_raw['Nama Bahan']==selected_pupuk], 
                               values='Jumlah Bahan', index='Bulan', columns='Estate', aggfunc='sum', fill_value=0)
    st.dataframe(piv_month.style.format("{:,.2f}"), use_container_width=True)

with tab2:
    st.subheader("Rekapan Pemakaian Per Jenis Pupuk")
    summary_pupuk = filtered_df.groupby('Nama Bahan')['Jumlah Bahan'].sum().reset_index()
    summary_pupuk['Persentase (%)'] = (summary_pupuk['Jumlah Bahan'] / summary_pupuk['Jumlah Bahan'].sum()) * 100
    summary_pupuk = summary_pupuk.sort_values(by='Jumlah Bahan', ascending=False)
    st.dataframe(summary_pupuk.style.format({'Jumlah Bahan': '{:,.2f}', 'Persentase (%)': '{:.2f}%'}), use_container_width=True)

with tab3:
    st.subheader("Rekapan Pemakaian Per Estate")
    summary_estate = filtered_df.groupby('Estate')['Jumlah Bahan'].sum().reset_index()
    summary_estate['Persentase (%)'] = (summary_estate['Jumlah Bahan'] / summary_estate['Jumlah Bahan'].sum()) * 100
    summary_estate = summary_estate.sort_values(by='Jumlah Bahan', ascending=False)
    st.dataframe(summary_estate.style.format({'Jumlah Bahan': '{:,.2f}', 'Persentase (%)': '{:.2f}%'}), use_container_width=True)

with tab4:
    st.subheader("Data Transaksi LHA & Input Update Data")
    st.dataframe(filtered_df, use_container_width=True)
