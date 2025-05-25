import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import AuthenticationPage from './pages/AuthenticationPage';
import MainPage from './pages/MainPage';
import YouthDevelopmentPage from './pages/YouthDevelopmentPage';
import PhysicalDevelopmentPage from './pages/PhysicalDevelopmentPage';
import ConditionalDevelopmentPage from './pages/ConditionalDevelopmentPage';
import EnduranceDevelopmentPage from './pages/EnduranceDevelopmentPage';
import ScoutingNetworkPage from './pages/ScoutingNetworkPage';
import TransferStrategyPage from './pages/TransferStrategyPage';
import PerformanceVisualizationPage from './pages/PerformanceVisualizationPage';
import ScorePredictionPage from './pages/ScorePredictionPage';
import MatchAnalysisPage from './pages/MatchAnalysisPage';
import AdminPanelPage from './pages/AdminPanelPage';
import LandingPage from './pages/LandingPage';
import TermsPage from './pages/TermsPage';
import PrivacyPage from './pages/PrivacyPage';
import DataPolicy from './pages/DataPolicy';
import { isAuthenticated, isAdmin } from './services/auth';

// Protected route component that checks if user is authenticated
const ProtectedRoute = ({ element, requireAdmin = false }) => {
  const authenticated = isAuthenticated();
  const admin = isAdmin();
  if (!authenticated) {
    return <Navigate to="/authentication" replace />;
  }

  if (requireAdmin && !admin) {
    return <Navigate to="/dashboard" replace />;
  }

  return element;
};

function App() {  return (
    <Router>
      <Routes>        {/* Landing and Authentication routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/authentication" element={<AuthenticationPage />} />
        
        {/* Admin panel route - protected and requires admin role */}
        <Route 
          path="/admin" 
          element={<ProtectedRoute element={<AdminPanelPage />} requireAdmin={true} />} 
        />

        {/* Dashboard route - protected for any authenticated user */}
        <Route 
          path="/dashboard" 
          element={<ProtectedRoute element={<MainPage />} />} 
        />

        {/* Youth Development routes - protected */}
        <Route 
          path="/youth-development" 
          element={<ProtectedRoute element={<YouthDevelopmentPage />} />} 
        />
        <Route 
          path="/youth-development/physical" 
          element={<ProtectedRoute element={<PhysicalDevelopmentPage />} />} 
        />
        <Route 
          path="/youth-development/conditional" 
          element={<ProtectedRoute element={<ConditionalDevelopmentPage />} />} 
        />
        <Route 
          path="/youth-development/endurance" 
          element={<ProtectedRoute element={<EnduranceDevelopmentPage />} />} 
        />

        {/* Other protected routes */}
        <Route 
          path="/scouting-network" 
          element={<ProtectedRoute element={<ScoutingNetworkPage />} />} 
        />
        <Route 
          path="/performance-visualization" 
          element={<ProtectedRoute element={<PerformanceVisualizationPage />} />} 
        />
        <Route 
          path="/transfer-strategy" 
          element={<ProtectedRoute element={<TransferStrategyPage />} />} 
        />
        <Route 
          path="/match-analysis" 
          element={<ProtectedRoute element={<MatchAnalysisPage />} />} 
        />        <Route 
          path="/score-prediction" 
          element={<ProtectedRoute element={<ScorePredictionPage />} />} 
        />

        {/* Legal pages - public access */}
        <Route path="/terms" element={<TermsPage />} />
        <Route path="/privacy" element={<PrivacyPage />} />
        <Route path="/data-policy" element={<DataPolicy />} />
      </Routes>
    </Router>
  );
}

export default App;