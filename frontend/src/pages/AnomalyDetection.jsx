import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import AnomalyDetailsModal from '../components/AnomalyDetailsModal';
import { getAnomalies, triggerAnomalyDetection, getSubjects } from '../services/api';
import { Play, ShieldAlert, Filter, Search, Eye, Sliders, Cpu, CheckCircle } from 'lucide-react';

const AnomalyDetection = () => {
  const [anomalies, setAnomalies] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [runningMl, setRunningMl] = useState(false);
  const [selectedAnomaly, setSelectedAnomaly] = useState(null);

  // Filters & ML Settings
  const [contamination, setContamination] = useState(0.10);
  const [method, setMethod] = useState("Isolation Forest");
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSubject, setSelectedSubject] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [anomalyOnly, setAnomalyOnly] = useState(true);
  const [metrics, setMetrics] = useState(null);

  const fetchAnomaliesData = async () => {
    setLoading(true);
    try {
      const [anomRes, subRes] = await Promise.all([
        getAnomalies({
          student_id: searchQuery,
          subject_code: selectedSubject,
          status_filter: statusFilter,
          anomaly_only: anomalyOnly
        }),
        getSubjects()
      ]);
      setAnomalies(anomRes.data.results);
      setSubjects(subRes.data);
    } catch (err) {
      console.error("Error fetching anomalies:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnomaliesData();
  }, [searchQuery, selectedSubject, statusFilter, anomalyOnly]);

  const handleExecutePipeline = async () => {
    setRunningMl(true);
    try {
      const res = await triggerAnomalyDetection({ contamination, method });
      setMetrics(res.data.summary_metrics);
      await fetchAnomaliesData();
    } catch (err) {
      console.error("Error executing anomaly pipeline:", err);
    } finally {
      setRunningMl(false);
    }
  };

  return (
    <div>
      <Navbar title="ML Anomaly Detection Workbench" onRefresh={fetchAnomaliesData} />
      <div className="content-area">
        
        {/* ML Execution Control Panel */}
        <div className="card" style={{ marginBottom: '2rem', background: 'linear-gradient(135deg, #ffffff 0%, #f8fafc 100%)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Cpu size={20} color="#4f46e5" /> ML Algorithm Execution Parameters
              </h3>
              <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                Adjust model sensitivity contamination parameter and run Isolation Forest + LOF feature evaluation.
              </p>
            </div>
            <button 
              onClick={handleExecutePipeline}
              disabled={runningMl}
              className="btn btn-primary"
              style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem' }}
            >
              <Play size={18} /> {runningMl ? "Training & Predicting..." : "Execute Anomaly Detection"}
            </button>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '1.5rem', paddingTop: '1rem', borderTop: '1px solid #e2e8f0' }}>
            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                Primary Algorithm Model:
              </label>
              <select 
                value={method} 
                onChange={(e) => setMethod(e.target.value)}
                style={{ width: '100%', padding: '0.6rem', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: '0.875rem' }}
              >
                <option value="Isolation Forest">Isolation Forest (Primary Ensemble Tree)</option>
                <option value="Local Outlier Factor">Local Outlier Factor (LOF Density Outlier)</option>
                <option value="Both Comparison">Ensemble Comparison (IF vs LOF)</option>
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.35rem' }}>
                <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155' }}>
                  Contamination Rate:
                </label>
                <span style={{ fontSize: '0.85rem', fontWeight: 700, color: '#4f46e5' }}>{(contamination * 100).toFixed(0)}%</span>
              </div>
              <input 
                type="range"
                min="0.02"
                max="0.25"
                step="0.01"
                value={contamination}
                onChange={(e) => setContamination(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: '#4f46e5' }}
              />
              <span style={{ fontSize: '0.75rem', color: '#64748b' }}>Expected anomaly proportion in population</span>
            </div>

            <div>
              <label style={{ fontSize: '0.85rem', fontWeight: 600, color: '#334155', display: 'block', marginBottom: '0.35rem' }}>
                Feature Space Pipeline:
              </label>
              <div style={{ fontSize: '0.8rem', color: '#475569', lineHeight: '1.4' }}>
                ✓ 13 Numerical Features (Status, Hours, Subject Deviation, Streak, Peer Outliers, Multi-Presence Conflict)
              </div>
            </div>
          </div>
        </div>

        {/* Model Metrics Summary if executed */}
        {metrics && (
          <div className="grid-2" style={{ marginBottom: '2rem' }}>
            <div className="card" style={{ borderLeft: '4px solid #4f46e5' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1e293b', marginBottom: '0.5rem' }}>Isolation Forest Metrics</h4>
              <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                Anomalies Flagged: <strong>{metrics.isolation_forest.anomalies_detected}</strong> ({metrics.isolation_forest.anomaly_percentage}%)
              </p>
              <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                Execution Time: <strong>{metrics.isolation_forest.execution_time_seconds}s</strong>
              </p>
            </div>

            <div className="card" style={{ borderLeft: '4px solid #0284c7' }}>
              <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#1e293b', marginBottom: '0.5rem' }}>Local Outlier Factor (LOF) Metrics</h4>
              <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                Anomalies Flagged: <strong>{metrics.local_outlier_factor.anomalies_detected}</strong> ({metrics.local_outlier_factor.anomaly_percentage}%)
              </p>
              <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
                Both Models Agreement: <strong>{metrics.model_agreement_count} records</strong>
              </p>
            </div>
          </div>
        )}

        {/* Filters Bar */}
        <div className="card" style={{ marginBottom: '1.5rem', padding: '1rem 1.5rem' }}>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', gap: '1rem', flex: 1, minWidth: 300 }}>
              <div style={{ position: 'relative', flex: 1 }}>
                <Search size={16} style={{ position: 'absolute', left: 12, top: 12, color: '#94a3b8' }} />
                <input 
                  type="text"
                  placeholder="Filter by Student ID..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  style={{ width: '100%', padding: '0.6rem 0.6rem 0.6rem 2.2rem', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: '0.875rem' }}
                />
              </div>

              <select 
                value={selectedSubject} 
                onChange={(e) => setSelectedSubject(e.target.value)}
                style={{ padding: '0.6rem', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: '0.875rem', backgroundColor: 'white' }}
              >
                <option value="">All Subjects</option>
                {subjects.map(s => (
                  <option key={s.subject_code} value={s.subject_code}>{s.subject_code}</option>
                ))}
              </select>

              <select 
                value={statusFilter} 
                onChange={(e) => setStatusFilter(e.target.value)}
                style={{ padding: '0.6rem', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: '0.875rem', backgroundColor: 'white' }}
              >
                <option value="">All Classifications</option>
                <option value="Normal">Normal</option>
                <option value="Suspicious">Suspicious</option>
                <option value="Highly Suspicious">Highly Suspicious</option>
              </select>
            </div>

            <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem', cursor: 'pointer', userSelect: 'none' }}>
              <input 
                type="checkbox" 
                checked={anomalyOnly}
                onChange={(e) => setAnomalyOnly(e.target.checked)}
                style={{ width: 16, height: 16, accentColor: '#4f46e5' }}
              />
              <span style={{ fontWeight: 600, color: '#1e293b' }}>Flagged Anomalies Only</span>
            </label>
          </div>
        </div>

        {/* Anomalies Table */}
        <div className="card">
          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Student ID</th>
                  <th>Student Name</th>
                  <th>Subject</th>
                  <th>Date & Time</th>
                  <th>Status</th>
                  <th>Anomaly Score</th>
                  <th>Classification</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2rem' }}>
                      Loading anomaly analysis...
                    </td>
                  </tr>
                ) : anomalies.length > 0 ? (
                  anomalies.map((anom) => (
                    <tr key={anom.id}>
                      <td><strong>{anom.student_id}</strong></td>
                      <td>{anom.student_name}</td>
                      <td>{anom.subject_code}</td>
                      <td>{anom.attendance_date} {anom.attendance_time}</td>
                      <td>
                        <span className={`badge ${anom.attendance_status === 'Present' ? 'badge-normal' : 'badge-highly-suspicious'}`}>
                          {anom.attendance_status}
                        </span>
                      </td>
                      <td>
                        <strong style={{ color: anom.anomaly_score >= 0.75 ? '#dc2626' : (anom.anomaly_score >= 0.50 ? '#c2410c' : '#059669') }}>
                          {anom.anomaly_score}
                        </strong>
                      </td>
                      <td>
                        <span className={`badge ${
                          anom.anomaly_status === 'Highly Suspicious' 
                            ? 'badge-highly-suspicious' 
                            : (anom.anomaly_status === 'Suspicious' ? 'badge-suspicious' : 'badge-normal')
                        }`}>
                          {anom.anomaly_status}
                        </span>
                      </td>
                      <td>
                        <button 
                          onClick={() => setSelectedAnomaly(anom)}
                          className="btn btn-secondary"
                          style={{ padding: '0.35rem 0.65rem', fontSize: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.35rem' }}
                        >
                          <Eye size={14} /> View Reasons
                        </button>
                      </td>
                    </tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan="8" style={{ textAlign: 'center', padding: '2rem', color: '#64748b' }}>
                      No anomaly records found matching criteria. Click "Execute Anomaly Detection" to run model over dataset.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Anomaly Details Modal */}
        {selectedAnomaly && (
          <AnomalyDetailsModal 
            anomaly={selectedAnomaly} 
            onClose={() => setSelectedAnomaly(null)} 
          />
        )}

      </div>
    </div>
  );
};

export default AnomalyDetection;
