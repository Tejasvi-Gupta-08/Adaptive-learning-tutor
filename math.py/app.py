import streamlit as st
import pandas as pd
import numpy as np
from collections import defaultdict

st.set_page_config(page_title="SDG 4 – Adaptive Learning Tutor", page_icon="📚", layout="wide")

class BKT:
    def _init_(self, p_init=0.2, p_learn=0.2, p_guess=0.2, p_slip=0.1):
        self.p_init = p_init
        self.p_learn = p_learn
        self.p_guess = p_guess
        self.p_slip = p_slip

    def update(self, prior_mastery: float, correct: bool) -> float:
        # Posterior given observation
        if correct:
            num = prior_mastery * (1 - self.p_slip)
            den = num + (1 - prior_mastery) * self.p_guess
        else:
            num = prior_mastery * self.p_slip
            den = num + (1 - prior_mastery) * (1 - self.p_guess)
        posterior = num / den if den > 0 else prior_mastery
        # Learning transition
        updated = posterior + (1 - posterior) * self.p_learn
        return float(np.clip(updated, 0.0, 1.0))
    

# Load data

@st.cache_data
def load_questions(path="questions.csv"):
    df = pd.read_csv("questions.csv", quotechar='"')
    # sanitize
    df["concept"] = df["concept"].fillna("General").astype(str)
    df["difficulty"] = pd.to_numeric(df["difficulty"], errors="coerce").fillna(1).astype(int)
    return df

questions_df = load_questions("questions.csv")


# Session state

if "mastery" not in st.session_state:
    # per concept mastery probability
    concepts = questions_df["concept"].unique().tolist()
    st.session_state.mastery = {c: 0.2 for c in concepts}
if "history" not in st.session_state:
    st.session_state.history = []  # list of dicts: {id, concept, correct}
if "asked" not in st.session_state:
    st.session_state.asked = set()
if "current_q" not in st.session_state:
    st.session_state.current_q = None
if "bkt" not in st.session_state:
    st.session_state.bkt = BKT()

def pick_next_question():
    # Choose the lowest-mastery concept first
    mastery = st.session_state.mastery
    sorted_concepts = sorted(mastery.items(), key=lambda x: x[1])
    for concept, _ in sorted_concepts:
        # filter questions not asked for this concept
        remaining = questions_df[(questions_df["concept"] == concept) & (~questions_df["id"].isin(st.session_state.asked))]
        if not remaining.empty:
            # choose a question with difficulty near the learner's mastery (simple heuristic)
            # map mastery in [0,1] to difficulty in [1,4]
            target_diff = int(np.clip(np.round(1 + 3 * mastery[concept]), 1, 4))
            candidates = remaining.iloc[(remaining["difficulty"] - target_diff).abs().argsort()]
            return candidates.iloc[0].to_dict()
    # If everything asked, return None
    return None

def reset_progress():
    st.session_state.mastery = {c: 0.2 for c in questions_df["concept"].unique().tolist()}
    st.session_state.history = []
    st.session_state.asked = set()
    st.session_state.current_q = None


# Layout

st.title("📚 SDG 4 – Adaptive Learning Tutor")
st.write("*Personalized practice that adapts to each learner, aligned with UN SDG 4 (Quality Education).*")

with st.sidebar:
    st.header("Controls")
    if st.button("Start / Next Question", use_container_width=True):
        q = pick_next_question()
        st.session_state.current_q = q
    if st.button("Reset Progress", use_container_width=True):
        reset_progress()
    st.markdown("---")
    st.subheader("Mastery by Concept")
    mastery_series = pd.Series(st.session_state.mastery).sort_values(ascending=False)
    st.bar_chart(mastery_series)


# Main question card

q = st.session_state.current_q
if q is None:
    st.info("Click *Start / Next Question* in the sidebar to begin.")

else:
    st.subheader(f"Concept: {q['concept']} • Difficulty: {q['difficulty']}")
    st.write(f"*Q{int(q['id'])}.* {q['question']}")
    choice = st.radio("Your answer:", [
        ("a", q["option_a"]),
        ("b", q["option_b"]),
        ("c", q["option_c"]),
        ("d", q["option_d"]),
    ], format_func=lambda x: f"{x[0].upper()}: {x[1]}", index=None, horizontal=False)

    cols = st.columns([1,1,2])
    with cols[0]:
        if st.button("Submit Answer", disabled=choice is None):
            is_correct = (choice[0] == str(q["correct"]).lower().strip())
            st.session_state.history.append({"id": int(q["id"]), "concept": q["concept"], "correct": bool(is_correct)})
            st.session_state.asked.add(int(q["id"]))
            # Update mastery via BKT
            c = q["concept"]
            st.session_state.mastery[c] = st.session_state.bkt.update(st.session_state.mastery[c], is_correct)
            # Feedback
            if is_correct:
                st.success("✅ Correct!")
            else:
                st.error("❌ Not quite.")
            st.caption(f"Explanation: {q.get('explanation','')}")
            if isinstance(q.get("resource_url"), str) and q["resource_url"].startswith("http"):
                st.markdown(f"[Learn this concept]({q['resource_url']})")

    with cols[1]:
        if st.button("Skip"):
            st.session_state.asked.add(int(q["id"]))
            st.session_state.current_q = pick_next_question()

    with cols[2]:
        if st.button("Get Next Question ➡", use_container_width=True):
            st.session_state.current_q = pick_next_question()


# Recommendations & Analytics

st.markdown("---")
st.header("📈 Recommendations")
low_mastery = [c for c, m in st.session_state.mastery.items() if m < 0.6]
if low_mastery:
    st.write("Focus on these concepts next: ", ", ".join(low_mastery))
    recs = questions_df[questions_df["concept"].isin(low_mastery)][["concept","resource_url"]].drop_duplicates()
    st.dataframe(recs.reset_index(drop=True))
else:
    st.success("Great job! Your mastery is ≥ 0.6 on all concepts.")

st.markdown("### 📒 Session History")
if st.session_state.history:
    hist_df = pd.DataFrame(st.session_state.history)
    hist_df = hist_df.merge(questions_df[["id","concept","difficulty"]], on="id", how="left")
    st.dataframe(hist_df)
else:
    st.write("No attempts yet.")

st.caption("Built for hackathons: simple CSV question bank, BKT mastery model, adaptive question selection, and actionable recommendations.")