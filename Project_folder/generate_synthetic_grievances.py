import pandas as pd
import random
from datetime import datetime, timedelta

# Configuration
NUM_RECORDS = 1000
CATEGORIES = {
    "Water Supply": ["Municipal Corporation", "Public Works Department (PWD)"],
    "Electricity": ["Electricity Board", "Urban Development Authority"],
    "Roads & Infrastructure": ["Public Works Department (PWD)", "Urban Development Authority"],
    "Sanitation": ["Municipal Corporation", "Health & Family Welfare"],
    "Public Safety": ["Police Department", "Municipal Corporation"],
    "Healthcare": ["Health & Family Welfare", "Municipal Corporation"],
    "Education": ["Education Department", "Urban Development Authority"],
    "Waste Management": ["Municipal Corporation", "Sanitation Department"],
    "Drainage": ["Public Works Department (PWD)", "Municipal Corporation"],
    "Street Lighting": ["Electricity Board", "Municipal Corporation"]
}

LOCATIONS = [f"Ward {i}, Central Zone" for i in range(1, 11)] + \
            [f"Sector {i}, Heritage Colony" for i in range(10, 20)] + \
            [f"Garden City, Phase {i}" for i in range(1, 6)]

PRIORITIES = ["Low", "Medium", "High", "Urgent"]
STATUSES = ["New", "In Progress", "Resolved", "Escalated"]

# Templates for generating unique descriptions
TEMPLATES = {
    "Water Supply": [
        "Continuous leakage in the main pipeline near {location}.",
        "No water supply for the last {days} days in {location}.",
        "Low pressure water being received at {location}.",
        "Contaminated water with foul smell reported at {location}."
    ],
    "Electricity": [
        "Frequent power cuts without notice in {location}.",
        "High voltage fluctuations causing damage to appliances in {location}.",
        "Street pole spark observed near {location}.",
        "Electricity bill incorrectly calculated for {location}."
    ],
    "Roads & Infrastructure": [
        "Major potholes on the main road of {location}.",
        "Street pavement broken near {location}.",
        "Illegal speed breaker installed at {location}.",
        "Road construction halted for {days} months in {location}."
    ],
    "Sanitation": [
        "Public toilets in {location} are extremely dirty and unusable.",
        "Sewage overflow reported in the back alley of {location}.",
        "Illegal dumping of construction waste in {location}.",
        "Drainage blockage causing water logging in {location}."
    ],
    "Public Safety": [
        "Increase in petty thefts reported in {location} after 9 PM.",
        "Illegal parking blocking emergency exits in {location}.",
        "Stray animal menace in the parks of {location}.",
        "Lack of police patrolling observed during night in {location}."
    ],
    "Healthcare": [
        "Government clinic in {location} lacks basic medicines.",
        "Long waiting hours and no doctors available in {location} PHC.",
        "Unsanitary conditions in the ward area of {location} hospital.",
        "Emergency ambulance delayed by {days} hours for {location}."
    ],
    "Education": [
        "School building in {location} needs urgent structural repairs.",
        "Lack of pure drinking water facilities in {location} primary school.",
        "Shortage of teaching staff for {days} semesters in {location}.",
        "Illegal encroachments near the playground of {location} school."
    ],
    "Waste Management": [
        "Garbage collection truck hasn't visited {location} for a week.",
        "Open garbage bin overflowing and spreading disease in {location}.",
        "Illegal burning of waste in the open area of {location}.",
        "Biomedical waste found dumped in the residential area of {location}."
    ],
    "Drainage": [
        "Main drain choked with plastic waste near {location}.",
        "Stinking smell from the open drain in {location}.",
        "Drain cover missing, posing a risk to children in {location}.",
        "Monsoon preparation for cleaning drains not started in {location}."
    ],
    "Street Lighting": [
        "Street lights not working for {days} nights in {location}.",
        "Flickering street light causing disturbance in {location}.",
        "New street light poles installed but not connected in {location}.",
        "Dark spots on the road due to non-functional lights in {location}."
    ]
}

def generate_data():
    records = []
    seen_titles = set()
    
    while len(records) < NUM_RECORDS:
        category = random.choice(list(CATEGORIES.keys()))
        dept = random.choice(CATEGORIES[category])
        location = random.choice(LOCATIONS)
        days = random.randint(2, 60)
        
        template = random.choice(TEMPLATES[category])
        description = template.format(location=location, days=days)
        
        title = f"{category} Issue at {location} - {random.randint(100, 999)}"
        if title in seen_titles:
            continue
        seen_titles.add(title)
        
        summary = f"Complaint regarding {category.lower()} in {location}."
        priority = random.choice(PRIORITIES)
        status = random.choice(STATUSES)
        date_submitted = (datetime.now() - timedelta(days=random.randint(0, 365))).strftime("%Y-%m-%d")
        
        records.append({
            "Grievance Title": title,
            "Brief Summary": summary,
            "Category": category,
            "Department": dept,
            "Detailed Description": description,
            "Location / Ward No": location,
            "Priority Level": priority,
            "Attachment Name": f"evidence_{len(records)}.jpg" if random.random() > 0.7 else "None",
            "Internal Notes": f"Assigned to {dept} team.",
            "Date Submitted": date_submitted,
            "Status": status
        })
        
    df = pd.DataFrame(records)
    df.to_csv("synthetic_grievances.csv", index=False)
    print(f"Generated {NUM_RECORDS} records into synthetic_grievances.csv")

if __name__ == "__main__":
    generate_data()
