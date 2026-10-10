# Smart Attendance Anomaly Detection Using Machine Learning

## 1. Project Title and Overview
**Amlis_project: Smart Attendance Anomaly Detection Using Machine Learning** is an academic project designed to identify suspicious patterns in student attendance data. By utilizing unsupervised machine learning algorithms, the system highlights unusual attendance behavior that may indicate proxy attendance, erratic absenteeism, or anomalous schedule deviations. It provides a full-stack web application for uploading datasets, executing the detection pipeline, and visualizing the anomalies.

## 2. Problem Statement
Traditional attendance systems rely heavily on manual verification, which is prone to errors and proxy attendance. When attendance is recorded automatically or in bulk, detecting fraudulent or highly irregular patterns becomes challenging. This project addresses the need for an automated, intelligent layer that analyzes historical attendance records to flag statistically significant deviations for further review.

## 3. Objectives and Major Features
*   **Automated Data Ingestion:** Upload CSV datasets to automatically populate the database.
*   **Feature Engineering:** Transform raw attendance logs into meaningful behavioral metrics (e.g., consecutive absences, time conflicts, peer deviations).
*   **Unsupervised Anomaly Detection:** Identify outliers without requiring a pre-labeled "cheating" dataset.
*   **Comparative ML Modeling:** Run both Isolation Forest (Primary) and Local Outlier Factor (Secondary) to evaluate agreement.
*   **Interactive Dashboard:** A React-based UI to view metrics, filter anomalies by severity, and inspect the specific reasons for flagged records.

## 4. Actual Technology Stack
*   **Backend:** Python 3, FastAPI, SQLAlchemy, Uvicorn
*   **Machine Learning:** scikit-learn, pandas, NumPy
*   **Database:** SQLite (Default, configured via SQLAlchemy)
*   **Frontend:** JavaScript, React 19, Vite, Axios, Recharts, Lucide React

## 5. Architecture and Directory Structure
The repository is split into a separated backend and frontend architecture:
```
Amlis_project/
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers (attendance, anomaly, dashboard)
│   │   ├── database/       # DB session management and initialization
│   │   ├── ml/             # ML pipeline, feature engineering, IF, and LOF models
│   │   ├── models/         # SQLAlchemy ORM models (Student, Subject, Attendance, Anomaly)
│   │   ├── schemas/        # Pydantic schemas for request/response validation
│   │   ├── services/       # Core business logic bridging API and ML models
│   │   └── main.py         # FastAPI application entry point
│   ├── requirements.txt    # Python dependencies
│   └── smart_attendance.db # SQLite database (created on startup)
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components (Sidebar, Navbar, Modals)
│   │   ├── pages/          # Core views (Dashboard, AnomalyDetection, UploadData)
│   │   └── services/       # Axios API client setup (api.js)
│   ├── package.json        # Node.js dependencies and scripts
│   └── vite.config.js      # Vite build configuration
└── dataset/
    └── sample_attendance.csv # Template and sample dataset
```

## 6. How the Anomaly Detection Pipeline Works
1.  **Data Extraction:** Raw attendance records are fetched from the SQLite database.
2.  **Preprocessing & Feature Engineering:** The pipeline calculates 13 distinct numerical features from the raw temporal data.
3.  **Model Execution:** The feature matrix is scaled and passed to both the Isolation Forest and LOF models.
4.  **Scoring & Classification:** The models output a continuous anomaly score, normalized between 0.0 and 1.0. Scores above a specific threshold are categorized as "Suspicious" or "Highly Suspicious".
5.  **Explainability:** Human-readable reasons are generated based on which feature thresholds the anomalous record exceeded.
6.  **Storage:** Results are purged and re-inserted into the `anomaly_results` table for UI consumption.

## 7. Isolation Forest and Local Outlier Factor Implementations
*   **Isolation Forest (Primary):** Implemented via `sklearn.ensemble.IsolationForest`. It isolates anomalies by randomly selecting a feature and a split value. Outliers require fewer splits to be isolated, resulting in a shorter path length in the tree.
*   **Local Outlier Factor (LOF):** Implemented via `sklearn.neighbors.LocalOutlierFactor`. It compares the local density of a record against its neighbors. A substantially lower density indicates an outlier. 

## 8. Input Dataset Format and Required Columns
The system accepts CSV and Excel formats. A sample is provided in `dataset/sample_attendance.csv`. The required columns are:
*   `student_id` (String)
*   `student_name` (String)
*   `date` (YYYY-MM-DD)
*   `time` (HH:MM)
*   `subject_code` (String)
*   `subject_name` (String)
*   `status` ('Present' or 'Absent')

## 9. Data Preprocessing and Feature Engineering
The `feature_engineering.py` module generates 13 numerical features without modifying the raw data. Key features include:
*   **Overall/Subject Percentages:** Student's attendance rates compared to class averages.
*   **Deviations:** Discrepancies between a student's normal behavior and specific subject behavior.
*   **Streaks:** Rolling counts of consecutive absences or presences.
*   **Time Conflicts:** Flags multiple 'Present' statuses for the exact same date and time (indicative of proxy attendance).
*   **Unusual Hours:** Flags attendance logged outside standard operating hours (8 AM - 6 PM).

## 10. Backend Installation and Startup
1.  Navigate to the backend directory:
    ```bash
    cd backend
    ```
2.  Create and activate a virtual environment (optional but recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
4.  Start the FastAPI server:
    ```bash
    uvicorn app.main:app --reload
    ```
    The backend runs on `http://localhost:8000`.

## 11. Frontend Installation and Startup
1.  Navigate to the frontend directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    The frontend runs typically on `http://localhost:5173`.

## 12. Environment Variables and Configuration
*   **Backend:** Configuration is handled in `backend/app/config.py`. 
    *   `DATABASE_URL`: Defaults to `sqlite:///./smart_attendance.db`.
    *   `SECRET_KEY`: Can be overridden via environment variables.
*   **Frontend:** The API base URL is statically configured in `frontend/src/services/api.js` as `http://localhost:8000/api`.

## 13. Database Initialization and Persistence
Upon starting the FastAPI backend, the `init_db()` function is triggered during the `@app.on_event("startup")` hook. This automatically creates the SQLite file (`smart_attendance.db`) and generates all required tables (`students`, `subjects`, `attendance_records`, `anomaly_results`) if they do not already exist.

## 14. API Endpoints and Example Requests
The backend exposes several REST API endpoints prefixed with `/api`.
*   **`GET /api/health`**: Check system health.
*   **`POST /api/attendance/upload`**: Upload a multipart/form-data CSV.
*   **`GET /api/attendance`**: Retrieve paginated attendance logs.
*   **`POST /api/anomaly/detect`**: Trigger the ML pipeline.
    *   Body: `{"contamination": 0.10, "method": "Isolation Forest"}`
*   **`GET /api/anomalies`**: Retrieve detected anomalies (supports query filters like `?anomaly_only=true`).

## 15. How to Upload or Process an Attendance Dataset
1.  Open the frontend application in your browser.
2.  Navigate to the **Upload Data** tab via the sidebar.
3.  Select a valid CSV file (e.g., `dataset/sample_attendance.csv`).
4.  Click Upload. The backend will parse the file, validate columns, and populate the database.

## 16. How to Interpret Anomaly Detection Results
After running the detection pipeline, navigate to the **Anomaly Detection** page.
*   **Normal:** Follows standard attendance patterns.
*   **Suspicious (Score >= 0.65):** Exhibits mild deviations (e.g., unusual absence streaks).
*   **Highly Suspicious (Score >= 0.78):** Exhibits severe deviations. Clicking **View Reasons** will reveal why it was flagged (e.g., simultaneous presence in two classes indicating possible proxy, or drastic deviation from class averages).
*   *Note:* The system flags statistical anomalies; it does not explicitly prove cheating or proxy attendance without human verification.

## 17. How to Run Existing Tests
Currently, there are no automated tests implemented in this project (0% test coverage). Developing a test suite using `pytest` for the backend and `vitest` for the frontend is prioritized on the roadmap.

## 18. Troubleshooting Common Startup and API Errors
*   **`CORS Error` on frontend:** Ensure the backend is running on `http://localhost:8000`, as the frontend relies on this exact address.
*   **`sqlite3.OperationalError`:** The database file might be locked or corrupted. Delete `backend/smart_attendance.db` and restart the backend to recreate it.
*   **Missing packages:** Ensure you have installed packages from `backend/requirements.txt` using the correct Python interpreter.

## 19. Limitations and Future Improvements
### Implemented Capabilities
*   End-to-end data ingestion and UI dashboarding.
*   Functional, deterministic feature extraction.
*   Fully integrated ML pipeline (IF + LOF) executing directly against the database.
### Known Limitations
*   **No Automated Testing:** Lacks unit and integration tests.
*   **Unsupervised Limitations:** Without labeled cheating data, evaluation metrics rely solely on mathematical outlier detection rather than precision/recall against actual fraud.
*   **Scalability:** SQLite is used currently, which may lock under heavy concurrent writes. 
### Future Improvements
*   Implement `pytest` and CI/CD pipelines.
*   Migrate to PostgreSQL for production scalability.
*   Add supervised learning layers if labeled data becomes available.

## 20. Contributors and Academic Project Context
**Subject:** Applied Machine Learning for Industry Solutions (AMLIS)
**Contributors:** Kshitij Shinde, Swarup
**Status:** Under Active Development (Feature Completion Branch)
