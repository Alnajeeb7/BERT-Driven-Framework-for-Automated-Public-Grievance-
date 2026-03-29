import traceback
import sys
import os
import pandas as pd
import nltk
from tokenization import tokenize_data

try:
    print(f"Current Directory: {os.getcwd()}")
    print(f"Files: {os.listdir('.')}")
    tokenize_data()
    print("TOKENIZATION SUCCESS")
except Exception as e:
    print("TOKENIZATION FAILED")
    traceback.print_exc()
    sys.exit(1)
