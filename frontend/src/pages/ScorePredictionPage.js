import React, { useState, useEffect } from "react";
import { fetchLeagues, fetchTeamsByLeague, fetchPredictions } from "../services/prediction_api";
import "../styles/ScorePredictionPage.css";
import scorePredictionIcon from "../assets/images/score_prediction_icon.png";

const defaultLeagueLogo = "https://tmssl.akamaized.net//images/logo/header/tr1.png?lm=1723019495"; // Placeholder for default league logo
const defaultTeamLogo = "https://tmssl.akamaized.net/images/wappen/head/10484.png"; // Default team logo
const defaultPlayerImage = "https://img.a.transfermarkt.technology/portrait/header/default.jpg?lm=1";

const ScorePredictionPage = () => {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [selectedLeagueLogo, setSelectedLeagueLogo] = useState(defaultLeagueLogo);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedTeamLogo, setSelectedTeamLogo] = useState(defaultTeamLogo);
  const [predictions, setPredictions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Fetch leagues on component mount
  useEffect(() => {
    fetchLeagues()
      .then((data) => {
        setLeagues(data);
        if (data.length > 0) {
          handleLeagueSelect(data[0].league_id); // Auto-select the first league
        }
      })
      .catch((err) => console.error("Error fetching leagues:", err));
  }, []);

  // Fetch teams when league is selected
  const handleLeagueSelect = (leagueId) => {
    const leagueIdStr = String(leagueId);
    const selectedLeagueObj = leagues.find((league) => String(league.league_id) === leagueIdStr);
    
    setSelectedLeague(leagueIdStr);
    setSelectedLeagueLogo(selectedLeagueObj?.league_logo_path || defaultLeagueLogo);
    
    if (selectedLeagueObj) {
      fetchTeamsByLeague(leagueIdStr)
        .then((data) => {
          setTeams(data);
          if (data.length > 0) {
            // Takım seçimini sıfırla ve yeni takımı seç
            setSelectedTeam(null);
            setSelectedTeamLogo(defaultTeamLogo);
            const firstTeam = data[0];
            setSelectedTeam(firstTeam.team_id);
            setSelectedTeamLogo(firstTeam.img_path || defaultTeamLogo);
            handleTeamSelect(firstTeam.team_id);
          } else {
            setSelectedTeam(null);
            setSelectedTeamLogo(defaultTeamLogo);
            setPredictions([]);
          }
        })
        .catch((err) => {
          console.error("Error fetching teams:", err);
          setTeams([]);
          setSelectedTeam(null);
          setSelectedTeamLogo(defaultTeamLogo);
          setPredictions([]);
        });
    }
  };

  // Fetch prediction data for selected team
  const handleTeamSelect = (teamId) => {
    // Convert teamId to number for proper comparison
    const teamIdNumber = parseInt(teamId);
    const selectedTeam = teams.find((team) => team.team_id === teamIdNumber);
    setSelectedTeam(teamIdNumber);
    setSelectedTeamLogo(selectedTeam?.img_path || defaultTeamLogo);
    
    if (teamIdNumber) {
      setLoading(true);
      fetchPredictions(teamIdNumber)
        .then((data) => {
          setPredictions(data);
          setLoading(false);
        })
        .catch((err) => {
          console.error("Error fetching predictions:", err);
          setLoading(false);
        });
    }
  };

  // Function to calculate match outcome probabilities based on confidence scores
  const calculateOdds = (match) => {
    // Determine if the selected team is home or away
    const isHomeTeam = match.home_team_id === parseInt(selectedTeam);
    
    // Use confidence values from backend
    const confidence = match.confidence || 0.5; // Default to 0.5 if not provided
    
    // Calculate odds based on predicted score
    const homeGoals = match.predicted_home_goals;
    const awayGoals = match.predicted_away_goals;
    
    let homeWinProb, drawProb, awayWinProb;
    
    if (homeGoals > awayGoals) {
      // Home team predicted to win
      homeWinProb = 0.6 + (confidence * 0.2); // Base 60% + up to 20% from confidence
      drawProb = 0.3 - (confidence * 0.1); // Base 30% - up to 10% from confidence
      awayWinProb = 0.1 - (confidence * 0.05) + 0.05; // Remainder with minimum 5%
    } else if (homeGoals < awayGoals) {
      // Away team predicted to win
      awayWinProb = 0.6 + (confidence * 0.2); // Base 60% + up to 20% from confidence
      drawProb = 0.3 - (confidence * 0.1); // Base 30% - up to 10% from confidence
      homeWinProb = 0.1 - (confidence * 0.05) + 0.05; // Remainder with minimum 5%
    } else {
      // Draw predicted - higher probability when scores are equal
      drawProb = 0.7; // 70% probability for draw when scores are equal
      homeWinProb = 0.15; // Equal distribution for home/away wins
      awayWinProb = 0.15;
    }
    
    // Ensure probabilities sum to 100%
    const total = homeWinProb + drawProb + awayWinProb;
    homeWinProb = homeWinProb / total;
    drawProb = drawProb / total;
    awayWinProb = awayWinProb / total;
    
    // Return probabilities as percentages and actual decimal values for width calculation
    return [
      { 
        type: "home", 
        label: "Home Win",
        percent: Math.round(homeWinProb * 100),
        decimal: homeWinProb,
        color: "#9ACD32" // Light green
      },
      { 
        type: "draw", 
        label: "Draw",
        percent: Math.round(drawProb * 100),
        decimal: drawProb,
        color: "#FFD700" // Gold
      },
      { 
        type: "away", 
        label: "Away Win",
        percent: Math.round(awayWinProb * 100),
        decimal: awayWinProb,
        color: "#FF6347" // Tomato red
      }
    ];
  };

  return (
    <div className="score-prediction-page">
      <div className="selectors">
        <div className="handle-league-select">
          <select 
            value={selectedLeague || ""} 
            onChange={(e) => handleLeagueSelect(e.target.value)}
          >
            <option value="">Select League</option>
            {leagues.map((league) => (
              <option key={league.league_id} value={league.league_id}>
                {league.league_name}
              </option>
            ))}
          </select>
          <img 
            src={selectedLeagueLogo || defaultLeagueLogo} 
            alt="League Logo" 
            onError={(e) => e.target.src = defaultLeagueLogo}
          />
        </div>
        
        <div className="handle-team-select">
          <select 
            value={selectedTeam || ""} 
            onChange={(e) => handleTeamSelect(e.target.value)} 
            disabled={!selectedLeague}
          >
            <option value="">Select Team</option>
            {teams.map((team) => (
              <option key={team.team_id} value={team.team_id}>
                {team.team_name}
              </option>
            ))}
          </select>
          <img 
            src={selectedTeamLogo || defaultTeamLogo} 
            alt="Team Logo" 
            onError={(e) => e.target.src = defaultTeamLogo}
          />
        </div>
        
        <div className="score-prediction-icon">
          <img src={scorePredictionIcon} alt="Score Prediction Icon" className="icon-image" />
        </div>
      </div>

      {/* Fixture & Predictions Header */}
      <div className="predictions-header">
        <h1>Fixture & Predictions</h1>
      </div>

      {/* Predictions Container */}
      {loading ? (
        <div className="loading">Loading predictions...</div>
      ) : predictions.length > 0 ? (
        <div className="predictions-container">
          {predictions.slice(0, 4).map((match) => {
            const odds = calculateOdds(match);
            
            return (
              <div key={match.match_id} className="match-prediction-card">
                <div className="week-label">
                  <img 
                    src={match.league_logo || defaultLeagueLogo} 
                    alt="League Logo" 
                    className="league-logo-small"
                    onError={(e) => e.target.src = defaultLeagueLogo}
                  />
                  <span>{match.week}</span>
                </div>
                
                <div className="match-content">
                  {/* Left Player */}
                  <div className="player-container">
                    <img 
                      src={match.home_footballer_img_path || defaultPlayerImage} 
                      alt="Home Player" 
                      className="player-image"
                      onError={(e) => e.target.src = defaultPlayerImage}
                    />
                  </div>
                  
                  {/* Match Score */}
                  <div className="match-score">
                    <div className="team-logos">
                      <img 
                        src={match.home_team_logo || defaultTeamLogo} 
                        alt={match.home_team_name} 
                        className="team-logo"
                        onError={(e) => e.target.src = defaultTeamLogo}
                      />
                    </div>
                    <div className="predicted-score">
                      {match.predicted_home_goals}-{match.predicted_away_goals}
                    </div>
                    <div className="team-logos">
                      <img 
                        src={match.away_team_logo || defaultTeamLogo} 
                        alt={match.away_team_name} 
                        className="team-logo"
                        onError={(e) => e.target.src = defaultTeamLogo}
                      />
                    </div>
                  </div>
                  
                  {/* Right Player */}
                  <div className="player-container">
                    <img 
                      src={match.away_footballer_img_path || defaultPlayerImage} 
                      alt="Away Player" 
                      className="player-image"
                      onError={(e) => e.target.src = defaultPlayerImage}
                    />
                  </div>
                </div>
                
                {/* Combined Betting Odds Bar */}
                <div className="combined-odds-container">
                  <div className="combined-odds-bar">
                    {odds.map((odd, index) => (
                      <div 
                        key={odd.type} 
                        className="odds-segment"
                        style={{ 
                          width: `${odd.percent}%`, 
                          backgroundColor: odd.color 
                        }}
                      >
                        <span className="odds-label">{odd.label}</span>
                        <span className="odds-percent">{odd.percent}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="no-predictions">No predictions available for the selected team.</div>
      )}
    </div>
  );
};

export default ScorePredictionPage;