import React from 'react';
import { ShieldAlert, RefreshCw } from 'lucide-react';

const Navbar = ({ title = "Dashboard", onRefresh }) => {
  return (
    <header className="top-navbar">
      <div className="page-header-title">
        <h2>{title}</h2>
      </div>
      <div className="top-navbar-actions">
        <div className="system-status-chip">
          <div className="status-dot"></div>
          <span>ML Pipeline Active</span>
        </div>
        {onRefresh && (
          <button 
            onClick={onRefresh} 
            className="btn btn-secondary" 
            style={{ padding: '0.4rem 0.85rem', fontSize: '0.8rem' }}
          >
            <RefreshCw size={14} /> Refresh Data
          </button>
        )}
      </div>
    </header>
  );
};

export default Navbar;
