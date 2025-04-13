import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AuthenticationPage from './pages/AuthenticationPage';
import MainPage from './pages/MainPage';
import YouthDevelopmentPage from './pages/YouthDevelopmentPage';
import PhysicalDevelopmentPage from './pages/PhysicalDevelopmentPage';
import ConditionalDevelopmentPage from './pages/ConditionalDevelopmentPage';
import EnduranceDevelopmentPage from './pages/EnduranceDevelopmentPage';
import ScoutingNetworkPage from './pages/ScoutingNetworkPage';
import TransferStrategyPage from './pages/TransferStrategyPage';
import PerformanceVisualizationPage from './pages/PerformanceVisualizationPage'
import ScorePredictionPage from './pages/ScorePredictionPage'
import MatchAnalysisPage from './pages/MatchAnalysisPage'

function App() {
  return (
    <Router>
      <Routes>
        {/* Ana rotalar */}
        <Route path="/" element={<AuthenticationPage />} />
        <Route path="/dashboard" element={<MainPage />} />

        {/* Youth Development rotaları */}
        <Route path="/youth-development" element={<YouthDevelopmentPage />} />
        <Route path="/youth-development/physical" element={<PhysicalDevelopmentPage />} />
        <Route path="/youth-development/conditional" element={<ConditionalDevelopmentPage />} />
        <Route path="/youth-development/endurance" element={<EnduranceDevelopmentPage />} />

        {/* Diğer rotalar */}
        <Route path="/scouting-network" element={<ScoutingNetworkPage />} />
        <Route path="/performance-visualization" element={<PerformanceVisualizationPage />} />
        <Route path="/transfer-strategy" element={<TransferStrategyPage />} />
        <Route path="/match-analysis" element={<MatchAnalysisPage />} />
        <Route path="/score-prediction" element={<ScorePredictionPage />} />
      </Routes>
    </Router>
  );
}

export default App;
