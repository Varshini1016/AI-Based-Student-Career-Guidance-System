import pandas as pd
import numpy as np
import random
import os

# Define the possible values
interests = ["AI", "Development", "Security", "Data", "Cloud", "Business", "Networking"]
careers = [
    "Data Scientist",
    "Software Developer",
    "Cybersecurity Analyst",
    "AI/ML Engineer",
    "Web Developer",
    "Cloud Engineer",
    "Business Analyst"
]

# Create an empty list to store records
data = []

np.random.seed(42)
random.seed(42)

for i in range(500):
    # Base randomized values
    cgpa = round(np.random.uniform(6.0, 9.8), 1)
    python = random.randint(3, 10)
    java = random.randint(3, 10)
    aptitude = random.randint(50, 100)
    communication = random.randint(4, 10)
    
    interest = random.choice(interests)
    
    # Logic to map combinations to careers to make the model learn well
    if interest == "AI" or interest == "Data":
        if python >= 7 and aptitude >= 70:
            career = "Data Scientist" if interest == "Data" else "AI/ML Engineer"
        else:
            career = "Business Analyst" # fallback
    elif interest == "Security":
        if aptitude >= 75:
            career = "Cybersecurity Analyst"
        else:
            career = "Software Developer"
    elif interest == "Cloud" or interest == "Networking":
        if python >= 6:
            career = "Cloud Engineer"
        else:
            career = "Web Developer"
    elif interest == "Development":
        if java >= 7 or python >= 7:
            career = "Software Developer" if java >= python else "Web Developer"
        else:
            career = "Business Analyst"
    elif interest == "Business":
        if communication >= 7:
            career = "Business Analyst"
        else:
            career = "Data Scientist" # random fallback
    else:
        career = random.choice(careers)

    # Add some noise to the data (random selection occasionally)
    if random.random() < 0.1: # 10% noise
        career = random.choice(careers)

    data.append([cgpa, python, java, aptitude, communication, interest, career])

# Create DataFrame
df = pd.DataFrame(data, columns=["CGPA", "Python", "Java", "Aptitude", "Communication", "Interest", "Career"])

# Ensure directory exists
os.makedirs('dataset', exist_ok=True)

# Save to CSV
df.to_csv("dataset/career_dataset.csv", index=False)
print("Dataset created successfully with 500 records at dataset/career_dataset.csv!")
