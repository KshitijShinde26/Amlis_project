import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { uploadAttendanceFile, getSampleDatasetUrl } from '../services/api';
import { Upload, FileText, Download, CheckCircle2, AlertCircle, Play } from 'lucide-react';

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

            <div style={{ display: 'flex', gap: '1rem', justifyContent: 'space-between', alignItems: 'center' }}>
              <a 
                href={getSampleDatasetUrl()}
                download="sample_attendance.csv"
                className="btn btn-secondary"
                style={{ textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Download size={16} /> Download Sample Dataset (CSV)
              </a>

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
                <h4 style={{ fontSize: '1.05rem', fontWeight: 700 }}>Dataset Successfully Uploaded & Validated!</h4>
              </div>
              <p style={{ fontSize: '0.875rem', marginBottom: '1rem' }}>{result.message}</p>
              
              <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.875rem', marginBottom: '1.25rem' }}>
                <div><strong>Records Stored:</strong> {result.records_processed}</div>
                <div><strong>Students Count:</strong> {result.students_count}</div>
                <div><strong>Subjects Count:</strong> {result.subjects_count}</div>
              </div>

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
