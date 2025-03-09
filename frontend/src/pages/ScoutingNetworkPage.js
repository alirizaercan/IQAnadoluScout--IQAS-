import React, { useState, useEffect } from "react";
import {
  fetchAllTeams,
  fetchCriticalPositions,
  fetchRecommendedPlayers,
  fetchPlayerById
} from "../services/scouting_api";
import "../styles/ScoutingNetworkPage.css";

const ScoutingNetworkPage = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedTeamLogo, setSelectedTeamLogo] = useState(null);
  const [criticalPositions, setCriticalPositions] = useState([]);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [recommendedPlayers, setRecommendedPlayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchQuery, setSearchQuery] = useState("");
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const [compareMode, setCompareMode] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);

  // Fetch all teams on component mount
  useEffect(() => {
    const getTeams = async () => {
      setLoading(true);
      try {
        const teamsData = await fetchAllTeams();
        setTeams(teamsData);
      } catch (error) {
        console.error("Error fetching teams:", error);
      } finally {
        setLoading(false);
      }
    };
    getTeams();
  }, []);

  // Fetch critical positions and team logo when a team is selected
  useEffect(() => {
    if (selectedTeam) {
      const getTeamData = async () => {
        setLoading(true);
        try {
          // Fetch team logo
          const teamData = teams.find(team => team.team_id === Number(selectedTeam));
          if (teamData && teamData.img_path) setSelectedTeamLogo(teamData.img_path);

          // Fetch critical positions
          const positionsData = await fetchCriticalPositions(selectedTeam);
          if (positionsData && positionsData.length > 0) {
            setCriticalPositions(positionsData);
            setSelectedPosition(positionsData[0].position); // Set first position as default
          } else {
            setCriticalPositions([]);
            setSelectedPosition(null);
            setRecommendedPlayers([]);
          }

          // Removed the problematic fetchTeamRecommendationSummary call
        } catch (error) {
          console.error("Error fetching team data:", error);
          setCriticalPositions([]);
          setSelectedPosition(null);
          setRecommendedPlayers([]);
        } finally {
          setLoading(false);
        }
      };
      getTeamData();
    } else {
      // Reset state if no team is selected
      setCriticalPositions([]);
      setSelectedPosition(null);
      setRecommendedPlayers([]);
      setSelectedTeamLogo(null);
    }
  }, [selectedTeam, teams]);

  // Fetch recommended players when selectedPosition changes
  useEffect(() => {
    if (selectedTeam && selectedPosition) {
      const getRecommendations = async () => {
        setLoading(true);
        try {
          const recommendations = await fetchRecommendedPlayers(selectedTeam, selectedPosition);
          if (recommendations && recommendations.length > 0) {
            setRecommendedPlayers(recommendations);
            setFilteredPlayers(recommendations);
            setTotalPages(Math.ceil(recommendations.length / 3));
            setCurrentPage(1); // Reset to first page
          } else {
            setRecommendedPlayers([]);
            setFilteredPlayers([]);
            setTotalPages(1);
          }
        } catch (error) {
          console.error("Error fetching player recommendations:", error);
          setRecommendedPlayers([]);
          setFilteredPlayers([]);
          setTotalPages(1);
        } finally {
          setLoading(false);
        }
      };
      getRecommendations();
    }
  }, [selectedTeam, selectedPosition]);

  // Filter players based on search query
  useEffect(() => {
    if (searchQuery.trim() === "") {
      setFilteredPlayers(recommendedPlayers);
      setTotalPages(Math.ceil(recommendedPlayers.length / 3));
    } else {
      const filtered = recommendedPlayers.filter(player => 
        player.footballer_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
      setFilteredPlayers(filtered);
      setTotalPages(Math.ceil(filtered.length / 3));
      setCurrentPage(1); // Reset to first page when search changes
    }
  }, [searchQuery, recommendedPlayers]);

  const handleTeamChange = (e) => setSelectedTeam(e.target.value);
  const handlePositionChange = (position) => setSelectedPosition(position);
  const handlePageChange = (page) => setCurrentPage(page);
  const handleSearchChange = (e) => setSearchQuery(e.target.value);

  const togglePlayerSelection = (playerId) => {
    if (selectedPlayers.includes(playerId)) {
      setSelectedPlayers(selectedPlayers.filter(id => id !== playerId));
    } else {
      if (selectedPlayers.length < 3) { // Limit to 3 players for comparison
        setSelectedPlayers([...selectedPlayers, playerId]);
      }
    }
  };

  const handleCompareClick = async () => {
    if (selectedPlayers.length < 2) {
      alert("Please select at least 2 players to compare");
      return;
    }

    setLoading(true);
    try {
      // Since comparePlayersByIds might not be available, we'll fetch each player individually
      const playerPromises = selectedPlayers.map(id => fetchPlayerById(id));
      const results = await Promise.all(playerPromises);
      
      setComparisonResults(results.filter(player => player !== null));
      setCompareMode(true);
    } catch (error) {
      console.error("Error comparing players:", error);
      alert("Failed to compare players");
    } finally {
      setLoading(false);
    }
  };

  const exitCompareMode = () => {
    setCompareMode(false);
    setComparisonResults(null);
    setSelectedPlayers([]);
  };

  const renderDots = () => {
    return (
      <div className="pagination-dots">
        {Array.from({ length: totalPages }).map((_, index) => (
          <span
            key={index}
            className={`pagination-dot ${currentPage === index + 1 ? 'active' : ''}`}
            onClick={() => handlePageChange(index + 1)}
          ></span>
        ))}
      </div>
    );
  };

  const renderPlayerCards = () => {
    return filteredPlayers
      .slice((currentPage - 1) * 3, currentPage * 3)
      .map(player => (
        <div 
          key={player.player_id} 
          className={`player-card ${selectedPlayers.includes(player.player_id) ? 'selected' : ''}`}
          onClick={() => togglePlayerSelection(player.player_id)}
        >
          <div className="card-header">
            <div className="sponsor-logo">trendarol<sup>TM</sup></div>
            <div className="team-badge">
              {player.current_team_logo && (
                <img src={player.current_team_logo} alt="Team Badge" />
              )}
            </div>
          </div>
          <div className="player-image">
            {player.footballer_img_path && (
              <img src={player.footballer_img_path} alt={player.footballer_name} />
            )}
          </div>
          <h3 className="player-name">{player.footballer_name}</h3>
          <div className="player-details">
            <div className="detail-item">
              <span className="detail-icon doc"></span>
              <div className="nationality">
                {player.nationality_img_path && (
                  <img src={player.nationality_img_path} alt="Country" />
                )}
              </div>
            </div>
            <div className="detail-item">
              <span className="detail-icon calendar"></span>
              <span>{player.birthday || "N/A"}</span>
            </div>
          </div>
          <h4 className="attributes-title">Attributes</h4>
          <div className="attributes-grid">
            <div className="attribute-row">
              <span className="attribute-name">Rating</span>
              <span className="attribute-value">{player.rating || "N/A"}</span>
              <span className="attribute-name">Potential</span>
              <span className="attribute-value">{player.potential || "N/A"}</span>
            </div>
            {player.score && (
              <div className="attribute-row score-row">
                <span className="attribute-name">Match Score</span>
                <span className="attribute-value score">{Math.round(player.score)}%</span>
              </div>
            )}
          </div>
        </div>
    ));
  };

  const renderComparisonView = () => {
    if (!comparisonResults || comparisonResults.length === 0) return null;
    
    return (
      <div className="comparison-container">
        <div className="comparison-header">
          <h2>Player Comparison</h2>
          <button className="close-button" onClick={exitCompareMode}>×</button>
        </div>
        <div className="comparison-content">
          <div className="comparison-players">
            {comparisonResults.map(player => (
              <div key={player.player_id} className="comparison-player">
                <div className="player-image">
                  {player.footballer_img_path && (
                    <img src={player.footballer_img_path} alt={player.footballer_name} />
                  )}
                </div>
                <h3>{player.footballer_name}</h3>
                <div className="player-team">
                  {player.current_team_logo && (
                    <img src={player.current_team_logo} alt="Team" className="team-logo-small" />
                  )}
                  <span>{player.current_team_name}</span>
                </div>
              </div>
            ))}
          </div>
          <div className="comparison-stats">
            {comparisonResults[0] && Object.keys(comparisonResults[0])
              .filter(key => 
                // Only show numeric attributes that aren't IDs
                typeof comparisonResults[0][key] === 'number' && 
                !key.includes('_id') && 
                key !== 'age'
              )
              .map(attribute => (
                <div key={attribute} className="comparison-stat-row">
                  <div className="stat-name">{attribute.replace('_', ' ')}</div>
                  <div className="stat-bars">
                    {comparisonResults.map(player => {
                      const maxValue = Math.max(...comparisonResults.map(p => p[attribute] || 0));
                      const percentage = maxValue > 0 ? (player[attribute] || 0) / maxValue * 100 : 0;
                      
                      return (
                        <div key={player.player_id} className="stat-bar-container">
                          <div 
                            className="stat-bar" 
                            style={{width: `${percentage}%`}}
                          ></div>
                          <span className="stat-value">{player[attribute] || 0}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              ))
            }
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="scouting-page">
      <div className="scouting-header">
        <div className="search-container">
          <div className="logo-container">
            <div className="magnifier-logo"></div>
          </div>
          <input 
            type="text" 
            className="search-input" 
            placeholder="Search player..." 
            value={searchQuery}
            onChange={handleSearchChange}
          />
          <button className="filter-button">
            <div className="filter-icon"></div>
          </button>
        </div>
        <h1 className="section-title">Scouting Recommendations</h1>
        {selectedPlayers.length > 1 && (
          <button 
            className="compare-button"
            onClick={handleCompareClick}
            disabled={loading}
          >
            Compare Players ({selectedPlayers.length})
          </button>
        )}
      </div>

      <div className="selection-section">
        <select 
          onChange={handleTeamChange} 
          value={selectedTeam || ""}
          disabled={loading}
        >
          <option value="">Select Team</option>
          {teams.map((team) => (
            <option key={team.team_id} value={team.team_id}>
              {team.team_name}
            </option>
          ))}
        </select>
      </div>

      {compareMode ? renderComparisonView() : (
        <div className="recommendation-section">
          <div className="team-card">
            {selectedTeamLogo && <img src={selectedTeamLogo} alt="Team Logo" className="team-logo" />}
            <div className="team-info">
              <h2>Recommendation</h2>
              <div className="position-tags">
                {criticalPositions.map(position => (
                  <span
                    key={position.position}
                    className={`position-tag ${selectedPosition === position.position ? 'active' : ''}`}
                    onClick={() => handlePositionChange(position.position)}
                  >
                    {position.position}
                    {position.priority && (
                      <span className="priority-indicator" title={`Priority: ${position.priority}`}>
                        {Array(position.priority).fill('!').join('')}
                      </span>
                    )}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading recommendations...</p>
            </div>
          ) : (
            <>
              <div className="player-cards-container">
                {filteredPlayers.length > 0 ? (
                  renderPlayerCards()
                ) : (
                  <div className="no-players">
                    {selectedPosition ? 
                      `No recommended players found for ${selectedPosition} position` : 
                      "Select a team to see recommendations"}
                  </div>
                )}
              </div>
              {filteredPlayers.length > 0 && renderDots()}
              {filteredPlayers.length > 0 && selectedPosition && (
                <div className="recommendation-info">
                  <p>Showing {filteredPlayers.length} recommended players for {selectedPosition} position</p>
                  {selectedPlayers.length > 0 && (
                    <p>Select up to 3 players to compare their stats</p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default ScoutingNetworkPage;