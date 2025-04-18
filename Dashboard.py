import pandas as pd
import streamlit as st
import altair as alt
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from io import BytesIO

# Set judul dan ikon pada browser
st.set_page_config(
    page_title='PT Higo Fitur Indonesia',
    page_icon='📈',
    layout='wide'
)

# Sidebar logo (tampilan lebih proporsional)
st.sidebar.image('Higo.jpg', width=150)

# Judul
st.title("📊 Dashboard Analisis - PT Higo Fitur Indonesia")

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

    # Sidebar filters (select box biasa)
    st.sidebar.subheader("Filter Data")

    def selectbox_with_all(label, options):
        selected = st.sidebar.selectbox(f"Pilihan {label}", options=["All"] + sorted(list(set(options)))))
        return options if selected == "All" else [selected]

    lokasi_filter = selectbox_with_all("Nama Lokasi", df['Nama Lokasi'])
    tipe_lokasi_filter = selectbox_with_all("Tipe Lokasi", df['Tipe Lokasi'])
    generasi_filter = selectbox_with_all("Kategori Generasi", df['Kategori Generasi'])
    merk_hp_filter = selectbox_with_all("Merk HP", df['Merk HP'])

    # Terapkan filter
    df = df[
        df['Nama Lokasi'].isin(lokasi_filter) &
        df['Tipe Lokasi'].isin(tipe_lokasi_filter) &
        df['Kategori Generasi'].isin(generasi_filter) &
        df['Merk HP'].isin(merk_hp_filter)
    ]

    # Ringkasan Data (tetap pada 3 kolom)
    st.subheader("Ringkasan Data")
    col1, col2, col3 = st.columns(3)
    col1.markdown(f"<h4 style='color:red;'>Rata-rata Usia:<br> <b>{df['Usia'].mean():.2f} Tahun</b></h4>", unsafe_allow_html=True)
    col2.markdown(f"<h4 style='color:red;'>Rata-rata Minat Digital:<br> <b>{df['Minat Digital'].mean():.2f}</b></h4>", unsafe_allow_html=True)
    col3.markdown(f"<h4 style='color:red;'>Jumlah Pengguna:<br> <b>{len(df)}</b></h4>", unsafe_allow_html=True)

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
    st.subheader("📊 Visualisasi Data")

    # Distribusi Usia Pengguna
    st.write("### Distribusi Usia Pengguna")
    fig, ax = plt.subplots(figsize=(5, 3))  # Ukuran visualisasi disesuaikan
    ax.hist(df['Usia'], bins=20, color='skyblue', edgecolor='black')
    ax.set_xlabel("Usia")
    ax.set_ylabel("Jumlah")
    st.pyplot(fig)

    with st.expander("Lihat Tabel Distribusi Usia"):
        usia_dist = df['Usia'].value_counts().sort_index().reset_index()
        usia_dist.columns = ['Usia', 'Jumlah']
        st.dataframe(usia_dist)
        csv = usia_dist.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Unduh Tabel Distribusi Usia", csv, "distribusi_usia.csv", "text/csv")

    # Persentase Penggunaan Merk HP
    st.write("### Persentase Penggunaan Merk HP")
    merk_counts = df['Merk HP'].value_counts()
    fig2, ax2 = plt.subplots(figsize=(5, 3))  # Ukuran visualisasi disesuaikan
    ax2.pie(merk_counts, labels=merk_counts.index, autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)

    with st.expander("Lihat Tabel Persentase Merk HP"):
        merk_table = merk_counts.reset_index()
        merk_table.columns = ['Merk HP', 'Jumlah']
        st.dataframe(merk_table)
        csv = merk_table.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Unduh Tabel Merk HP", csv, "merk_hp.csv", "text/csv")

    # Rata-rata Minat Digital per Lokasi
    st.write("### Rata-rata Minat Digital per Lokasi")
    avg_interest = df.groupby('Nama Lokasi')['Minat Digital'].mean().reset_index()
    chart = alt.Chart(avg_interest).mark_bar().encode(
        x=alt.X('Minat Digital:Q', title='Rata-rata Minat Digital'),
        y=alt.Y('Nama Lokasi:N', sort='-x'),
        color=alt.Color('Nama Lokasi:N', legend=None)
    ).properties(width=500, height=300)  # Ukuran visualisasi disesuaikan
    st.altair_chart(chart)

    with st.expander("Lihat Tabel Rata-rata Minat Digital"):
        st.dataframe(avg_interest)
        st.download_button("📥 Unduh Tabel Minat Digital per Lokasi", avg_interest.to_csv(index=False).encode('utf-8'), "minat_lokasi.csv", "text/csv")

    # Jumlah Pengguna per Generasi
    st.write("### Jumlah Pengguna per Generasi")
    gen_count = df['Kategori Generasi'].value_counts().reset_index()
    gen_count.columns = ['Kategori Generasi', 'Jumlah']
    chart_gen = alt.Chart(gen_count).mark_bar().encode(
        x=alt.X('Jumlah:Q', title='Jumlah Pengguna'),
        y=alt.Y('Kategori Generasi:N', sort='-x'),
        color=alt.Color('Kategori Generasi:N', legend=None)
    ).properties(width=500, height=300)  # Ukuran visualisasi disesuaikan
    st.altair_chart(chart_gen)

    with st.expander("Lihat Tabel Jumlah per Generasi"):
        st.dataframe(gen_count)
        st.download_button("📥 Unduh Tabel Pengguna per Generasi", gen_count.to_csv(index=False).encode('utf-8'), "pengguna_generasi.csv", "text/csv")

    # Jumlah Pengguna per Lokasi dan Tipe Lokasi
    st.write("### Jumlah Pengguna per Lokasi dan Tipe Lokasi")
    lokasi_tipe = df.groupby(['Nama Lokasi', 'Tipe Lokasi']).size().reset_index(name='Jumlah')
    chart_loc = alt.Chart(lokasi_tipe).mark_circle(size=100).encode(
        x='Nama Lokasi:N',
        y='Tipe Lokasi:N',
        size='Jumlah:Q',
        color='Tipe Lokasi:N',
        tooltip=['Nama Lokasi', 'Tipe Lokasi', 'Jumlah']
    ).properties(width=500, height=300)  # Ukuran visualisasi disesuaikan
    st.altair_chart(chart_loc)

    with st.expander("Lihat Tabel Jumlah per Lokasi dan Tipe Lokasi"):
        st.dataframe(lokasi_tipe)
        st.download_button("📥 Unduh Tabel Lokasi & Tipe", lokasi_tipe.to_csv(index=False).encode('utf-8'), "lokasi_tipe.csv", "text/csv")

    st.markdown("---")
    st.subheader("📄 Data Lengkap")
    st.dataframe(df.reset_index(drop=True))
