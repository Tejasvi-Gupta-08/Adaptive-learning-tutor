# 📚 SDG 4 – Adaptive Learning Tutor

An AI-powered adaptive learning platform designed to provide personalized practice for students, aligned with UN Sustainable Development Goal 4 (Quality Education).
The system dynamically adjusts questions based on learner mastery using Bayesian Knowledge Tracing (BKT), ensuring a tailored learning experience.

🚀 Features

✔ Adaptive Question Selection based on learner's mastery
✔ Bayesian Knowledge Tracing (BKT) for tracking concept mastery
✔ Concept-wise Mastery Visualization with progress bars and charts
✔ Dynamic Recommendations for low-mastery concepts with resource links
✔ Session History to review performance
✔ Built with Streamlit for an interactive and responsive UI

🛠 Tech Stack

Python 3.8+

Streamlit (UI Framework)

Pandas & NumPy (Data Handling)

Matplotlib / Streamlit Charts (Mastery Visualization)

📂 Project Structure
adaptive-learning-tutor/
│
├── app.py                  # Main Streamlit App
├── questions.csv           # Question bank (CSV file)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

📊 How It Works

Mastery Initialization: Each concept starts with a mastery probability of 0.2.

Question Selection: The system selects the next question from the concept with the lowest mastery.

Bayesian Knowledge Tracing (BKT) updates mastery after every response.

Recommendations: If mastery < 0.6, the app suggests concepts and resources to review.

🔮 Future Enhancements

✅ User Authentication for saving progress across sessions

✅ More Subjects & Concepts

✅ Gamification (Badges, Points)

✅ Integration with AI Tutors (GPT-based explanation for wrong answers)
