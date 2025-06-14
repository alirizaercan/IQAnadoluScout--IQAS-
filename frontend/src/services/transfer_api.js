/* frontend/src/services/transfer_api.js */
const API_BASE_URL = "http://localhost:5056/api/transfer";

// Get market value range
export const getMarketValueRange = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/market-value-range`);
    if (!response.ok) throw new Error("Failed to fetch market value range");
    return await response.json();
  } catch (error) {
    console.error("Error fetching market value range:", error);
    return { min: 0, max: 0 };
  }
};

// Get players by budget
export const getPlayersByBudget = async (budget, limit = 200, league_id = null) => {
  try {
    let url = new URL(`${API_BASE_URL}/players-by-budget`);
    url.searchParams.append("budget", budget);
    url.searchParams.append("limit", limit);
    if (league_id) {
      url.searchParams.append("league_id", league_id);
    }
    
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch players by budget");
    return await response.json();
  } catch (error) {
    console.error("Error fetching players by budget:", error);
    return [];
  }
};

// Get filtered players
export const getFilteredPlayers = async (params) => {
  try {
    const { budget, position, league_id, min_age, max_age, min_rating, limit = 200 } = params;
    let url = new URL(`${API_BASE_URL}/filtered-players`);
    
    // Sadece belirtilen parametreleri ekleyin
    if (budget) url.searchParams.append("budget", budget);
    if (position) url.searchParams.append("position", position);
    if (league_id) url.searchParams.append("league_id", league_id); // Opsiyonel
    if (min_age) url.searchParams.append("min_age", min_age);
    if (max_age) url.searchParams.append("max_age", max_age);
    if (min_rating) url.searchParams.append("min_rating", min_rating);
    url.searchParams.append("limit", limit);
    
    const response = await fetch(url);
    if (!response.ok) throw new Error("Failed to fetch filtered players");
    return await response.json();
  } catch (error) {
    console.error("Error fetching filtered players:", error);
    return [];
  }
};

// Get player details
export const getPlayerDetails = async (footballerId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/player-details/${footballerId}`);
    if (!response.ok) throw new Error(`Failed to fetch player details: ${footballerId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching player details:", error);
    return null;
  }
};

// Get similar players
export const getSimilarPlayers = async (footballerId, limit = 10) => {
  try {
    const response = await fetch(`${API_BASE_URL}/similar-players/${footballerId}?limit=${limit}`);
    if (!response.ok) throw new Error(`Failed to fetch similar players for: ${footballerId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching similar players:", error);
    return [];
  }
};

// Get transfer dashboard data
export const getTransferDashboardData = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/dashboard-data`);
    if (!response.ok) throw new Error("Failed to fetch transfer dashboard data");
    return await response.json();
  } catch (error) {
    console.error("Error fetching transfer dashboard data:", error);
    return null;
  }
};

// Get all leagues
export const getAllLeagues = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/leagues`);
    if (!response.ok) throw new Error("Failed to fetch leagues");
    return await response.json();
  } catch (error) {
    console.error("Error fetching leagues:", error);
    return [];
  }
};

// Get all teams
export const getAllTeams = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams`);
    if (!response.ok) throw new Error("Failed to fetch teams");
    return await response.json();
  } catch (error) {
    console.error("Error fetching teams:", error);
    return [];
  }
};

// Get teams by league
export const getTeamsByLeague = async (leagueId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams/league/${leagueId}`);
    if (!response.ok) throw new Error(`Failed to fetch teams for league: ${leagueId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching teams by league:", error);
    return [];
  }
};

// Get team by ID
export const getTeamById = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching team details:", error);
    return null;
  }
};

// Get team players
export const getTeamPlayers = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/team/players/${teamId}`);
    if (!response.ok) throw new Error(`Failed to fetch players for team: ${teamId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching team players:", error);
    return [];
  }
};