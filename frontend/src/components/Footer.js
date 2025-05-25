import React from 'react';
import { useNavigate } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faTwitter, 
  faLinkedinIn, 
  faInstagram 
} from '@fortawesome/free-brands-svg-icons';
import { 
  faEnvelope, 
  faPhone, 
  faMapMarkerAlt 
} from '@fortawesome/free-solid-svg-icons';
import '../styles/Footer.css';
import TYFORLogo from '../assets/images/TYFOR_logo_circle.png';

const Footer = () => {
  const navigate = useNavigate();
  const currentYear = new Date().getFullYear();

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-section">          <div className="company-info">
            <div className="footer-branding">
              <img src={TYFORLogo} alt="TYFOR Logo" className="footer-logo" />
              <h4 className="footer-title">TYFOR</h4>
            </div>
            <p className="footer-description">
              Transforming football data into actionable insights. Our cutting-edge AI technology
              helps teams and scouts make better decisions for youth development and talent acquisition.
            </p>
            <div className="social-links">
              <a href="https://twitter.com/tyfor" target="_blank" rel="noopener noreferrer" className="social-icon">
                <FontAwesomeIcon icon={faTwitter} />
              </a>
              <a href="https://linkedin.com/company/tyfor" target="_blank" rel="noopener noreferrer" className="social-icon">
                <FontAwesomeIcon icon={faLinkedinIn} />
              </a>
              <a href="https://instagram.com/tyfor" target="_blank" rel="noopener noreferrer" className="social-icon">
                <FontAwesomeIcon icon={faInstagram} />
              </a>
            </div>
          </div>
        </div>

        <div className="footer-section">
          <h4 className="footer-title">Quick Links</h4>
          <ul className="footer-links">
            <li><button onClick={() => navigate('/youth-development')} className="footer-link">Youth Development</button></li>
            <li><button onClick={() => navigate('/scouting-network')} className="footer-link">Scouting Network</button></li>
            <li><button onClick={() => navigate('/performance-visualization')} className="footer-link">Performance Analysis</button></li>
            <li><button onClick={() => navigate('/match-analysis')} className="footer-link">Match Analysis</button></li>
          </ul>
        </div>

        <div className="footer-section">
          <h4 className="footer-title">Contact</h4>
          <ul className="footer-contact">
            <li>
              <span className="contact-icon">
                <FontAwesomeIcon icon={faEnvelope} />
              </span>
              <a href="mailto:info.tyfor@gmail.com" className="contact-link">info.tyfor@gmail.com</a>
            </li>            <li>
              <span className="contact-icon">
                <FontAwesomeIcon icon={faPhone} />
              </span>
              <a href="tel:+905342402651" className="contact-link">+90 534 240 2651</a>
            </li>
            <li>
              <span className="contact-icon">
                <FontAwesomeIcon icon={faMapMarkerAlt} />
              </span>
              <span className="contact-text">Turkey</span>
            </li>
          </ul>
        </div>
      </div>
      
      <div className="footer-divider"></div>
      
      <div className="footer-bottom">
        <div className="footer-copyright">
          © {currentYear} TYFOR. All rights reserved.
        </div>
        <div className="footer-legal">
          <button onClick={() => navigate('/privacy')} className="footer-link">Privacy Policy</button>
          <button onClick={() => navigate('/terms')} className="footer-link">Terms of Service</button>
        </div>
      </div>
    </footer>
  );
};

export default Footer;