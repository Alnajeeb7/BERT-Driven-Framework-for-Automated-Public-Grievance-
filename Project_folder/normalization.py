import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string

import os

# Ensure local nltk_data is found
nltk.data.path.insert(0, os.getcwd())

def normalize_text(tokens):
    if not isinstance(tokens, list):
        # Handle cases where tokens might be string representation from CSV
        try:
            import ast
            tokens = ast.literal_eval(tokens)
        except:
            return ""
            
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    # Normalization: Lowercase, No punctuation, No stopwords, Lemmatization
    normalized = [
        lemmatizer.lemmatize(token.lower()) 
        for token in tokens 
        if token.lower() not in stop_words and token not in string.punctuation
    ]
    return " ".join(normalized)

def normalize_data():
    print("Loading tokenized_grievances.csv...")
    df = pd.read_csv("tokenized_grievances.csv")
    
    print("Performing normalization...")
    df['Normalized Title'] = df['Title Tokens'].apply(normalize_text)
    df['Normalized Summary'] = df['Summary Tokens'].apply(normalize_text)
    df['Normalized Description'] = df['Description Tokens'].apply(normalize_text)
    
    df.to_csv("normalized_grievances.csv", index=False)
    print("Normalization complete. Saved to normalized_grievances.csv")

if __name__ == "__main__":
    normalize_data()
