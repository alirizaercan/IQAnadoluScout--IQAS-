// frontend/src/services/prediction_api.js
const API_BASE_URL = "http://localhost:5056/api/match-score-prediction";

export const fetchLeagues = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/leagues`);
    if (!response.ok) throw new Error("Failed to fetch leagues");
    return await response.json();
  } catch (error) {
    console.error("Error fetching leagues:", error);
    return [];
  }
};

export const fetchTeamsByLeague = async (leagueId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams/${leagueId}`);
    if (!response.ok) throw new Error(`Failed to fetch teams for league: ${leagueId}`);
    return await response.json();
  } catch (error) {
    console.error("Error fetching teams:", error);
    return [];
  }
};

export const fetchPredictions = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/predictions/${teamId}`);
    if (!response.ok) throw new Error("Failed to fetch predictions");
    return await response.json();
  } catch (error) {
    console.error("Error fetching predictions:", error);
    return [];
  }
};