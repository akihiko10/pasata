import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

st.set_page_config(page_title="Finances", layout="centered")

filename = 'manajemen_keuangan.csv'

try:
    df = pd.read_csv(filename)
    df['Tanggal'] = pd.to_datetime(df['Tanggal'])
except FileNotFoundError:
    df = pd.DataFrame(columns=['Tanggal', 'Kategori', 'Jumlah', 'Keterangan'])
    df.to_csv(filename, index=False)

st.title("📊 Financial Tracker")

st.header("📝 Catat Pengeluaran")
with st.form("input_form", clear_on_submit=True):
    kategori = st.selectbox("Kategori", ["Bensin", "Vape", "Date", "Tabungan", "Lainnya"])
    jumlah = st.number_input("Nominal (Rp)", min_value=0, step=1000)
    keterangan = st.text_input("Keterangan (Opsional)")
    submit = st.form_submit_button("Simpan Transaksi")

    if submit and jumlah > 0:
        hari_ini = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
        new_data = pd.DataFrame([[hari_ini, kategori, jumlah, keterangan]], columns=df.columns)
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_csv(filename, index=False)
        st.success(f"✔️ Rp{jumlah:,} dicatat ke {kategori}!")

st.header("📉 Dashboard Monitoring")
hari_ini = pd.to_datetime(datetime.now().strftime('%Y-%m-%d'))
awal_minggu = hari_ini - timedelta(days=6)

pengeluaran_mingguan = df[(df['Tanggal'] >= awal_minggu) & (df['Tanggal'] <= hari_ini)]['Jumlah'].sum()
budget_mingguan = 400000
sisa_total = budget_mingguan - pengeluaran_mingguan

col1, col2 = st.columns(2)
col1.metric("Terpakai (7 Hari)", f"Rp{pengeluaran_mingguan:,}")
col2.metric("Sisa Uang Aman", f"Rp{sisa_total:,}")

if sisa_total < 0:
    st.error("🚨 LO UDAH BOCOR DARI JATAH 400RB MINGGUAN!")
elif sisa_total < 50000:
    st.warning("⚠️ SIAGA: Duit menipis, rem dompet lo!")

st.subheader("Detail Kuota Pos Utama")
rules = {
    'Bensin': {'limit': 50000, 'hari': 7, 'tipe': 'Mingguan'},
    'Date': {'limit': 100000, 'hari': 7, 'tipe': 'Mingguan'},
    'Tabungan': {'limit': 70000, 'hari': 7, 'tipe': 'Target 7 Hari'},
    'Vape': {'limit': 155000, 'hari': 30, 'tipe': 'Bulanan'}
}

for kat, rule in rules.items():
    tgl_mulai = hari_ini - timedelta(days=rule['hari'] - 1)
    kondisi = (df['Kategori'] == kat) & (df['Tanggal'] >= tgl_mulai) & (df['Tanggal'] <= hari_ini)
    terpakai = df[kondisi]['Jumlah'].sum()

    if kat == 'Tabungan':
        sisa = terpakai
        persentase = min(float(terpakai / rule['limit']), 1.0)
        st.write(f"💪 **{kat}** — Berhasil Nabung: **Rp{sisa:,}** / Target: Rp{rule['limit']:,}")
        st.progress(persentase)
    else:
        sisa = rule['limit'] - terpakai
        persentase = min(float(terpakai / rule['limit']), 1.0)
        st.write(f"**{kat}** ({rule['tipe']}) — Sisa Kuota: **Rp{sisa:,}** / Rp{rule['limit']:,}")
        st.progress(persentase)

st.subheader("📋 5 Transaksi Terakhir")
if not df.empty:
    # UPDATE: Mengubah use_container_width=True menjadi width='stretch' sesuai aturan Streamlit 2026
    st.dataframe(df.tail(5)[['Tanggal', 'Kategori', 'Jumlah', 'Keterangan']].sort_values(by='Tanggal', ascending=False), width='stretch')
