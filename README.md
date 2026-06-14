<<<<<<< HEAD
# AI-Based Student Career Guidance System ⭐⭐⭐⭐⭐

An intelligent, full-stack Machine Learning web application designed to help final-year students identify suitable career paths based on academic performance, technical skills, interests, and aptitude scores. 

## Features
- **Top 3 Career Predictions**: Uses Random Forest probability distribution to suggest the top 3 most suitable careers.
- **Model Interpretability Dashboard**: Interactive `Chart.js` graphs displaying exactly which features (CGPA, Aptitude, Skills) influenced the AI's decision.
- **Advanced Resume Analyzer (ATS)**: Upload a `.pdf` or `.txt` resume. The system uses NLP keyword matching to generate an ATS Compatibility Score (/100) and lists explicitly missing skills for your target career.
- **Dynamic Career Roadmaps**: Generates a 5-step structured learning path for the predicted career.
- **NLP Career Chatbot**: Integrated `NLTK` + `Scikit-Learn` TF-IDF intent-classification bot to answer career-related queries.
- **SQLite Database**: Automatically logs student profiles, predictions, and resume analysis history.

## Architecture Diagram

```text
User Inputs (UI)   --->   Flask Backend   --->   SQLite Database (Logging)
      │                         │
      v                         v
PDF / TXT Resume   --->   NLP Parser & ATS Scoring
                                │
                                v
                   Machine Learning Core (Random Forest)
                   - Data Preprocessing (Label Encoding)
                   - Probability Distribution (predict_proba)
                   - Feature Importance Extraction
                                │
                                v
                   Dynamic Results Generation
                   - Top 3 Predictions
                   - 5-Step Career Roadmap
                   - Interactive Chart.js Graphs
```

## ML Workflow
1. **Algorithm Used**: Random Forest Classifier
2. **Why Random Forest?**: It handles non-linear relationships well, is robust to overfitting with 500 records, and easily provides Feature Importances (which we display in the UI) and probabilities (for the Top 3 rankings).
3. **Accuracy**: ~88.5%
4. **Training Records**: 500 synthetically generated realistic student profiles.

## Installation Steps

### 1. Prerequisites
Ensure you have Python 3.8+ installed. 

### 2. Clone the Repository
```bash
git clone https://github.com/yourusername/AI-Career-Guidance-System.git
cd AI-Career-Guidance-System
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database & Train Models
Initialize the SQLite database:
```bash
python database.py
```
Generate the dataset:
```bash
python dataset/generate_dataset.py
```
Train the ML Model & NLP Chatbot:
```bash
python train_model.py
python train_chatbot.py
```

### 5. Run the Application
```bash
python app.py
```
Navigate to `http://127.0.0.1:5000` in your web browser.

## Future Enhancements
- **Java Spring Boot Backend Integration**: Refactor the Python Flask app into a microservice, allowing a Java Spring Boot backend to handle user authentication, routing, and heavier enterprise logic.
- **Web Scraping for Jobs**: Scrape real-time job postings based on the predicted career.

---
## 🔗 Live Demo
https://ai-based-student-career-guidance-system-gu27magissezmmnmb5t5hk.streamlit.app/

*Developed as a Final Year AI & DS Project.*
=======
# AI-Based-Student-Career-Guidance-System
>>>>>>> 45bfa442d818f38a905e5b40697f8f3cffc231d0
