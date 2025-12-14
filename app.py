import streamlit as st
import os
from services.mcq_service import generate_mcqs_from_pdf
import tempfile

st.set_page_config(
    page_title="MCQ Agent",
    page_icon="📝",
    layout="centered"
)

st.markdown("""
<style>
    /* Import Hack font */
    @import url('https://cdn.jsdelivr.net/npm/hack-font@3/build/web/hack.css');
    
    * {
        font-family: 'Hack', monospace !important;
    }
    
    /* Color palette: #803416, #141111, #A6A6A6 */
    
    .main {
        background-color: #141111;
        padding: 2rem;
    }
    
    .stApp {
        background-color: #141111;
    }
    
    h1, h2, h3, p, label, .stMarkdown {
        color: #A6A6A6 !important;
    }
    
    /* Header */
    .main-header {
        color: #803416 !important;
        text-align: center;
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 2rem;
    }
    
    /* Question card */
    .question-box {
        background-color: #1a1818;
        border-left: 4px solid #803416;
        padding: 1.5rem;
        margin: 1.5rem 0;
        border-radius: 5px;
    }
    
    .question-text {
        color: #A6A6A6;
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Correct answer */
    .correct-box {
        background-color: #803416;
        color: #A6A6A6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Wrong answer */
    .wrong-box {
        background-color: #2a2020;
        border: 2px solid #803416;
        color: #A6A6A6;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Results */
    .results-box {
        background-color: #803416;
        color: #A6A6A6;
        padding: 2rem;
        border-radius: 5px;
        text-align: center;
        margin: 2rem 0;
    }
    
    .score-text {
        font-size: 3rem;
        font-weight: 700;
        color: #A6A6A6;
    }
    
    /* Progress */
    .stProgress > div > div > div > div {
        background-color: #803416 !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #803416;
        color: #A6A6A6;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border-radius: 5px;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #a04520;
        color: #ffffff;
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: #1a1818;
        border: 2px dashed #803416;
        border-radius: 5px;
        padding: 1rem;
    }
    
    /* Radio buttons */
    .stRadio > label {
        color: #A6A6A6 !important;
    }
    
    /* Input fields */
    .stNumberInput > div > div > input {
        background-color: #1a1818;
        color: #A6A6A6;
        border: 1px solid #803416;
    }
    
    /* Divider */
    hr {
        border-color: #803416;
    }
</style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'quiz_data' not in st.session_state:
        st.session_state.quiz_data = None
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

init_session_state()

# Header
st.markdown('<h1 class="main-header">📝 MCQ Agent</h1>', unsafe_allow_html=True)

# Upload Section
if not st.session_state.quiz_data:
    st.markdown("---")
    
    # Number of questions
    num_questions = st.number_input(
        "Number of Questions",
        min_value=3,
        max_value=100,
        value=5,
        step=1
    )
    
    st.markdown("")
    
    # PDF upload
    uploaded_file = st.file_uploader(
        "Upload PDF (Max 10MB)",
        type=['pdf'],
        help="Maximum file size: 10MB"
    )
    
    if uploaded_file:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        
        if file_size_mb > 10:
            st.error(f"File too large: {file_size_mb:.2f}MB (Max: 10MB)")
        else:
            st.info(f"📄 {uploaded_file.name} ({file_size_mb:.2f}MB)")
            
            if st.button("Generate Quiz"):
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name
                
                try:
                    with st.spinner("Generating questions..."):
                        result = generate_mcqs_from_pdf(
                            pdf_path=tmp_path,
                            num_questions=num_questions
                        )
                        
                        st.session_state.quiz_data = result
                        st.success(f"✓ Generated {len(result['questions'])} questions")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)

# Quiz Interface
elif st.session_state.quiz_data and not st.session_state.quiz_submitted:
    questions = st.session_state.quiz_data['questions']
    current_q = st.session_state.current_question
    question = questions[current_q]
    
    # Progress
    progress = (current_q + 1) / len(questions)
    st.progress(progress)
    st.markdown(f"**Question {current_q + 1} of {len(questions)}**")
    
    # Question
    st.markdown(f"""
    <div class="question-box">
        <div class="question-text">{question['question']}</div>
        <small style="color: #803416; font-weight: 600;">{question['difficulty'].upper()}</small>
    </div>
    """, unsafe_allow_html=True)
    
    # Options
    user_answer = st.radio(
        "Select your answer:",
        options=question['options'],
        key=f"q_{current_q}",
        index=None if current_q not in st.session_state.user_answers else question['options'].index(st.session_state.user_answers[current_q])
    )
    
    # Feedback
    if user_answer:
        st.session_state.user_answers[current_q] = user_answer
        is_correct = user_answer.startswith(question['correct_answer'])
        
        if is_correct:
            st.markdown(f"""
            <div class="correct-box">
                <strong>✓ Correct</strong><br>
                {question['explanation']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="wrong-box">
                <strong>✗ Wrong</strong><br><br>
                💡 Hint: {question['hint']}
            </div>
            """, unsafe_allow_html=True)
    
    # Navigation
    st.markdown("")
    col1, col2 = st.columns(2)
    
    with col1:
        if current_q > 0:
            if st.button("← Previous"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col2:
        if current_q < len(questions) - 1:
            if st.button("Next →"):
                st.session_state.current_question += 1
                st.rerun()
        else:
            if st.button("Finish"):
                st.session_state.quiz_submitted = True
                st.rerun()

# Results
elif st.session_state.quiz_submitted:
    questions = st.session_state.quiz_data['questions']
    
    # Calculate score
    correct_count = sum(
        1 for i, q in enumerate(questions)
        if i in st.session_state.user_answers and 
        st.session_state.user_answers[i].startswith(q['correct_answer'])
    )
    total_questions = len(questions)
    percentage = (correct_count / total_questions) * 100
    
    # Results
    st.markdown(f"""
    <div class="results-box">
        <h2>Quiz Complete</h2>
        <div class="score-text">{correct_count}/{total_questions}</div>
        <p style="font-size: 1.3rem;">{percentage:.0f}%</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Review
    st.markdown("---")
    st.markdown("### Review")
    
    for i, q in enumerate(questions):
        user_ans = st.session_state.user_answers.get(i, "Not answered")
        is_correct = user_ans.startswith(q['correct_answer'])
        status = "✓" if is_correct else "✗"
        
        st.markdown(f"""
        **{status} Q{i + 1}:** {q['question']}  
        Your answer: {user_ans}  
        Correct: {q['correct_answer']}  
        *{q['explanation']}*
        """)
        st.markdown("")
    
    # Restart
    st.markdown("---")
    if st.button("New Quiz"):
        st.session_state.quiz_data = None
        st.session_state.current_question = 0
        st.session_state.user_answers = {}
        st.session_state.quiz_submitted = False
        st.rerun()
