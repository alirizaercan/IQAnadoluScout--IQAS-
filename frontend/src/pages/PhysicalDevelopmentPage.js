import React, { useState, useEffect } from "react";
import { fetchLeagues, fetchTeamsByLeague, fetchFootballersByTeam, fetchPhysicalData } from "../services/api";
import '../styles/PhysicalDevelopmentPage.css';

const PhysicalDevelopmentPage = () => {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [footballers, setFootballers] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedFootballer, setSelectedFootballer] = useState(null);
  const [graphType, setGraphType] = useState("");
  const [graphData, setGraphData] = useState(null);
  const [dateRange, setDateRange] = useState({ start: "", end: "" });

  useEffect(() => {
    fetchLeagues()
      .then((data) => setLeagues(data))
      .catch((err) => console.error("Error fetching leagues:", err));
  }, []);

  const handleLeagueSelect = (leagueId) => {
    setSelectedLeague(leagueId);
    fetchTeamsByLeague(leagueId)
      .then((data) => setTeams(data))
      .catch((err) => console.error("Error fetching teams:", err));
  };

  const handleTeamSelect = (teamId) => {
    setSelectedTeam(teamId);
    fetchFootballersByTeam(teamId)
      .then((data) => setFootballers(data))
      .catch((err) => console.error("Error fetching footballers:", err));
  };

  const handleGraphFetch = () => {
    const payload = {
      footballer_id: selectedFootballer,
      graph_type: graphType,
      start_date: dateRange.start,
      end_date: dateRange.end,
    };

    fetchPhysicalData(payload)
      .then((data) => setGraphData(data))
      .catch((err) => console.error("Error fetching graph data:", err));
  };

  return (
    <div className="physical-development-page">
      <div className="selectors">
        <select onChange={(e) => handleLeagueSelect(e.target.value)}>
          <option value="">Select League</option>
          {leagues && leagues.length > 0 ? (
            leagues.map((league) => (
              <option key={league.league_id} value={league.league_id}>
                {league.league_name}
              </option>
            ))
          ) : (
            <option>No leagues available</option>
          )}
        </select>
        <select onChange={(e) => handleTeamSelect(e.target.value)} disabled={!selectedLeague}>
          <option value="">Select Team</option>
          {teams.map((team) => (
            <option key={team.team_id} value={team.team_id}>
              {team.team_name}
            </option>
          ))}
        </select>
        <select onChange={(e) => setSelectedFootballer(e.target.value)} disabled={!selectedTeam}>
          <option value="">Select Footballer</option>
          {footballers.map((footballer) => (
            <option key={footballer.footballer_id} value={footballer.footballer_id}>
              {footballer.footballer_name}
            </option>
          ))}
        </select>
        <input
          type="date"
          onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
        />
        <input
          type="date"
          onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
        />
        <button onClick={handleGraphFetch}>Fetch Graph</button>
      </div>
      <div className="graph-container">
        {graphData && <pre>{JSON.stringify(graphData, null, 2)}</pre>}
      </div>
    </div>
  );
};

export default PhysicalDevelopmentPage;
