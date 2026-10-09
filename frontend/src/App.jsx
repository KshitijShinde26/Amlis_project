import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';
import UploadData from './pages/UploadData';
import AttendanceRecords from './pages/AttendanceRecords';
import AnomalyDetection from './pages/AnomalyDetection';
import Students from './pages/Students';
import StudentDetails from './pages/StudentDetails';
import Subjects from './pages/Subjects';
import Reports from './pages/Reports';
import ModelAnalytics from './pages/ModelAnalytics';

function App() {
  return (
    <Router>
      <div className="app-container">
        <Sidebar />
        <div className="main-wrapper">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/upload" element={<UploadData />} />
            <Route path="/records" element={<AttendanceRecords />} />
            <Route path="/anomaly-detection" element={<AnomalyDetection />} />
            <Route path="/students" element={<Students />} />
            <Route path="/students/:studentId" element={<StudentDetails />} />
            <Route path="/subjects" element={<Subjects />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/model-analytics" element={<ModelAnalytics />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;
