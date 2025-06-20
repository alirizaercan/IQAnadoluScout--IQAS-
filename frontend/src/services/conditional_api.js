/* frontend/src/services/conditional_api.js */

const API_BASE_URL = "http://localhost:5056/api/conditional-development";

// Function to fetch all leagues
export const fetchLeagues = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/leagues`);
    if (!response.ok) {
      throw new Error("Failed to fetch leagues");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching leagues:", error);
    return []; // Return an empty array in case of an error
  }
};

// Function to fetch teams by league
export const fetchTeamsByLeague = async (leagueId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/teams/${leagueId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch teams for league: ${leagueId}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching teams:", error);
    return []; // Return an empty array in case of an error
  }
};

// Function to fetch footballers by team
export const fetchFootballersByTeam = async (teamId) => {
  try {
    const response = await fetch(`${API_BASE_URL}/footballers/${teamId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch footballers for team: ${teamId}`);
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching footballers:", error);
    return []; // Return an empty array in case of an error
  }
};

// Function to fetch conditional data for a footballer within a date range
export const fetchConditionalData = async (payload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/conditional-data`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error("Failed to fetch conditional data");
    }
    return await response.json();
  } catch (error) {
    console.error("Error fetching conditional data:", error);
    return []; // Return an empty array or error response
  }
};

export const generateGraph = async (payload) => {
  try {
    const response = await fetch(`${API_BASE_URL}/generate-graph`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    if (!response.ok) {
      throw new Error("Failed to generate graph");
    }
    return await response.json();
  } catch (error) {
    console.error("Error generating graph:", error);
    return null;
  }
};