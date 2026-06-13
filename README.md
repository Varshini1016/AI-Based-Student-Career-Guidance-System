# AI-Based Student Career Guidance System

This is a Machine Learning-based web application designed to help students identify suitable career paths based on their academic performance, technical skills, interests, and aptitude scores.

## Features

- **Career Prediction**: Uses a trained Random Forest model to predict the most suitable career.
- **Skill Gap Analysis**: Compares a student's current skills with the skills required for the target career.
- **Learning Recommendations**: Suggests targeted learning resources.
- **Placement Probability**: Predicts placement chances using a custom heuristic algorithm.
- **Resume Analyzer**: Upload a text resume to automatically extract your skills.
- **Career Chatbot**: An interactive chatbot providing basic career guidance.

## Architecture

```text
Student Inputs
      ↓
Data Preprocessing (Label Encoding)
      ↓
Machine Learning Model (Random Forest)
      ↓
Career Prediction & Placement Probability
      ↓
Recommendations & Skill Gap Analysis
```

## Setup Instructions

### 1. Prerequisites
Ensure you have Python 3 installed. 

### 2. Install Dependencies
Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

### 3. Generate Dataset
Generate the synthetic dataset containing student profiles and corresponding careers:
```bash
python dataset/generate_dataset.py
```
*This will create `dataset/career_dataset.csv` with 500 records.*

### 4. Train the Model
Train the Random Forest Classifier on the generated dataset:
```bash
python train_model.py
```
*This will save the trained model and label encoders in the `models/` directory.*

### 5. Run the Application
Start the Flask backend server:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000`.

## Directory Structure
```
AI-Career-Guidance-System/
├── dataset/
│   ├── generate_dataset.py
│   └── career_dataset.csv
├── models/
│   ├── career_model.pkl
│   ├── label_encoders.pkl
│   └── features.pkl
├── static/
│   ├── style.css
│   └── script.js
├── templates/
│   └── index.html
├── train_model.py
├── app.py
├── requirements.txt
└── README.md
```

## Technologies Used
- **Frontend**: HTML5, Vanilla CSS (Glassmorphism design), JavaScript
- **Backend**: Python, Flask
- **Machine Learning**: Pandas, NumPy, Scikit-Learn
