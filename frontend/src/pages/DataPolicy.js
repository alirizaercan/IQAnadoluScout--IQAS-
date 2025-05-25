import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LegalPages.css';
import Footer from '../components/Footer';
import logoImage from '../assets/images/TYFOR_logo_circle.png';
import { isAuthenticated } from '../services/auth';

const DataPolicy = () => {
  const navigate = useNavigate();
  
  const handleHomeClick = () => {
    if (window.location.pathname === '/privacy' || window.location.pathname === '/terms' || window.location.pathname === '/data-policy') {
      navigate('/');
    } else if (isAuthenticated()) {
      navigate('/dashboard');
    } else {
      navigate('/authentication');
    }
  };
  
  return (
    <div className="legal-page-container">
      <div className="legal-nav">
        <div className="legal-logo-container" onClick={handleHomeClick}>
          <img src={logoImage} alt="TYFOR Logo" className="legal-logo" />
          <h1 className="legal-brand">TYFOR</h1>
        </div>
        <div className="legal-nav-links">
          <button onClick={() => navigate('/privacy')} className="legal-nav-button">Privacy Policy</button>
          <button onClick={() => navigate('/terms')} className="legal-nav-button">Terms of Service</button>
        </div>
      </div>
      
      <div className="legal-content">
        <h1 className="legal-title">Data Policy</h1>
        <div className="legal-last-updated">Last Updated: May 22, 2025</div>
        
        <section className="legal-section">
          <h2>1. Introduction</h2>
          <p>This Data Policy outlines how TYFOR collects, processes, and utilizes football-related data through our platform. We are committed to transparency in our data practices and ensuring the highest standards of data management in football analytics.</p>
        </section>
        
        <section className="legal-section">
          <h2>2. Data Collection</h2>
          <p><strong>2.1. Player Data</strong></p>
          <ul className="legal-list">
            <li>Performance statistics and metrics</li>
            <li>Physical and technical attributes</li>
            <li>Match participation and event data</li>
            <li>Development and progress tracking information</li>
          </ul>
          
          <p><strong>2.2. Match Data</strong></p>
          <ul className="legal-list">
            <li>Match events and statistics</li>
            <li>Tactical analysis data</li>
            <li>Video analysis outputs</li>
            <li>Team performance metrics</li>
          </ul>
          
          <p><strong>2.3. Scouting Data</strong></p>
          <ul className="legal-list">
            <li>Player evaluation reports</li>
            <li>Recruitment analysis data</li>
            <li>Performance comparison metrics</li>
            <li>Historical development data</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>3. Data Processing</h2>
          <p>Our data processing activities include:</p>
          <ul className="legal-list">
            <li>Statistical analysis and modeling</li>
            <li>Performance prediction and forecasting</li>
            <li>Player development tracking</li>
            <li>Match analysis and tactical insights</li>
            <li>Scouting recommendations and reports</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>4. Data Quality and Accuracy</h2>
          <p>We maintain high standards of data quality through:</p>
          <ul className="legal-list">
            <li>Regular data validation and verification</li>
            <li>Multiple data source cross-referencing</li>
            <li>Automated error detection systems</li>
            <li>Manual quality control processes</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>5. Data Access and Control</h2>
          <p>Access to data is strictly controlled through:</p>
          <ul className="legal-list">
            <li>Role-based access control systems</li>
            <li>Data access logging and monitoring</li>
            <li>Secure authentication mechanisms</li>
            <li>Regular access review and auditing</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>6. Data Retention</h2>
          <p>Our data retention policies ensure:</p>
          <ul className="legal-list">
            <li>Historical data preservation for analysis</li>
            <li>Regular data archiving processes</li>
            <li>Compliance with legal requirements</li>
            <li>Secure data disposal when necessary</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>7. Data Protection</h2>
          <p>We protect all collected data through:</p>
          <ul className="legal-list">
            <li>Advanced encryption systems</li>
            <li>Secure data storage facilities</li>
            <li>Regular security audits</li>
            <li>Incident response procedures</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>8. Data Sharing</h2>
          <p>Data sharing is governed by:</p>
          <ul className="legal-list">
            <li>Strict confidentiality agreements</li>
            <li>Data sharing protocols</li>
            <li>Access control mechanisms</li>
            <li>Usage monitoring systems</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>9. Updates to Data Policy</h2>
          <p>We may update this Data Policy periodically to reflect changes in our data practices, platform capabilities, or legal requirements. Users will be notified of significant changes to this policy.</p>
        </section>
        
        <section className="legal-section">
          <h2>10. Contact Information</h2>
          <p>For questions about our data practices or to request information about your data, please contact us via GitHub at <a href="https://github.com/alirizaercan/TYFOR" className="legal-link" target="_blank" rel="noopener noreferrer">github.com/alirizaercan/TYFOR</a>.</p>
        </section>
      </div>
      
      <Footer />
    </div>
  );
};

export default DataPolicy;
