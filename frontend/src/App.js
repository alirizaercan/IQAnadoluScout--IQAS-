import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AuthenticationPage from './pages/AuthenticationPage';
import MainPage from './pages/MainPage';
import YouthDevelopmentPage from './pages/YouthDevelopmentPage';

const ScoutingNetworkPage = () => <h1>Scouting Network</h1>;
const PerformanceVisualizationPage = () => <h1>Performance Visualization</h1>;
const TransferStrategyPage = () => <h1>Transfer Strategy</h1>;
const MatchAnalysisPage = () => <h1>Match Analysis</h1>;
const ScorePredictionPage = () => <h1>Score Prediction</h1>;

const PhysicalDevelopmentPage = () => <h1>Physical Development</h1>;
const ConditionalDevelopmentPage = () => <h1>Conditional Development</h1>;
const EnduranceDevelopmentPage = () => <h1>Endurance Development</h1>;

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
