import React, { useState, useRef } from 'react';
import { uploadMatchVideo, getAnalysisResults } from '../services/match_analysis_api';
import '../styles/MatchAnalysisPage.css';
import matchAnalysisIcon from "../assets/images/match_analysis_icon.png";

const MatchAnalysisPage = () => {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [matchDate, setMatchDate] = useState('');
  const [videoFile, setVideoFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [analysisId, setAnalysisId] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!videoFile || !homeTeam || !awayTeam || !matchDate) {
      alert('Please fill all fields and select a video file');
      return;
    }

    setIsUploading(true);
    try {
      const response = await uploadMatchVideo(videoFile, homeTeam, awayTeam, matchDate);
      setAnalysisId(response.analysis_id);
      alert('Video uploaded successfully! Analysis in progress...');
    } catch (error) {
      console.error('Upload error:', error);
      alert('Upload failed: ' + error.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleGetResults = async () => {
    if (!analysisId) return;
    
    try {
      const results = await getAnalysisResults(analysisId);
      setAnalysisResults(results);
    } catch (error) {
      console.error('Error fetching results:', error);
      alert('Failed to get analysis results');
    }
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  return (
    <div className="match-analysis-container">
      <div className="upload-section">
        <h2>Upload Match Video</h2>
        
        <div className="upload-box" onClick={triggerFileInput}>
          {videoFile ? (
            <p>{videoFile.name}</p>
          ) : (
            <p>Click to select video file</p>
          )}
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="video/*"
            style={{ display: 'none' }}
          />
        </div>

        <div className="score-prediction-icon">
          <img src={scorePredictionIcon} alt="Score Prediction Icon" className="icon-image" />
        </div>
        
        <div className="team-inputs">
          <input
            type="text"
            placeholder="Home Team"
            value={homeTeam}
            onChange={(e) => setHomeTeam(e.target.value)}
          />
          <input
            type="text"
            placeholder="Away Team"
            value={awayTeam}
            onChange={(e) => setAwayTeam(e.target.value)}
          />
          <input
            type="date"
            value={matchDate}
            onChange={(e) => setMatchDate(e.target.value)}
          />
        </div>
        
        <button 
          onClick={handleUpload} 
          disabled={isUploading}
          className="upload-button"
        >
          {isUploading ? 'Uploading...' : 'Upload & Analyze'}
        </button>
      </div>

      <div className="branding">
        <div className="brand-logos">
          <span>WOLDSG</span>
          <span>USB</span>
          <span>TUV</span>
          <span>DK</span>
          <span>SIG</span>
          <span>ASTORE</span>
        </div>
        <div className="slogan">BETTER NEVER STOPS</div>
      </div>

      {analysisId && (
        <div className="results-section">
          <button onClick={handleGetResults} className="get-results-button">
            Get Analysis Results
          </button>
          
          {analysisResults && (
            <div className="analysis-results">
              <h3>Match Analysis Report</h3>
              
              <div className="stats-grid">
                <div className="stat-card">
                  <h4>Possession</h4>
                  <div className="possession-bar">
                    <div 
                      className="home-possession" 
                      style={{ width: `${analysisResults.home_possession}%` }}
                    >
                      {analysisResults.home_possession}%
                    </div>
                    <div 
                      className="away-possession" 
                      style={{ width: `${analysisResults.away_possession}%` }}
                    >
                      {analysisResults.away_possession}%
                    </div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <h4>Formations</h4>
                  <div className="formations">
                    <div className="formation">
                      <span>Home: {analysisResults.home_formation}</span>
                    </div>
                    <div className="formation">
                      <span>Away: {analysisResults.away_formation}</span>
                    </div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <h4>Shots</h4>
                  <div className="shots">
                    <div className="shot-type">
                      <span>Home: {analysisResults.home_shots} ({analysisResults.home_shots_on_target} on target)</span>
                    </div>
                    <div className="shot-type">
                      <span>Away: {analysisResults.away_shots} ({analysisResults.away_shots_on_target} on target)</span>
                    </div>
                  </div>
                </div>
                
                <div className="stat-card">
                  <h4>Pass Accuracy</h4>
                  <div className="pass-accuracy">
                    <div className="pass-type">
                      <span>Home: {analysisResults.home_pass_accuracy}%</span>
                    </div>
                    <div className="pass-type">
                      <span>Away: {analysisResults.away_pass_accuracy}%</span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="advanced-stats">
                <h4>Formation Changes</h4>
                <p>Home: {analysisResults.home_formation_changes} changes</p>
                <p>Away: {analysisResults.away_formation_changes} changes</p>
              </div>
              
              <div className="report-actions">
                <button className="req-button">REQ</button>
                <button className="rec-button">REC</button>
                <button className="report-button">Report</button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MatchAnalysisPage;