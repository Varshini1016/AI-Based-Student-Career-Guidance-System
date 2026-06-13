import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
import pickle
import os

# Load dataset
print("Loading dataset...")
data = pd.read_csv("dataset/career_dataset.csv")

# Separate Features and Target
X = data.drop(columns=['Career'])
y = data['Career']

# Initialize LabelEncoder for Categorical data
le_interest = LabelEncoder()
le_career = LabelEncoder()

# Fit and transform
X['Interest'] = le_interest.fit_transform(X['Interest'])
y_encoded = le_career.fit_transform(y)

# Train Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# Train Model
print("Training Random Forest Model...")
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
accuracy = model.score(X_test, y_test)
print(f"Model Accuracy: {accuracy * 100:.2f}%")

# Create models directory if not exists
os.makedirs('models', exist_ok=True)

# Save the model and encoders
print("Saving model and encoders...")
with open("models/career_model.pkl", "wb") as f:
    pickle.dump(model, f)

with open("models/label_encoders.pkl", "wb") as f:
    pickle.dump({
        'interest': le_interest,
        'career': le_career
    }, f)

# Let's save feature columns used for prediction
with open("models/features.pkl", "wb") as f:
    pickle.dump(X.columns.tolist(), f)

print("Training completed successfully!")
