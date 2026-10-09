import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import { getReportExportUrl } from '../services/api';
import { FileSpreadsheet, Download, FileText, CheckSquare, Filter } from 'lucide-react';

const Reports = () => {
  const [anomalyOnly, setAnomalyOnly] = useState(false);

  const handleDownload = (format) => {
    const url = getReportExportUrl(format, anomalyOnly);
    window.open(url, '_blank');
  };

  return (
    <div>
      <Navbar title="Anomaly Detection Reports & Data Export" />
      <div className="content-area" style={{ maxWidth: 850 }}>
        
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileSpreadsheet size={22} color="#4f46e5" /> Generate & Download Attendance Anomaly Reports
          </h3>
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Export comprehensive evaluation reports containing student details, subject records, machine learning Isolation Forest risk scores, and rule-assisted reason indicators.
          </p>

          {/* Filter Options */}
          <div style={{ background: '#f8fafc', padding: '1rem 1.25rem', borderRadius: 10, border: '1px solid #e2e8f0', marginBottom: '1.75rem' }}>
            <h4 style={{ fontSize: '0.875rem', fontWeight: 700, marginBottom: '0.5rem', color: '#334155' }}>Export Scope Filter</h4>
            <label style={{ display: 'flex', alignItems: 'center', gap: '0.65rem', cursor: 'pointer', userSelect: 'none' }}>
              <input 
                type="checkbox" 
                checked={anomalyOnly}
                onChange={(e) => setAnomalyOnly(e.target.checked)}
                style={{ width: 18, height: 18, accentColor: '#4f46e5' }}
              />
              <span style={{ fontSize: '0.9rem', fontWeight: 600, color: '#1e293b' }}>
                Export Flagged Suspicious / Anomalous Records Only
              </span>
            </label>
            <p style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '0.35rem', marginLeft: '1.75rem' }}>
              {anomalyOnly 
                ? "Report will include only records flagged as 'Suspicious' or 'Highly Suspicious'."
                : "Report will include all analyzed student attendance records along with their status classification."
              }
            </p>
          </div>

          {/* Export Options Grid */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1.25rem' }}>
            
            {/* CSV Card */}
            <div style={{ border: '1px solid #e2e8f0', borderRadius: 10, padding: '1.25rem', textAlign: 'center', backgroundColor: '#ffffff' }}>
              <div style={{ width: 44, height: 44, borderRadius: 8, background: '#e0e7ff', color: '#4338ca', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.75rem auto' }}>
                <FileText size={22} />
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>CSV Format</h4>
              <p style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '1rem' }}>Standard comma-separated dataset export</p>
              <button onClick={() => handleDownload('csv')} className="btn btn-primary" style={{ width: '100%', fontSize: '0.8rem' }}>
                <Download size={14} /> Download CSV
              </button>
            </div>

            {/* Excel Card */}
            <div style={{ border: '1px solid #e2e8f0', borderRadius: 10, padding: '1.25rem', textAlign: 'center', backgroundColor: '#ffffff' }}>
              <div style={{ width: 44, height: 44, borderRadius: 8, background: '#dcfce7', color: '#15803d', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.75rem auto' }}>
                <FileSpreadsheet size={22} />
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>Excel (.xlsx)</h4>
              <p style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '1rem' }}>Formatted spreadsheet with styled columns</p>
              <button onClick={() => handleDownload('excel')} className="btn btn-primary" style={{ width: '100%', fontSize: '0.8rem', background: '#16a34a' }}>
                <Download size={14} /> Download Excel
              </button>
            </div>

            {/* PDF Card */}
            <div style={{ border: '1px solid #e2e8f0', borderRadius: 10, padding: '1.25rem', textAlign: 'center', backgroundColor: '#ffffff' }}>
              <div style={{ width: 44, height: 44, borderRadius: 8, background: '#fee2e2', color: '#b91c1c', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 0.75rem auto' }}>
                <FileText size={22} />
              </div>
              <h4 style={{ fontSize: '1rem', fontWeight: 700 }}>PDF Document</h4>
              <p style={{ fontSize: '0.75rem', color: '#64748b', marginBottom: '1rem' }}>Printable academic presentation report</p>
              <button onClick={() => handleDownload('pdf')} className="btn btn-primary" style={{ width: '100%', fontSize: '0.8rem', background: '#dc2626' }}>
                <Download size={14} /> Download PDF
              </button>
            </div>

          </div>
        </div>

      </div>
    </div>
  );
};

export default Reports;
