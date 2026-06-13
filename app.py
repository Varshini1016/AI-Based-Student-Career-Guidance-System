from flask import Flask, request, jsonify, render_template
import pandas as pd
import pickle
import random
import re
import os
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

LEARNING_RESOURCES = {
    "Data Scientist": ["Coursera: IBM Data Science", "Kaggle tutorials", "Book: Introduction to Statistical Learning"],
    "Software Developer": ["LeetCode", "Udemy: Complete Java Masterclass", "Clean Code by Robert C. Martin"],
    "Cybersecurity Analyst": ["CompTIA Security+", "TryHackMe", "Cybrary"],
    "AI/ML Engineer": ["DeepLearning.AI", "Fast.ai", "Hands-On Machine Learning with Scikit-Learn"],
    "Web Developer": ["FreeCodeCamp", "The Odin Project", "MDN Web Docs"],
    "Cloud Engineer": ["AWS Cloud Practitioner training", "A Cloud Guru", "Docker documentation"],
    "Business Analyst": ["Google Data Analytics Certificate", "Tableau Training", "SQL Zoo"]
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
        pred_encoded = model.predict(input_df)
        pred_proba = model.predict_proba(input_df)
        
        career = le_career.inverse_transform(pred_encoded)[0]
        confidence = round(max(pred_proba[0]) * 100, 2)
        
        # Calculate Placement Probability (Heuristic based on CGPA and Aptitude)
        placement_prob = min(99, max(10, round(((cgpa / 10) * 0.5 + (aptitude / 100) * 0.5) * 100) + random.randint(-5, 5)))
        
        # Skill Gap Analysis
        student_skills = data.get("student_skills", "").lower()
        target_skills = REQUIRED_SKILLS.get(career, [])
        skill_gaps = []
        for skill in target_skills:
            if skill.lower() not in student_skills:
                skill_gaps.append(skill)
                
        # Learning Recommendations
        recommendations = LEARNING_RESOURCES.get(career, ["Generic Tech Blog", "Coursera"])
        
        return jsonify({
            "status": "success",
            "career": career,
            "confidence": confidence,
            "placement_probability": placement_prob,
            "target_skills": target_skills,
            "skill_gaps": skill_gaps,
            "recommendations": recommendations
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
        
        # Simple keyword extraction
        all_skills = set(skill.lower() for skills in REQUIRED_SKILLS.values() for skill in skills)
        all_skills.update(["python", "java", "c++", "sql", "react", "html", "css", "machine learning"])
        
        found_skills = [skill for skill in all_skills if re.search(r'\b' + re.escape(skill) + r'\b', content)]
        
        return jsonify({
            "status": "success",
            "skills_found": found_skills,
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
