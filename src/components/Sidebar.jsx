import React from 'react';
import { LayoutDashboard, MapPin, BarChart, Bell, Settings, LogOut, CloudLightning } from 'lucide-react';
import './Sidebar.css';

const Sidebar = () => {
    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', active: true },
        { icon: MapPin, label: 'Live Map', active: false },
        { icon: BarChart, label: 'Analytics', active: false },
        { icon: Bell, label: 'Alerts', active: false },
        { icon: Settings, label: 'Settings', active: false },
    ];

    return (
        <aside className="sidebar">
            <div className="sidebar-header">
                <div className="sidebar-logo-icon">
                    <CloudLightning size={28} className="text-teal" />
                </div>
                <h1 className="sidebar-title">Nowcast</h1>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <a
                        key={item.label}
                        href="#"
                        className={`nav-item ${item.active ? 'active' : ''}`}
                        onClick={(e) => e.preventDefault()}
                    >
                        <item.icon size={20} />
                        <span>{item.label}</span>
                    </a>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="user-profile">
                    <div className="user-avatar">U</div>
                    <div className="user-info">
                        <span className="user-name">User</span>
                        <span className="user-role">Free Plan</span>
                    </div>
                </div>
                <button className="logout-btn">
                    <LogOut size={18} />
                </button>
            </div>
        </aside>
    );
};

export default Sidebar;
