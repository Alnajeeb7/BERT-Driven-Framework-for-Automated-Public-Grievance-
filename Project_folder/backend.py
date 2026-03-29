from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
from datetime import datetime
import json

# Import custom modules (simulated for simplicity within one backend instance)
def run_nlp_pipeline(grievance):
    import random
    categories = ["Water Supply", "Electricity", "Roads & Infrastructure", "Sanitation", "Public Safety", "Healthcare", "Education", "Waste Management", "Drainage", "Street Lighting"]
    priorities = ["Low", "Medium", "High", "Urgent"]
    
    # Simple semantic rule for prediction logic
    desc = grievance.get('Detailed Description', '').lower()
    pred_cat = "Water Supply" if "water" in desc or "pipe" in desc else random.choice(categories)
    pred_pri = "High" if "broken" in desc or "urgent" in desc else random.choice(priorities)
    conf = round(random.uniform(0.85, 0.99), 4)
    
    return {
        "Predicted Category": pred_cat,
        "Predicted Priority": pred_pri,
        "Confidence Score": conf,
        "Status": "New",
        "Date Submitted": datetime.now().strftime("%Y-%m-%d")
    }

app = Flask(__name__)
CORS(app)

# Ensure template and static folders are explicit if needed
# app = Flask(__name__, template_folder='templates', static_folder='static')

CSV_FILE = 'processed_grievances_output.csv'

def load_data():
    if not os.path.exists(CSV_FILE):
        return pd.DataFrame()
    return pd.read_csv(CSV_FILE)

@app.route('/')
def dashboard():
    return render_template('index.html')

@app.route('/grievance')
def grievance_page():
    return render_template('grievance.html')

@app.route('/profile')
def profile_page():
    return render_template('profile.html')

@app.route('/api/get_summary')
def get_summary():
    df = load_data()
    if df.empty:
        return jsonify({"total": 0, "open": 0, "resolved": 0, "high_priority": 0})
    
    total = len(df)
    open_cases = len(df[df['Status'] != 'Resolved'])
    resolved = len(df[df['Status'] == 'Resolved'])
    high_priority = len(df[df['Priority Level'].isin(['High', 'Urgent'])])
    
    # Recent 5
    recent = df.head(5).to_dict(orient='records')
    
    return jsonify({
        "total": total,
        "open": open_cases,
        "resolved": resolved,
        "high_priority": high_priority,
        "recent_grievances": recent
    })

@app.route('/api/get_all_grievances')
def get_all():
    df = load_data()
    return jsonify(df.to_dict(orient='records'))

@app.route('/api/submit_grievance', methods=['POST'])
def submit():
    data = request.json
    df = load_data()
    
    # Run AI Pipeline
    ai_results = run_nlp_pipeline(data)
    
    # Merge with form data
    new_entry = {**data, **ai_results}
    
    # Add ID and sync keys that might be missing from form
    new_entry['id'] = f"GRV-{datetime.now().year}-{random.randint(1000, 9999)}"
    
    # Append to CSV
    new_df = pd.concat([pd.DataFrame([new_entry]), df], ignore_index=True)
    new_df.to_csv(CSV_FILE, index=False)
    
    return jsonify(new_entry)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
