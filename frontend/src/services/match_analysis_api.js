// frontend/src/services/match_analysis_api.js
const API_BASE_URL = "http://localhost:5000/api/match-analysis";

export const uploadMatchVideo = async (videoFile, homeTeam, awayTeam, matchDate) => {
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('home_team', homeTeam);
  formData.append('away_team', awayTeam);
  formData.append('match_date', matchDate);

  const response = await fetch(`${API_BASE_URL}/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Failed to upload and analyze video');
  }

  return await response.json();
};

export const getAnalysisResults = async (analysisId) => {
  const response = await fetch(`${API_BASE_URL}/results/${analysisId}`);
  if (!response.ok) {
    throw new Error('Failed to fetch analysis results');
  }
  return await response.json();
};