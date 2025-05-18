import React, { useState, useEffect } from "react";
import { fetchLeagues, fetchTeamsByLeague, fetchFootballersByTeam, generateGraph, fetchPerformanceData } from "../services/performance_api";
import "../styles/PerformanceVisualizationPage.css";
import citizenshipIcon from "../assets/images/citizenship_icon.png";
import birthdayIcon from "../assets/images/birthday_icon.png";
import performancePageIcon from "../assets/images/performance_visualization_icon.png";
import Header from "../components/Header";
import Footer from "../components/Footer";

const graphOptions = [
  { value: "Goals and Assists Analysis", label: "Goals and Assists Analysis" },
  { value: "Shooting Accuracy Analysis", label: "Shooting Accuracy Analysis" },
  { value: "Defensive Performance Analysis", label: "Defensive Performance Analysis" },
  { value: "Passing Accuracy Analysis", label: "Passing Accuracy Analysis" },
  { value: "Dribbling Success Analysis", label: "Dribbling Success Analysis" },
  { value: "Playing Time Analysis", label: "Playing Time Analysis" },
  { value: "Physical Duels Analysis", label: "Physical Duels Analysis" },
  { value: "Error Analysis", label: "Error Analysis" },
  { value: "Disciplinary Analysis", label: "Disciplinary Analysis" },
  { value: "Overall Performance Radar Analysis", label: "Overall Performance Radar Analysis" }
];

const defaultLeagueLogo = "https://tmssl.akamaized.net//images/logo/header/tr1.png?lm=1723019495";
const defaultTeamLogo = "https://tmssl.akamaized.net/images/wappen/head/10484.png";

const PerformanceVisualizationPage = () => {
  const [leagues, setLeagues] = useState([]);
  const [teams, setTeams] = useState([]);
  const [footballers, setFootballers] = useState([]);
  const [selectedLeague, setSelectedLeague] = useState(null);
  const [selectedLeagueLogo, setSelectedLeagueLogo] = useState(defaultLeagueLogo);
  const [selectedTeam, setSelectedTeam] = useState(null);
  const [selectedTeamLogo, setSelectedTeamLogo] = useState(defaultTeamLogo);
  const [selectedFootballer, setSelectedFootballer] = useState(null);
  const [graphType, setGraphType] = useState("Goals and Assists Analysis");
  const [graphImage, setGraphImage] = useState(null);
  const [selectedFootballerData, setSelectedFootballerData] = useState(null);
  const [graphPath, setGraphPath] = useState("");
  const [isLoading, setIsLoading] = useState(false);

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
    setSelectedLeagueLogo(selectedLeague?.league_logo_path || defaultLeagueLogo);

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
      setSelectedTeamLogo(selectedTeam.img_path || defaultTeamLogo);

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
    if (!selectedFootballer || !graphType) {
      console.error("Please select a footballer and graph type");
      return;
    }

    setIsLoading(true);
    
    const payload = {
      graph_type: graphType,
      footballer_id: selectedFootballer,
    };
  
    try {
      const response = await generateGraph(payload);
      if (response && response.path) {
        console.log("Generated graph path:", response.path);
        setGraphPath(response.path);
      } else {
        console.error("Graph generation failed or path missing in response:", response);
      }
    } catch (error) {
      console.error("Error generating graph:", error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="page-container">
      <Header />
      <div className="performance-visualization-page">
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

          <div className="performance-page-icon">
            <img src={performancePageIcon} alt="Performance Page Icon" className="icon-image" />
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

          {/* Generate Graph Button */}
          <button
            onClick={handleGenerateGraph}
            disabled={!selectedFootballer || !graphType || isLoading}
            className="generate-graph-button"
          >
            {isLoading ? "Generating..." : "Generate"}
          </button>
        </div>

        <div className="graph-container">
          {graphPath && (
            <img
              src={`${graphPath}?t=${new Date().getTime()}`}
              alt="Generated Performance Graph"
              className="graph-image"
            />
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default PerformanceVisualizationPage;