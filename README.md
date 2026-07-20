# 🎯 AI Mock Interviewer

A Streamlit web app that simulates beginner job interviews and gives instant, structured feedback using Google's Gemini AI.

Built as the final capstone project for **Samsung Innovation Campus — Coding & Programming**, Presidency University, Bengaluru.

## 🔗 Try it now — no setup, no API key needed

### 👉 [ai-mock-interviewer-cklgiym4djpjcukkm7rhes.streamlit.app](https://ai-mock-interviewer-cklgiym4djpjcukkm7rhes.streamlit.app)

Just click the link above and start the interview directly.

## What it does

- Pick a role — Software Developer, HR/General, or Data/Analyst
- Choose your experience level — feedback difficulty adjusts accordingly
- Answer real interview questions one at a time
- Get instant AI feedback: a reasoned evaluation, a score out of 10, and specific improvement tips
- Review a full summary at the end of the session

## GenAI techniques used

- **Few-shot prompting** — the model is shown one weak and one strong example answer so it learns the evaluation pattern instead of guessing.
- **Chain-of-Thought reasoning** — the model reasons through the answer before scoring it, for more consistent and explainable feedback.
- **Persona framing** — the model is instructed to act as an encouraging, professional interviewer, keeping feedback constructive.

## Tech stack

Python · Streamlit · Google Gemini API (`gemini-flash-latest`)

## Running it locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

You'll need a free Gemini API key from [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) — enter it in the sidebar when the app opens. Your key is never stored; it's only used for your session.

## Author

Abdul Khader — Presidency University, Bengaluru
