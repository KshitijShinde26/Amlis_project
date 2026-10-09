import os
import random
import datetime
import pandas as pd

FIRST_NAMES = ["Rahul", "Amit", "Neha", "Priya", "Rohan", "Sneha", "Vikas", "Ananya", "Karan", "Pooja",
               "Siddharth", "Divya", "Aditya", "Riya", "Yash", "Tanvi", "Akash", "Shreya", "Manish", "Kavya",
               "Gaurav", "Nisha", "Deepak", "Aarti", "Suresh", "Megha", "Vikram", "Swati", "Nikhil", "Simran"]

LAST_NAMES = ["Sharma", "Verma", "Patel", "Gupta", "Singh", "Kumar", "Joshi", "Deshmukh", "Shah", "Mehta",
              "Rao", "Nair", "Kulkarni", "Reddy", "Chaudhary", "Mishra", "Pandey", "Bhat", "Agarwal", "Shetty"]

SUBJECTS = [
    {"code": "IT601", "name": "Applied Machine Learning"},
    {"code": "IT602", "name": "Web Technologies & Frameworks"},
    {"code": "IT603", "name": "Database Management Systems"},
    {"code": "IT604", "name": "Software Architecture & Engineering"},
    {"code": "IT605", "name": "Computer Networks & Security"},
]

LECTURE_TIMES = ["09:00", "10:15", "11:30", "14:00", "15:15"]

def generate_sample_dataset(num_students=50, days=25, anomaly_rate=0.08, output_path="dataset/sample_attendance.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    random.seed(42)
    
    # 1. Generate Students
    students = []
    for i in range(1, num_students + 1):
        s_id = f"STU{i:03d}"
        s_name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        # Random baseline attendance propensity for student (between 0.65 and 0.95)
        base_rate = round(random.uniform(0.65, 0.95), 2)
        students.append({"student_id": s_id, "student_name": s_name, "base_rate": base_rate})

    start_date = datetime.date(2026, 8, 1)
    dates = []
    curr = start_date
    while len(dates) < days:
        if curr.weekday() < 5: # Monday to Friday
            dates.append(curr)
        curr += datetime.timedelta(days=1)

    records = []

    # Normal attendance records generation
    for date_obj in dates:
        date_str = date_obj.strftime("%Y-%m-%d")
        for subj in SUBJECTS:
            # 2 to 3 lectures per day
            time_str = LECTURE_TIMES[(date_obj.day + SUBJECTS.index(subj)) % len(LECTURE_TIMES)]
            
            for s in students:
                # Normal attendance determination
                is_present = random.random() < s['base_rate']
                status = "Present" if is_present else "Absent"
                
                records.append({
                    "student_id": s['student_id'],
                    "student_name": s['student_name'],
                    "date": date_str,
                    "time": time_str,
                    "subject_code": subj['code'],
                    "subject_name": subj['name'],
                    "status": status
                })

    df = pd.DataFrame(records)

    # 2. Inject Controlled Synthetic Anomalies for Testing & Validation
    num_anomalies = int(len(df) * anomaly_rate)
    anomaly_indices = random.sample(range(len(df)), num_anomalies)

    for idx in anomaly_indices:
        anomaly_type = random.choice([
            "proxy_conflict",
            "unusual_hour",
            "sudden_absent_streak",
            "extreme_subject_bias"
        ])

        if anomaly_type == "proxy_conflict":
            # Student is marked Present at an impossible date & time in 2 subjects
            original_row = df.iloc[idx]
            other_subj = random.choice([s for s in SUBJECTS if s['code'] != original_row['subject_code']])
            # Create duplicate present entry at exact same date & time for different subject
            df.loc[idx, 'status'] = 'Present'
            df.loc[idx, 'subject_code'] = other_subj['code']
            df.loc[idx, 'subject_name'] = other_subj['name']

        elif anomaly_type == "unusual_hour":
            # Attendance logged at 02:45 AM or 23:30 PM
            df.loc[idx, 'time'] = random.choice(["02:45", "03:15", "23:30", "01:20"])
            df.loc[idx, 'status'] = 'Present'

        elif anomaly_type == "sudden_absent_streak":
            # Mark consecutive rows for this student as Absent
            target_student = df.loc[idx, 'student_id']
            stu_indices = df[df['student_id'] == target_student].index.tolist()
            if len(stu_indices) > 5:
                pos = stu_indices.index(idx) if idx in stu_indices else 0
                for offset in range(0, min(5, len(stu_indices) - pos)):
                    df.loc[stu_indices[pos + offset], 'status'] = 'Absent'

        elif anomaly_type == "extreme_subject_bias":
            # Student absent in specific subject repeatedly
            target_student = df.loc[idx, 'student_id']
            target_subj = df.loc[idx, 'subject_code']
            bias_indices = df[(df['student_id'] == target_student) & (df['subject_code'] == target_subj)].index
            for b_idx in bias_indices:
                df.loc[b_idx, 'status'] = 'Absent'

    df.to_csv(output_path, index=False)
    print(f"Generated sample dataset with {len(df)} records at {output_path}")
    return df

if __name__ == "__main__":
    generate_sample_dataset(num_students=40, days=20, output_path="dataset/sample_attendance.csv")
