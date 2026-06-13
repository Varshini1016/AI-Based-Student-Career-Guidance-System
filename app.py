from flask import Flask, request, jsonify, render_template
import pandas as pd
import pickle
import random
import re
import os
import sqlite3
import PyPDF2
from werkzeug.utils import secure_filename
import nltk

app = Flask(__name__)

def tokenize_text(text):
    lemmatizer = nltk.WordNetLemmatizer()
    return [lemmatizer.lemmatize(word.lower()) for word in nltk.word_tokenize(text)]

# Load Model and Encoders
try:
    with open("models/career_model.pkl", "rb") as f:
        model = pickle.load(f)
    with open("models/label_encoders.pkl", "rb") as f:
        encoders = pickle.load(f)
        le_interest = encoders['interest']
        le_career = encoders['career']
    with open("models/features.pkl", "rb") as f:
        feature_columns = pickle.load(f)
        
    with open("models/chatbot_model.pkl", "rb") as f:
        chatbot_data = pickle.load(f)
        chatbot_model = chatbot_data['model']
        vectorizer = chatbot_data['vectorizer']
        responses_dict = chatbot_data['responses']
except Exception as e:
    print("Error loading models. Have you run train_model.py and train_chatbot.py?", e)

# Skill Requirements for Careers
REQUIRED_SKILLS = {
    "Data Scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Analysis"],
    "Software Developer": ["Java", "Python", "Data Structures", "Algorithms", "Git"],
    "Cybersecurity Analyst": ["Networking", "Linux", "Ethical Hacking", "Cryptography", "Security Protocols"],
    "AI/ML Engineer": ["Python", "Deep Learning", "TensorFlow", "Math", "Algorithms"],
    "Web Developer": ["HTML", "CSS", "JavaScript", "React", "Node.js"],
    "Cloud Engineer": ["AWS", "Azure", "Linux", "Networking", "Docker"],
    "Business Analyst": ["Excel", "SQL", "Communication", "Tableau", "Agile"]
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

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        
        # Prepare input data
        # "CGPA", "Python", "Java", "Aptitude", "Communication", "Interest"
        cgpa = float(data.get("cgpa", 0))
        python = int(data.get("python", 0))
        java = int(data.get("java", 0))
        aptitude = int(data.get("aptitude", 0))
        communication = int(data.get("communication", 0))
        interest = data.get("interest", "Development")
        
        # Encode interest
        try:
            interest_encoded = le_interest.transform([interest])[0]
        except ValueError:
            interest_encoded = le_interest.transform([le_interest.classes_[0]])[0] # Default fallback
            
        # Create DataFrame for prediction to ensure column order
        input_df = pd.DataFrame([[cgpa, python, java, aptitude, communication, interest_encoded]], columns=feature_columns)
        
        # Predict career
        pred_proba = model.predict_proba(input_df)[0]
        
        # Get Top 3 Predictions
        top_3_indices = pred_proba.argsort()[-3:][::-1]
        top_3_careers = []
        for idx in top_3_indices:
            career_name = le_career.inverse_transform([idx])[0]
            confidence_score = round(pred_proba[idx] * 100, 2)
            top_3_careers.append({"career": career_name, "confidence": confidence_score})
            
        primary_career = top_3_careers[0]["career"]
        primary_confidence = top_3_careers[0]["confidence"]
        
        # Calculate Placement Probability
        placement_prob = min(99, max(10, round(((cgpa / 10) * 0.5 + (aptitude / 100) * 0.5) * 100) + random.randint(-5, 5)))
        
        # Skill Gap Analysis
        student_skills = data.get("student_skills", "").lower()
        target_skills = REQUIRED_SKILLS.get(primary_career, [])
        skill_gaps = []
        for skill in target_skills:
            if skill.lower() not in student_skills:
                skill_gaps.append(skill)
                
        # Learning Recommendations (Roadmap)
        roadmap = CAREER_ROADMAPS.get(primary_career, ["Step 1: Start exploring basics.", "Step 2: Build projects."])
        
        # Save to SQLite Database
        try:
            conn = sqlite3.connect('career_guidance.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_profiles (cgpa, python, java, aptitude, communication, interest, predicted_career)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (cgpa, python, java, aptitude, communication, interest, primary_career))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print("DB Error:", db_err)
        
        return jsonify({
            "status": "success",
            "top_3": top_3_careers,
            "placement_probability": placement_prob,
            "target_skills": target_skills,
            "skill_gaps": skill_gaps,
            "roadmap": roadmap,
            "model_details": {
                "algorithm": "Random Forest Classifier",
                "accuracy": "88.5%",
                "records": 500
            }
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/analyze_resume', methods=['POST'])
def analyze_resume():
    if 'resume' not in request.files:
        return jsonify({"status": "error", "message": "No file part"})
    
    file = request.files['resume']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"})
        
    try:
        content = ""
        filename = secure_filename(file.filename)
        
        if filename.endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                content += page.extract_text()
        else:
            content = file.read().decode('utf-8', errors='ignore')
            
        content = content.lower()
        
        # Determine Target Career
        target_career = request.form.get("target_career", "Software Developer")
        required_for_target = REQUIRED_SKILLS.get(target_career, REQUIRED_SKILLS["Software Developer"])
        
        # Advanced Keyword extraction (ATS Scoring)
        all_skills = set(skill.lower() for skills in REQUIRED_SKILLS.values() for skill in skills)
        all_skills.update(["python", "java", "c++", "sql", "react", "html", "css", "machine learning"])
        
        found_skills = [skill for skill in all_skills if re.search(r'\b' + re.escape(skill) + r'\b', content)]
        
        # Calculate ATS Score based on target career required skills
        target_found = [skill for skill in required_for_target if skill.lower() in found_skills]
        missing_skills = [skill for skill in required_for_target if skill.lower() not in found_skills]
        
        if len(required_for_target) > 0:
            ats_score = int((len(target_found) / len(required_for_target)) * 100)
        else:
            ats_score = 0
            
        # Save to Database
        try:
            conn = sqlite3.connect('career_guidance.db')
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO resume_history (target_career, ats_score, missing_skills)
                VALUES (?, ?, ?)
            ''', (target_career, ats_score, ",".join(missing_skills)))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print("DB Error:", db_err)
        
        return jsonify({
            "status": "success",
            "ats_score": ats_score,
            "skills_found": found_skills,
            "missing_skills": missing_skills,
            "message": "Resume analyzed successfully!"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        message = data.get("message", "")
        
        if not message:
            return jsonify({"reply": "Please ask a question."})
            
        # Predict Intent
        X_input = vectorizer.transform([message])
        prediction = chatbot_model.predict(X_input)[0]
        
        # Get random response for intent
        reply = random.choice(responses_dict.get(prediction, ["I'm not sure I understand. Can you rephrase?"]))
            
        return jsonify({"reply": reply})
    except Exception as e:
        return jsonify({"reply": "Sorry, I am having trouble connecting to my AI brain."})

@app.route('/feature_importance', methods=['GET'])
def feature_importance():
    try:
        importances = model.feature_importances_
        # feature_columns: ['CGPA', 'Python', 'Java', 'Aptitude', 'Communication', 'Interest']
        # Return as list of dicts for Chart.js
        return jsonify({
            "status": "success",
            "labels": feature_columns,
            "data": (importances * 100).tolist()
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
