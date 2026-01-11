import streamlit as st
from backend import app, extract_pdf_text
import re
import pandas as pd

st.set_page_config(page_title="Doc Assis", layout="wide")

def reset_app():
    st.session_state.chat = []
    st.session_state.history_text = ""
    st.session_state.lab_text = ""
    st.session_state.final_diagnosis = ""
    st.rerun()

for key, default in {
    "chat": [],
    "history_text": "",
    "lab_text": "",
    "final_diagnosis": ""
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

st.markdown("""
<style>
.stApp { background: #f8fafc; }
.block-container { padding: 2.5rem; }

body, p, span, div { color: #020617 !important; }
h1, h2, h3 { font-weight: 700; color: #020617 !important; }

/* Header */
.header-card {
    background: linear-gradient(135deg, #1f77ff, #2563eb);
    padding: 2rem;
    border-radius: 22px;
    color: white;
    text-align: center;
    margin-bottom: 2rem;
}

/* Cards */
.card {
    background: white;
    border-radius: 18px;
    padding: 1.5rem;
    box-shadow: 0 6px 18px rgba(0,0,0,0.08);
    margin-bottom: 1.5rem;
}

/* Chat */
div[data-testid="stChatMessage"][data-role="user"] {
    background: #dbeafe;
    border-radius: 14px;
    padding: 12px;
}
div[data-testid="stChatMessage"][data-role="assistant"] {
    background: white;
    border-left: 5px solid #1f77ff;
    border-radius: 14px;
    padding: 12px;
}

/* Diagnosis */
.diagnosis-card {
    background: #ecfeff;
    border-left: 6px solid #0ea5e9;
    border-radius: 18px;
    padding: 1.5rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #020617;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}

/* Input */
textarea {
    min-height: 120px !important;
    border-radius: 16px !important;
    border: 2px solid #1f77ff !important;
}

/* ✅ FORCE BUTTON COLOR (FIXES DARK BUTTON) */
div.stButton > button {
    background: linear-gradient(135deg, #1f77ff, #2563eb) !important;
    color: white !important;
    border-radius: 18px !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    border: none !important;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #2563eb, #1f77ff) !important;
}
</style>
""", unsafe_allow_html=True)

if st.button("🩺 Doc Assis – New Patient", use_container_width=True):
    reset_app()

st.markdown("""
<div class="header-card">
    <h1>Doc Assis</h1>
    <p>Clinical Decision Support AI</p>
</div>
""", unsafe_allow_html=True)

st.markdown("<div class='card'><h3>📄 Upload Patient Records</h3></div>", unsafe_allow_html=True)

c1, c2 = st.columns(2)

with c1:
    history_pdf = st.file_uploader("Patient History PDF", type="pdf")
    if history_pdf:
        st.session_state.history_text = extract_pdf_text(history_pdf)
        st.success(f"Uploaded: {history_pdf.name}")

with c2:
    lab_pdf = st.file_uploader("Lab Results PDF", type="pdf")
    if lab_pdf:
        st.session_state.lab_text = extract_pdf_text(lab_pdf)
        st.success(f"Uploaded: {lab_pdf.name}")


if st.session_state.history_text or st.session_state.lab_text:
    st.sidebar.title("🧾 Patient Snapshot")

    combined = st.session_state.history_text + "\n" + st.session_state.lab_text

    def find(pattern):
        m = re.search(pattern, combined, re.IGNORECASE)
        return m.group(1) if m else None

    name = find(r"name[:\- ]+([A-Za-z ]+)")
    age = find(r"age[:\- ]+(\d+)")
    gender = find(r"gender[:\- ]+(male|female|other)")

    st.sidebar.markdown(
        f"**Name:** {name or 'Not available'}\n\n"
        f"**Age:** {age or 'Not available'}\n\n"
        f"**Gender:** {gender or 'Not available'}"
    )

 
    labs = {}
    hba1c = find(r"hba1c[:\- ]+([\d.]+)")
    chol = find(r"cholesterol[:\- ]+([\d.]+)")
    bp = find(r"(\d{2,3})/\d{2,3}")

    if hba1c:
        labs["HbA1c"] = float(hba1c)
    if chol:
        labs["Cholesterol"] = float(chol)
    if bp:
        labs["Systolic BP"] = float(bp)

    if labs:
        st.sidebar.markdown("---")
        st.sidebar.subheader("📊 Lab Chart")
        df = pd.DataFrame(labs.values(), index=labs.keys(), columns=["Value"])
        st.sidebar.bar_chart(df)


st.markdown("<div class='card'><h3>💬 Clinical Conversation</h3></div>", unsafe_allow_html=True)

for msg in st.session_state.chat:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])


user_input = st.chat_input("Describe symptoms or answer follow-up questions")

if user_input:
    st.session_state.chat.append({"role": "user", "content": user_input})

    conversation = [
        f"{m['role'].upper()}: {m['content']}"
        for m in st.session_state.chat
    ]

    result = app.invoke({
        "history_text": st.session_state.history_text,
        "lab_text": st.session_state.lab_text,
        "conversation": conversation
    })

    if result.get("diagnosis"):
        st.session_state.final_diagnosis = result["diagnosis"]

    st.session_state.chat.append({
        "role": "assistant",
        "content": result["followup_question"]
    })

    st.rerun()

if st.session_state.final_diagnosis:
    st.markdown(
        f"""
        <div class="diagnosis-card">
            <h3>🩺 Final Clinical Impression</h3>
            <p>{st.session_state.final_diagnosis}</p>
            <p><i>⚠ For clinical decision support only. Doctor confirmation required.</i></p>
        </div>
        """,
        unsafe_allow_html=True
    )
