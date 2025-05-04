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
  
  // Basit filtre durumları
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    minRating: 0,
    maxRating: 100,
    minPotential: 0,
    maxPotential: 100,
    minAge: 15,
    maxAge: 45
  });

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

  // Filter players based on search query AND filter criteria
  useEffect(() => {
    if (recommendedPlayers.length === 0) return;
    
    let filtered = [...recommendedPlayers];
    
    // Apply search filter
    if (searchQuery.trim() !== "") {
      filtered = filtered.filter(player => 
        player.footballer_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // Apply filters
    filtered = filtered.filter(player => {
      // Değerleri alma ve sayısal olduğundan emin olma
      const playerRating = parseFloat(player.rating) || 0;
      const playerPotential = parseFloat(player.potential) || 0;
      const playerAge = parseFloat(player.age) || 25; // Default age if not provided
      
      // Filtreleri uygulama
      return (
        playerRating >= filters.minRating && 
        playerRating <= filters.maxRating &&
        playerPotential >= filters.minPotential && 
        playerPotential <= filters.maxPotential &&
        playerAge >= filters.minAge && 
        playerAge <= filters.maxAge
      );
    });
    
    setFilteredPlayers(filtered);
    setTotalPages(Math.ceil(filtered.length / 3));
    setCurrentPage(1); // Reset to first page when filters change
  }, [searchQuery, recommendedPlayers, filters]);

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

  const handleSearch = () => {
    console.log("Searching for:", searchQuery);
  };

  // Function to handle Enter key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  // Filtre panelini aç/kapat
  const toggleFilterPanel = () => {
    setShowFilters(!showFilters);
  };

  // Filter values güncelleme
  const handleFilterChange = (field, value) => {
    setFilters({
      ...filters,
      [field]: value
    });
  };

const resetFilters = () => {
  setFilters({
    minRating: 0,
    maxRating: 100,
    minPotential: 0,
    maxPotential: 100,
    minAge: 15,
    maxAge: 45
  });
};

  // Filtreleri uygula
  const applyFilters = () => {
    // Filtreler useEffect ile otomatik uygulanıyor
    setShowFilters(false);
  };

  const handleCompareClick = async () => {
    if (selectedPlayers.length < 2) {
      alert("Please select at least 2 players to compare");
      return;
    }
    setLoading(true);
    try {
      // Her oyuncuyu ayrı ayrı getir
      const playerPromises = selectedPlayers.map(id => fetchPlayerById(id));
      const results = await Promise.all(playerPromises);
      
      // Karşılaştırma sonuçlarını ayarla ve karşılaştırma moduna geç
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
    // Only render dots if we have pages to show
    if (totalPages <= 1) return null;
    
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

  const renderFilterPanel = () => {
    if (!showFilters) return null;
    
    return (
      <div className="filter-panel">
        <div className="filter-header">
          <h3>Filter Players</h3>
          <button className="close-filter-button" onClick={toggleFilterPanel}>×</button>
        </div>
        <div className="filter-section">
          <h4>Rating</h4>
          <div className="filter-range">
            <span>{filters.minRating}</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={filters.minRating} 
              onChange={(e) => handleFilterChange('minRating', parseInt(e.target.value))} 
            />
            <span>{filters.maxRating}</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={filters.maxRating} 
              onChange={(e) => handleFilterChange('maxRating', parseInt(e.target.value))} 
            />
          </div>
        </div>
        <div className="filter-section">
          <h4>Potential</h4>
          <div className="filter-range">
            <span>{filters.minPotential}</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={filters.minPotential} 
              onChange={(e) => handleFilterChange('minPotential', parseInt(e.target.value))} 
            />
            <span>{filters.maxPotential}</span>
            <input 
              type="range" 
              min="0" 
              max="100" 
              value={filters.maxPotential} 
              onChange={(e) => handleFilterChange('maxPotential', parseInt(e.target.value))} 
            />
          </div>
        </div>
        <div className="filter-section">
          <h4>Age</h4>
          <div className="filter-range">
            <span>{filters.minAge}</span>
            <input 
              type="range" 
              min="15" 
              max="45" 
              value={filters.minAge} 
              onChange={(e) => handleFilterChange('minAge', parseInt(e.target.value))} 
            />
            <span>{filters.maxAge}</span>
            <input 
              type="range" 
              min="15" 
              max="45" 
              value={filters.maxAge} 
              onChange={(e) => handleFilterChange('maxAge', parseInt(e.target.value))} 
            />
          </div>
        </div>
        <div className="filter-actions">
          <button className="reset-button" onClick={resetFilters}>Reset</button>
          <button className="apply-button" onClick={applyFilters}>Apply</button>
        </div>
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
            {/* League Logo in the top-left corner */}
            <div className="league-logo">
              {player.league_logo_path && (
                <img src={player.league_logo_path} alt="League Logo" />
              )}
            </div>
            {/* Team Logo in the top-right corner */}
            <div className="team-badge">
              {player.current_team_img && (
                <img src={player.current_team_img} alt="Team Badge" />
              )}
            </div>
          </div>
          <div className="player-image">
            {player.footballer_img_path && (
              <img src={player.footballer_img_path} alt={player.footballer_name} />
            )}
          </div>
          <h3 className="player-name">{player.footballer_name}</h3>
          {/* Position Acronym */}
          <div className="position-acronym">
            {player.position_acronym}
          </div>
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
              <span className="attribute-name">Positioning</span>
              <span className="attribute-value">{player.positioning || "N/A"}</span>
              <span className="attribute-name">Acceleration</span>
              <span className="attribute-value">{player.acceleration || "N/A"}</span>
              <span className="attribute-name">Passing</span>
              <span className="attribute-value">{player.passing || "N/A"}</span>
              <span className="attribute-name">Long Shots</span>
              <span className="attribute-value">{player.long_shots || "N/A"}</span>
              <span className="attribute-name">Marking</span>
              <span className="attribute-value">{player.marking || "N/A"}</span>
              <span className="attribute-name">Decisions</span>
              <span className="attribute-value">{player.decisions || "N/A"}</span>  
              <span className="attribute-name">Finishing</span>
              <span className="attribute-value">{player.finishing || "N/A"}</span>
              <span className="attribute-name">Leadership</span>
              <span className="attribute-value">{player.leadership || "N/A"}</span>
              <span className="attribute-name">Dribbling</span>
              <span className="attribute-value">{player.dribbling || "N/A"}</span>
              <span className="attribute-name">Concentration</span>
              <span className="attribute-value">{player.concentration || "N/A"}</span>
              <span className="attribute-name">Fitness</span>
              <span className="attribute-value">{player.fitness || "N/A"}</span>
              <span className="attribute-name">Tackling</span>
              <span className="attribute-value">{player.tackling || "N/A"}</span>
              <span className="attribute-name">Stamina</span>
              <span className="attribute-value">{player.stamina || "N/A"}</span>
              <span className="attribute-name">Jumping</span>
              <span className="attribute-value">{player.jumping || "N/A"}</span>
              <span className="attribute-name">Heading</span>
              <span className="attribute-value">{player.heading || "N/A"}</span>
              <span className="attribute-name">Balance</span>
              <span className="attribute-value">{player.balance || "N/A"}</span>
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

  // Karşılaştırma görünümünü iyileştirilmiş olarak render eder
  const renderComparisonView = () => {
    if (!comparisonResults || comparisonResults.length === 0) return null;
    
    // Karşılaştırılabilir sayısal nitelikleri belirle
    const numericAttributes = [
      { key: 'rating', label: 'Rating' },
      { key: 'potential', label: 'Potential' },
      { key: 'age', label: 'Age' },
      { key: 'positioning', label: 'Positioning' },
      { key: 'acceleration', label: 'Acceleration' },
      { key: 'passing', label: 'Passing' },
      { key: 'long_shots', label: 'Long Shots' },
      { key: 'marking', label: 'Marking' },
      { key: 'decisions', label: 'Decisions' },
      { key: 'finishing', label: 'Finishing' },
      { key: 'leadership', label: 'Leadership' },
      { key: 'dribbling', label: 'Dribbling' },
      { key: 'concentration', label: 'Concentration' },
      { key: 'fitness', label: 'Fitness' },
      { key: 'tackling', label: 'Tackling' },
      { key: 'stamina', label: 'Stamina' },
      { key: 'jumping', label: 'Jumping' },
      { key: 'heading', label: 'Heading' },
      { key: 'balance', label: 'Balance' }
    ];
    
    // Her oyuncu için rastgele renk ata (gerçek uygulamada sabit renk belirleyebilirsiniz)
    const playerColors = [
      '#4285F4', // Mavi
      '#EA4335', // Kırmızı
      '#FBBC05'  // Sarı
    ];
    
    return (
      <div className="comparison-container">
        <div className="comparison-header">
          <h2>Player Comparison</h2>
          <button className="close-button" onClick={exitCompareMode}>×</button>
        </div>
        
        <div className="comparison-content">
          {/* Oyuncu başlıkları ve temel bilgiler */}
          <div className="comparison-players">
            {comparisonResults.map((player, index) => (
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
                  <span>{player.current_team_name || 'Unknown Team'}</span>
                </div>
                <div className="player-info">
                  <div className="info-item">
                    <span className="info-label">Position:</span>
                    <span className="info-value">{player.position || selectedPosition || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Age:</span>
                    <span className="info-value">{player.age || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Rating:</span>
                    <span className="info-value">{player.rating || 'N/A'}</span>
                  </div>
                  <div className="info-item">
                    <span className="info-label">Potential:</span>
                    <span className="info-value">{player.potential || 'N/A'}</span>
                  </div>
                </div>
                {/* Oyuncu için renk göstergesi */}
                <div 
                  className="player-color-indicator" 
                  style={{backgroundColor: playerColors[index % playerColors.length]}}
                ></div>
              </div>
            ))}
          </div>
          
          {/* İstatistik karşılaştırmaları */}
          <div className="comparison-stats">
            <h3>Attributes Comparison</h3>
            
            {numericAttributes.map(attr => {
              // İlgili nitelik için en yüksek değeri bul
              const values = comparisonResults.map(player => 
                parseFloat(player[attr.key]) || 0
              );
              const maxValue = Math.max(...values);
              
              return (
                <div key={attr.key} className="comparison-stat-row">
                  <div className="stat-name">{attr.label}</div>
                  <div className="stat-bars">
                    {comparisonResults.map((player, index) => {
                      const value = parseFloat(player[attr.key]) || 0;
                      const percentage = maxValue > 0 ? (value / maxValue * 100) : 0;
                      
                      // En yüksek değer için vurgu
                      const isHighest = value === maxValue && maxValue > 0;
                      
                      return (
                        <div key={`${player.player_id}-${attr.key}`} className="stat-bar-container">
                          <div 
                            className={`stat-bar ${isHighest ? 'highest' : ''}`}
                            style={{
                              width: `${percentage}%`,
                              backgroundColor: playerColors[index % playerColors.length]
                            }}
                          ></div>
                          <span className="stat-value">{value}</span>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })}
            
            {/* Genel karşılaştırma özeti */}
            <div className="comparison-summary">
              <h3>Overall Comparison</h3>
              <div className="radar-chart-placeholder">
                {/* Gerçek uygulamada burada bir radar grafiği veya örümcek ağı grafiği olabilir */}
                <p>Radar chart visualization would be here</p>
              </div>
              
              {/* Her oyuncu için üstün olduğu özellikler */}
              <div className="player-strengths">
                {comparisonResults.map((player, playerIndex) => {
                  // Bu oyuncunun üstün olduğu nitelikleri bul
                  const strengths = numericAttributes.filter(attr => {
                    const playerValue = parseFloat(player[attr.key]) || 0;
                    // Diğer tüm oyuncuların değerlerini kontrol et
                    for (let i = 0; i < comparisonResults.length; i++) {
                      if (i !== playerIndex) {
                        const otherValue = parseFloat(comparisonResults[i][attr.key]) || 0;
                        if (otherValue >= playerValue) return false;
                      }
                    }
                    return true;
                  }).map(attr => attr.label);
                  
                  return (
                    <div key={player.player_id} className="player-strength">
                      <h4 style={{color: playerColors[playerIndex % playerColors.length]}}>
                        {player.footballer_name}'s Strengths
                      </h4>
                      {strengths.length > 0 ? (
                        <ul>
                          {strengths.map(strength => (
                            <li key={strength}>{strength}</li>
                          ))}
                        </ul>
                      ) : (
                        <p>No outstanding attributes compared to others</p>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
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
            onKeyPress={handleKeyPress}
          />
          <button className="search-button" onClick={handleSearch}>
            <div className="search-icon"></div>
          </button>
          <button 
            className={`filter-button ${showFilters ? 'active' : ''}`} 
            onClick={toggleFilterPanel}
          >
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
      
      {/* Basit filtre paneli */}
      {renderFilterPanel()}
      
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
      
      {/* Ana içerik: normal mod veya karşılaştırma modu */}
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