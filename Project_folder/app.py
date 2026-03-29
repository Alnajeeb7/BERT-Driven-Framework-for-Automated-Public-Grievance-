import os
import random
import pandas as pd
from flask import Flask, render_template, request, jsonify, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename
from datetime import datetime
import json
import csv
import io

# Import utilities
from data_utils import load_processed_data, save_processed_data, preprocess_text, ensure_upload_dir, ensure_nltk_data, merge_synthetic_data
from model_utils import get_bert_prediction

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = ensure_upload_dir()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB limit
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/grievance')
def grievance():
    return render_template('grievance.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/api/get_summary')
def get_summary():
    df = load_processed_data()
    if df.empty:
        return jsonify({
            "total": 0, "open": 0, "resolved": 0, "high_priority": 0,
            "recent_grievances": [],
            "category_summary": [],
            "priority_distribution": {}
        })

    total = len(df)
    open_cases = len(df[df['Status'] != 'Resolved'])
    resolved = len(df[df['Status'] == 'Resolved'])
    high_priority = len(df[df['Priority Level'].isin(['High', 'Urgent'])])

    # Recent 5
    recent = df.head(5).fillna('').to_dict(orient='records')

    # Category summary
    cat_summary = []
    if 'Category' in df.columns:
        for cat, group in df.groupby('Category'):
            cat_open = len(group[group['Status'] != 'Resolved'])
            cat_closed = len(group[group['Status'] == 'Resolved'])
            cat_summary.append({
                "category": cat,
                "total": len(group),
                "open": cat_open,
                "closed": cat_closed
            })
        cat_summary.sort(key=lambda x: x['total'], reverse=True)

    # Priority distribution
    priority_dist = {}
    if 'Priority Level' in df.columns:
        for pri in ['Low', 'Medium', 'High', 'Urgent']:
            priority_dist[pri] = len(df[df['Priority Level'] == pri])

    return jsonify({
        "total": total,
        "open": open_cases,
        "resolved": resolved,
        "high_priority": high_priority,
        "recent_grievances": recent,
        "category_summary": cat_summary,
        "priority_distribution": priority_dist
    })

@app.route('/api/get_all_grievances')
def get_all_grievances():
    df = load_processed_data()
    if df.empty:
        return jsonify([])
    return jsonify(df.fillna('').to_dict(orient='records'))

@app.route('/api/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({
            "status": "success",
            "filename": filename
        })
    return jsonify({"status": "error", "message": "File type not allowed. Use PNG, JPG, JPEG, or PDF"}), 400

@app.route('/api/submit_grievance', methods=['POST'])
def submit_grievance():
    data = request.json
    if not data:
        return jsonify({"status": "error", "message": "No data received"}), 400

    title = data.get('Grievance Title', '').strip()
    description = data.get('Detailed Description', '').strip()

    if not title:
        return jsonify({"status": "error", "message": "Grievance title is required"}), 400
    if not description:
        return jsonify({"status": "error", "message": "Description is required"}), 400

    # Run AI Prediction
    combined_text = f"{title} {description}"
    pred_cat, pred_pri, confidence = get_bert_prediction(combined_text)

    # Use user-provided category/priority if given, otherwise use AI prediction
    user_cat = data.get('Category', '').strip()
    user_pri = data.get('Priority Level', '').strip()

    # Construct Entry
    new_entry = {
        "id": f"GRV-{datetime.now().year}-{random.randint(1000, 9999)}",
        "Grievance Title": title,
        "Detailed Description": description,
        "Category": user_cat if user_cat and user_cat != 'Select Category' else pred_cat,
        "Priority Level": user_pri if user_pri else pred_pri,
        "Location / Ward No": data.get('Location / Ward No', 'Not Specified'),
        "Department": data.get('Department', 'General'),
        "Status": "New",
        "Date Submitted": datetime.now().strftime("%Y-%m-%d"),
        "Predicted Category": pred_cat,
        "Predicted Priority": pred_pri,
        "Confidence Score": confidence,
        "Attachment Name": data.get('Attachment Name', 'None'),
        "Internal Notes": data.get('Internal Notes', '')
    }

    # Save to CSV
    df = load_processed_data()
    if df.empty:
        df = pd.DataFrame([new_entry])
    else:
        df = pd.concat([pd.DataFrame([new_entry]), df], ignore_index=True)

    save_processed_data(df)

    return jsonify(new_entry)

@app.route('/api/update_status', methods=['POST'])
def update_status():
    data = request.json
    if not data or 'id' not in data or 'status' not in data:
        return jsonify({"status": "error", "message": "id and status are required"}), 400

    df = load_processed_data()
    if df.empty:
        return jsonify({"status": "error", "message": "No data found"}), 404

    mask = df['id'] == data['id']
    if not mask.any():
        return jsonify({"status": "error", "message": "Grievance not found"}), 404

    df.loc[mask, 'Status'] = data['status']
    save_processed_data(df)
    return jsonify({"status": "success", "message": f"Status updated to {data['status']}"})

@app.route('/api/get_categories')
def get_categories():
    df = load_processed_data()
    if df.empty or 'Category' not in df.columns:
        return jsonify([])
    cats = sorted(df['Category'].dropna().unique().tolist())
    return jsonify(cats)

@app.route('/api/export_csv')
def export_csv():
    df = load_processed_data()
    if df.empty:
        return jsonify({"status": "error", "message": "No data to export"}), 404

    # Optional filter by category
    category = request.args.get('category', '').strip()
    if category and category.lower() != 'all':
        df = df[df['Category'].str.lower() == category.lower()]
        if df.empty:
            return jsonify({"status": "error", "message": f"No records for category: {category}"}), 404

    # Optional filter by status
    status_filter = request.args.get('status', '').strip()
    if status_filter and status_filter.lower() != 'all':
        df = df[df['Status'].str.lower() == status_filter.lower()]

    filename_cat = f"_{category}" if category and category.lower() != 'all' else ""
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={
            "Content-Disposition": f"attachment;filename=grievances{filename_cat}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        }
    )

@app.route('/api/delete_grievance', methods=['POST'])
def delete_grievance():
    data = request.json
    if not data or 'id' not in data:
        return jsonify({"status": "error", "message": "id is required"}), 400

    df = load_processed_data()
    if df.empty:
        return jsonify({"status": "error", "message": "No data found"}), 404

    original_len = len(df)
    df = df[df['id'] != data['id']]
    if len(df) == original_len:
        return jsonify({"status": "error", "message": "Grievance not found"}), 404

    save_processed_data(df)
    return jsonify({"status": "success", "message": "Grievance deleted"})

if __name__ == '__main__':
    ensure_nltk_data()
    merge_synthetic_data()
    app.run(debug=True, port=5000)
