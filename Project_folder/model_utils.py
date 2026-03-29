import random
import torch
from transformers import BertTokenizer, BertForSequenceClassification
import torch.nn.functional as F

# Simulated BERT for now to avoid heavy downloads if not needed, 
# but structured for real model swap.
# In a real production environment, we'd load a fine-tuned model here.

CATEGORIES = ["Water Supply", "Electricity", "Roads & Infrastructure", "Sanitation", "Public Safety", "Healthcare", "Education", "Waste Management", "Drainage", "Street Lighting"]
PRIORITIES = ["Low", "Medium", "High", "Urgent"]

class BERTClassifier:
    def __init__(self):
        # In a real scenario:
        # self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        # self.model = BertForSequenceClassification.from_pretrained('./path_to_model')
        # self.model.eval()
        pass

    def predict(self, text):
        """
        Simulate BERT inference.
        Returns predicted category, priority, and confidence.
        """
        text_lower = text.lower()
        
        # Keyword-based simulation for 'BERT' feel
        scores = {cat: 0.1 for cat in CATEGORIES}
        if "water" in text_lower or "leak" in text_lower: scores["Water Supply"] += 0.8
        if "light" in text_lower or "dark" in text_lower: scores["Street Lighting"] += 0.8
        if "waste" in text_lower or "garbage" in text_lower: scores["Waste Management"] += 0.8
        if "road" in text_lower or "pothole" in text_lower: scores["Roads & Infrastructure"] += 0.8
        if "safe" in text_lower or "crime" in text_lower: scores["Public Safety"] += 0.8
        
        # Softmax-like normalization
        total = sum(scores.values())
        probs = {k: v/total for k, v in scores.items()}
        
        pred_cat = max(probs, key=probs.get)
        confidence = round(probs[pred_cat], 4)
        
        # Priority logic
        priority = "Low"
        if any(word in text_lower for word in ["urgent", "broken", "danger", "emergency"]):
            priority = "High"
        elif any(word in text_lower for word in ["broken", "immediate"]):
            priority = "Urgent"
        elif len(text_lower) > 50:
            priority = "Medium"
            
        return pred_cat, priority, confidence

# Singleton instance
classifier = BERTClassifier()

def get_bert_prediction(text):
    return classifier.predict(text)
