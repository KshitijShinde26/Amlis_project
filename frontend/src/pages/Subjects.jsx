import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { getSubjects } from '../services/api';
import { BookOpen, AlertTriangle } from 'lucide-react';

const Subjects = () => {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSubjectsList = async () => {
    setLoading(true);
    try {
      const res = await getSubjects();
      setSubjects(res.data);
    } catch (err) {
      console.error("Error fetching subjects:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSubjectsList();
  }, []);

  return (
    <div>
      <Navbar title="Subject Analytics & Attendance Overview" onRefresh={fetchSubjectsList} />
      <div className="content-area">
        
        <div className="grid-2" style={{ marginBottom: '2rem' }}>
          {loading ? (
            <p>Loading subjects...</p>
          ) : subjects.map((sub) => (
            <div key={sub.subject_code} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                <div>
                  <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#4f46e5', textTransform: 'uppercase' }}>
                    {sub.subject_code}
                  </span>
                  <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#1e293b' }}>{sub.subject_name}</h3>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Dept: {sub.department} | Sem {sub.semester}</p>
                </div>
                <div className="stat-icon-wrapper" style={{ backgroundColor: '#6366f1', width: 40, height: 40 }}>
                  <BookOpen size={20} />
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '0.75rem', background: '#f8fafc', padding: '0.85rem', borderRadius: 8, fontSize: '0.85rem' }}>
                <div>
                  <span style={{ color: '#64748b', fontSize: '0.75rem' }}>Class Average</span>
                  <p style={{ fontWeight: 700, fontSize: '1.1rem', color: sub.attendance_percentage < 75 ? '#dc2626' : '#059669' }}>
                    {sub.attendance_percentage}%
                  </p>
                </div>
                <div>
                  <span style={{ color: '#64748b', fontSize: '0.75rem' }}>Total Lectures</span>
                  <p style={{ fontWeight: 700, fontSize: '1.1rem', color: '#334155' }}>
                    {sub.total_records}
                  </p>
                </div>
                <div>
                  <span style={{ color: '#64748b', fontSize: '0.75rem' }}>Anomalies</span>
                  <p style={{ fontWeight: 700, fontSize: '1.1rem', color: sub.anomalies_count > 0 ? '#dc2626' : '#059669' }}>
                    {sub.anomalies_count}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>

      </div>
    </div>
  );
};

export default Subjects;
