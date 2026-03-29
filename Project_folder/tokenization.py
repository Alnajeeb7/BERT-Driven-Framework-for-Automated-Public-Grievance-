import pandas as pd
import nltk
from nltk.tokenize import word_tokenize

import os

# Ensure local nltk_data is found
nltk.data.path.insert(0, os.getcwd())

def tokenize_data():
    print("Loading synthetic_grievances.csv...")
    file_path = "synthetic_grievances.csv"
    df = pd.read_csv(file_path)
    
    print("Performing tokenization...")
    df['Title Tokens'] = df['Grievance Title'].apply(lambda x: word_tokenize(str(x)))
    df['Summary Tokens'] = df['Brief Summary'].apply(lambda x: word_tokenize(str(x)))
    df['Description Tokens'] = df['Detailed Description'].apply(lambda x: word_tokenize(str(x)))
    
    df.to_csv("tokenized_grievances.csv", index=False)
    print("Tokenization complete. Saved to tokenized_grievances.csv")

if __name__ == "__main__":
    tokenize_data()
