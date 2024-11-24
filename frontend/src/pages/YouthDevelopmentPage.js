import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/YouthDevelopmentPage.css'; // CSS dosyasını bağlayın

import physicalImage from '../assets/images/phyical_page_icon.png';
import conditioningImage from '../assets/images/conditioning_page_icon.png';
import enduranceImage from '../assets/images/ednurance_page_icon.png';

const YouthDevelopmentPage = () => {
  const navigate = useNavigate();

  return (
    <div className="youth-development-container">
      <button
        className="development-button"
        onClick={() => navigate('/youth-development/physical')}
      >
        <img src={physicalImage} alt="Physical Development" className="development-icon" />
        <span>PHYSICAL</span>
      </button>

      <button
        className="development-button"
        onClick={() => navigate('/youth-development/conditional')}
      >
        <img src={conditioningImage} alt="Conditional Development" className="development-icon" />
        <span>CONDITIONING</span>
      </button>

      <button
        className="development-button"
        onClick={() => navigate('/youth-development/endurance')}
      >
        <img src={enduranceImage} alt="Endurance Development" className="development-icon" />
        <span>ENDURANCE</span>
      </button>
    </div>
  );
};

export default YouthDevelopmentPage;
