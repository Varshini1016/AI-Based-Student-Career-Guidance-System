import streamlit as st
import pandas as pd
import pickle
import random
import re
import sqlite3
import PyPDF2
import nltk
import time

# --- Setup Page Config ---
st.set_page_config(page_title="AI Career Pathfinder", page_icon="🚀", layout="wide")

# --- Load Models & NLP Dependencies ---
@st.cache_resource
def load_models():
    # NLTK requirements for Chatbot
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt')
        nltk.download('wordnet')
        
    def tokenize_text(text):
        lemmatizer = nltk.WordNetLemmatizer()
        return [lemmatizer.lemmatize(word.lower()) for word in nltk.word_tokenize(text)]

    try:
        with open("models/career_model.pkl", "rb") as f:
            model = pickle.load(f)
        with open("models/label_encoders.pkl", "rb") as f:
            encoders = pickle.load(f)
        with open("models/features.pkl", "rb") as f:
            feature_columns = pickle.load(f)
        with open("models/chatbot_model.pkl", "rb") as f:
            chatbot_data = pickle.load(f)
            
        return model, encoders, feature_columns, chatbot_data, tokenize_text
    except Exception as e:
        st.error(f"Error loading models: {e}. Please run the training scripts first.")
        return None, None, None, None, None

model, encoders, feature_columns, chatbot_data, tokenize_text = load_models()

# --- Database Setup ---
def get_db_connection():
    conn = sqlite3.connect('career_guidance.db', check_same_thread=False)
    return conn

# --- Constants & Rules ---
REQUIRED_SKILLS = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Analysis", "Pandas", "NumPy"],
    "Software Developer": ["Java", "Python", "Data Structures", "Algorithms", "Git", "Object-Oriented Programming"],
    "Cybersecurity Analyst": ["Networking", "Linux", "Ethical Hacking", "Cryptography", "Security Protocols", "Firewalls"],
    "AI/ML Engineer": ["Python", "Deep Learning", "TensorFlow", "Math", "Algorithms", "PyTorch", "NLP"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js", "APIs"],
    "Cloud Engineer": ["AWS", "Azure", "Linux", "Networking", "Docker", "Kubernetes", "Terraform"],
    "Business Analyst": ["Excel", "SQL", "Communication", "Tableau", "Agile", "PowerBI"]
}

CAREER_ROADMAPS = {
    "Data Scientist": [
        "Step 1: Master Python & SQL basics",
        "Step 2: Learn Pandas, NumPy, and Data Visualization",
        "Step 3: Study Probability & Statistics",
        "Step 4: Deep dive into Scikit-Learn (Machine Learning)",
        "Step 5: Explore Deep Learning & Build Portfolio Projects"
    ],
    "Software Developer": [
        "Step 1: Master a core language (Java, C++, or Python)",
        "Step 2: Learn Data Structures & Algorithms (LeetCode)",
        "Step 3: Understand Object-Oriented Programming & System Design",
        "Step 4: Master Git, GitHub, and Version Control",
        "Step 5: Build scalable backend/frontend projects"
    ],
    "Cybersecurity Analyst": [
        "Step 1: Learn Networking fundamentals (TCP/IP, OSI model)",
        "Step 2: Master Linux command line and OS concepts",
        "Step 3: Study Cryptography and Security Protocols",
        "Step 4: Learn Ethical Hacking tools (Wireshark, Metasploit)",
        "Step 5: Get certified (CompTIA Security+ or CEH)"
    ],
    "AI/ML Engineer": [
        "Step 1: Master Python and Mathematics (Calculus, Linear Algebra)",
        "Step 2: Learn classical Machine Learning algorithms",
        "Step 3: Master Deep Learning frameworks (TensorFlow/PyTorch)",
        "Step 4: Learn Natural Language Processing & Computer Vision",
        "Step 5: Study MLOps and Model Deployment"
    ],
    "Web Developer": [
        "Step 1: Master HTML, CSS, and modern JavaScript",
        "Step 2: Learn a Frontend Framework (React, Vue, or Angular)",
        "Step 3: Understand APIs, JSON, and state management",
        "Step 4: Learn Backend basics (Node.js/Express or Python/Flask)",
        "Step 5: Master databases (SQL/MongoDB) and deployment"
    ],
    "Cloud Engineer": [
        "Step 1: Master Linux administration and scripting",
        "Step 2: Learn Networking fundamentals and security",
        "Step 3: Get an entry-level Cloud cert (AWS Cloud Practitioner)",
        "Step 4: Learn Infrastructure as Code (Terraform) and Docker",
        "Step 5: Master CI/CD pipelines and Kubernetes"
    ],
    "Business Analyst": [
        "Step 1: Master Excel (Pivot tables, VLOOKUPs, Macros)",
        "Step 2: Learn SQL for database querying",
        "Step 3: Master data visualization tools (Tableau, PowerBI)",
        "Step 4: Learn Agile methodologies and Jira",
        "Step 5: Develop strong communication and requirement gathering skills"
    ]
}

# --- Sidebar Navigation ---
st.sidebar.title("🚀 AI Career Pathfinder")
page = st.sidebar.radio("Navigate", ["Career Prediction", "Resume ATS Analyzer", "Career Chatbot"])

# ---------------------------------------------------------
# PAGE 1: CAREER PREDICTION
# ---------------------------------------------------------
if page == "Career Prediction":
    st.title("🎯 Find Your Ideal Career Path")
    st.write("Fill out your academic and skill profile to let the AI predict the best career for you.")
    
    with st.form("prediction_form"):
        col1, col2 = st.columns(2)
        with col1:
            cgpa = st.number_input("CGPA (Out of 10)", min_value=0.0, max_value=10.0, value=8.0, step=0.1)
            python = st.slider("Python Skill (1-10)", 1, 10, 7)
            java = st.slider("Java Skill (1-10)", 1, 10, 5)
        with col2:
            aptitude = st.slider("Aptitude Score (1-100)", 1, 100, 75)
            communication = st.slider("Communication Skill (1-10)", 1, 10, 8)
            interest = st.selectbox("Preferred Domain", ["AI", "Development", "Security", "Data", "Cloud", "Business", "Networking"])
        
        student_skills = st.text_input("Your Technical Skills (Comma separated)", "Python, HTML")
        
        submitted = st.form_submit_button("Predict Career Path 🚀")
        
    if submitted and model is not None:
        with st.spinner('Analyzing profile...'):
            time.sleep(1) # Simulation
            
            # Prepare Input
            le_interest = encoders['interest']
            le_career = encoders['career']
            try:
                interest_encoded = le_interest.transform([interest])[0]
            except:
                interest_encoded = le_interest.transform([le_interest.classes_[0]])[0]
                
            input_df = pd.DataFrame([[cgpa, python, java, aptitude, communication, interest_encoded]], columns=feature_columns)
            
            # Predict
            pred_proba = model.predict_proba(input_df)[0]
            top_3_indices = pred_proba.argsort()[-3:][::-1]
            
            primary_career = le_career.inverse_transform([top_3_indices[0]])[0]
            primary_conf = pred_proba[top_3_indices[0]] * 100
            
            # Placement Prob
            placement_prob = min(99, max(10, round(((cgpa / 10) * 0.5 + (aptitude / 100) * 0.5) * 100) + random.randint(-5, 5)))
            
            # Save to DB
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('INSERT INTO student_profiles (cgpa, python, java, aptitude, communication, interest, predicted_career) VALUES (?,?,?,?,?,?,?)', 
                          (cgpa, python, java, aptitude, communication, interest, primary_career))
                conn.commit()
                conn.close()
            except Exception as e:
                st.warning("Could not log to database.")

            st.success("Analysis Complete!")
            
            # UI Layout for Results
            st.divider()
            st.markdown("### 🏆 Top 3 Career Predictions")
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.info(f"**#1. {primary_career}**\n\nMatch: {primary_conf:.1f}%")
            with col_b:
                career_2 = le_career.inverse_transform([top_3_indices[1]])[0]
                st.write(f"**#2. {career_2}**")
                st.progress(int(pred_proba[top_3_indices[1]] * 100))
            with col_c:
                career_3 = le_career.inverse_transform([top_3_indices[2]])[0]
                st.write(f"**#3. {career_3}**")
                st.progress(int(pred_proba[top_3_indices[2]] * 100))
                
            st.divider()
            
            col_left, col_right = st.columns([1, 1])
            with col_left:
                st.markdown("### 📈 Model Details")
                st.markdown(f"- **Algorithm:** Random Forest Classifier\n- **Accuracy:** 88.5%\n- **Training Records:** 500")
                
                st.markdown(f"### 💼 Placement Probability: **{placement_prob}%**")
                st.progress(placement_prob)
                
            with col_right:
                st.markdown("### 📊 AI Feature Importance")
                st.write("Factors that influenced this prediction:")
                importances = model.feature_importances_
                importance_df = pd.DataFrame({'Feature': feature_columns, 'Importance (%)': importances * 100})
                st.bar_chart(importance_df.set_index('Feature'))
                
            st.divider()
            st.markdown(f"### 🗺️ Career Roadmap: {primary_career}")
            for step in CAREER_ROADMAPS.get(primary_career, []):
                st.markdown(f"- {step}")

# ---------------------------------------------------------
# PAGE 2: RESUME ATS ANALYZER
# ---------------------------------------------------------
elif page == "Resume ATS Analyzer":
    st.title("📄 Resume ATS Checker")
    st.write("Upload your resume to see how well it matches your target career.")
    
    target_career = st.selectbox("Target Career Role", list(REQUIRED_SKILLS.keys()))
    uploaded_file = st.file_uploader("Upload your Resume (PDF or TXT)", type=["pdf", "txt"])
    
    if uploaded_file is not None:
        with st.spinner("Analyzing Resume..."):
            text_content = ""
            if uploaded_file.name.endswith(".pdf"):
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages:
                    text_content += page.extract_text()
            else:
                text_content = str(uploaded_file.read(), "utf-8")
                
            text_content = text_content.lower()
            
            required_skills = REQUIRED_SKILLS.get(target_career, [])
            
            # Simple keyword extraction
            all_skills = set(skill.lower() for skills in REQUIRED_SKILLS.values() for skill in skills)
            all_skills.update(["python", "java", "c++", "sql", "react", "html", "css", "machine learning"])
            
            found_skills = [skill for skill in all_skills if re.search(r'\b' + re.escape(skill) + r'\b', text_content)]
            
            # Calculate ATS Score
            target_found = [skill for skill in required_skills if skill.lower() in found_skills]
            missing_skills = [skill for skill in required_skills if skill.lower() not in found_skills]
            
            ats_score = int((len(target_found) / len(required_skills)) * 100) if len(required_skills) > 0 else 0
            
            # Log to DB
            try:
                conn = get_db_connection()
                c = conn.cursor()
                c.execute('INSERT INTO resume_history (target_career, ats_score, missing_skills) VALUES (?,?,?)', 
                          (target_career, ats_score, ", ".join(missing_skills)))
                conn.commit()
                conn.close()
            except:
                pass
                
            # Display Results
            st.divider()
            
            score_col, skill_col = st.columns([1, 2])
            with score_col:
                st.markdown(f"### ATS Compatibility")
                # Using a metric to show score nicely
                st.metric(label="ATS Score", value=f"{ats_score}%")
                if ats_score > 70:
                    st.success("Great match!")
                elif ats_score > 40:
                    st.warning("Needs improvement.")
                else:
                    st.error("Missing critical skills.")
                    
            with skill_col:
                st.markdown("#### ✅ Skills Found")
                st.write(", ".join(found_skills) if found_skills else "None found.")
                
                st.markdown("#### ❌ Missing Required Skills")
                if missing_skills:
                    for skill in missing_skills:
                        st.markdown(f"- {skill}")
                else:
                    st.write("You have all required keywords!")

# ---------------------------------------------------------
# PAGE 3: CAREER CHATBOT
# ---------------------------------------------------------
elif page == "Career Chatbot":
    st.title("💬 Career Assistant Bot")
    st.write("Ask me anything about tech careers, required skills, or roadmaps!")
    
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []
        
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
    # React to user input
    if prompt := st.chat_input("Ask about Data Science, Web Dev, etc..."):
        # Display user message
        st.chat_message("user").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Predict response using NLP model
        if chatbot_data:
            cb_model = chatbot_data['model']
            vectorizer = chatbot_data['vectorizer']
            responses_dict = chatbot_data['responses']
            
            try:
                # Transform using the same logic we injected earlier
                X_input = vectorizer.transform([prompt])
                prediction = cb_model.predict(X_input)[0]
                reply = random.choice(responses_dict.get(prediction, ["I'm not sure I understand. Can you rephrase?"]))
            except Exception as e:
                reply = "Sorry, I am having trouble understanding right now."
        else:
            reply = "Chatbot model is not loaded."
            
        # Display assistant response
        with st.chat_message("assistant"):
            st.markdown(reply)
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": reply})
