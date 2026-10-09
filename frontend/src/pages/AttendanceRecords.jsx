import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import { getAttendanceRecords, getSubjects } from '../services/api';
import { Search, Filter, RefreshCw } from 'lucide-react';

const AttendanceRecords = () => {
  const [records, setRecords] = useState([]);
  const [total, setTotal] = useState(0);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');

  const fetchRecords = async () => {
    setLoading(true);
    try {
      const [recRes, subRes] = await Promise.all([
        getAttendanceRecords(0, 300),
        getSubjects()
      ]);
      setRecords(recRes.data.records);
      setTotal(recRes.data.total);
      setSubjects(subRes.data);
    } catch (err) {
      console.error("Error fetching attendance records:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecords();
  }, []);

  const filteredRecords = records.filter(r => {
    const matchesSearch = r.student_id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSubject = selectedSubject ? r.subject_code === selectedSubject : true;
    return matchesSearch && matchesSubject;
  });

  return (
    <div>
      <Navbar title="Attendance Records Log" onRefresh={fetchRecords} />
      <div className="content-area">
        
        {/* Controls Card */}
        <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.5rem' }}>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', gap: '1rem', flex: 1, minWidth: 280 }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: '#94a3b8' }} />
                <input 
                  type="text"
                  placeholder="Search by Student ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{
                    width: '100%',
                    padding: '0.6rem 0.6rem 0.6rem 2.2rem',
                    borderRadius: 8,
                    border: '1px solid #cbd5e1',
                    fontSize: '0.875rem'
                  }}
                />
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Filter size={16} color="#64748b" />
                <select 
                  value={selectedSubject}
                  onChange={(e) => setSelectedSubject(e.target.value)}
                  style={{
                    padding: '0.6rem 1rem',
                    borderRadius: 8,
                    border: '1px solid #cbd5e1',
                    fontSize: '0.875rem',
                    backgroundColor: 'white'
                  }}
                >
                  <option value="">All Subjects</option>
                  {subjects.map(s => (
                    <option key={s.subject_code} value={s.subject_code}>
                      {s.subject_code} - {s.subject_name}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div style={{ fontSize: '0.875rem', color: '#64748b' }}>
              Showing {filteredRecords.length} of {total} records
            </div>
          </div>
        </div>

        {/* Table Card */}
        <div className="card">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Record ID</th>
                  <th>Student ID</th>
                  <th>Subject Code</th>
                  <th>Date</th>
                  <th>Time</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2rem' }}>
                      Loading attendance records...
                    </td>
                  </tr>
                ) : filteredRecords.length > 0 ? (
                  filteredRecords.map((r) => (
                    <tr key={r.id}>
                      <td>#{r.id}</td>
                      <td><strong>{r.student_id}</strong></td>
                      <td>{r.subject_code}</td>
                      <td>{r.attendance_date}</td>
                      <td>{r.attendance_time}</td>
                      <td>
                        <span className={`badge ${r.status === 'Present' ? 'badge-normal' : 'badge-highly-suspicious'}`}>
                          {r.status}
                        </span>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="6" style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                      No attendance records found matching filters.
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

export default AttendanceRecords;
