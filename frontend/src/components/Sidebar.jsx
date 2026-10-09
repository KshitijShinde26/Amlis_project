import React from 'react';
import { NavLink } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Upload, 
  Table, 
  ShieldAlert, 
  Users, 
  BookOpen, 
  FileSpreadsheet, 
  Cpu 
} from 'lucide-react';

const Sidebar = () => {
  const navItems = [
    { path: '/', label: 'Dashboard', icon: LayoutDashboard },
    { path: '/upload', label: 'Upload Data', icon: Upload },
    { path: '/records', label: 'Attendance Records', icon: Table },
    { path: '/anomaly-detection', label: 'Anomaly Detection', icon: ShieldAlert },
    { path: '/students', label: 'Students', icon: Users },
    { path: '/subjects', label: 'Subjects', icon: BookOpen },
    { path: '/reports', label: 'Reports & Export', icon: FileSpreadsheet },
    { path: '/model-analytics', label: 'ML Analytics', icon: Cpu },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="logo-badge">SA</div>
        <div className="sidebar-title">
          <h1>Smart Attendance</h1>
          <span>ML Anomaly Engine</span>
        </div>
      </div>
      <ul className="nav-list">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <li key={item.path} className="nav-item">
              <NavLink 
                to={item.path} 
                className={({ isActive }) => (isActive ? 'active' : '')}
                end={item.path === '/'}
              >
                <Icon size={18} />
                <span>{item.label}</span>
              </NavLink>
            </li>
          );
        })}
      </ul>
      <div style={{ padding: '1.25rem', borderTop: '1px solid #1e293b', fontSize: '0.75rem', color: '#64748b' }}>
        <p>AMLIS Academic Project</p>
        <p style={{ color: '#94a3b8', fontWeight: 600, marginTop: '0.2rem' }}>Isolation Forest & LOF</p>
      </div>
    </aside>
  );
};

export default Sidebar;
