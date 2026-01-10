🩺 Doc Assis – Clinical Decision Support AI

Doc Assis is an AI-based clinical decision support system that helps doctors or nurses analyze patient history, lab reports, and symptoms through a conversational interface.
It assists in clinical reasoning by asking follow-up questions and providing a tentative diagnosis only when requested.

🔍 What This Project Does

Accepts Patient History PDF and Lab Results PDF

Extracts and analyzes medical text from PDFs

Interacts with the user like a doctor by asking relevant questions

Displays a patient snapshot (name, age, gender if available)

Shows basic lab charts (HbA1c, Cholesterol, Blood Pressure)

Generates a clinical impression only when the user asks

Allows resetting the system for a new patient

⚠️ This system is for clinical decision support only and does not replace a doctor.

🛠️ Tech Stack Used

Frontend: Streamlit

Backend: Python

AI Model: OpenAI (GPT-based model)

Workflow Orchestration: LangGraph

PDF Processing: PyPDF

Charts & Visualization: Pandas, Streamlit

Environment Management: python-dotenv