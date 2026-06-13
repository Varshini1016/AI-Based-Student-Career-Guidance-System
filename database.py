import sqlite3
import os

DB_NAME = "career_guidance.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Create Profiles Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cgpa REAL,
            python INTEGER,
            java INTEGER,
            aptitude INTEGER,
            communication INTEGER,
            interest TEXT,
            predicted_career TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create Resume Analysis History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resume_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_career TEXT,
            ats_score INTEGER,
            missing_skills TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized successfully!")

if __name__ == "__main__":
    init_db()
