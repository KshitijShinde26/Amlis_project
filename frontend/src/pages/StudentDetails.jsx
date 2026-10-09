import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getStudentDetails, getStudentAttendance } from '../services/api';
import { ArrowLeft, User, BookOpen, AlertTriangle, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

const StudentDetails = () => {
  const { studentId } = useParams();
  const navigate = useNavigate();

  const [student, setStudent] = useState(null);
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [stuRes, attRes] = await Promise.all([
        getStudentDetails(studentId),
        getStudentAttendance(studentId)
      ]);
      setStudent(stuRes.data);
      setHistory(attRes.data);
    } catch (err) {
      console.error("Error fetching student profile:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [studentId]);

  if (loading) {
    return (
      <div>
        <Navbar title={`Student Profile - ${studentId}`} />
        <div className="content-area" style={{ textAlign: 'center', paddingTop: '4rem' }}>
          <p>Loading student profile data...</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <Navbar title={`Student Profile: ${student?.name} (${studentId})`} />
      <div className="content-area">
        
        <button 
          onClick={() => navigate('/students')} 
          className="btn btn-secondary" 
          style={{ marginBottom: '1.25rem', display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
        >
          <ArrowLeft size={16} /> Back to Students List
        </button>

        {/* Student Profile Card */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem' }}>
            <div>
              <h3 style={{ fontSize: '1.4rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
                <User size={24} color="#4f46e5" /> {student?.name}
              </h3>
              <p style={{ color: '#64748b', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                Student ID: <strong>{student?.student_id}</strong> | Dept: {student?.department} | Semester: {student?.semester}
              </p>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ background: '#f1f5f9', padding: '0.75rem 1.25rem', borderRadius: 10, textAlign: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase' }}>Overall Attendance</span>
                <p style={{ fontSize: '1.35rem', fontWeight: 700, color: student?.attendance_percentage < 75 ? '#dc2626' : '#059669' }}>
                  {student?.attendance_percentage}%
                </p>
              </div>
              <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '0.75rem 1.25rem', borderRadius: 10, textAlign: 'center' }}>
                <span style={{ fontSize: '0.75rem', color: '#991b1b', textTransform: 'uppercase' }}>Flagged Anomalies</span>
                <p style={{ fontSize: '1.35rem', fontWeight: 700, color: '#dc2626' }}>
                  {student?.anomalies_count}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Subject Breakdown Chart */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Subject-wise Attendance Rates</h4>
          <div style={{ width: '100%', height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={student?.subject_breakdown || []}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                <XAxis dataKey="subject_code" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Bar dataKey="percentage" fill="#4f46e5" radius={[6, 6, 0, 0]} name="Subject Attendance %" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Attendance & Anomaly History */}
        <div className="card">
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Attendance History & Anomaly Evaluations</h4>
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Subject</th>
                  <th>Status</th>
                  <th>Anomaly Score</th>
                  <th>Evaluation Status</th>
                </tr>
              </thead>
              <tbody>
                {history.length > 0 ? (
                  history.map((rec) => (
                    <tr key={rec.id}>
                      <td>{rec.date}</td>
                      <td>{rec.time}</td>
                      <td>{rec.subject_code} - {rec.subject_name}</td>
                      <td>
                        <span className={`badge ${rec.status === 'Present' ? 'badge-normal' : 'badge-highly-suspicious'}`}>
                          {rec.status}
                        </span>
                      </td>
                      <td><strong>{rec.anomaly_score}</strong></td>
                      <td>
                        <span className={`badge ${
                          rec.anomaly_status === 'Highly Suspicious' 
                            ? 'badge-highly-suspicious' 
                            : (rec.anomaly_status === 'Suspicious' ? 'badge-suspicious' : 'badge-normal')
                        }`}>
                          {rec.anomaly_status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '1.5rem', color: '#64748b' }}>
                      No history found for student.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default StudentDetails;
