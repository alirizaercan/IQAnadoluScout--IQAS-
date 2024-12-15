/* frontend/src/pages/EnduranceDevelopmentPage.js */

import React, { useState, useEffect } from "react";
import { fetchLeagues, fetchTeamsByLeague, fetchFootballersByTeam, generateGraph, fetchEnduranceData } from "../services/endurance_api";
import "../styles/EnduranceDevelopmentPage.css";
import citizenshipIcon from "../assets/images/citizenship_icon.png";
import birthdayIcon from "../assets/images/birthday_icon.png";
import endurancePageIcon from "../assets/images/endurance_page_icon.png";

const graphOptions = [
  { value: "Key Endurance Metrics Overview", label: "Key Endurance Metrics Overview" },
  { value: "Endurance Trends", label: "Endurance Trends" },
  { value: "Peak Heart Rate Focused Endurance Development", label: "Peak Heart Rate Focused Endurance Development"},
  { value: "Performance Radar", label: "Performance Radar"}
];

const defaultLeagueLogo = "https://tmssl.akamaized.net//images/logo/header/tr1.png?lm=1723019495";  // Placeholder for default league logo
const defaultTeamLogo = "https://tmssl.akamaized.net/images/wappen/head/10484.png";  // Default team logo

const EnduranceDevelopmentPage = () => {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [footballers, setFootballers] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [selectedLeagueLogo, setSelectedLeagueLogo] = useState(defaultLeagueLogo);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedTeamLogo, setSelectedTeamLogo] = useState(defaultTeamLogo);
  const [selectedFootballer, setSelectedFootballer] = useState(null);
  const [graphType, setGraphType] = useState("Key Endurance Metrics Overview");
  const [dateRange, setDateRange] = useState({ start: "", end: "" });
  const [graphImage, setGraphImage] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [selectedFootballerData, setSelectedFootballerData] = useState(null);
  const [graphPath, setGraphPath] = useState("");

  // Fetch leagues on component mount
  useEffect(() => {
    fetchLeagues()
      .then((data) => {
        setLeagues(data);
        if (data.length > 0) {
          handleLeagueSelect(data[0].league_id);  // Auto-select the first league
        }
      })
      .catch((err) => console.error("Error fetching leagues:", err));
  }, []);

  // Update selected footballer data when footballer is selected
  useEffect(() => {
    if (selectedFootballer) {
      const selected = footballers.find((footballer) => footballer.footballer_id === Number(selectedFootballer));
      if (selected) {
        setSelectedFootballerData(selected);
      } else {
        console.error("Footballer not found in the list!");
      }
    }
  }, [selectedFootballer, footballers]);

  // Fetch teams when league is selected
  const handleLeagueSelect = (leagueId) => {
    const selectedLeague = leagues.find((league) => league.league_id === leagueId);
    setSelectedLeague(leagueId);
    setSelectedLeagueLogo(selectedLeague?.league_logo_path || defaultLeagueLogo);  // Set league logo

    if (selectedLeague) {
      fetchTeamsByLeague(leagueId)
        .then((data) => {
          setTeams(data);
          if (data.length > 0) {
            handleTeamSelect(data[0].team_id);  // Auto-select the first team if available
          }
        })
        .catch((err) => console.error("Error fetching teams:", err));
    }
  };
  

  useEffect(() => {
    if (graphPath) {
      setGraphImage(graphPath);
    }
  }, [graphPath]);
  

  // Fetch footballers when team is selected
  const handleTeamSelect = (teamId) => {
    const selectedTeam = teams.find((team) => team.team_id === Number(teamId));
    if (selectedTeam) {
      setSelectedTeam(teamId);
      setSelectedTeamLogo(selectedTeam.img_path || "https://tmssl.akamaized.net/images/wappen/head/10484.png");

      fetchFootballersByTeam(teamId)
        .then((data) => {
          setFootballers(data);
          if (data.length > 0) {
            setSelectedFootballer(data[0].footballer_id);  // Auto-select first footballer
          }
        })
        .catch((err) => console.error("Error fetching footballers:", err));
    } else {
      console.error("Selected team not found!");
    }
  };
  
  // Handle graph type change
  const handleGraphTypeChange = (e) => {
    setGraphType(e.target.value);
  };

  const handleGenerateGraph = async () => {
    const payload = {
      graph_type: graphType,
      start_date: dateRange.start,
      end_date: dateRange.end,
      footballer_id: selectedFootballer,
    };
  
    const response = await generateGraph(payload);
    if (response && response.path) {
      console.log("Generated graph path:", response.path);
      setGraphPath(response.path);
    } else {
      console.error("Graph generation failed or path missing in response:", response);
    }
  };
  
  // Fetch endurance data for selected footballer and graph type
  useEffect(() => {
    if (selectedFootballer && dateRange.start && dateRange.end) {
      const payload = {
        footballer_id: selectedFootballer,
        graph_type: graphType,
        start_date: dateRange.start,
        end_date: dateRange.end,
      };

      fetchEnduranceData(payload)
        .then((data) => setGraphData(data))
        .catch((err) => console.error("Error fetching graph data:", err));
    } else {
      console.error("Error: Missing required selections: footballer, start date, or end date");
    }
  }, [selectedFootballer, graphType, dateRange]);

  // Generate graph once the graph data and required conditions are met
  useEffect(() => {
    if (dateRange.start && dateRange.end && selectedFootballer && graphData) {
      const graphPayload = {
        footballer_id: selectedFootballer,
        graph_type: graphType,
        start_date: dateRange.start,
        end_date: dateRange.end,
        data: graphData
      };
      
      generateGraph(graphPayload)
        .then((generatedGraph) => setGraphImage(generatedGraph))
        .catch((err) => console.error("Error generating graph:", err));
    }
  }, [dateRange, selectedFootballer, graphData, graphType]);

  return (
    <div className="endurance-development-page">
      <div className="selectors">
        <div className="handle-league-select">
          <select onChange={(e) => handleLeagueSelect(e.target.value)}>
            <option value="">Select League</option>
            {leagues.map((league) => (
              <option key={league.league_id} value={league.league_id}>
                {league.league_name}
              </option>
            ))}
          </select>
          {selectedLeagueLogo && <img src={selectedLeagueLogo} alt="League Logo" />}
        </div>

        <div className="handle-team-select">
          <select onChange={(e) => handleTeamSelect(e.target.value)} disabled={!selectedLeague}>
            <option value="">Select Team</option>
            {teams.map((team) => (
              <option key={team.team_id} value={team.team_id}>
                {team.team_name}
              </option>
            ))}
          </select>
          {selectedTeamLogo && <img src={selectedTeamLogo} alt="Team Logo" />}
        </div>

        <div className="endurance-page-icon">
          <img src={endurancePageIcon} alt="Endurance Page Icon" className="icon-image" />
        </div>

      </div>

      <div className="player-selection-container">
        {/* Display the selected footballer's image */}
        {selectedFootballerData && selectedFootballerData.footballer_img_path && (
          <img
            src={selectedFootballerData.footballer_img_path}
            alt={selectedFootballerData.footballer_name}
            className="footballer-img"
          />
        )}

        {/* Dropdown */}
        <select onChange={(e) => setSelectedFootballer(e.target.value)} disabled={!selectedTeam}>
          <option value="">Select Footballer</option>
          {footballers.map((footballer) => (
            <option key={footballer.footballer_id} value={footballer.footballer_id}>
              {footballer.footballer_name}
            </option>
          ))}
        </select>

        {/* Citizenship, Nationality, and Birthday Information */}
        {selectedFootballerData && (
          <div className="info-section">
            {/* Citizenship Icon */}
            <div className="info-item">
              <img src={citizenshipIcon} alt="Citizenship" className="citizenship-icon" />
              <img
                src={selectedFootballerData.nationality_img_path}
                alt="Nationality"
                className="nationality-icon"
              />
            </div>

            {/* Birthday Icon */}
            <div className="info-item">
              <img src={birthdayIcon} alt="Birthday" className="birthday-icon" />
              <span className="birthday-date">{selectedFootballerData.birthday}</span>
            </div>
          </div>
        )}
      </div>

      {/* Graph Type Selection */}
      <div className="graph-type-container">
        <select
          onChange={handleGraphTypeChange}
          disabled={!selectedFootballer}
          className="graph-type-select"
        >
          <option value="">Select Graph Type</option>
          {graphOptions.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>

        {/* Date Range Inputs */}
        <div className="date-range">
          <input
            type="date"
            onChange={(e) => setDateRange({ ...dateRange, start: e.target.value })}
            disabled={!graphType}
            className="date-input"
          />
          <input
            type="date"
            onChange={(e) => setDateRange({ ...dateRange, end: e.target.value })}
            disabled={!graphType}
            className="date-input"
          />
        </div>

        {/* Generate Graph Button */}
        <button
          onClick={handleGenerateGraph}
          className="generate-graph-button"
        >
          Generate
        </button>
      </div>

      <div className="graph-container">
        {graphPath && (
          <img
              src={`${graphPath}?t=${new Date().getTime()}`}
              alt="Generated Endurance Progress Graph"
              className="graph-image"
          />
        )}
      </div>


    </div>
  );
};

export default EnduranceDevelopmentPage;