import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

#KODE TERAKHIR DIBUAT
# --- Autentikasi Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gcred"], scope)
client = gspread.authorize(creds)
spreadsheet = client.open_by_url("https://docs.google.com/spreadsheets/d/1z8i_J3rylC0w-kuKRu_PZ-UfbgrdF8a9w8i2s5CFjz4")
worksheet = spreadsheet.sheet1

# Ambil data dari spreadsheet
try:
    data = worksheet.get_all_records()
    df = pd.DataFrame(data)
except:
    df = pd.DataFrame(columns=[
        "No", "NAMA", "GDP", "Gelar BELAKANG", "JABATAN", "JK", "TTL",
        "kode OPD", "PENDIDIKAN AWAL", "PENDIDIKAN AKHIR", "USIA", "OPD"
    ])

# --- Konfigurasi Streamlit ---
st.set_page_config(page_title="Dinas Komuniasi dan Informatika", layout="wide")

# CSS Styling
st.markdown("""
    <style>
        .main { background-color: #fdfcf9; }
        .card {
            padding: 1.5rem; background-color: #f0f4f8; border-radius: 1rem;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05); text-align: center;
        }
        .card h3 { margin: 0.5rem 0 0.2rem 0; font-size: 1.5rem; }
        .card p { margin: 0; font-size: 1rem; color: #555; }
        .st-emotion-cache-18ni7ap { justify-content: flex-end; }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <h1 style='text-align: center;'>Dinas Komunikasi dan Informatika</h1>
    <p style='text-align: center;'>Data dan Statistik Pegawai Negeri Sipil Non-Guru</p>
    <hr>
""", unsafe_allow_html=True)

# Navigasi
menu = st.sidebar.radio("Navigasi", ["Home", "Data Pegawai", "Tabel Pegawai", "Hasil Analisis"])

if menu == "Home":
    col1, col2, col3, col4 = st.columns(4)
    total_pegawai = len(df)
    laki_laki = df[df['JK'].str.upper().str.contains("LAKI")].shape[0]
    perempuan = df[df['JK'].str.upper().str.contains("PEREMPUAN|WANITA|CEWEK|P")].shape[0]
    total_opd = df['OPD'].nunique()
    pendidikan_tertinggi = df['PENDIDIKAN AKHIR'].mode()[0] if not df.empty else "-"

    with col1:
        st.markdown(f"""
            <div class="card">
                <p>🧑‍💼 Total Pegawai</p>
                <h3>{total_pegawai}</h3>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="card">
                <p>🎓 Pendidikan Tertinggi</p>
                <h3>{pendidikan_tertinggi}</h3>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
            <div class="card">
                <p>👥 Proporsi JK</p>
                <h3>{laki_laki} L / {perempuan} P</h3>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
            <div class="card">
                <p>🏢 Jumlah OPD</p>
                <h3>{total_opd}</h3>
            </div>
        """, unsafe_allow_html=True)

elif menu == "Data Pegawai":
    st.subheader("➕ Tambah Data Pegawai")
    with st.form("form_tambah"):
        nama = st.text_input("Nama")
        gdp = st.text_input("GDP")
        gelar_belakang = st.text_input("Gelar Belakang")
        jabatan = st.text_input("Jabatan")
        jk = st.selectbox("Jenis Kelamin", ["LAKI-LAKI", "PEREMPUAN"])
        ttl = st.date_input("Tanggal Lahir")
        kode_opd = st.text_input("Kode OPD")
        pendidikan_awal = st.text_input("Pendidikan Awal")
        pendidikan_akhir = st.text_input("Pendidikan Akhir")
        usia = st.number_input("Usia", min_value=0)
        opd = st.text_input("OPD")
        submit = st.form_submit_button("Simpan Data")

    if submit:
        no_baru = len(df) + 1
        new_data = {
            "No": no_baru,
            "NAMA": nama,
            "GDP": gdp,
            "Gelar BELAKANG": gelar_belakang,
            "JABATAN": jabatan,
            "JK": jk,
            "TTL": ttl.strftime("%d-%m-%Y"),
            "kode OPD": kode_opd,
            "PENDIDIKAN AWAL": pendidikan_awal,
            "PENDIDIKAN AKHIR": pendidikan_akhir,
            "USIA": usia,
            "OPD": opd
        }

        worksheet.append_row(list(new_data.values()))
        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)
        st.success("✅ Data berhasil ditambahkan dan disimpan ke Google Sheets!")

    st.subheader("📄 Data Pegawai Terkini")
    st.dataframe(df)

    # --- Hapus Data ---
    st.subheader("🗑️ Hapus Data Pegawai")
    if not df.empty:
        df['label_hapus'] = df['No'].astype(str) + " - " + df['NAMA'] + " (" + df['JABATAN'] + ")"
        selected_label = st.selectbox("Pilih pegawai yang ingin dihapus:", df['label_hapus'].tolist())

        if st.button("Hapus Data Ini"):
            selected_no = int(selected_label.split(" - ")[0])  # Ambil No pegawai
            matching_rows = df[df["No"] == selected_no]  # Pencarian data yang matching berdasarkan No

            if not matching_rows.empty:  # Cek jika data masih ada
                idx_to_delete = matching_rows.index[0]  # Ambil index baris yang akan dihapus
                worksheet.delete_rows(int(idx_to_delete) + 2)  # +2 karena header ada di baris pertama
                st.success(f"✅ Data pegawai No {selected_no} berhasil dihapus.")
            else:
                st.error("❌ Data tidak ditemukan. Mungkin sudah dihapus sebelumnya.")

    st.markdown("### ⬇️ Download Data dari Spreadsheet Google")
    st.markdown("[Buka Spreadsheet 📃](https://docs.google.com/spreadsheets/d/1z8i_J3rylC0w-kuKRu_PZ-UfbgrdF8a9w8i2s5CFjz4)", unsafe_allow_html=True)

elif menu == "Tabel Pegawai":
    st.subheader("📄 Tabel Data Pegawai")
    st.dataframe(df)

elif menu == "Hasil Analisis":
    st.subheader("📊 Statistik Pendidikan Akhir")
    pendidikan_counts = df['PENDIDIKAN AKHIR'].value_counts().reset_index()
    pendidikan_counts.columns = ['PENDIDIKAN AKHIR', 'count']
    st.dataframe(pendidikan_counts)

    st.subheader("🏢 Distribusi Pegawai per OPD")
    opd_counts = df['OPD'].value_counts().reset_index()
    opd_counts.columns = ['OPD', 'count']
    st.dataframe(opd_counts)

    st.subheader("📈 Visualisasi Data")
    col5, col6 = st.columns(2)
    with col5:
        st.bar_chart(df['JK'].value_counts())
        st.caption("Distribusi Jenis Kelamin")
    with col6:
        st.bar_chart(pendidikan_counts.set_index('PENDIDIKAN AKHIR'))
        st.caption("Distribusi Pendidikan Akhir")