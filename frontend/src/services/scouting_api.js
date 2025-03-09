/* frontend/src/services/scouting_api.js */
const API_BASE_URL = "http://localhost:5000/api/scouting";

// Fetch all leagues
export const fetchAllLeagues = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/leagues`);
    if (!response.ok) throw new Error("Failed to fetch leagues");
    return await response.json();
  } catch (error) {
    console.error("Error fetching leagues:", error);
    return [];
  }
};

// Fetch all teams
export const fetchAllTeams = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams`);
    if (!response.ok) throw new Error("Failed to fetch teams");
    return await response.json();
  } catch (error) {
    console.error("Error fetching teams:", error);
    return [];
  }
};

// Fetch teams by league
export const fetchTeamsByLeague = async (leagueId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams/league/${leagueId}`);
    if (!response.ok) throw new Error(`Failed to fetch teams for league: ${leagueId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching teams by league:", error);
    return [];
  }
};

// Fetch footballers by team
export const fetchFootballersByTeam = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/footballers/team/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch footballers for team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching footballers:", error);
    return [];
  }
};

// Fetch player details
export const fetchPlayerById = async (playerId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/player/${playerId}`);
    if (!response.ok) throw new Error(`Failed to fetch player: ${playerId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching player details:", error);
    return null;
  }
};

// Fetch players by footballer ID
export const fetchPlayersByFootballerId = async (footballerId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/players/footballer/${footballerId}`);
    if (!response.ok) throw new Error(`Failed to fetch players for footballer: ${footballerId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching players by footballer:", error);
    return [];
  }
};

// Fetch team position distribution
export const fetchTeamPositions = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/positions/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch positions for team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching team positions:", error);
    return [];
  }
};

// Fetch critical positions for a team
export const fetchCriticalPositions = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/critical-positions/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch critical positions for team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching critical positions:", error);
    return [];
  }
};

// Fetch recommended players for a specific position
export const fetchRecommendedPlayers = async (teamId, position) => {
  try {
    const response = await fetch(`${API_BASE_URL}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ team_id: teamId, position }),
    });
    if (!response.ok) throw new Error("Failed to fetch player recommendations");
    return await response.json();
  } catch (error) {
    console.error("Error fetching player recommendations:", error);
    return [];
  }
};

// Fetch recommended players based on team needs
export const fetchRecommendationsByTeamNeeds = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/needs/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch recommendations for team needs: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching recommendations by team needs:", error);
    return [];
  }
};

// Fetch team recommendation summary
export const fetchTeamRecommendationSummary = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/recommendation-summary/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch recommendation summary for team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching team recommendation summary:", error);
    return null;
  }
};

// Calculate player score for a position
export const calculatePlayerScore = async (playerData, position) => {
  try {
    const response = await fetch(`${API_BASE_URL}/player/calculate-score`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_data: playerData, position }),
    });
    if (!response.ok) throw new Error("Failed to calculate player score");
    return await response.json();
  } catch (error) {
    console.error("Error calculating player score:", error);
    return { score: 0 };
  }
};

// Fetch position mapping
export const fetchPositionMapping = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/position-mapping`);
    if (!response.ok) throw new Error("Failed to fetch position mapping");
    return await response.json();
  } catch (error) {
    console.error("Error fetching position mapping:", error);
    return {};
  }
};

// Fetch ideal position distribution
export const fetchIdealDistribution = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/ideal-distribution`);
    if (!response.ok) throw new Error("Failed to fetch ideal position distribution");
    return await response.json();
  } catch (error) {
    console.error("Error fetching ideal distribution:", error);
    return {};
  }
};

// Fetch position features
export const fetchPositionFeatures = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/position-features`);
    if (!response.ok) throw new Error("Failed to fetch position features");
    return await response.json();
  } catch (error) {
    console.error("Error fetching position features:", error);
    return {};
  }
};

// Compare multiple players
export const comparePlayersByIds = async (playerIds) => {
  try {
    const response = await fetch(`${API_BASE_URL}/compare-players`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ player_ids: playerIds }),
    });
    if (!response.ok) throw new Error("Failed to compare players");
    return await response.json();
  } catch (error) {
    console.error("Error comparing players:", error);
    return [];
  }
};

// Fetch a complete scouting report for a team
export const fetchScoutingReport = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/scouting-report/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch scouting report for team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching scouting report:", error);
    return null;
  }
};