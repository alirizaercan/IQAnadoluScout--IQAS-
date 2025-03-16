import React, { useState, useEffect } from "react";
import {
  getMarketValueRange,
  getPlayersByBudget,
  getFilteredPlayers,
  getPlayerDetails,
  getAllLeagues,
  getTeamsByLeague,
  getTeamById,
  getTeamPlayers
} from "../services/transfer_api";
import "../styles/TransferStrategyPage.css";

const TransferStrategyPage = () => {
  const [teams, setTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedTeamLogo, setSelectedTeamLogo] = useState(null);
  const [criticalPositions, setCriticalPositions] = useState([]);
  const [selectedPosition, setSelectedPosition] = useState(null);
  const [recommendedPlayers, setRecommendedPlayers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [budget, setBudget] = useState(0);
  const [filteredPlayers, setFilteredPlayers] = useState([]);
  const [selectedPlayers, setSelectedPlayers] = useState([]);
  const [compareMode, setCompareMode] = useState(false);
  const [comparisonResults, setComparisonResults] = useState(null);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedPlayerInfo, setSelectedPlayerInfo] = useState(null);
  const [showPlayerInfoModal, setShowPlayerInfoModal] = useState(false);
  const [filters, setFilters] = useState({
    minRating: 0,
    maxRating: 100,
    minPotential: 0,
    maxPotential: 100,
    minAge: 15,
    maxAge: 45,
    position: '',
    league_id: '',
    team_id: ''
  });
  
  // Fetch all teams on component mount
  useEffect(() => {
    const getTeams = async () => {
      setLoading(true);
      try {
        const leaguesData = await getAllLeagues();
        let allTeams = [];
        
        for (const league of leaguesData) {
          try {
            const teamsFromLeague = await getTeamsByLeague(league.league_id);
            if (teamsFromLeague && Array.isArray(teamsFromLeague)) {
              allTeams = [...allTeams, ...teamsFromLeague];
            }
          } catch (err) {
            console.error(`Error fetching teams for league ${league.league_id}:`, err);
            // Continue with other leagues even if one fails
          }
        }
        
        setTeams(allTeams);
      } catch (error) {
        console.error("Error fetching leagues:", error);
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
          const teamData = await getTeamById(selectedTeam);
          if (teamData && teamData.img_path) setSelectedTeamLogo(teamData.img_path);
          const positionsData = await getTeamPlayers(selectedTeam);
          if (positionsData && positionsData.length > 0) {
            setCriticalPositions(positionsData);
            setSelectedPosition(positionsData[0].position);
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
      setCriticalPositions([]);
      setSelectedPosition(null);
      setRecommendedPlayers([]);
      setSelectedTeamLogo(null);
    }
  }, [selectedTeam]);

  // Fetch players by budget when budget changes
  useEffect(() => {
    if (budget) {
      const fetchPlayersByBudget = async () => {
        setLoading(true);
        try {
          // Bütçeyi doğru formata çeviriyoruz
          const budgetValue = parseInt(budget, 10);
          
          // Yükleme sırasında gösterge
          setRecommendedPlayers([]);
          setFilteredPlayers([]);
          
          // Yüksek limit ile tüm oyuncuları çekiyoruz (500 yerine 1000)
          const playersData = await getPlayersByBudget(budgetValue, 1000);
          
          if (!playersData || !Array.isArray(playersData)) {
            console.error("Invalid player data received:", playersData);
            setRecommendedPlayers([]);
            setFilteredPlayers([]);
            setTotalPages(0);
            return;
          }
          
          // Tüm oyuncular için market değerlerini doğru şekilde parse ediyoruz
          const allPlayers = playersData.map(player => {
            // Market değerini doğru formatta çeviriyoruz
            let marketValue = player.market_value;
            if (typeof marketValue === 'string') {
              // Sayısal olmayan karakterleri kaldırıyoruz
              marketValue = parseFloat(marketValue.replace(/[^0-9.]/g, '')) || 0;
            } else if (typeof marketValue === 'number') {
              marketValue = marketValue;
            } else {
              marketValue = 0;
            }
            
            // Oyuncuyu güncellenmiş market değeriyle döndürüyoruz
            return {
              ...player,
              parsed_market_value: marketValue
            };
          });
          
          // Bütçeye göre filtreliyoruz - <= kullanarak bütçeden düşük veya eşit olanları alıyoruz
          const filteredByBudget = allPlayers.filter(player => {
            return player.parsed_market_value <= budgetValue;
          });
          
          console.log(`Found ${filteredByBudget.length} players within budget ${budgetValue}`);
          
          // Tüm ligler için filtrelenmiş oyuncuları gösteriyoruz
          setRecommendedPlayers(filteredByBudget);
          setFilteredPlayers(filteredByBudget);
          setTotalPages(Math.ceil(filteredByBudget.length / 8));
          setCurrentPage(1);
        } catch (error) {
          console.error("Error fetching players by budget:", error);
          setRecommendedPlayers([]);
          setFilteredPlayers([]);
        } finally {
          setLoading(false);
        }
      };
      
      // API çağrısı için kısa bir gecikme ekleyerek kullanıcının veri girerken sürekli 
      // API çağrısı yapılmasını önlüyoruz
      const timeoutId = setTimeout(() => {
        fetchPlayersByBudget();
      }, 800); // 800ms bekle
      
      return () => clearTimeout(timeoutId); // Temizlik fonksiyonu
    } else {
      // Bütçe temizlendiğinde oyuncuları da temizliyoruz
      setRecommendedPlayers([]);
      setFilteredPlayers([]);
    }
  }, [budget]);

  // Apply filters to recommended players
  useEffect(() => {
    if (recommendedPlayers.length === 0) return;
    
    let filtered = [...recommendedPlayers];
    filtered = filtered.filter(player => {
      // Ensure all values are properly converted to numbers for comparison
      const playerRating = parseFloat(player.rating) || 0;
      const playerPotential = parseFloat(player.potential) || 0;
      const playerAge = parseFloat(player.age) || 0;
      
      // Handle position which might be stored in different formats
      const playerPositions = player.position_acronym 
        ? player.position_acronym.split(',').map(p => p.trim()) 
        : [];
      
      // Extract nationality from image path if available
      const playerNationality = player.nationality_img_path 
        ? player.nationality_img_path.split('/').pop().split('.')[0] 
        : '';
  
      return (
        playerRating >= filters.minRating &&
        playerRating <= filters.maxRating &&
        playerPotential >= filters.minPotential &&
        playerPotential <= filters.maxPotential &&
        playerAge >= filters.minAge &&
        playerAge <= filters.maxAge &&
        (!filters.position || playerPositions.includes(filters.position)) &&
        (!filters.league_id || player.league_id === filters.league_id) &&
        (!filters.team_id || player.team_id === filters.team_id) &&
        (!filters.nationality || playerNationality.toLowerCase() === filters.nationality.toLowerCase())
      );
    });
    
    setFilteredPlayers(filtered);
    setTotalPages(Math.ceil(filtered.length / 8));
    setCurrentPage(1);
  }, [recommendedPlayers, filters]);

  const handleTeamChange = (e) => setSelectedTeam(e.target.value);
  const handlePositionChange = (position) => setSelectedPosition(position);
  
  const handlePageChange = (page) => {
    // Make sure we don't go beyond valid pages
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };
  
  const handleBudgetChange = (e) => {
    const value = e.target.value;
    setBudget(value);
  };
  
  const togglePlayerSelection = (playerId) => {
    if (selectedPlayers.includes(playerId)) {
      setSelectedPlayers(selectedPlayers.filter(id => id !== playerId));
    } else {
      if (selectedPlayers.length < 3) {
        setSelectedPlayers([...selectedPlayers, playerId]);
      }
    }
  };
  
  const toggleFilterPanel = () => setShowFilters(!showFilters);
  
  const togglePlayerInfoModal = (player) => {
    setSelectedPlayerInfo(player);
    setShowPlayerInfoModal(!showPlayerInfoModal);
  };
  
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
      maxAge: 45,
      position: '',
      league_id: '',
      team_id: ''
    });
  };
  
  const applyFilters = () => {
    setShowFilters(false);
  };
  
  const handleCompareClick = async () => {
    if (selectedPlayers.length < 2) {
      alert("Please select at least 2 players to compare");
      return;
    }
    setLoading(true);
    try {
      const playerPromises = selectedPlayers.map(id => getPlayerDetails(id));
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
    if (totalPages <= 1) return null;
    
    // Limit the number of dots to display to avoid overflow
    const maxDotsToShow = 5;
    let startPage = 1;
    let endPage = totalPages;
    
    if (totalPages > maxDotsToShow) {
      // Calculate start and end page for pagination dots
      const halfWay = Math.floor(maxDotsToShow / 2);
      
      if (currentPage <= halfWay) {
        endPage = maxDotsToShow;
      } else if (currentPage >= totalPages - halfWay) {
        startPage = totalPages - maxDotsToShow + 1;
      } else {
        startPage = currentPage - halfWay;
        endPage = currentPage + halfWay;
      }
    }
    
    return (
      <div className="pagination-dots-transfer">
        {/* Add first page and previous indicator if needed */}
        {startPage > 1 && (
          <>
            <span
              className={`pagination-dot-transfer ${currentPage === 1 ? 'active' : ''}`}
              onClick={() => handlePageChange(1)}
            ></span>
            {startPage > 2 && <span className="pagination-ellipsis">...</span>}
          </>
        )}
        
        {/* Generate dots for the current view */}
        {Array.from({ length: endPage - startPage + 1 }).map((_, index) => {
          const pageNum = startPage + index;
          return (
            <span
              key={pageNum}
              className={`pagination-dot-transfer ${currentPage === pageNum ? 'active' : ''}`}
              onClick={() => handlePageChange(pageNum)}
            ></span>
          );
        })}
        
        {/* Add next and last page indicator if needed */}
        {endPage < totalPages && (
          <>
            {endPage < totalPages - 1 && <span className="pagination-ellipsis">...</span>}
            <span
              className={`pagination-dot-transfer ${currentPage === totalPages ? 'active' : ''}`}
              onClick={() => handlePageChange(totalPages)}
            ></span>
          </>
        )}
      </div>
    );
  };
  
  const renderFilterPanel = () => {
    if (!showFilters) return null;
    
    // Define positions from the mapping provided
    const positions = [
      { value: '', label: 'All Positions' },
      { value: 'GK', label: 'Goalkeeper (GK)' },
      { value: 'CB', label: 'Centre-Back (CB)' },
      { value: 'LB', label: 'Left-Back (LB)' },
      { value: 'RB', label: 'Right-Back (RB)' },
      { value: 'DM', label: 'Defensive Midfield (DM)' },
      { value: 'CM', label: 'Central Midfield (CM)' },
      { value: 'LW', label: 'Left Winger (LW)' },
      { value: 'RW', label: 'Right Winger (RW)' },
      { value: 'SS', label: 'Second Striker (SS)' },
      { value: 'CF', label: 'Centre-Forward (CF)' },
      { value: 'AM', label: 'Attacking Midfield (AM)' },
      { value: 'LM', label: 'Left Midfield (LM)' },
      { value: 'RM', label: 'Right Midfield (RM)' },
      { value: 'MID', label: 'Midfielder (MID)' },
      { value: 'DEF', label: 'Defender (DEF)' },
      { value: 'ST', label: 'Striker (ST)' }
    ];
    
    return (
      <div className="filter-panel-transfer">
        <div className="filter-header-transfer">
          <h3>Filter Players</h3>
          <button className="close-filter-button-transfer" onClick={toggleFilterPanel}>×</button>
        </div>
        
        {/* Add Position Filter */}
        <div className="filter-section-transfer">
          <h4>Position</h4>
          <div className="filter-select-transfer">
            <select 
              value={filters.position}
              onChange={(e) => handleFilterChange('position', e.target.value)}
              className="position-select"
            >
              {positions.map(pos => (
                <option key={pos.value} value={pos.value}>
                  {pos.label}
                </option>
              ))}
            </select>
          </div>
        </div>
        
        <div className="filter-section-transfer">
          <h4>Rating</h4>
          <div className="filter-range-transfer">
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
        
        <div className="filter-section-transfer">
          <h4>Potential</h4>
          <div className="filter-range-transfer">
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
        
        <div className="filter-section-transfer">
          <h4>Age</h4>
          <div className="filter-range-transfer">
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
        
        <div className="filter-actions-transfer">
          <button className="reset-button-transfer" onClick={resetFilters}>Reset</button>
          <button className="apply-button-transfer" onClick={applyFilters}>Apply</button>
        </div>
      </div>
    );
  };
  
  const renderPlayerCards = () => {
    // Check if we have filtered players
    if (filteredPlayers.length === 0) {
      return (
        <div className="no-players-transfer">
          No players match your criteria. Try adjusting your filters or budget.
        </div>
      );
    }
    
    // Calculate start and end indices for the current page
    const startIndex = (currentPage - 1) * 8;
    const endIndex = Math.min(startIndex + 8, filteredPlayers.length);
    
    // Get the players for the current page
    const currentPlayers = filteredPlayers.slice(startIndex, endIndex);
    
    // If no players for current page but we have filtered players, we might be on an invalid page
    if (currentPlayers.length === 0 && filteredPlayers.length > 0) {
      // Automatically adjust to the last valid page
      const lastValidPage = Math.ceil(filteredPlayers.length / 8);
      if (currentPage !== lastValidPage) {
        setCurrentPage(lastValidPage);
        return null; // Return null to avoid rendering invalid data
      }
    }
    
    return currentPlayers.map(player => (
      <div
        key={player.player_id}
        className={`player-card-transfer ${selectedPlayers.includes(player.player_id) ? 'selected' : ''}`}
        onClick={() => togglePlayerSelection(player.player_id)}
      >
        <div className="card-header-transfer">
          <div className="league-logo-transfer">
            {player.league_logo_path && (
              <img src={player.league_logo_path} alt="League Logo" />
            )}
          </div>
          <div className="team-badge-transfer">
            {player.team_img_path && (
              <img src={player.team_img_path} alt="Team Badge" />
            )}
          </div>
        </div>
        <div className="player-image-transfer">
          {player.footballer_img_path && (
            <img src={player.footballer_img_path} alt={player.footballer_name} />
          )}
        </div>
        <h3 className="player-name-transfer">{player.footballer_name}</h3>
        <div className="position-acronym-transfer">
          {player.position_acronym}
        </div>
        <div className="player-details-transfer">
          <div className="detail-item-transfer">
            <span className="detail-icon-transfer doc"></span>
            <div className="nationality-transfer">
              {player.nationality_img_path && (
                <img src={player.nationality_img_path} alt="Country" />
              )}
            </div>
          </div>
          <div className="detail-item-transfer">
            <span className="detail-icon-transfer calendar"></span>
            <span>{player.birthday || "N/A"}</span>
          </div>
          <div className="detail-item-transfer">
            <span 
              className="detail-icon-transfer info"
              onClick={(e) => {
                e.stopPropagation(); // Prevent triggering parent onClick
                togglePlayerInfoModal(player);
              }}
            ></span>
          </div>
        </div>
        <div className="value-grid">
          <div className="value-row">
            <span className="value-name">Market Value: </span>
            <span className="market-value">
              {player.market_value ? 
                `€${player.market_value >= 1000000 ? 
                  `${(player.market_value / 1000000).toFixed(1)}M` : 
                  `${(player.market_value / 1000).toFixed(1)}k`
                }` 
                : "N/A"
              }
            </span>
          </div>
          {player.score && (
            <div className="attribute-row-transfer score-row">
              <span className="attribute-name-transfer">Match Score: </span>
              <span className="attribute-value-transfer score">{Math.round(player.score)}%</span>
            </div>
          )}
        </div>
      </div>
    ));
  };
  
  // Player Info Modal Component - Dış scope'a taşındı
  const PlayerInfoModal = ({ player, onClose }) => {
    if (!player) return null;
    
    return (
      <div className="transfer-info-detail-overlay" onClick={onClose}>
        <div className="transfer-info-detail-modal" onClick={(e) => e.stopPropagation()}>
          <div className="transfer-info-detail-card">
            <div className="card-header-transfer-info">
              <div className="league-logo-transfer-info">
                {player.league_logo_path && (
                  <img src={player.league_logo_path} alt="League Logo" />
                )}
              </div>
              <div className="team-badge-transfer-info">
                {player.team_img_path && (
                  <img src={player.team_img_path} alt="Team Badge" />
                )}
              </div>
            </div>
            <div className="player-image-transfer-info">
              {player.footballer_img_path && (
                <img src={player.footballer_img_path} alt={player.footballer_name} />
              )}
            </div>
            <h3 className="player-name-transfer-info">{player.footballer_name}</h3>
            <div className="position-acronym-transfer-info">
              {player.position_acronym}
            </div>
            <div className="player-details-transfer-info">
              <div className="detail-item-transfer-info">
                <span className="detail-icon-transfer-info doc"></span>
                <div className="nationality-transfer-info">
                  {player.nationality_img_path && (
                    <img src={player.nationality_img_path} alt="Country" />
                  )}
                </div>
              </div>
              <div className="detail-item-transfer-info">
                <span className="detail-icon-transfer-info calendar"></span>
                <span>{player.birthday || "N/A"}</span>
              </div>
            </div>
            <h4 className="attributes-title-transfer-info">Attributes</h4>
            <div className="attributes-grid-transfer-info">
              <div className="attribute-row-transfer-info">
                <span className="attribute-name-transfer-info">Rating</span>
                <span className="attribute-value-transfer-info">{player.rating || "N/A"}</span>
                <span className="attribute-name-transfer-info">Potential</span>
                <span className="attribute-value-transfer-info">{player.potential || "N/A"}</span>
                <span className="attribute-name-transfer-info">Positioning</span>
                <span className="attribute-value-transfer-info">{player.positioning || "N/A"}</span>
                <span className="attribute-name-transfer-info">Acceleration</span>
                <span className="attribute-value-transfer-info">{player.acceleration || "N/A"}</span>
                <span className="attribute-name-transfer-info">Passing</span>
                <span className="attribute-value-transfer-info">{player.passing || "N/A"}</span>
                <span className="attribute-name-transfer-info">Long Shots</span>
                <span className="attribute-value-transfer-info">{player.long_shots || "N/A"}</span>
                <span className="attribute-name-transfer-info">Marking</span>
                <span className="attribute-value-transfer-info">{player.marking || "N/A"}</span>
                <span className="attribute-name-transfer-info">Decisions</span>
                <span className="attribute-value-transfer-info">{player.decisions || "N/A"}</span>  
                <span className="attribute-name-transfer-info">Finishing</span>
                <span className="attribute-value-transfer-info">{player.finishing || "N/A"}</span>
                <span className="attribute-name-transfer-info">Leadership</span>
                <span className="attribute-value-transfer-info">{player.leadership || "N/A"}</span>
                <span className="attribute-name-transfer-info">Dribbling</span>
                <span className="attribute-value-transfer-info">{player.dribbling || "N/A"}</span>
                <span className="attribute-name-transfer-info">Concentration</span>
                <span className="attribute-value-transfer-info">{player.concentration || "N/A"}</span>
                <span className="attribute-name-transfer-info">Fitness</span>
                <span className="attribute-value-transfer-info">{player.fitness || "N/A"}</span>
                <span className="attribute-name-transfer-info">Tackling</span>
                <span className="attribute-value-transfer-info">{player.tackling || "N/A"}</span>
                <span className="attribute-name-transfer-info">Stamina</span>
                <span className="attribute-value-transfer-info">{player.stamina || "N/A"}</span>
                <span className="attribute-name-transfer-info">Jumping</span>
                <span className="attribute-value-transfer-info">{player.jumping || "N/A"}</span>
                <span className="attribute-name-transfer-info">Heading</span>
                <span className="attribute-value-transfer-info">{player.heading || "N/A"}</span>
                <span className="attribute-name-transfer-info">Balance</span>
                <span className="attribute-value-transfer-info">{player.balance || "N/A"}</span>
              </div>
              {player.score && (
                <div className="attribute-row-transfer-info score-row-transfer-info">
                  <span className="attribute-name-transfer-info">Match Score</span>
                  <span className="attribute-value-transfer-info score-transfer-info">{Math.round(player.score)}%</span>
                </div>
              )}
            </div>
            <button className="close-button-transfer-info" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    );
  };
  
  const renderComparisonView = () => {
    if (!comparisonResults || comparisonResults.length === 0) return null;
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
    const playerColors = ['#4285F4', '#EA4335', '#FBBC05'];
    return (
      <div className="comparison-container-transfer">
        <div className="comparison-header-transfer">
          <h2>Player Comparison</h2>
          <button className="close-button-transfer" onClick={exitCompareMode}>×</button>
        </div>
        <div className="comparison-content-transfer">
          <div className="comparison-players-transfer">
            {comparisonResults.map((player, index) => (
              <div key={player.player_id} className="comparison-player-transfer">
                <div className="player-image-transfer">
                  {player.footballer_img_path && (
                    <img src={player.footballer_img_path} alt={player.footballer_name} />
                  )}
                </div>
                <h3>{player.footballer_name}</h3>
                <div className="player-team-transfer">
                  {player.team_img_path && (
                    <img src={player.team_img_path} alt="Team" className="team-logo-small" />
                  )}
                  <span>{player.current_team_name || 'Unknown Team'}</span>
                </div>
                <div className="player-info-transfer">
                  <div className="info-item-transfer">
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
                <div
                  className="player-color-indicator"
                  style={{ backgroundColor: playerColors[index % playerColors.length] }}
                ></div>
              </div>
            ))}
          </div>
          <div className="comparison-stats">
            <h3>Attributes Comparison</h3>
            {numericAttributes.map(attr => {
              const values = comparisonResults.map(player => parseFloat(player[attr.key]) || 0);
              const maxValue = Math.max(...values);
              return (
                <div key={attr.key} className="comparison-stat-row">
                  <div className="stat-name">{attr.label}</div>
                  <div className="stat-bars">
                    {comparisonResults.map((player, index) => {
                      const value = parseFloat(player[attr.key]) || 0;
                      const percentage = maxValue > 0 ? (value / maxValue * 100) : 0;
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
            <div className="comparison-summary">
              <h3>Overall Comparison</h3>
              <div className="radar-chart-placeholder">
                <p>Radar chart visualization would be here</p>
              </div>
              <div className="player-strengths">
                {comparisonResults.map((player, playerIndex) => {
                  const strengths = numericAttributes.filter(attr => {
                    const playerValue = parseFloat(player[attr.key]) || 0;
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
                      <h4 style={{ color: playerColors[playerIndex % playerColors.length] }}>
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
    <div className="transfer-page">
      <div className="transfer-header">
        <div className="search-container-transfer">
          <div className="logo-container-transfer">
            <div className="transfer-logo"></div>
          </div>
          <input
            type="number"
            className="search-input-transfer"
            placeholder="Enter budget (€)..."
            value={budget}
            onChange={handleBudgetChange}
          />
          <button
            className={`filter-button-transfer ${showFilters ? 'active' : ''}`}
            onClick={toggleFilterPanel}
          >
            <div className="filter-icon-transfer"></div>
          </button>
        </div>
        <h1 className="section-transfer-title">Transfer Recommendations</h1>
        {selectedPlayers.length > 1 && (
          <button
            className="compare-button-transfer"
            onClick={handleCompareClick}
            disabled={loading}
          >
            Compare Players ({selectedPlayers.length})
          </button>
        )}
      </div>
      {renderFilterPanel()}
      {compareMode ? renderComparisonView() : (
        <div className="recommendation-section-transfer">
          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              <p>Loading recommendations...</p>
            </div>
          ) : (
            <>
              <div className="player-cards-container-transfer">
                {filteredPlayers.length > 0 ? (
                  renderPlayerCards()
                ) : (
                  <div className="no-players-transfer">
                    {budget ? "No players match your criteria. Try adjusting your budget or filters." :
                             "Enter a budget to see player recommendations."}
                  </div>
                )}
              </div>
              {filteredPlayers.length > 0 && renderDots()}
              {filteredPlayers.length > 0 && (
                <div className="recommendation-info-transfer">
                  <p>Showing {filteredPlayers.length} recommended players {selectedPosition ? `for ${selectedPosition} position` : ''}</p>
                  <p>Page {currentPage} of {totalPages}</p>
                  {selectedPlayers.length > 0 && (
                    <p>Select up to 3 players to compare their stats</p>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      )}
      {/* Aşağıdaki kod parçası eklendi - Modal bileşenini göstermek için */}
      {showPlayerInfoModal && (
        <PlayerInfoModal
          player={selectedPlayerInfo}
          onClose={() => setShowPlayerInfoModal(false)}
        />
      )}
    </div>
  );
};

export default TransferStrategyPage;