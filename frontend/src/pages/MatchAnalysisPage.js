import React, { useState, useRef, useEffect } from 'react';
import { 
  uploadMatchVideo, 
  getAnalysisResults, 
  getProcessedVideoUrl,
  streamProcessedVideo,
  getTeams 
} from '../services/match_analysis_api';
import '../styles/MatchAnalysisPage.css';
import uploadIcon from '../assets/images/upload_icon.png';
import statsIcon from '../assets/images/statistics_icon.png';
import reportIcon from '../assets/images/report_icon.png';
import recIcon from '../assets/images/rec_icon.png';
import matchAnalysisIcon from '../assets/images/match_analysis_icon.png';
import statisticsPageIcon from '../assets/images/statistics_page.png';
// PDF oluşturma kütüphanelerini import ediyoruz
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';

const MatchAnalysisPage = () => {
  const [homeTeam, setHomeTeam] = useState('');
  const [awayTeam, setAwayTeam] = useState('');
  const [matchDate, setMatchDate] = useState(new Date().toISOString().split('T')[0]);
  const [videoFile, setVideoFile] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [analysisId, setAnalysisId] = useState(null);
  const [analysisResults, setAnalysisResults] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [availableTeams, setAvailableTeams] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showStatsPopup, setShowStatsPopup] = useState(false);
  
  const fileInputRef = useRef(null);
  const videoPlayerRef = useRef(null);
  const statsPopupRef = useRef(null);

  useEffect(() => {
    // Fetch available teams when component mounts
    const fetchTeams = async () => {
      try {
        const teams = await getTeams();
        setAvailableTeams(teams);
      } catch (error) {
        console.error('Failed to fetch teams:', error);
      }
    };
    
    fetchTeams();
  }, []);

  // Effect to load the video when analysisId changes
  useEffect(() => {
    if (analysisId && analysisResults) {
      const loadVideo = async () => {
        setIsLoading(true);
        try {
          const videoUrl = `/api/match-analysis/${analysisId}/video?t=${Date.now()}`;
          console.log("Loading video from:", videoUrl);
          
          if (videoPlayerRef.current) {
            const video = videoPlayerRef.current;
            
            // Reset video
            video.pause();
            video.src = '';
            video.load();
            
            // Set new source
            video.src = videoUrl;
            video.load();
            
            await new Promise((resolve, reject) => {
              const onCanPlay = () => {
                video.removeEventListener('canplay', onCanPlay);
                video.removeEventListener('error', onError);
                resolve();
              };
              
              const onError = (e) => {
                console.error("Video error:", e);
                video.removeEventListener('canplay', onCanPlay);
                video.removeEventListener('error', onError);
                reject(new Error("Video loading failed"));
              };
              
              video.addEventListener('canplay', onCanPlay);
              video.addEventListener('error', onError);
              
              // Timeout after 10 seconds
              setTimeout(() => {
                video.removeEventListener('canplay', onCanPlay);
                video.removeEventListener('error', onError);
                reject(new Error("Video loading timed out"));
              }, 10000);
            });
          }
        } catch (error) {
          console.error("Failed to load video:", error);
          // Try fallback URL
          const fallbackUrl = `http://localhost:5000/uploads/processed_videos/processed_${analysisId}.mp4?t=${Date.now()}`;
          console.log("Trying fallback URL:", fallbackUrl);
          videoPlayerRef.current.src = fallbackUrl;
          videoPlayerRef.current.load();
        } finally {
          setIsLoading(false);
        }
      };
      
      loadVideo();
    }
  }, [analysisId, analysisResults]);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideoFile(file);
      // Create a URL for the video file preview
      const videoUrl = URL.createObjectURL(file);
      setVideoPreview(videoUrl);
    }
  };

  const handleUpload = async () => {
    if (!videoFile || !homeTeam || !awayTeam || !matchDate) {
      return;
    }

    setIsUploading(true);
    setIsProcessing(true);
    setUploadProgress(0);
    
    try {
      // Start a progress simulation
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(progressInterval);
            return 95;
          }
          return prev + 5;
        });
      }, 1000);
      
      const response = await uploadMatchVideo(videoFile, homeTeam, awayTeam, matchDate);
      setAnalysisId(response.analysis_id);
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      // Fetch analysis results after successful upload
      await fetchAnalysisResults(response.analysis_id);
      
    } catch (error) {
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
      setIsProcessing(false);
    }
  };

  const fetchAnalysisResults = async (id) => {
    setIsLoading(true);
    try {
      const results = await getAnalysisResults(id);
      setAnalysisResults(results);
      
      // Directly trigger video loading after results are fetched
      if (videoPlayerRef.current) {
        await streamProcessedVideo(id, videoPlayerRef.current);
      }
    } catch (error) {
      console.error('Error fetching results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGetResults = () => {
    if (!analysisId) return;
    fetchAnalysisResults(analysisId);
  };

  const triggerFileInput = () => {
    fileInputRef.current.click();
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
  };
  
  const renderProcessingOverlay = () => {
    if (!isProcessing) return null;
    
    return (
      <div className="processing-overlay">
        <div className="spinner"></div>
        <p>Processing video... {uploadProgress}%</p>
      </div>
    );
  };

  // Toggle statistics popup
  const toggleStatsPopup = () => {
    if (analysisResults) {
      setShowStatsPopup(!showStatsPopup);
    }
  };

  // Yeni fonksiyon: PDF raporu oluşturma
  const generatePDFReport = async () => {
    if (!analysisResults) return;
    
    try {
      // PDF'in boyutunu ayarlama
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      
      // Rapor başlığı ekleme
      pdf.setFontSize(18);
      pdf.setTextColor(0, 0, 0);
      const title = `Match Analysis Report: ${analysisResults.home_team.name} vs ${analysisResults.away_team.name}`;
      pdf.text(title, pageWidth / 2, 20, { align: 'center' });
      
      // Maç bilgilerini ekleme
      pdf.setFontSize(12);
      pdf.text(`Match Date: ${analysisResults.match_date}`, 20, 30);
      pdf.text(`Analysis ID: ${analysisId}`, 20, 37);
      
      // Çizgi ekleme
      pdf.setLineWidth(0.5);
      pdf.line(20, 40, pageWidth - 20, 40);
      
      // İstatistikleri ekleme
      pdf.setFontSize(14);
      pdf.text('Match Statistics', 20, 50);
      
      // Possession stats
      pdf.setFontSize(12);
      pdf.text('Possession:', 20, 60);
      pdf.text(`${analysisResults.home_team.name}: ${Math.round(analysisResults.possession.home)}%`, 40, 67);
      pdf.text(`${analysisResults.away_team.name}: ${Math.round(analysisResults.possession.away)}%`, 40, 74);
      
      // Formations
      pdf.text('Formations:', 20, 84);
      pdf.text(`${analysisResults.home_team.name}: ${analysisResults.formations.home}`, 40, 91);
      pdf.text(`${analysisResults.away_team.name}: ${analysisResults.formations.away}`, 40, 98);
      
      // Ball Control Time
      pdf.text('Ball Control Time:', 20, 108);
      pdf.text(`${analysisResults.home_team.name}: ${analysisResults.ball_control.home.toFixed(2)} seconds`, 40, 115);
      pdf.text(`${analysisResults.away_team.name}: ${analysisResults.ball_control.away.toFixed(2)} seconds`, 40, 122);
      
      // Average Speed
      pdf.text('Average Speed:', 20, 132);
      pdf.text(`${analysisResults.home_team.name}: ${analysisResults.statistics.speed.home.toFixed(2)} km/h`, 40, 139);
      pdf.text(`${analysisResults.away_team.name}: ${analysisResults.statistics.speed.away.toFixed(2)} km/h`, 40, 146);
      
      // Total Distance
      pdf.text('Total Distance:', 20, 156);
      pdf.text(`${analysisResults.home_team.name}: ${analysisResults.statistics.distance.home.toFixed(2)} m`, 40, 163);
      pdf.text(`${analysisResults.away_team.name}: ${analysisResults.statistics.distance.away.toFixed(2)} m`, 40, 170);
      
      // Attack Phases
      pdf.text('Attack Phases:', 20, 180);
      pdf.text(`${analysisResults.home_team.name}: ${analysisResults.statistics.attack_phases.home}`, 40, 187);
      pdf.text(`${analysisResults.away_team.name}: ${analysisResults.statistics.attack_phases.away}`, 40, 194);
      
      // Altbilgi ekle
      pdf.setFontSize(10);
      pdf.text(`Generated on: ${new Date().toLocaleString()}`, 20, 270);
      
      // PDF'i indirme
      pdf.save(`match_report_${analysisResults.home_team.name}_vs_${analysisResults.away_team.name}.pdf`);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF report. Please try again.');
    }
  };

  // Eğer popup elementini doğrudan kullanmak istersek, bu fonksiyonu kullanabiliriz
  const generatePDFFromPopup = async () => {
    if (!statsPopupRef.current || !analysisResults) return;

    try {
      const content = statsPopupRef.current.querySelector('.stats-popup-content');
      
      // Stats popup içeriğini canvas'a dönüştürelim
      const canvas = await html2canvas(content, {
        scale: 2, // Daha yüksek kalite için ölçek
        useCORS: true,
        logging: false,
        backgroundColor: '#ffffff'
      });
      
      const imgData = canvas.toDataURL('image/png');
      
      // PDF oluşturma
      const pdf = new jsPDF('p', 'mm', 'a4');
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();
      
      // Başlık ekle
      pdf.setFontSize(18);
      pdf.text(`Match Statistics: ${analysisResults.home_team.name} vs ${analysisResults.away_team.name}`, pageWidth / 2, 20, { align: 'center' });
      
      // Canvas görüntüsünü PDF'e ekle
      const imgWidth = pageWidth - 40; // Kenar boşlukları için
      const imgHeight = (canvas.height * imgWidth) / canvas.width;
      
      pdf.addImage(imgData, 'PNG', 20, 30, imgWidth, imgHeight);
      
      // Altbilgi ekle
      pdf.setFontSize(10);
      pdf.text(`Generated on: ${new Date().toLocaleString()}`, 20, pageHeight - 10);
      
      // PDF'i indir
      pdf.save(`match_statistics_${analysisResults.home_team.name}_vs_${analysisResults.away_team.name}.pdf`);
    } catch (error) {
      console.error('Error generating PDF from popup:', error);
      alert('Failed to generate PDF report. Please try again.');
    }
  };
  
  const renderVideo = () => {
    if (isProcessing) {
      return (
        <div className="video-player-wrapper">
          <div className="video-player-container">
            {renderProcessingOverlay()}
            {videoPreview && (
              <video 
                ref={videoPlayerRef}
                className="video-player"
                src={videoPreview}
              />
            )}
          </div>
          <div className="rec-icon">
            <img src={recIcon} alt="Recording" />
          </div>
          <div className="report-button-container">
            <button 
              className="report-icon-button"
              disabled={!analysisResults}
              onClick={generatePDFReport}
            >
              <img src={reportIcon} alt="Generate Report" />
            </button>
          </div>
          <div className="statistics-icon-bottom" onClick={toggleStatsPopup}>
            <img src={statsIcon} alt="Statistics" />
          </div>
        </div>
      );
    }
    
    if (analysisId && analysisResults) {
      const videoUrl = getProcessedVideoUrl(analysisId);
      
      return (
        <div className="video-player-wrapper">
          <div className="video-player-container">
            {isLoading && <div className="loading-spinner">Loading video...</div>}
            <video
              ref={videoPlayerRef}
              className="video-player"
              controls
              width="100%"
              height="auto"
              preload="auto"
              playsInline
              key={`video-${analysisId}-${Date.now()}`}
              onError={(e) => console.error("Video error:", e.target.error)}
            >
              <source src={videoUrl} type="video/mp4; codecs=avc1.42E01E,mp4a.40.2" />
              Your browser does not support the video tag.
            </video>
          </div>
          <div className="rec-icon">
            <img src={recIcon} alt="Recording" />
          </div>
          <div className="report-button-container">
            <button 
              className="report-icon-button"
              disabled={!analysisResults}
              onClick={generatePDFReport}
            >
              <img src={reportIcon} alt="Generate Report" />
              <span>Report</span>
            </button>
          </div>
          <div className="statistics-icon-bottom">
            <img 
              src={statsIcon} 
              alt="Statistics" 
              onClick={toggleStatsPopup}
              style={{ cursor: analysisResults ? 'pointer' : 'default' }}
            />
          </div>
        </div>
      );
    }
    
    if (videoPreview) {
      return (
        <div className="video-player-wrapper">
          <div className="video-player-container">
            <video 
              ref={videoPlayerRef}
              className="video-player"
              src={videoPreview} 
              controls
            />
          </div>
          <div className="rec-icon">
            <img src={recIcon} alt="Recording" />
          </div>
          <div className="report-button-container">
            <button 
              className="report-icon-button"
              disabled={!analysisResults}
              onClick={generatePDFReport}
            >
              <img src={reportIcon} alt="Generate Report" />
              <span>Report</span>
            </button>
          </div>
          <div className="statistics-icon-bottom">
            <img src={statsIcon} alt="Statistics" />
          </div>
        </div>
      );
    }
    
    return (
      <div className="video-player-wrapper">
        <div className="upload-box" onClick={triggerFileInput}>
          <img src={uploadIcon} alt="Upload" className="upload-icon" />
          <p>Click to select match video file</p>
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileChange}
            accept="video/*"
            style={{ display: 'none' }}
          />
        </div>
      </div>
    );
  };

  // Statistics popup component
  const renderStatsPopup = () => {
    if (!showStatsPopup || !analysisResults) return null;
    
    return (
      <div className="stats-popup-overlay" ref={statsPopupRef}>
        <div className="stats-popup-container">
          <div className="stats-popup-header">
            <h2>Match Statistics</h2>
            <div className="header-buttons">
              <button className="close-button" onClick={toggleStatsPopup}>×</button>
            </div>
          </div>
          <div className="stats-popup-content">
            <div className="teams-header">
              <h3>{analysisResults.home_team.name} vs {analysisResults.away_team.name}</h3>
              <p>Match Date: {analysisResults.match_date}</p>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <h4>Possession</h4>
                <div className="possession-bar">
                  <div 
                    className="home-possession" 
                    style={{ 
                      width: `${analysisResults.possession.home}%`,
                      backgroundColor: analysisResults.home_team.color
                    }}
                  >
                    {Math.round(analysisResults.possession.home)}%
                  </div>
                  <div 
                    className="away-possession" 
                    style={{ 
                      width: `${analysisResults.possession.away}%`,
                      backgroundColor: analysisResults.away_team.color
                    }}
                  >
                    {Math.round(analysisResults.possession.away)}%
                  </div>
                </div>
                <div className="team-labels">
                  <span>{analysisResults.home_team.name}</span>
                  <span>{analysisResults.away_team.name}</span>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Formations</h4>
                <div className="formations">
                  <div className="formation">
                    <span>Home: {analysisResults.formations.home}</span>
                  </div>
                  <div className="formation">
                    <span>Away: {analysisResults.formations.away}</span>
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Ball Control Time</h4>
                <div className="ball-control">
                  <div className="control-item">
                    <span>Home: {analysisResults.ball_control.home.toFixed(2)} seconds</span>
                  </div>
                  <div className="control-item">
                    <span>Away: {analysisResults.ball_control.away.toFixed(2)} seconds</span>
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Average Speed</h4>
                <div className="speed-stats">
                  <div className="speed-item">
                    <span>Home: {analysisResults.statistics.speed.home.toFixed(2)} km/h</span>
                  </div>
                  <div className="speed-item">
                    <span>Away: {analysisResults.statistics.speed.away.toFixed(2)} km/h</span>
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Total Distance</h4>
                <div className="distance-stats">
                  <div className="distance-item">
                    <span>Home: {analysisResults.statistics.distance.home.toFixed(2)} m</span>
                  </div>
                  <div className="distance-item">
                    <span>Away: {analysisResults.statistics.distance.away.toFixed(2)} m</span>
                  </div>
                </div>
              </div>
              
              <div className="stat-card">
                <h4>Attack Phases</h4>
                <div className="attack-stats">
                  <div className="attack-item">
                    <span>Home: {analysisResults.statistics.attack_phases.home}</span>
                  </div>
                  <div className="attack-item">
                    <span>Away: {analysisResults.statistics.attack_phases.away}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="match-analysis-container">
      <div className="main-content">
        <div className="video-upload-section">
          <div className="page-header">
            <div className="match-analysis-icon">
              <img src={matchAnalysisIcon} alt="Match Analysis" />
            </div>
            <div className="video-upload-header">
              <div className="upload-icon-left">
                <img src={uploadIcon} alt="Upload" />
              </div>
              <h2>Upload the Match Video</h2>
              <div className="upload-icon-right">
                <img src={uploadIcon} alt="Upload" />
              </div>
            </div>
            <div className="statistics-page-icon" onClick={toggleStatsPopup} style={{ cursor: analysisResults ? 'pointer' : 'default' }}>
              <img src={statisticsPageIcon} alt="Statistics Page" />
            </div>
          </div>
          
          {renderVideo()}
          
          <div className="team-inputs">
            <input
              type="text"
              placeholder="Home Team"
              value={homeTeam}
              onChange={(e) => setHomeTeam(e.target.value)}
              list="home-teams"
            />
            <datalist id="home-teams">
              {availableTeams.map(team => (
                <option key={`home-${team.id}`} value={team.name} />
              ))}
            </datalist>
            
            <input
              type="text"
              placeholder="Away Team"
              value={awayTeam}
              onChange={(e) => setAwayTeam(e.target.value)}
              list="away-teams"
            />
            <datalist id="away-teams">
              {availableTeams.map(team => (
                <option key={`away-${team.id}`} value={team.name} />
              ))}
            </datalist>
            
            <input
              type="date"
              value={matchDate}
              onChange={(e) => setMatchDate(e.target.value)}
            />
          </div>
          
          <div className="action-buttons">
            <button 
              onClick={handleUpload} 
              disabled={isUploading || !videoFile}
              className="upload-button"
            >
              {isUploading ? 'Uploading...' : 'Upload & Analyze'}
            </button>
            
            {videoPreview && (
              <>
                <button 
                  onClick={toggleRecording} 
                  className={`record-button ${isRecording ? 'recording' : ''}`}
                  disabled={isProcessing}
                >
                  {isRecording ? 'Stop Recording' : 'Start Recording'}
                </button>
                
                {analysisId && (
                  <button 
                    onClick={handleGetResults} 
                    className="results-button"
                    disabled={isLoading}
                  >
                    {isLoading ? 'Loading...' : 'Refresh Analysis'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>

        {/* Stats popup rendered here */}
        {renderStatsPopup()}
      </div>
    </div>
  );
};

export default MatchAnalysisPage;