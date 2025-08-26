import streamlit as st
import google.generativeai as genai
import os

# --- PENGATURAN API KEY (Ambil dari Streamlit Secrets) ---
# Simpan API key Anda di Streamlit Secrets
# Caranya:
# 1. Buka aplikasi Streamlit Anda
# 2. Klik "Settings" di pojok kanan atas
# 3. Pilih "Secrets"
# 4. Tambahkan secret dengan nama "GEMINI_API_KEY" dan isikan API key Anda
#    contoh: GEMINI_API_KEY = "AIza..."
#    Detail lebih lanjut: https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/deploy-an-app#set-secrets
# 5. ATAU, jika menjalankan lokal, buat file .streamlit/secrets.toml di root proyek Anda.
#    Isi file tersebut:
#    [secrets]
#    GEMINI_API_KEY="AIza..."

try:
    API_KEY = st.secrets["GEMINI_API_KEY"]
except KeyError:
    st.error("API Key Gemini tidak ditemukan. Harap tambahkan 'GEMINI_API_KEY' ke Streamlit Secrets.")
    st.stop()

genai.configure(api_key=API_KEY)
MODEL_NAME = 'gemini-1.5-flash'

# --- KONFIGURASI APLIKASI STREAMLIT ---
st.set_page_config(page_title="🤖 Chatbot Koki Gemini", page_icon="👨‍🍳")
st.title("🤖 Chatbot Koki Gemini")
st.caption("Ayo tanya resep masakan apa pun! Saya hanya bisa menjawab tentang resep.")

# --- INISIALISASI CHATBOT ---
# Menggunakan st.session_state untuk menyimpan riwayat chat
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "user", "parts": ["Anda adalah seorang koki ahli. Berikan berbagai macam resep masakan. Jawablah dengan singkat dan jelas. Tolak pertanyaan yang tidak berhubungan dengan masakan."]},
        {"role": "model", "parts": ["Tentu! Tanyakan resep masakan yang Anda inginkan. Saya siap membantu!"]}
    ]

# Menginisialisasi model jika belum ada
if "model" not in st.session_state:
    st.session_state.model = genai.GenerativeModel(
        MODEL_NAME,
        generation_config=genai.types.GenerationConfig(
            temperature=0.4,
            max_output_tokens=500
        )
    )

# Menginisialisasi sesi chat
if "chat_session" not in st.session_state:
    st.session_state.chat_session = st.session_state.model.start_chat(
        history=st.session_state.chat_history
    )

# --- MENAMPILKAN RIWAYAT CHAT ---
# Tampilkan pesan dari history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.chat_message("user").markdown(message["parts"][0])
    else:
        st.chat_message("assistant").markdown(message["parts"][0])

# --- MENANGANI INPUT PENGGUNA ---
user_query = st.chat_input("Tulis pertanyaan resep di sini...")

if user_query:
    # Tampilkan pesan pengguna di UI
    st.chat_message("user").markdown(user_query)
    
    # Tambahkan query pengguna ke riwayat
    st.session_state.chat_history.append({"role": "user", "parts": [user_query]})

    try:
        # Kirim pesan ke model dan dapatkan balasan
        with st.spinner("Sedang mencari resep..."):
            response = st.session_state.chat_session.send_message(user_query, request_options={"timeout": 60})
        
        if response and response.text:
            # Tampilkan balasan dari model
            st.chat_message("assistant").markdown(response.text)
            # Tambahkan balasan model ke riwayat
            st.session_state.chat_history.append({"role": "model", "parts": [response.text]})
        else:
            st.chat_message("assistant").error("Maaf, saya tidak bisa memberikan balasan.")
            st.session_state.chat_history.append({"role": "model", "parts": ["Maaf, saya tidak bisa memberikan balasan."]})

    except Exception as e:
        st.chat_message("assistant").error(f"Terjadi kesalahan: {e}")
        st.session_state.chat_history.append({"role": "model", "parts": [f"Terjadi kesalahan: {e}"]})
