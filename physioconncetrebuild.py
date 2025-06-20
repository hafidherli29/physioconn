import streamlit as st
import pandas as pd
import time

# Konfigurasi halaman
st.set_page_config(page_title="PhysioConnect - Modern", layout="wide")

# CSS Custom untuk Animasi Keren (tanpa emoticon)
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #fdfbfb, #ebedee);
            animation: fadeIn 2s ease-in-out;
        }
        h1, h2, h3 {
            animation: slideDown 1s ease-out;
        }
        .stTabs [role="tab"] {
            background: #ffffff;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 10px;
            margin-right: 5px;
        }
        .stTabs [aria-selected="true"] {
            background: linear-gradient(90deg, #6dd5ed, #2193b0);
            color: white;
            font-weight: bold;
        }
        .card {
            background-color: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            animation: fadeInUp 1s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }
        @keyframes slideDown {
            from {transform: translateY(-20px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;}
        }
        @keyframes fadeInUp {
            from {transform: translateY(40px); opacity: 0;}
            to {transform: translateY(0); opacity: 1;}
        }
    </style>
""", unsafe_allow_html=True)

# Inisialisasi
if 'user_type' not in st.session_state: st.session_state.user_type = None
if 'physios' not in st.session_state:
    st.session_state.physios = pd.DataFrame(columns=["name", "phone", "lat", "lon"])
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'announcements' not in st.session_state:
    st.session_state.announcements = []

# Header Aplikasi
st.markdown("""
    <div class='card'>
        <h1>PhysioConnect</h1>
        <h3>Empowering Your Recovery, Digitally</h3>
    </div>
""", unsafe_allow_html=True)

# Sidebar Login
with st.sidebar:
    st.title("Login Area")
    role = st.radio("Login sebagai:", ["Pasien", "Admin"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if role == "Admin" and username == "admin" and password == "admin123":
            st.session_state.user_type = "admin"
            st.success("Berhasil login sebagai Admin")
        elif role == "Pasien" and username:
            st.session_state.user_type = "patient"
            st.session_state.username = username
            st.success(f"Selamat datang, {username}!")
        else:
            st.error("Login gagal. Coba lagi!")

# ADMIN PANEL
if st.session_state.user_type == "admin":
    st.subheader("Dashboard Admin")
    tabs = st.tabs(["Pesan Pasien", "Tambah Fisioterapis", "Pengaturan", "Broadcast", "Data Statistik"])

    # Tab 1: Balas Chat
    with tabs[0]:
        st.info("Balas pesan yang masuk dari pasien")
        for i, msg in enumerate(st.session_state.messages):
            with st.expander(f"{msg['user']}: {msg['text']}"):
                reply = st.text_input(f"Balas ke {msg['user']}", key=f"r{i}")
                if st.button("Kirim", key=f"s{i}"):
                    st.session_state.messages[i]["reply"] = reply
                    st.success("Balasan terkirim")

    # Tab 2: Tambah Fisioterapis
    with tabs[1]:
        st.info("Masukkan data fisioterapis untuk muncul di fitur Nearby")
        with st.form("add_physio"):
            nama = st.text_input("Nama")
            nohp = st.text_input("No HP")
            lat = st.number_input("Latitude")
            lon = st.number_input("Longitude")
            submit = st.form_submit_button("Tambah")
            if submit:
                st.session_state.physios = st.session_state.physios.append({"name": nama, "phone": nohp, "lat": lat, "lon": lon}, ignore_index=True)
                st.success("Fisioterapis berhasil ditambahkan")

    # Tab 3: Pengaturan Akun
    with tabs[2]:
        st.text_input("Ubah Password Admin")
        st.selectbox("Pilih Bahasa", ["Bahasa Indonesia", "English"])
        st.button("Simpan Pengaturan")

    # Tab 4: Broadcast Info
    with tabs[3]:
        new_announcement = st.text_area("Tulis Pengumuman Umum")
        if st.button("Kirim Pengumuman"):
            st.session_state.announcements.append(new_announcement)
            st.success("Pengumuman berhasil dikirim ke pasien")

    # Tab 5: Statistik Dummy
    with tabs[4]:
        st.metric("Total Pasien", "125")
        st.metric("Pesan Masuk", len(st.session_state.messages))
        st.metric("Fisioterapis Terdaftar", len(st.session_state.physios))

# PASIEN PANEL
elif st.session_state.user_type == "patient":
    st.subheader(f"Selamat datang, {st.session_state.username}")
    menu = st.selectbox("Pilih Menu Layanan:", ["Jurnal", "Fisioterapis Terdekat", "Chat", "Latihan Rekomendasi", "Info Terkini"])

    if menu == "Jurnal":
        st.markdown("[Lihat Jurnal Fisiomu UMS](https://journals.ums.ac.id/)")

    elif menu == "Fisioterapis Terdekat":
        if not st.session_state.physios.empty:
            st.map(st.session_state.physios.rename(columns={"lat": "latitude", "lon": "longitude"}))
            st.dataframe(st.session_state.physios)
        else:
            st.warning("Belum ada data fisioterapis terdaftar.")

    elif menu == "Chat":
        pesan = st.text_input("Tulis pesan ke Admin")
        if st.button("Kirim Pesan"):
            st.session_state.messages.append({"user": st.session_state.username, "text": pesan, "reply": ""})
            st.success("Pesan terkirim")
        for msg in st.session_state.messages:
            if msg["user"] == st.session_state.username:
                st.info(f"Kamu: {msg['text']}")
                if msg.get("reply"):
                    st.success(f"Admin: {msg['reply']}")

    elif menu == "Latihan Rekomendasi":
        kondisi = st.text_input("Masukkan nama kondisi medis")
        if st.button("Cari Latihan"):
            with st.spinner("Mencari video latihan terbaik..."):
                time.sleep(2)
                st.video("https://www.youtube.com/watch?v=4BOTvaRaDjI")
                st.success("Latihan berhasil dimuat")

    elif menu == "Info Terkini":
        if st.session_state.announcements:
            for pengumuman in reversed(st.session_state.announcements):
                st.markdown(f"**{pengumuman}**")
        else:
            st.info("Belum ada pengumuman saat ini.")

# Belum Login
else:
    st.info("Silakan login dari sidebar untuk mengakses layanan PhysioConnect.")
