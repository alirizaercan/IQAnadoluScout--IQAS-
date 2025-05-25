import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LegalPages.css';
import Footer from '../components/Footer';
import logoImage from '../assets/images/TYFOR_logo_circle.png';
import { isAuthenticated } from '../services/auth';

const TermsPage = () => {
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
          <button onClick={() => navigate('/privacy')} className="legal-nav-button">Privacy Policy</button>
        </div>
      </div>
      
      <div className="legal-content">
        <h1 className="legal-title">Terms of Service</h1>
        <div className="legal-last-updated">Last Updated: May 19, 2025</div>
        
        <section className="legal-section">
          <h2>1. Introduction</h2>
          <p>Welcome to TYFOR ("we," "our," or "us"). By accessing or using our data-driven scouting and performance analysis platform, you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of these terms, you do not have permission to access the platform.</p>
        </section>
        
        <section className="legal-section">
          <h2>2. Definitions</h2>
          <p>
            <strong>Platform:</strong> The TYFOR application, including all its modules: Young Talent Development, Scouting Network, Match Analysis, Football Player Performance Visualization, Transfer Strategy Development, and Match Score Prediction.<br />
            <strong>User:</strong> Any individual or organization that accesses or uses the TYFOR platform.<br />
            <strong>Content:</strong> All information, data, text, graphics, images, and other materials uploaded, downloaded, or appearing on the Platform.
          </p>
        </section>
        
        <section className="legal-section">
          <h2>3. User Account</h2>
          <p>3.1. To access certain features of the Platform, you may be required to create an account.</p>
          <p>3.2. You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.</p>
          <p>3.3. You agree to notify us immediately of any unauthorized use of your account.</p>
        </section>
        
        <section className="legal-section">
          <h2>4. Data and Privacy</h2>
          <p>4.1. Our collection and use of personal information in connection with your access to and use of the Platform is described in our <a href="/privacy" className="legal-link">Privacy Policy</a>.</p>
          <p>4.2. You agree that we may use the data provided by you for the purposes of improving our platform and providing analytics services.</p>
          <p>4.3. You acknowledge that the statistical models and predictions offered by TYFOR are based on historical data and algorithms and should not be the sole basis for decision-making.</p>
        </section>
        
        <section className="legal-section">
          <h2>5. User Responsibilities</h2>
          <p>5.1. You agree not to use the Platform for any illegal purpose or in any manner inconsistent with these Terms.</p>
          <p>5.2. You agree not to share your access credentials with third parties.</p>
          <p>5.3. You agree not to upload or transmit any malicious code or attempt to harm the Platform in any way.</p>
          <p>5.4. You agree not to attempt to access, tamper with, or use non-public areas of the Platform or our systems.</p>
        </section>
        
        <section className="legal-section">
          <h2>6. Intellectual Property</h2>
          <p>6.1. The Platform and its original content, features, and functionality are owned by TYFOR and are protected by international copyright, trademark, patent, trade secret, and other intellectual property or proprietary rights laws.</p>
          <p>6.2. You may not copy, modify, create derivative works, publicly display, publicly perform, republish, or transmit any material obtained from the Platform without our prior written consent.</p>
        </section>
        
        <section className="legal-section">
          <h2>7. Disclaimer of Warranties</h2>
          <p>7.1. The Platform is provided "as is" and "as available" without warranties of any kind, either express or implied, including, but not limited to, implied warranties of merchantability, fitness for a particular purpose, or non-infringement.</p>
          <p>7.2. We do not warrant that the Platform will be uninterrupted or error-free, that defects will be corrected, or that the Platform is free of viruses or other harmful components.</p>
        </section>
        
        <section className="legal-section">
          <h2>8. Limitation of Liability</h2>
          <p>8.1. To the maximum extent permitted by applicable law, TYFOR shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to, loss of profits, data, or use, arising out of or in any way connected with the use of or inability to use the Platform.</p>
        </section>
        
        <section className="legal-section">
          <h2>9. Modifications to Terms</h2>
          <p>9.1. We reserve the right to modify these Terms at any time. If we make changes, we will provide notice of such changes, such as by sending an email notification, providing notice through the Platform, or updating the "Last Updated" date at the beginning of these Terms.</p>
          <p>9.2. Your continued use of the Platform following the posting of revised Terms means that you accept and agree to the changes.</p>
        </section>
        
        <section className="legal-section">
          <h2>10. Governing Law</h2>
          <p>These Terms shall be governed by and construed in accordance with the laws of Turkey, without regard to its conflict of law provisions.</p>
        </section>
        
        <section className="legal-section">
          <h2>11. Contact Information</h2>
          <p>If you have any questions about these Terms, please contact us via GitHub at <a href="https://github.com/alirizaercan/TYFOR" className="legal-link" target="_blank" rel="noopener noreferrer">github.com/alirizaercan/TYFOR</a>.</p>
        </section>
      </div>
      
      <Footer />
    </div>
  );
};

export default TermsPage;
