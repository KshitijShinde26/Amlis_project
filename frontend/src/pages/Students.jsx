import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getStudents } from '../services/api';
import { Search, UserCheck, ArrowRight } from 'lucide-react';

const Students = () => {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const fetchStudentsList = async () => {
    setLoading(true);
    try {
      const res = await getStudents();
      setStudents(res.data);
    } catch (err) {
      console.error("Error fetching students list:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStudentsList();
  }, []);

  const filteredStudents = students.filter(s => 
    s.student_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
    s.name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      <Navbar title="Students Directory & Behavioral Risk Profiles" onRefresh={fetchStudentsList} />
      <div className="content-area">
        
        {/* Search Bar */}
        <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.5rem' }}>
          <div style={{ position: 'relative', maxWidth: 400 }}>
            <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: '#94a3b8' }} />
            <input 
              type="text"
              placeholder="Search student by Name or ID..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ width: '100%', padding: '0.6rem 0.6rem 0.6rem 2.2rem', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: '0.875rem' }}
            />
          </div>
        </div>

        {/* Table */}
        <div className="card">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Student Name</th>
                  <th>Department</th>
                  <th>Attendance %</th>
                  <th>Total Classes</th>
                  <th>Flagged Anomalies</th>
                  <th>Behavioral Risk Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>
                      Loading students list...
                    </td>
                  </tr>
                ) : filteredStudents.length > 0 ? (
                  filteredStudents.map((s) => (
                    <tr key={s.student_id}>
                      <td><strong>{s.student_id}</strong></td>
                      <td>{s.name}</td>
                      <td>{s.department}</td>
                      <td>
                        <strong style={{ color: s.attendance_percentage < 75 ? '#dc2626' : '#059669' }}>
                          {s.attendance_percentage}%
                        </strong>
                      </td>
                      <td>{s.total_records}</td>
                      <td>{s.anomalies_count}</td>
                      <td>
                        <span className={`badge ${
                          s.risk_status === 'High Risk' 
                            ? 'badge-highly-suspicious' 
                            : (s.risk_status === 'Medium Risk' ? 'badge-suspicious' : 'badge-normal')
                        }`}>
                          {s.risk_status}
                        </span>
                      </td>
                      <td>
                        <button 
                          onClick={() => navigate(`/students/${s.student_id}`)}
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                        >
                          Profile <ArrowRight size={14} />
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                      No students found.
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

export default Students;
