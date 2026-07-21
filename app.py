import streamlit as st
import google.generativeai as genai
import time

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Mock Interviewer",
    page_icon="🎯",
    layout="centered"
)

# ---------- STYLING ----------
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 0px;
    }
    .subtitle {
        text-align: center;
        color: #888;
        margin-bottom: 30px;
    }
    .question-box {
        background-color: #1e2a38;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #4CAF50;
        margin-bottom: 20px;
    }
    .feedback-box {
        background-color: #1a1a1a;
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid #FFA500;
        margin-top: 15px;
    }
    .score-badge {
        font-size: 1.3rem;
        font-weight: 700;
        color: #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# ---------- QUESTION BANK ----------
question_bank = {
    "Software Developer": [
        "Tell me about yourself.",
        "Walk me through a project you built and your specific contribution.",
        "Why did you choose this tech stack for your project?",
        "Describe a time you were stuck on a bug. How did you solve it?",
        "Where do you see yourself in 3 years?"
    ],
    "HR / General": [
        "Tell me about yourself.",
        "What are your strengths and weaknesses?",
        "Why should we hire you?",
        "Describe a challenge you faced and how you handled it.",
        "Why do you want to work at our company?"
    ],
    "Data / Analyst": [
        "Tell me about yourself.",
        "Explain a project where you worked with data.",
        "How do you approach solving an ambiguous problem?",
        "What tools have you used for analysis, and why?",
        "Where do you see yourself in 3 years?"
    ]
}

# ---------- FEW-SHOT + CHAIN-OF-THOUGHT PROMPT ----------
def build_evaluation_prompt(question, answer, level="Fresher / Beginner"):
    level_instruction = LEVEL_INFO.get(level, LEVEL_INFO["Fresher / Beginner"])
    return f"""
You are a professional, encouraging job interviewer conducting a mock interview.
Candidate level: {level}. {level_instruction}
Give constructive, honest feedback — never harsh, never sarcastic.

Example 1:
Question: "Tell me about yourself."
Answer: "I am good boy I like coding pls hire me."
Reasoning: The answer lacks structure, has no specific details about education, skills, or
projects, and does not follow a professional tone.
Score: 3/10
Feedback: Structure your answer around education, key skills, and one project. Avoid casual
phrases — keep it confident and professional.

Example 2:
Question: "Tell me about yourself."
Answer: "I am a final year Computer Science student with a CGPA of 7.5. I have focused on
Python and Django, and built a Task Management web application handling authentication and
database design. I am looking to apply these skills in a full-stack developer role."
Reasoning: The answer is structured (education, skills, project, goal), specific, and
professional in tone.
Score: 8/10
Feedback: Strong structure. Could be slightly improved by adding one sentence on why this role
specifically excites you.

Now evaluate this real answer the same way. Think step by step (Reasoning), then give a Score
out of 10, then 2-3 lines of specific, constructive Feedback.

Question: "{question}"
Answer: "{answer}"

Respond in exactly this format:
Reasoning: <your reasoning>
Score: <x>/10
Feedback: <your feedback>
"""

def call_gemini_with_retry(model, prompt, retries=2):
    for attempt in range(retries):
        try:
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                time.sleep(15)
                continue
            if "429" in str(e):
                return ("The shared free quota is busy right now (a few people may be using the app "
                        "at once). Please wait 30-60 seconds and try again, or check 'Use my own "
                        "Gemini API key' in the sidebar for uninterrupted access.")
            return f"Could not get feedback right now ({str(e)[:120]}...). Try again in a moment."

# ---------- SESSION STATE ----------
if "started" not in st.session_state:
    st.session_state.started = False
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "role" not in st.session_state:
    st.session_state.role = None
if "level" not in st.session_state:
    st.session_state.level = None
if "history" not in st.session_state:
    st.session_state.history = []

LEVEL_INFO = {
    "Fresher / Beginner": "Be extra encouraging. Focus feedback on structure and clarity over polish — this candidate has 0-1 years experience.",
    "Intermediate (1-3 yrs)": "Expect specific technical depth and measurable outcomes. Push for more detail if the answer is generic.",
    "Experienced (3+ yrs)": "Expect leadership, ownership, and impact framing. Push back if the answer lacks strategic thinking."
}

# ---------- HEADER ----------
st.markdown('<p class="main-title"> AI Mock Interviewer</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Practice real interview questions and get instant AI feedback</p>', unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.header("Setup")

    # Try to use a shared key stored in Streamlit secrets first
    shared_key = st.secrets.get("GEMINI_API_KEY", None) if hasattr(st, "secrets") else None

    if shared_key:
        st.success("Ready to go — no API key needed!")
        use_own_key = st.checkbox("Use my own Gemini API key instead")
        if use_own_key:
            api_key = st.text_input("Enter your Gemini API key", type="password",
                                     help="Get a free key at aistudio.google.com/app/apikey")
        else:
            api_key = shared_key
    else:
        api_key = st.text_input("Enter your Gemini API key", type="password",
                                 help="Get a free key at aistudio.google.com/app/apikey")
        st.caption("Your key is only used in your browser session — it is never stored or shared.")

    st.divider()
    st.subheader("About this project")
    st.write(
        "Built for the Samsung Innovation Campus GenAI. "
        "Uses few-shot prompting and Chain-of-Thought reasoning to evaluate interview answers, "
        "similar to how a real interviewer assesses structure, specificity, and tone."
    )

if not api_key:
    st.info("👈 Enter your Gemini API key in the sidebar to begin.")
    st.stop()

genai.configure(api_key=api_key)
model = genai.GenerativeModel("gemini-2.0-flash")

# ---------- ROLE SELECTION ----------
if not st.session_state.started:
    st.subheader("Set up your mock interview")

    col_a, col_b = st.columns(2)
    with col_a:
        role = st.selectbox("Role", list(question_bank.keys()))
    with col_b:
        level = st.selectbox("Experience level", list(LEVEL_INFO.keys()))

    num_questions = st.slider("Number of questions", min_value=2, max_value=5, value=5)

    if st.button("Start Interview", type="primary", use_container_width=True):
        st.session_state.started = True
        st.session_state.role = role
        st.session_state.level = level
        st.session_state.num_questions = num_questions
        st.session_state.q_index = 0
        st.session_state.history = []
        st.rerun()

# ---------- INTERVIEW FLOW ----------
else:
    role = st.session_state.role
    level = st.session_state.level
    questions = question_bank[role][:st.session_state.get("num_questions", 5)]
    q_index = st.session_state.q_index

    st.caption(f"Role: **{role}**  |  Level: **{level}**")
    st.progress(q_index / len(questions), text=f"Question {min(q_index+1, len(questions))} of {len(questions)}")

    if q_index < len(questions):
        current_q = questions[q_index]
        st.markdown(f'<div class="question-box"><b>Interviewer ({role}):</b><br>{current_q}</div>', unsafe_allow_html=True)

        answer = st.text_area("Your answer", height=150, key=f"answer_{q_index}")

        col1, col2 = st.columns([1, 1])
        with col1:
            submit = st.button("Submit Answer", type="primary", use_container_width=True)
        with col2:
            skip = st.button("Skip Question", use_container_width=True)

        if submit and answer.strip():
            with st.spinner("Evaluating your answer..."):
                feedback = call_gemini_with_retry(model, build_evaluation_prompt(current_q, answer, level))
            st.markdown(f'<div class="feedback-box">{feedback}</div>', unsafe_allow_html=True)
            st.session_state.history.append({"question": current_q, "answer": answer, "feedback": feedback})
            if st.button("Next Question →", type="primary", use_container_width=True):
                st.session_state.q_index += 1
                st.rerun()
        elif submit and not answer.strip():
            st.warning("Type an answer before submitting.")

        if skip:
            st.session_state.q_index += 1
            st.rerun()

    else:
        st.success("🎉 Interview complete!")
        st.subheader(f"Summary — {role}")
        for i, item in enumerate(st.session_state.history, start=1):
            with st.expander(f"Q{i}: {item['question']}"):
                st.write(f"**Your answer:** {item['answer']}")
                st.markdown(f'<div class="feedback-box">{item["feedback"]}</div>', unsafe_allow_html=True)

        if st.button("Start Over", type="primary", use_container_width=True):
            st.session_state.started = False
            st.session_state.q_index = 0
            st.session_state.history = []
            st.rerun()

st.divider()
st.caption("Samsung Innovation Campus — GenAI Project | Built by  Syed Abdul Khader")
