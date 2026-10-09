import React from 'react';
import { X, AlertTriangle, CheckCircle, Info, User, BookOpen, Calendar, Clock } from 'lucide-react';

const AnomalyDetailsModal = ({ anomaly, onClose }) => {
  if (!anomaly) return null;

  const isAnomalous = anomaly.anomaly_status !== 'Normal';

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div style={{
              width: 38,
              height: 38,
              borderRadius: 8,
              backgroundColor: isAnomalous ? '#fee2e2' : '#d1fae5',
              color: isAnomalous ? '#dc2626' : '#059669',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}>
              {isAnomalous ? <AlertTriangle size={20} /> : <CheckCircle size={20} />}
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700 }}>Attendance Anomaly Detail</h3>
              <span className={`badge ${isAnomalous ? 'badge-highly-suspicious' : 'badge-normal'}`}>
                {anomaly.anomaly_status} (Score: {anomaly.anomaly_score})
              </span>
            </div>
          </div>
          <button 
            onClick={onClose} 
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#64748b' }}
          >
            <X size={20} />
          </button>
        </div>

        <div style={{ backgroundColor: '#f8fafc', padding: '1rem', borderRadius: 10, border: '1px solid #e2e8f0', marginBottom: '1.25rem' }}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.875rem' }}>
            <div>
              <p style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Student</p>
              <p style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <User size={14} color="#4f46e5" /> {anomaly.student_name} ({anomaly.student_id})
              </p>
            </div>
            <div>
              <p style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Subject</p>
              <p style={{ fontWeight: 600, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <BookOpen size={14} color="#4f46e5" /> {anomaly.subject_name} ({anomaly.subject_code})
              </p>
            </div>
            <div>
              <p style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Date & Time</p>
              <p style={{ fontWeight: 500, display: 'flex', alignItems: 'center', gap: '0.35rem' }}>
                <Calendar size={14} /> {anomaly.attendance_date} <Clock size={14} /> {anomaly.attendance_time}
              </p>
            </div>
            <div>
              <p style={{ color: '#64748b', fontSize: '0.75rem', textTransform: 'uppercase' }}>Logged Status</p>
              <p style={{ fontWeight: 600, color: anomaly.attendance_status === 'Present' ? '#059669' : '#dc2626' }}>
                {anomaly.attendance_status}
              </p>
            </div>
          </div>
        </div>

        <div style={{ marginBottom: '1.25rem' }}>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.75rem', color: '#1e293b' }}>
            Machine Learning Evaluation
          </h4>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <div style={{ flex: 1, padding: '0.85rem', background: '#eef2ff', borderRadius: 8, border: '1px solid #c7d2fe' }}>
              <p style={{ fontSize: '0.75rem', color: '#4338ca', fontWeight: 600 }}>Primary Model</p>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: '#312e81' }}>Isolation Forest</p>
              <p style={{ fontSize: '0.8rem', color: '#4f46e5' }}>Risk Score: <strong>{anomaly.anomaly_score}</strong></p>
            </div>
            <div style={{ flex: 1, padding: '0.85rem', background: '#f8fafc', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <p style={{ fontSize: '0.75rem', color: '#64748b', fontWeight: 600 }}>Secondary Validation</p>
              <p style={{ fontSize: '1rem', fontWeight: 700, color: '#334155' }}>Local Outlier Factor (LOF)</p>
              <p style={{ fontSize: '0.8rem', color: '#64748b' }}>Status: <strong>Evaluated</strong></p>
            </div>
          </div>
        </div>

        <div>
          <h4 style={{ fontSize: '0.95rem', fontWeight: 700, marginBottom: '0.65rem', color: '#1e293b', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
            <Info size={16} color="#ef4444" /> Possible Contributing Factors (Reason Indicators)
          </h4>
          <div style={{ background: '#fef2f2', padding: '1rem', borderRadius: 8, border: '1px solid #fecaca' }}>
            {anomaly.reason_indicators && anomaly.reason_indicators.length > 0 ? (
              <ul style={{ paddingLeft: '1.2rem', margin: 0, fontSize: '0.875rem', color: '#991b1b', lineHeight: '1.6' }}>
                {anomaly.reason_indicators.map((reason, idx) => (
                  <li key={idx} style={{ marginBottom: '0.35rem' }}>{reason}</li>
                ))}
              </ul>
            ) : (
              <p style={{ fontSize: '0.875rem', color: '#047857', margin: 0 }}>
                No significant statistical anomaly flags detected for this record.
              </p>
            )}
          </div>
        </div>

        <div style={{ marginTop: '1.5rem', textAlign: 'right' }}>
          <button onClick={onClose} className="btn btn-secondary">
            Close Panel
          </button>
        </div>
      </div>
    </div>
  );
};

export default AnomalyDetailsModal;
