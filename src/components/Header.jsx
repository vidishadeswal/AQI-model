import React, { useState, useEffect } from 'react';
import { CloudLightning, Info, Moon, Sun } from 'lucide-react';
import './Header.css';

const Header = () => {
    const [isDark, setIsDark] = useState(false);

    useEffect(() => {
        if (isDark) {
            document.documentElement.setAttribute('data-theme', 'dark');
        } else {
            document.documentElement.removeAttribute('data-theme');
        }
    }, [isDark]);

    return (
        <header className="header sticky">
            <div className="container flex-between">
                <div className="logo-section flex-center">
                    <CloudLightning className="logo-icon" size={28} color="var(--color-teal)" />
                    <div className="title-group">
                        <h1 className="app-title">Air Quality Nowcast</h1>
                        <p className="app-subtitle">AI-powered PM2.5 forecast</p>
                    </div>
                </div>

                <div className="actions flex-center">
                    <button className="icon-btn" aria-label="Info">
                        <Info size={20} color="var(--color-text-secondary)" />
                    </button>
                    <button
                        className="icon-btn"
                        onClick={() => setIsDark(!isDark)}
                        aria-label="Toggle Theme"
                    >
                        {isDark ? (
                            <Sun size={20} color="var(--color-text-secondary)" />
                        ) : (
                            <Moon size={20} color="var(--color-text-secondary)" />
                        )}
                    </button>
                </div>
            </div>
        </header>
    );
};

export default Header;
