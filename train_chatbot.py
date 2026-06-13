import json
import pickle
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import nltk
from nltk.stem import WordNetLemmatizer
import os

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('wordnet')

lemmatizer = WordNetLemmatizer()

# Load intents
with open('dataset/intents.json', 'r') as file:
    intents = json.load(file)

documents = []
classes = []
responses_dict = {}

for intent in intents['intents']:
    for pattern in intent['patterns']:
        documents.append(pattern)
        classes.append(intent['tag'])
    responses_dict[intent['tag']] = intent['responses']

def tokenize_text(text):
    return [lemmatizer.lemmatize(word.lower()) for word in nltk.word_tokenize(text)]

# TF-IDF Vectorizer
vectorizer = TfidfVectorizer(tokenizer=tokenize_text, stop_words='english')
X = vectorizer.fit_transform(documents)

# Train a classifier (Logistic Regression works well for intent classification)
model = LogisticRegression(random_state=42, max_iter=200)
model.fit(X, classes)

# Ensure models directory exists
os.makedirs('models', exist_ok=True)

# Save the model, vectorizer, and responses
with open('models/chatbot_model.pkl', 'wb') as f:
    pickle.dump({
        'model': model,
        'vectorizer': vectorizer,
        'responses': responses_dict
    }, f)

print("Chatbot model trained and saved successfully!")
