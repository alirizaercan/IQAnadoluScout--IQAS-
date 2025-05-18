import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/MainPage.css';
import Header from '../components/Header';
import Footer from '../components/Footer';
import youthDevelopmentIcon from '../assets/images/youth_development_icon.png';
import scoutingNetworkIcon from '../assets/images/scouting_network_icon.png';
import performanceVisualizationIcon from '../assets/images/performance_visualization_icon.png';
import transferStrategyIcon from '../assets/images/transfer_strategy_icon.png';
import matchAnalysisIcon from '../assets/images/match_analysis_icon.png';
import scorePredictionIcon from '../assets/images/score_prediction_icon.png';

const MainPage = () => {
  const navigate = useNavigate();

  return (
    <div className="main-page-container">
      <Header />
      <div className="main-page">
        <div className="button-row">
          <button
            onClick={() => navigate('/youth-development')}
            className="custom-button"
          >
            <img src={youthDevelopmentIcon} alt="Youth Development" />
          </button>
          <button
            onClick={() => navigate('/scouting-network')}
            className="custom-button"
          >
            <img src={scoutingNetworkIcon} alt="Scouting Network" />
          </button>
          <button
            onClick={() => navigate('/performance-visualization')}
            className="custom-button"
          >
            <img src={performanceVisualizationIcon} alt="Performance Visualization" />
          </button>
        </div>

        <div className="button-row">
          <button
            onClick={() => navigate('/transfer-strategy')}
            className="custom-button"
          >
            <img src={transferStrategyIcon} alt="Transfer Strategy" />
          </button>
          <button
            onClick={() => navigate('/match-analysis')}
            className="custom-button"
          >
            <img src={matchAnalysisIcon} alt="Match Analysis" />
          </button>
          <button
            onClick={() => navigate('/score-prediction')}
            className="custom-button"
          >
            <img src={scorePredictionIcon} alt="Score Prediction" />
          </button>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default MainPage;
