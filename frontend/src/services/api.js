import axios from 'axios';

const API_BASE = 'http://localhost:8001/api';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getHealth = () => api.get('/health');

export const uploadAttendanceFile = (formData) => {
  return api.post('/attendance/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
};

export const getAttendanceRecords = (skip = 0, limit = 100) => {
  return api.get(`/attendance?skip=${skip}&limit=${limit}`);
};

export const triggerAnomalyDetection = (params = { contamination: 0.10, method: 'Isolation Forest' }) => {
  return api.post('/anomaly/detect', params);
};

export const getAnomalies = (filters = {}) => {
  const query = new URLSearchParams();
  if (filters.student_id) query.append('student_id', filters.student_id);
  if (filters.subject_code) query.append('subject_code', filters.subject_code);
  if (filters.status_filter) query.append('status_filter', filters.status_filter);
  if (filters.anomaly_only) query.append('anomaly_only', 'true');
  
  return api.get(`/anomalies?${query.toString()}`);
};

export const getAnomalyDetails = (id) => api.get(`/anomalies/details/${id}`);

export const getStudents = () => api.get('/students');

export const getStudentDetails = (studentId) => api.get(`/students/${studentId}`);

export const getStudentAttendance = (studentId) => api.get(`/students/${studentId}/attendance`);

export const getSubjects = () => api.get('/subjects');

export const getDashboardStats = () => api.get('/dashboard/statistics');

export const getSampleDatasetUrl = () => `${API_BASE}/dataset/sample`;
export const getTemplateDatasetUrl = () => `${API_BASE}/dataset/template`;

export const getReportExportUrl = (format = 'csv', anomalyOnly = false) => {
  return `${API_BASE}/reports/anomalies/export?format=${format}&anomaly_only=${anomalyOnly}`;
};

export default api;
