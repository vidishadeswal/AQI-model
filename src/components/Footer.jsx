import React from 'react';
import './Footer.css';

const Footer = () => {
    return (
        <footer className="footer">
            <div className="container">
                <div className="footer-links flex-center">
                    <a href="#" className="footer-link">FAQ</a>
                    <span className="divider">|</span>
                    <a href="#" className="footer-link">About</a>
                    <span className="divider">|</span>
                    <a href="#" className="footer-link">Data Sources</a>
                    <span className="divider">|</span>
                    <a href="#" className="footer-link">Privacy</a>
                </div>

                <div className="footer-text text-center">
                    <p>Powered by AI — PM2.5 Nowcasting Model (XGBoost / LSTM)</p>
                    <p className="disclaimer">
                        Air quality predictions may vary based on sensor accuracy and weather conditions.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;
