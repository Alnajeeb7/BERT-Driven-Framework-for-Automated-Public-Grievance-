import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import string
import ast

# Setup NLTK paths
NLTK_DATA_DIR = os.path.join(os.getcwd(), 'nltk_data')
if not os.path.exists(NLTK_DATA_DIR):
    os.makedirs(NLTK_DATA_DIR)
nltk.data.path.insert(0, NLTK_DATA_DIR)

def ensure_nltk_data():
    """Ensure all required NLTK resources are available locally."""
    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4')
    ]
    for resource_path, package in resources:
        try:
            nltk.data.find(resource_path)
        except LookupError:
            print(f"Downloading NLTK package: {package}")
            nltk.download(package, download_dir=NLTK_DATA_DIR)

def get_processed_csv_path():
    return 'processed_grievances_output.csv'

def load_processed_data():
    path = get_processed_csv_path()
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return pd.DataFrame()

def save_processed_data(df):
    path = get_processed_csv_path()
    df.to_csv(path, index=False)

def preprocess_text(text):
    """Tokenize and normalize text."""
    ensure_nltk_data()
    tokens = word_tokenize(str(text).lower())
    stop_words = set(stopwords.words('english'))
    lemmatizer = WordNetLemmatizer()
    
    normalized = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token not in stop_words and token not in string.punctuation and token.isalnum()
    ]
    return " ".join(normalized)

def ensure_upload_dir():
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    return upload_dir

SYNTHETIC_CSV = 'synthetic_grievances.csv'
DUMMY_MERGED_FLAG = '.dummy_merged'

def merge_synthetic_data():
    """Merge synthetic_grievances.csv into processed_grievances_output.csv once."""
    if os.path.exists(DUMMY_MERGED_FLAG):
        return  # already done

    synthetic_path = SYNTHETIC_CSV
    if not os.path.exists(synthetic_path):
        return

    try:
        syn = pd.read_csv(synthetic_path)
    except Exception as e:
        print(f"Could not read synthetic data: {e}")
        return

    # Normalize synthetic rows to match processed schema
    import hashlib
    rows = []
    for _, row in syn.iterrows():
        title = str(row.get('Grievance Title', ''))
        uid = 'SYN-' + hashlib.md5(title.encode()).hexdigest()[:8].upper()
        rows.append({
            'id': uid,
            'Grievance Title': title,
            'Detailed Description': str(row.get('Detailed Description', '')),
            'Category': str(row.get('Category', '')),
            'Priority Level': str(row.get('Priority Level', '')),
            'Location / Ward No': str(row.get('Location / Ward No', '')),
            'Department': str(row.get('Department', '')),
            'Status': str(row.get('Status', 'New')),
            'Date Submitted': str(row.get('Date Submitted', '')),
            'Predicted Category': str(row.get('Category', '')),
            'Predicted Priority': str(row.get('Priority Level', '')),
            'Confidence Score': 0.9,
            'Attachment Name': str(row.get('Attachment Name', 'None')),
            'Internal Notes': str(row.get('Internal Notes', '')),
        })

    syn_df = pd.DataFrame(rows)

    existing = load_processed_data()
    if existing.empty:
        combined = syn_df
    else:
        # Avoid duplicating SYN- rows already present
        existing_ids = set(existing['id'].astype(str).tolist())
        syn_df = syn_df[~syn_df['id'].isin(existing_ids)]
        combined = pd.concat([existing, syn_df], ignore_index=True)

    save_processed_data(combined)

    # Write flag so we never re-merge
    with open(DUMMY_MERGED_FLAG, 'w') as f:
        f.write('merged')

    print(f"Merged {len(syn_df)} synthetic records into processed data.")
