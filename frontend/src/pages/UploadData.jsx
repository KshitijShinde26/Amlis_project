import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { uploadAttendanceFile, getSampleDatasetUrl, getTemplateDatasetUrl } from '../services/api';
import { Upload, FileText, Download, CheckCircle2, AlertCircle, Play, AlertTriangle } from 'lucide-react';

const UploadData = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError(null);
      setResult(null);
    }
  };

  const handleUpload = async (e) => {
    e.preventDefault();
    if (!file) {
      setError("Please select a valid CSV or Excel file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    setError(null);

    try {
      const res = await uploadAttendanceFile(formData);
      setResult(res.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Error uploading attendance file.");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <Navbar title="Upload Attendance Dataset" />
      <div className="content-area" style={{ maxWidth: 900 }}>
        
        {/* Main Upload Box */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h3 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>Upload CSV or Excel File</h3>
          <p style={{ color: '#64748b', fontSize: '0.875rem', marginBottom: '1.5rem' }}>
            Upload raw attendance records to validate structure, process metrics, and store for ML anomaly detection.
          </p>

          <form onSubmit={handleUpload}>
            <div style={{
              border: '2px dashed #cbd5e1',
              borderRadius: 12,
              padding: '3rem 2rem',
              textAlign: 'center',
              backgroundColor: '#f8fafc',
              cursor: 'pointer',
              marginBottom: '1.5rem',
              transition: 'border-color 0.2s ease'
            }}
            onClick={() => document.getElementById('fileInput').click()}
            >
              <input 
                type="file" 
                id="fileInput" 
                accept=".csv, .xlsx, .xls"
                onChange={handleFileChange}
                style={{ display: 'none' }}
              />
              <div style={{
                width: 56,
                height: 56,
                borderRadius: '50%',
                backgroundColor: '#eef2ff',
                color: '#4f46e5',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 1rem auto'
              }}>
                <Upload size={28} />
              </div>
              
              {file ? (
                <div>
                  <p style={{ fontSize: '1rem', fontWeight: 600, color: '#1e293b' }}>Selected: {file.name}</p>
                  <p style={{ fontSize: '0.8rem', color: '#64748b' }}>({(file.size / 1024).toFixed(1)} KB)</p>
                </div>
              ) : (
                <div>
                  <p style={{ fontSize: '1rem', fontWeight: 600, color: '#1e293b' }}>
                    Click to select CSV or Excel (.xlsx) file
                  </p>
                  <p style={{ fontSize: '0.8rem', color: '#64748b', marginTop: '0.25rem' }}>
                    Maximum recommended batch size: 50,000 records
                  </p>
                </div>
              )}
            </div>

            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.75rem', justifyContent: 'space-between', alignItems: 'center' }}>
              <div style={{ display: 'flex', gap: '0.75rem' }}>
                <a 
                  href={getTemplateDatasetUrl()}
                  download="template_attendance.csv"
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <Download size={16} /> Download Blank Template (CSV)
                </a>
                <a 
                  href={getSampleDatasetUrl()}
                  download="sample_attendance.csv"
                  className="btn btn-secondary"
                  style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                >
                  <Download size={16} /> Download Sample Dataset
                </a>
              </div>

              <button 
                type="submit" 
                disabled={!file || uploading} 
                className="btn btn-primary"
                style={{ minWidth: 160 }}
              >
                {uploading ? "Uploading & Validating..." : "Process Dataset"}
              </button>
            </div>
          </form>

          {error && (
            <div style={{
              marginTop: '1.25rem',
              padding: '1rem',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: 8,
              color: '#991b1b',
              fontSize: '0.875rem',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}>
              <AlertCircle size={18} /> {error}
            </div>
          )}

          {result && (
            <div style={{
              marginTop: '1.5rem',
              padding: '1.25rem',
              backgroundColor: '#ecfdf5',
              border: '1px solid #a7f3d0',
              borderRadius: 10,
              color: '#065f46'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                <CheckCircle2 size={22} color="#059669" />
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Dataset Processed & Validated!</h4>
              </div>
              <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>{result.message}</p>
              
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '0.75rem', fontSize: '0.875rem', marginBottom: '1.25rem', backgroundColor: '#ffffff', padding: '0.75rem', borderRadius: 8, border: '1px solid #d1fae5' }}>
                <div><span style={{ color: '#64748b', fontSize: '0.75rem', display: 'block' }}>Received</span><strong>{result.records_received || result.records_processed}</strong></div>
                <div><span style={{ color: '#059669', fontSize: '0.75rem', display: 'block' }}>Inserted</span><strong style={{ color: '#059669' }}>{result.records_inserted ?? result.records_processed}</strong></div>
                <div><span style={{ color: '#d97706', fontSize: '0.75rem', display: 'block' }}>Duplicates Skipped</span><strong style={{ color: '#d97706' }}>{result.duplicates_skipped || 0}</strong></div>
                <div><span style={{ color: '#dc2626', fontSize: '0.75rem', display: 'block' }}>Invalid Skipped</span><strong style={{ color: '#dc2626' }}>{result.invalid_records_skipped || 0}</strong></div>
                <div><span style={{ color: '#64748b', fontSize: '0.75rem', display: 'block' }}>Unique Students</span><strong>{result.students_count}</strong></div>
                <div><span style={{ color: '#64748b', fontSize: '0.75rem', display: 'block' }}>Unique Subjects</span><strong>{result.subjects_count}</strong></div>
              </div>

              {result.warnings && result.warnings.length > 0 && (
                <div style={{
                  marginBottom: '1rem',
                  padding: '0.75rem',
                  backgroundColor: '#fffbeb',
                  border: '1px solid #fef3c7',
                  borderRadius: 6,
                  color: '#92400e',
                  fontSize: '0.8rem'
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', fontWeight: 600, marginBottom: '0.25rem' }}>
                    <AlertTriangle size={15} /> Upload Notices ({result.warnings.length}):
                  </div>
                  <ul style={{ margin: 0, paddingLeft: '1.25rem', maxHeight: 90, overflowY: 'auto' }}>
                    {result.warnings.slice(0, 5).map((w, i) => (
                      <li key={i}>{w}</li>
                    ))}
                    {result.warnings.length > 5 && (
                      <li>...and {result.warnings.length - 5} more notices.</li>
                    )}
                  </ul>
                </div>
              )}

              <button 
                onClick={() => navigate('/anomaly-detection')}
                className="btn btn-primary"
                style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Play size={16} /> Proceed to ML Anomaly Detection
              </button>
            </div>
          )}
        </div>

        {/* Expected Format Guide */}
        <div className="card">
          <h4 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <FileText size={18} color="#4f46e5" /> Expected Dataset Schema Format
          </h4>
          <p style={{ fontSize: '0.85rem', color: '#64748b', marginBottom: '1rem' }}>
            Ensure your CSV file contains header columns matching or similar to the following:
          </p>

          <div className="table-responsive">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Column Name</th>
                  <th>Type</th>
                  <th>Mandatory</th>
                  <th>Example Value</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td><code>student_id</code></td>
                  <td>String</td>
                  <td><span className="badge badge-highly-suspicious">Yes</span></td>
                  <td>STU001</td>
                </tr>
                <tr>
                  <td><code>student_name</code></td>
                  <td>String</td>
                  <td>Optional</td>
                  <td>Rahul Sharma</td>
                </tr>
                <tr>
                  <td><code>date</code></td>
                  <td>YYYY-MM-DD</td>
                  <td><span className="badge badge-highly-suspicious">Yes</span></td>
                  <td>2026-08-15</td>
                </tr>
                <tr>
                  <td><code>time</code></td>
                  <td>HH:MM</td>
                  <td>Optional</td>
                  <td>10:30</td>
                </tr>
                <tr>
                  <td><code>subject_code</code></td>
                  <td>String</td>
                  <td>Optional</td>
                  <td>IT601</td>
                </tr>
                <tr>
                  <td><code>subject_name</code></td>
                  <td>String</td>
                  <td>Optional</td>
                  <td>Applied Machine Learning</td>
                </tr>
                <tr>
                  <td><code>status</code></td>
                  <td>Present/Absent</td>
                  <td><span className="badge badge-highly-suspicious">Yes</span></td>
                  <td>Present</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </div>
  );
};

export default UploadData;
