// src/services/match_analysis_api.js
import axios from 'axios';
const API_BASE_URL = "http://localhost:5000/api/match-analysis";

export const uploadMatchVideo = async (videoFile, homeTeam, awayTeam, matchDate) => {
  const formData = new FormData();
  formData.append('video', videoFile);
  formData.append('home_team', homeTeam);
  formData.append('away_team', awayTeam);
  formData.append('match_date', matchDate);
  
  try {
    const response = await axios.post(`${API_BASE_URL}/analyze`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading video:', error);
    throw new Error(error.response?.data?.error || 'Failed to upload and analyze video');
  }
};

export const getAnalysisResults = async (analysisId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/${analysisId}`);
    return response.data;
  } catch (error) {
    console.error('Error fetching analysis results:', error);
    throw new Error(error.response?.data?.error || 'Failed to fetch analysis results');
  }
};

export const getProcessedVideoUrl = (analysisId) => {
  return `${API_BASE_URL}/${analysisId}/video?cachebust=${Date.now()}`;
};

export const streamProcessedVideo = async (analysisId, videoElement) => {
  try {
    // URL'e zaman damgası ekleyerek önbelleklemeyi önlüyoruz
    const videoUrl = `${API_BASE_URL}/${analysisId}/video?t=${Date.now()}`;
    console.log("Loading video from:", videoUrl);
    
    // Video elementini sıfırlıyoruz
    videoElement.pause();
    videoElement.removeAttribute('src');
    videoElement.load();
    
    // Yeni URL'i atıyoruz
    videoElement.src = videoUrl;
    
    // Kontrolleri açıyoruz
    videoElement.controls = true;
    videoElement.autoplay = false; // Otomatik oynatmayı kapatıyoruz
    
    // Video durumunu loglamak için olay dinleyicileri ekliyoruz
    videoElement.addEventListener('loadstart', () => console.log('Video loadstart event fired'));
    videoElement.addEventListener('canplay', () => console.log('Video canplay event fired'));
    videoElement.addEventListener('playing', () => console.log('Video playing event fired'));
    videoElement.addEventListener('error', (e) => console.error('Video error event:', e));
    
    // Video başlatmayı promise ile yönetiyoruz
    return new Promise((resolve, reject) => {
      const onCanPlay = () => {
        console.log('Video can now be played');
        videoElement.removeEventListener('canplay', onCanPlay);
        resolve();
      };
      
      const onError = (e) => {
        console.error('Video error occurred:', videoElement.error);
        videoElement.removeEventListener('error', onError);
        reject(new Error(`Video loading failed: ${videoElement.error?.message || 'Unknown error'}`));
      };
      
      videoElement.addEventListener('canplay', onCanPlay);
      videoElement.addEventListener('error', onError);
      
      // 10 saniye içinde yüklenmezse timeout
      const timeout = setTimeout(() => {
        videoElement.removeEventListener('canplay', onCanPlay);
        videoElement.removeEventListener('error', onError);
        reject(new Error('Video loading timed out after 10 seconds'));
      }, 10000);
      
      // Başarılı olursa timeout'u temizliyoruz
      videoElement.addEventListener('canplay', () => clearTimeout(timeout));
    });
  } catch (error) {
    console.error('Error streaming video:', error);
    throw error;
  }
};

export const getTeams = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/teams`);
    return response.data.teams;
  } catch (error) {
    console.error('Error fetching teams:', error);
    throw new Error(error.response?.data?.error || 'Failed to fetch teams');
  }
};

export const getRecentAnalyses = async (limit = 5) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/recent?limit=${limit}`);
    return response.data.analyses;
  } catch (error) {
    console.error('Error fetching recent analyses:', error);
    throw new Error(error.response?.data?.error || 'Failed to fetch recent analyses');
  }
};