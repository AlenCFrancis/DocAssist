import os
from dotenv import load_dotenv
from typing import TypedDict, List

from openai import OpenAI
from langgraph.graph import StateGraph, END
from pypdf import PdfReader

# ==================================================
# ENV + OPENAI CLIENT
# ==================================================
load_dotenv()

client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

MODEL_NAME = "gpt-4o-mini"  # fast, cheap, reliable

# ==================================================
# STATE
# ==================================================
class PatientState(TypedDict):
    history_text: str
    lab_text: str
    conversation: List[str]
    diagnosis: str
    followup_question: str

# ==================================================
# OPENAI CALL (SAFE, CHAT-STYLE)
# ==================================================
def call_openai(prompt: str) -> str:
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a clinical decision support AI assisting doctors. "
                    "You must ask follow-up questions before concluding. "
                    "Do not give final medical decisions."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return response.choices[0].message.content.strip()

# ==================================================
# GRAPH NODES
# ==================================================
def diagnosis_step(state: PatientState):
    convo = "\n".join(state["conversation"])

    prompt = f"""
Patient History:
{state["history_text"]}

Lab Results:
{state["lab_text"]}

Conversation so far:
{convo}

Task:
Infer the MOST LIKELY diagnosis.
Do NOT prescribe medicine.
Be concise.
"""

    diagnosis = call_openai(prompt)
    return {"diagnosis": diagnosis}


def followup_step(state: PatientState):
    prompt = f"""
Current diagnosis hypothesis:
{state["diagnosis"]}

Task:
Ask 1–2 follow-up questions like a real doctor.
Do NOT conclude.
"""

    question = call_openai(prompt)
    return {"followup_question": question}

# ==================================================
# LANGGRAPH
# ==================================================
graph = StateGraph(PatientState)

graph.add_node("diagnosis_step", diagnosis_step)
graph.add_node("followup_step", followup_step)

graph.set_entry_point("diagnosis_step")
graph.add_edge("diagnosis_step", "followup_step")
graph.add_edge("followup_step", END)

app = graph.compile()

# ==================================================
# PDF TEXT EXTRACTION (UNCHANGED)
# ==================================================
def extract_pdf_text(file):
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text() + "\n"
    return text.strip()
