import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LegalPages.css';
import Footer from '../components/Footer';
import logoImage from '../assets/images/TYFOR_logo_circle.png';
import { isAuthenticated } from '../services/auth';

const PrivacyPage = () => {
  const navigate = useNavigate();
    const handleHomeClick = () => {
    if (window.location.pathname === '/privacy' || window.location.pathname === '/terms') {
      navigate('/');
    } else if (isAuthenticated()) {
      navigate('/dashboard');
    } else {
      navigate('/authentication');
    }
  };
  
  return (    <div className="legal-page-container">      <div className="legal-nav">
        <div className="legal-logo-container" onClick={handleHomeClick}>
          <img src={logoImage} alt="TYFOR Logo" className="legal-logo" />
          <h1 className="legal-brand">TYFOR</h1>
        </div>
        <div className="legal-nav-links">
          <button onClick={() => navigate('/terms')} className="legal-nav-button">Terms of Service</button>
        </div>
      </div>
      
      <div className="legal-content">
        <h1 className="legal-title">Privacy Policy</h1>
        <div className="legal-last-updated">Last Updated: May 19, 2025</div>
        
        <section className="legal-section">
          <h2>1. Introduction</h2>
          <p>TYFOR ("we," "our," or "us") is committed to protecting your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our data-driven scouting and performance analysis platform ("Platform"). Please read this Privacy Policy carefully. By accessing or using the Platform, you consent to the practices described in this policy.</p>
        </section>
        
        <section className="legal-section">
          <h2>2. Information We Collect</h2>
          <p><strong>2.1. Personal Information</strong></p>
          <ul className="legal-list">
            <li>Account information: When you create an account, we collect your name, email address, and organization affiliation.</li>
            <li>Profile information: Information you provide in your user profile, such as job title, profile picture, and contact information.</li>
            <li>Authentication data: Usernames, passwords, and similar security information used for authentication and account access.</li>
          </ul>
          
          <p><strong>2.2. Football Analytics Data</strong></p>
          <ul className="legal-list">
            <li>Player performance data: Statistics, metrics, and analysis related to football players' performance.</li>
            <li>Team data: Match results, team composition, and tactical information.</li>
            <li>Video analysis data: Data extracted from football match videos through our analysis tools.</li>
            <li>Scouting reports: Information generated or uploaded about players being scouted.</li>
          </ul>
          
          <p><strong>2.3. Technical Data</strong></p>
          <ul className="legal-list">
            <li>Usage data: How you interact with our Platform, including features accessed, time spent, and actions taken.</li>
            <li>Device information: Information about your device, operating system, browser type, and IP address.</li>
            <li>Log data: Error reports, activity logs, and performance data related to your use of the Platform.</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>3. How We Use Your Information</h2>
          <p>We use the information we collect for various purposes, including:</p>
          <ul className="legal-list">
            <li>Providing and improving the Platform's functionality and user experience.</li>
            <li>Generating analytics, reports, and insights for football clubs and scouts.</li>
            <li>Processing and completing transactions related to your use of the Platform.</li>
            <li>Communicating with you about your account, updates to our Platform, or responding to your inquiries.</li>
            <li>Ensuring the security and integrity of our Platform.</li>
            <li>Analyzing usage patterns to improve our services and develop new features.</li>
            <li>Complying with legal obligations and enforcing our Terms of Service.</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>4. Data Sharing and Disclosure</h2>
          <p>We may share your information in the following circumstances:</p>
          <ul className="legal-list">
            <li><strong>Football Clubs and Organizations:</strong> If you are affiliated with a football club, certain data may be shared within your organization according to your access level.</li>
            <li><strong>Service Providers:</strong> We may share information with third-party vendors and service providers that perform services on our behalf.</li>
            <li><strong>Legal Requirements:</strong> We may disclose your information if required to do so by law or in response to valid requests by public authorities.</li>
            <li><strong>Business Transfers:</strong> If we are involved in a merger, acquisition, or sale of all or a portion of our assets, your information may be transferred as part of that transaction.</li>
            <li><strong>With Your Consent:</strong> We may share your information with third parties when we have your consent to do so.</li>
          </ul>
        </section>
        
        <section className="legal-section">
          <h2>5. Data Security</h2>
          <p>We implement appropriate technical and organizational measures to protect the information we collect and store. However, no electronic transmission or storage system is guaranteed to be 100% secure, and we cannot ensure or warrant the security of any information you transmit to us.</p>
        </section>
        
        <section className="legal-section">
          <h2>6. Data Retention</h2>
          <p>We retain your personal information for as long as necessary to fulfill the purposes outlined in this Privacy Policy, unless a longer retention period is required or permitted by law. Football analytics data may be retained indefinitely in an anonymized form for historical analysis and benchmarking purposes.</p>
        </section>
        
        <section className="legal-section">
          <h2>7. Your Rights</h2>
          <p>Depending on your location, you may have certain rights regarding your personal information, including:</p>
          <ul className="legal-list">
            <li>The right to access the personal information we hold about you.</li>
            <li>The right to request correction of inaccurate personal information.</li>
            <li>The right to request deletion of your personal information under certain circumstances.</li>
            <li>The right to restrict or object to certain processing of your personal information.</li>
            <li>The right to data portability.</li>
            <li>The right to withdraw consent where processing is based on your consent.</li>
          </ul>
          <p>To exercise these rights, please contact us using the information provided at the end of this Privacy Policy.</p>
        </section>
        
        <section className="legal-section">
          <h2>8. Children's Privacy</h2>
          <p>Our Platform is not intended for individuals under the age of 16. We do not knowingly collect personal information from children under 16. If you are a parent or guardian and believe that your child has provided us with personal information, please contact us immediately.</p>
        </section>
        
        <section className="legal-section">
          <h2>9. Changes to This Privacy Policy</h2>
          <p>We may update this Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last Updated" date. You are advised to review this Privacy Policy periodically for any changes.</p>
        </section>
        
        <section className="legal-section">
          <h2>10. Contact Information</h2>
          <p>If you have any questions or concerns about this Privacy Policy or our data practices, please contact us via GitHub at <a href="https://github.com/alirizaercan/TYFOR" className="legal-link" target="_blank" rel="noopener noreferrer">github.com/alirizaercan/TYFOR</a>.</p>
        </section>
      </div>
      
      <Footer />
    </div>
  );
};

export default PrivacyPage;
