import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# Set judul dan ikon pada browser
st.set_page_config(
    page_title='Dashboard - PT Higo Fitur Indonesia',
    page_icon='📈',
    layout='wide'
)

# Sidebar logo
st.sidebar.image('Higo.jpg', use_container_width=True)

# Judul
st.title("📊 Dashboard Analisis Pengguna Digital - PT Higo Fitur Indonesia")

# Upload file Excel
uploaded_file = st.file_uploader("Unggah file Excel", type=["xlsx", "xls"])

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)

    # Buat variabel tambahan jika belum ada
    if 'Usia' not in df.columns:
        df['Usia'] = 2025 - df['Tahun Lahir']

    if 'Kategori Generasi' not in df.columns:
        def get_generation(year):
            if year <= 1964:
                return 'Boomers'
            elif 1965 <= year <= 1980:
                return 'Gen X'
            elif 1981 <= year <= 1996:
                return 'Gen Y'
            elif 1997 <= year <= 2012:
                return 'Gen Z'
            else:
                return 'Undefined'
        df['Kategori Generasi'] = df['Tahun Lahir'].apply(get_generation)

    # Sidebar filters
    st.sidebar.subheader("Filter Data")
    lokasi_filter = st.sidebar.multiselect("Pilih Nama Lokasi", options=df['Nama Lokasi'].unique(), default=df['Nama Lokasi'].unique())
    tipe_lokasi_filter = st.sidebar.multiselect("Pilih Tipe Lokasi", options=df['Tipe Lokasi'].unique(), default=df['Tipe Lokasi'].unique())
    generasi_filter = st.sidebar.multiselect("Pilih Kategori Generasi", options=df['Kategori Generasi'].unique(), default=df['Kategori Generasi'].unique())
    merk_hp_filter = st.sidebar.multiselect("Pilih Merk HP", options=df['Merk HP'].unique(), default=df['Merk HP'].unique())

    # Terapkan filter
    df = df[
        df['Nama Lokasi'].isin(lokasi_filter) &
        df['Tipe Lokasi'].isin(tipe_lokasi_filter) &
        df['Kategori Generasi'].isin(generasi_filter) &
        df['Merk HP'].isin(merk_hp_filter)
    ]

    st.subheader("Ringkasan Data")
    col1, col2, col3 = st.columns(3)
    col1.metric("Rata-rata Usia", f"{df['Usia'].mean():.2f} Tahun")
    col2.metric("Rata-rata Minat Digital", f"{df['Minat Digital'].mean():.2f}")
    col3.metric("Jumlah Pengguna", f"{len(df)}")

    st.markdown("---")

    # Confidence Interval untuk Usia
    st.subheader("Confidence Interval Rata-rata Usia (95%)")
    mean_age = df['Usia'].mean()
    std_dev = df['Usia'].std()
    n = len(df)
    z_score = 1.96
    margin_of_error = z_score * (std_dev / np.sqrt(n))
    lower_bound = mean_age - margin_of_error
    upper_bound = mean_age + margin_of_error

    st.write(f"Rata-rata usia: **{mean_age:.2f}** tahun")
    st.write(f"Interval kepercayaan 95%: **{lower_bound:.2f} - {upper_bound:.2f}** tahun")

    st.markdown("---")

    # Visualisasi
    st.subheader("Visualisasi Data")

    col4, col5 = st.columns(2)
    with col4:
        st.write("### Distribusi Usia Pengguna")
        fig, ax = plt.subplots()
        ax.hist(df['Usia'], bins=20, color='skyblue', edgecolor='black')
        ax.set_xlabel("Usia")
        ax.set_ylabel("Jumlah")
        st.pyplot(fig)

    with col5:
        st.write("### Persentase Penggunaan Merk HP")
        merk_counts = df['Merk HP'].value_counts()
        fig2, ax2 = plt.subplots()
        ax2.pie(merk_counts, labels=merk_counts.index, autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)

    st.write("### Rata-rata Minat Digital per Lokasi")
    avg_interest = df.groupby('Nama Lokasi')['Minat Digital'].mean().reset_index()
    chart = alt.Chart(avg_interest).mark_bar().encode(
        x=alt.X('Minat Digital:Q', title='Rata-rata Minat Digital'),
        y=alt.Y('Nama Lokasi:N', sort='-x'),
        color=alt.Color('Nama Lokasi:N', legend=None)
    ).properties(width=700, height=400)
    st.altair_chart(chart)

    st.markdown("---")
    st.subheader("📄 Data Lengkap")
    st.dataframe(df.reset_index(drop=True))
