import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { getDashboardStats, triggerAnomalyDetection } from '../services/api';
import { Users, BookOpen, AlertTriangle, CheckCircle, ArrowUpRight, Play, ShieldAlert } from 'lucide-react';
import { 
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, 
  PieChart, Pie, Cell, AreaChart, Area, CartesianGrid, Legend 
} from 'recharts';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [runningMl, setRunningMl] = useState(false);
  const navigate = useNavigate();

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await getDashboardStats();
      setStats(res.data);
    } catch (err) {
      console.error("Error fetching dashboard statistics:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleRunPipeline = async () => {
    setRunningMl(true);
    try {
      await triggerAnomalyDetection();
      await fetchStats();
    } catch (err) {
      console.error("Error running ML pipeline:", err);
    } finally {
      setRunningMl(false);
    }
  };

  if (loading) {
    return (
      <div>
        <Navbar title="Dashboard Overview" />
        <div className="content-area" style={{ textAlign: 'center', paddingTop: '4rem' }}>
          <p style={{ color: '#64748b' }}>Loading Smart Attendance Analytics...</p>
        </div>
      </div>
    );
  }

  const pieData = [
    { name: 'Normal Records', value: stats?.normal_records || 0, color: '#10b981' },
    { name: 'Anomalous Records', value: stats?.anomalous_records || 0, color: '#ef4444' }
  ];

  return (
    <div>
      <Navbar title="Smart Attendance Dashboard" onRefresh={fetchStats} />
      <div className="content-area">
        
        {/* Banner Action */}
        <div style={{
          background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)',
          borderRadius: 14,
          padding: '1.5rem 2rem',
          color: 'white',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          marginBottom: '1.5rem',
          boxShadow: '0 10px 20px rgba(49, 46, 129, 0.25)'
        }}>
          <div>
            <h3 style={{ fontSize: '1.35rem', fontWeight: 700 }}>Machine Learning Anomaly Detection System</h3>
            <p style={{ color: '#c7d2fe', fontSize: '0.9rem', marginTop: '0.25rem' }}>
              Automated behavioral evaluation of student attendance using Isolation Forest & LOF algorithm models.
            </p>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button 
              onClick={handleRunPipeline} 
              disabled={runningMl}
              className="btn btn-primary"
              style={{ background: '#6366f1', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
            >
              <Play size={16} /> {runningMl ? "Running ML Pipeline..." : "Execute ML Detection"}
            </button>
            <button 
              onClick={() => navigate('/upload')}
              className="btn btn-secondary"
            >
              Upload Dataset
            </button>
          </div>
        </div>

        {/* Stale Detection Notice */}
        {stats?.is_stale && (
          <div style={{
            backgroundColor: '#fffbeb',
            border: '1px solid #fef3c7',
            borderRadius: 10,
            padding: '1rem 1.5rem',
            marginBottom: '1.5rem',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            color: '#92400e'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
              <AlertTriangle size={22} color="#d97706" />
              <div>
                <strong style={{ fontSize: '0.95rem' }}>New Attendance Records Uploaded</strong>
                <p style={{ margin: 0, fontSize: '0.85rem', color: '#b45309' }}>
                  There are {stats.total_records} total records but only {stats.analyzed_records || 0} evaluated in the latest ML run. Anomaly metrics are currently stale.
                </p>
              </div>
            </div>
            <button 
              onClick={handleRunPipeline} 
              disabled={runningMl}
              className="btn btn-primary"
              style={{ fontSize: '0.8rem', padding: '0.4rem 0.85rem', backgroundColor: '#d97706', borderColor: '#d97706' }}
            >
              {runningMl ? "Refreshing..." : "Re-run Detection"}
            </button>
          </div>
        )}

        {/* KPI Grid */}
        <div className="grid-4">
          <div className="card stat-card">
            <div className="stat-info">
              <h3>Total Students</h3>
              <p>{stats?.total_students || 0}</p>
            </div>
            <div className="stat-icon-wrapper" style={{ backgroundColor: '#4f46e5' }}>
              <Users size={22} />
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-info">
              <h3>Attendance Records</h3>
              <p>{stats?.total_records || 0}</p>
            </div>
            <div className="stat-icon-wrapper" style={{ backgroundColor: '#0284c7' }}>
              <BookOpen size={22} />
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-info">
              <h3>Normal Records</h3>
              <p>{stats?.normal_records || 0}</p>
            </div>
            <div className="stat-icon-wrapper" style={{ backgroundColor: '#10b981' }}>
              <CheckCircle size={22} />
            </div>
          </div>

          <div className="card stat-card">
            <div className="stat-info">
              <h3>Flagged Anomalies</h3>
              <p>{stats?.anomalous_records || 0} <span style={{ fontSize: '0.85rem', color: '#ef4444', fontWeight: 600 }}>({stats?.anomaly_percentage}%)</span></p>
            </div>
            <div className="stat-icon-wrapper" style={{ backgroundColor: '#ef4444' }}>
              <AlertTriangle size={22} />
            </div>
          </div>
        </div>

        {/* Charts Row */}
        <div className="grid-2">
          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Normal vs Anomalous Distribution</h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={90}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Subject-wise Attendance Rate (%)</h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={stats?.subject_wise_stats || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="subject_code" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="attendance_rate" fill="#6366f1" radius={[6, 6, 0, 0]} name="Attendance Rate %" />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Trend & Suspicious Table */}
        <div className="grid-2">
          <div className="card">
            <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '1rem' }}>Class Attendance Trend</h3>
            <div style={{ width: '100%', height: 260 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={stats?.attendance_trends || []}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Area type="monotone" dataKey="present" stroke="#10b981" fill="#d1fae5" name="Present Count" />
                  <Area type="monotone" dataKey="absent" stroke="#ef4444" fill="#fee2e2" name="Absent Count" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
              <h3 style={{ fontSize: '1rem', fontWeight: 700 }}>Top Flagged Suspicious Students</h3>
              <button onClick={() => navigate('/anomaly-detection')} className="btn btn-secondary" style={{ padding: '0.35rem 0.75rem', fontSize: '0.78rem' }}>
                View All Anomalies <ArrowUpRight size={14} />
              </button>
            </div>
            
            <div className="table-responsive">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Student ID</th>
                    <th>Name</th>
                    <th>Flagged Count</th>
                    <th>Avg Risk Score</th>
                  </tr>
                </thead>
                <tbody>
                  {stats?.top_suspicious_students && stats.top_suspicious_students.length > 0 ? (
                    stats.top_suspicious_students.map((student) => (
                      <tr key={student.student_id} style={{ cursor: 'pointer' }} onClick={() => navigate(`/students/${student.student_id}`)}>
                        <td><strong>{student.student_id}</strong></td>
                        <td>{student.student_name}</td>
                        <td>
                          <span className="badge badge-highly-suspicious">{student.anomaly_count} Anomalies</span>
                        </td>
                        <td><strong>{student.avg_anomaly_score}</strong></td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan="4" style={{ textAlign: 'center', color: '#64748b', padding: '1.5rem' }}>
                        No suspicious student patterns flagged yet. Run ML detection pipeline.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
