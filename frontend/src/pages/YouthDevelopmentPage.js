import React from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import '../styles/YouthDevelopmentPage.css';

import physicalImage from '../assets/images/physical_page_icon.png';
import conditioningImage from '../assets/images/conditioning_page_icon.png';
import enduranceImage from '../assets/images/endurance_page_icon.png';

const YouthDevelopmentPage = () => {
  const navigate = useNavigate();

  return (
    <div className="youth-page-wrapper">
      <Header />
      <main className="youth-development-container">
        <h1 className="youth-page-title">Youth Development Programs</h1>
        <div className="development-buttons-container">
          <button
            className="development-button"
            onClick={() => navigate('/youth-development/physical')}
          >
            <div className="button-content">
              <img src={physicalImage} alt="Physical Development" className="development-icon" />
              <span>PHYSICAL</span>
              <p className="button-description">Physical strength and athletic development training</p>
            </div>
          </button>

          <button
            className="development-button"
            onClick={() => navigate('/youth-development/conditional')}
          >
            <div className="button-content">
              <img src={conditioningImage} alt="Conditional Development" className="development-icon" />
              <span>CONDITIONING</span>
              <p className="button-description">Football-specific conditioning and skill development</p>
            </div>
          </button>

          <button
            className="development-button"
            onClick={() => navigate('/youth-development/endurance')}
          >
            <div className="button-content">
              <img src={enduranceImage} alt="Endurance Development" className="development-icon" />
              <span>ENDURANCE</span>
              <p className="button-description">Cardiovascular and stamina enhancement programs</p>
            </div>
          </button>
        </div>
      </main>
      <Footer />
    </div>
  );
};

export default YouthDevelopmentPage;
