import React from 'react';
import Navbar from '../components/Navbar';
import { Cpu, ShieldCheck, HelpCircle, Layers, FileCode } from 'lucide-react';

const ModelAnalytics = () => {
  return (
    <div>
      <Navbar title="Machine Learning Analytics & Model Architecture" />
      <div className="content-area" style={{ maxWidth: 950 }}>
        
        {/* Header Summary */}
        <div className="card" style={{ marginBottom: '2rem', borderLeft: '4px solid #4f46e5' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Cpu size={22} color="#4f46e5" /> Academic ML Architecture Overview
          </h3>
          <p style={{ color: '#475569', fontSize: '0.9rem', lineHeight: '1.6' }}>
            This system implements an unsupervised Machine Learning pipeline to identify abnormal student attendance behavior. 
            Because ground-truth labels are generally absent in real-world attendance tracking, the model constructs statistical feature boundaries to isolate spatial and temporal anomalies.
          </p>
        </div>

        {/* Pipeline Diagram / Breakdown */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h4 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} color="#0284c7" /> Feature Engineering Vector Space (13 Features)
          </h4>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem', fontSize: '0.85rem' }}>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>1. Attendance Status Numeric (0 or 1)</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Encodes attendance binary status (Present=1, Absent=0).</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>2. Hour of Day (0–23) & Day of Week (0–6)</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Captures temporal lecture scheduling patterns.</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>3. Student Overall Attendance Rate (%)</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Historical baseline attendance rate for student across all subjects.</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>4. Subject Attendance Rate (%)</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Specific student attendance percentage in target subject.</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>5. Subject Discrepancy & Peer Outlier Deviation</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Delta between student subject attendance rate and class average.</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>6. Streak & Recent Moving Average</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Consecutive absence streak count & 5-class rolling average.</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>7. Unusual Lecture Hour Flag</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Flags timestamps outside standard 08:00–18:00 window.</p>
            </div>
            <div style={{ background: '#f8fafc', padding: '1rem', borderRadius: 8, border: '1px solid #e2e8f0' }}>
              <strong style={{ color: '#1e293b' }}>8. Multi-Presence Time Conflict Flag</strong>
              <p style={{ color: '#64748b', marginTop: '0.25rem' }}>Detects impossible simultaneous presence across multiple subjects.</p>
            </div>
          </div>
        </div>

        {/* Algorithm Comparison Details */}
        <div className="grid-2">
          <div className="card">
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#4338ca', marginBottom: '0.5rem' }}>
              Primary Algorithm: Isolation Forest
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: '1.5' }}>
              Isolation Forest explicitly isolates anomalies by randomly selecting a feature and splitting the value between min and max. 
              Because anomalies are few and attribute-wise different, they require fewer splits to isolate in random trees.
            </p>
          </div>

          <div className="card">
            <h4 style={{ fontSize: '1rem', fontWeight: 700, color: '#0369a1', marginBottom: '0.5rem' }}>
              Secondary Model: Local Outlier Factor (LOF)
            </h4>
            <p style={{ fontSize: '0.85rem', color: '#475569', lineHeight: '1.5' }}>
              LOF computes the local density of a record relative to its k-nearest neighbors. 
              Samples with substantially lower local density than their neighbors are identified as density-based outliers.
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ModelAnalytics;
