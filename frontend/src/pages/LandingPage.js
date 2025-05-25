import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/LandingPage.css';
import '../styles/FeaturesSection.css';
import '../styles/testimonials.css';
import '../styles/contact.css';
import '../styles/LandingFooter.css';
import '../styles/Navigation.css';
import logoImage from '../assets/images/TYFOR_logo_circle.png';
import logoGif from '../assets/images/TYFOR_auth.gif';
import statisticsImg from '../assets/images/statistics_page.png';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faChartLine, 
  faUsers, 
  faFutbol, 
  faBrain,
  faArrowRight,
  faLightbulb,
  faChartPie,
  faBullseye,
  faRunning,
  faTools,
  faDatabase,
  faSearch,
  faShieldAlt,
  faStar,
  faQuoteRight,
  faChevronLeft,
  faChevronRight,
  faUser,
  faEnvelope,
  faPhone,
  faMapMarkerAlt,
  faPaperPlane
} from '@fortawesome/free-solid-svg-icons';
import {
  faTwitter,
  faLinkedinIn,
  faInstagram
} from '@fortawesome/free-brands-svg-icons';

const LandingPage = () => {  
  const navigate = useNavigate();  
  const [activeSection, setActiveSection] = useState('home');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isVisible, setIsVisible] = useState({
    hero: false,
    features: false,
    product: false,
    about: false,
    tech: false,
    testimonials: false,
    contact: false
  });
  const [scrollPosition, setScrollPosition] = useState(0);
  const [animateCount, setAnimateCount] = useState(false);
  const [navScrolled, setNavScrolled] = useState(false);
  const [activeTestimonial, setActiveTestimonial] = useState(0);
  const [activeTab, setActiveTab] = useState(0);
  const statsRef = useRef(null);
  const statsInView = useRef(false);
  const testimonialsRef = useRef(null);  const counters = useRef({ users: 0, teams: 0, players: 0 });
  const targetStats = { users: 0, teams: 0, players: 0 };
  
  // Animation triggers for sections when scrolling
  useEffect(() => {
    setIsVisible({ hero: true, features: false, product: false, about: false, tech: false, testimonials: false });
      const handleScroll = () => {
      const currentScrollPos = window.scrollY;
      setScrollPosition(currentScrollPos);
      const windowHeight = window.innerHeight;
      
      // Change navbar style on scroll
      if (currentScrollPos > 50) {
        setNavScrolled(true);
      } else {
        setNavScrolled(false);
      }
      
      // Update active section based on scroll position
      if (currentScrollPos < windowHeight * 0.5) {
        setActiveSection('home');
      } else if (currentScrollPos < windowHeight * 1.2) {
        setActiveSection('features');
      } else if (currentScrollPos < windowHeight * 2.0) {
        setActiveSection('product');
      } else if (currentScrollPos < windowHeight * 2.6) {
        setActiveSection('tech');
      } else if (currentScrollPos < windowHeight * 3.3) {
        setActiveSection('about');
      } else {
        setActiveSection('contact');
      }
      
      // Animating sections based on scroll position - adjusted thresholds to fix overlapping
      if (currentScrollPos > windowHeight * 0.05) {
        setIsVisible(prev => ({ ...prev, features: true }));
      }
      
      if (currentScrollPos > windowHeight * 0.3) {
        setIsVisible(prev => ({ ...prev, product: true }));
      }
      
      if (currentScrollPos > windowHeight * 0.6) {
        setIsVisible(prev => ({ ...prev, about: true }));
      }

      if (currentScrollPos > windowHeight * 0.85) {
        setIsVisible(prev => ({ ...prev, tech: true }));
      }if (currentScrollPos > windowHeight * 1.1) {
        setIsVisible(prev => ({ ...prev, testimonials: true }));
      }
      
      if (currentScrollPos > windowHeight * 1.3) {
        setIsVisible(prev => ({ ...prev, contact: true }));
      }
      
      // Check if stats section is in view
      if (statsRef.current) {
        const statsPosition = statsRef.current.getBoundingClientRect();
        if (statsPosition.top < window.innerHeight && statsPosition.bottom >= 0) {
          if (!statsInView.current) {
            statsInView.current = true;
            setAnimateCount(true);
          }
        } else {
          statsInView.current = false;
        }
      }
    };
    
    // Initialize animations
    handleScroll();
    
    // Add parallax and other animation effects
    const updateParallaxElements = () => {
      const parallaxElements = document.querySelectorAll('.parallax');
      parallaxElements.forEach(element => {
        const speed = element.getAttribute('data-speed') || 0.2;
        const offset = window.scrollY * speed;
        element.style.transform = `translateY(${offset}px)`;
      });
    };
    
    const handleScrollEvents = () => {
      handleScroll();
      updateParallaxElements();
    };
    
    window.addEventListener('scroll', handleScrollEvents);
    return () => window.removeEventListener('scroll', handleScrollEvents);
  }, []);

  // Counter animation effect
  useEffect(() => {
    if (animateCount) {
      const duration = 2000; // 2 seconds animation
      const interval = 16; // ~60fps
      let startTimestamp = null;
      
      const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        
        // Update counter values based on progress
        counters.current = {
          users: Math.floor(progress * targetStats.users),
          teams: Math.floor(progress * targetStats.teams),
          players: Math.floor(progress * targetStats.players)
        };
        
        // Force a re-render
        setAnimateCount(prevState => ({ ...prevState }));
        
        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      };
      
      window.requestAnimationFrame(step);
    }
  }, [animateCount]);
  // Testimonial slider effect
  useEffect(() => {
    const interval = setInterval(() => {
      setActiveTestimonial(prev => (prev + 1) % 3);
    }, 6000); // Increased time to 6 seconds for a more comfortable reading pace
    
    return () => clearInterval(interval);
  }, []);

  // Card flip behavior
  const handleCardFlip = (index) => {
    const cards = document.querySelectorAll('.card-animate');
    cards[index].classList.toggle('flipped');
  }

  // Enhanced tab switching with animations
  const handleTabChange = (tabIndex) => {
    // First animate current tab out
    const currentPanel = document.querySelector(`.feature-panel.active`);
    if (currentPanel) {
      currentPanel.style.animation = 'panelFadeOut 0.3s forwards';
      
      // After the animation completes, change the active tab
      setTimeout(() => {
        setActiveTab(tabIndex);
        
        // Get the new active panel and animate it in
        setTimeout(() => {
          const newPanel = document.querySelector(`.feature-panel.active`);
          if (newPanel) {
            newPanel.style.animation = 'panelFadeIn 0.5s forwards';
          }
        }, 50);
      }, 300);
    } else {
      setActiveTab(tabIndex);
    }
  };

  return (
    <div className="landing-page">      
      {/* Enhanced Professional Navigation Bar */}
      <nav className={`landing-nav ${navScrolled ? 'scrolled' : ''}`}>        <div className="landing-logo" onClick={() => navigate('/')}>
          <img src={logoImage} alt="TYFOR Logo" />
          <span>TYFOR</span>
        </div>
        
        <div className={`landing-nav-links ${mobileMenuOpen ? 'mobile-open' : ''}`}>
          <a href="#home" className={activeSection === 'home' ? 'active' : ''} 
            onClick={() => {
              setActiveSection('home');
              setMobileMenuOpen(false);
            }}>Home</a>
          <a href="#features" className={activeSection === 'features' ? 'active' : ''} 
            onClick={() => {
              setActiveSection('features');
              setMobileMenuOpen(false);
            }}>Solutions</a>
          <a href="#product" className={activeSection === 'product' ? 'active' : ''} 
            onClick={() => {
              setActiveSection('product'); 
              setMobileMenuOpen(false);
            }}>Benefits</a>
          <a href="#tech" className={activeSection === 'tech' ? 'active' : ''} 
            onClick={() => {
              setActiveSection('tech');
              setMobileMenuOpen(false);
            }}>Technology</a>
          <a href="#about" className={activeSection === 'about' ? 'active' : ''} 
            onClick={() => {
              setActiveSection('about');
              setMobileMenuOpen(false);
            }}>Company</a>
          <a href="#contact" className={activeSection === 'contact' ? 'active' : ''} 
            onClick={() => {
              setActiveSection('contact');
              setMobileMenuOpen(false);
            }}>Connect</a>
        </div>
          <button className="landing-cta-button" onClick={() => navigate('/authentication')}>
          Access Platform
          <FontAwesomeIcon icon={faArrowRight} className="landing-button-icon" />
        </button>
        
        <button className="mobile-menu-button" onClick={() => setMobileMenuOpen(!mobileMenuOpen)}>
          <div className={`menu-icon ${mobileMenuOpen ? 'open' : ''}`}>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </button>
        
        {/* Mobile menu overlay */}
        {mobileMenuOpen && <div className="mobile-overlay" onClick={() => setMobileMenuOpen(false)}></div>}
      </nav>
      
      {/* Hero Section */}
      <section className={`landing-hero ${isVisible.hero ? 'visible' : ''}`} id="home">
        <div className="hero-background">
          <div className="animated-bg-shape shape1"></div>
          <div className="animated-bg-shape shape2"></div>
          <div className="animated-bg-shape shape3"></div>
          <div className="hero-particles"></div>
        </div>
        
        <div className="landing-hero-content">
          <div className="hero-logo-animation">
            <img src={logoImage} alt="TYFOR Animated Logo" className="hero-animated-logo" />
          </div>
          <h1 className="landing-hero-title animate-text">
            <span className="text-gradient">Transform</span> Football Management Through <span className="text-accent">Data Science</span>
          </h1>
          <p className="landing-hero-subtitle">
            TYFOR empowers Anatolian football clubs with cutting-edge analytics for youth development, 
            talent scouting, and strategic decision-making through advanced AI technology.
          </p>
          <div className="landing-hero-buttons">
            <button 
              className="landing-primary-button" 
              onClick={() => navigate('/authentication')}
            >
              <span className="button-text">Start Free Trial</span>
              <span className="button-shine"></span>
            </button>
            <button className="landing-secondary-button" 
              onClick={() => document.getElementById('features').scrollIntoView({ behavior: 'smooth' })}
            >
              Explore Solutions
              <FontAwesomeIcon icon={faArrowRight} className="button-icon-right" />
            </button>
          </div>
          
          <div className="hero-badges">
            <div className="hero-badge">
              <FontAwesomeIcon icon={faShieldAlt} className="badge-icon" />
              <span>Built for Turkish Football</span>
            </div>
            <div className="hero-badge">
              <FontAwesomeIcon icon={faStar} className="badge-icon" />
              <span>Research-Driven Solution</span>
            </div>
            <div className="hero-badge">
              <FontAwesomeIcon icon={faDatabase} className="badge-icon" />
              <span>Powered by Data Science</span>
            </div>
          </div>
        </div>
        
        <div className="landing-hero-image">
          <div className="landing-hero-image-container">
            <div className="image-glow"></div>
            <img src={logoGif} alt="TYFOR Dashboard" className="landing-hero-img animated-dashboard" />

          </div>
        </div>
        
        <div className="hero-scroll-indicator">
          <div className="mouse"></div>
          <p>Scroll to explore</p>
        </div>
      </section>
      
      {/* Features Section - Professional Redesign */}
      <section className={`landing-features ${isVisible.features ? 'visible' : ''}`} id="features">
        <div className="features-background">
          <div className="features-gradient"></div>
          <div className="features-particles"></div>
          <div className="features-geometric"></div>
          <div className="features-overlay"></div>
        </div>
        
        <div className="features-container">
          <div className="features-header">
            <span className="features-eyebrow">Comprehensive Platform</span>
            <h2 className="features-title">
              Powerful Data-Driven Football <span className="features-title-highlight">Analytics</span>
            </h2>
            <div className="features-description">
              <p>Six integrated modules engineered to transform football operations, youth development, 
              and talent acquisition through advanced data science.</p>
            </div>
          </div>
          
          <div className="features-tabs">
            <div className="features-tabs-nav">
              <button 
                className={`tab-btn ${activeTab === 0 ? 'active' : ''}`} 
                onClick={() => handleTabChange(0)}
                data-feature="youth"
              >
                <FontAwesomeIcon icon={faUsers} />
                <span>Youth Development</span>
              </button>
              <button 
                className={`tab-btn ${activeTab === 1 ? 'active' : ''}`} 
                onClick={() => handleTabChange(1)}
                data-feature="scout"
              >
                <FontAwesomeIcon icon={faLightbulb} />
                <span>Scouting Network</span>
              </button>
              <button 
                className={`tab-btn ${activeTab === 2 ? 'active' : ''}`} 
                onClick={() => handleTabChange(2)}
                data-feature="match"
              >
                <FontAwesomeIcon icon={faFutbol} />
                <span>Match Analysis</span>
              </button>
              <button 
                className={`tab-btn ${activeTab === 3 ? 'active' : ''}`} 
                onClick={() => handleTabChange(3)}
                data-feature="viz"
              >
                <FontAwesomeIcon icon={faChartPie} />
                <span>Performance Visualization</span>
              </button>
              <button 
                className={`tab-btn ${activeTab === 4 ? 'active' : ''}`} 
                onClick={() => handleTabChange(4)}
                data-feature="transfer"
              >
                <FontAwesomeIcon icon={faBullseye} />
                <span>Transfer Strategy</span>
              </button>
              <button 
                className={`tab-btn ${activeTab === 5 ? 'active' : ''}`} 
                onClick={() => handleTabChange(5)}
                data-feature="prediction"
              >
                <FontAwesomeIcon icon={faBrain} />
                <span>Score Prediction</span>
              </button>
            </div>
            
            <div className="features-content">
              <div className={`feature-panel ${activeTab === 0 ? 'active' : ''}`} data-feature="youth">
                <div className="feature-grid">
                  <div className="feature-content">
                    <h3 className="feature-title">Youth Development</h3>
                    <p className="feature-description">Track and monitor young players' training sessions and match performances with detailed metrics and visualization tools.</p>
                    
                    <ul className="feature-list">
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faRunning} /></span>
                        <div className="feature-list-content">
                          <h4>Physical Performance Metrics</h4>
                          <p>Collect and analyze data on speed, agility, and strength for young athletes.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartLine} /></span>
                        <div className="feature-list-content">
                          <h4>Endurance Tracking</h4>
                          <p>Monitor stamina and cardiovascular development over time.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartPie} /></span>
                        <div className="feature-list-content">
                          <h4>Progress Visualization</h4>
                          <p>Interactive dashboards showing development trajectories and key milestones.</p>
                        </div>
                      </li>
                    </ul>
                    
                    <div className="feature-action">
                      <button className="feature-btn" onClick={() => navigate('/authentication')}>
                        <span>Try Youth Development</span>
                        <FontAwesomeIcon icon={faArrowRight} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="feature-visual">
                    <div className="feature-visual-wrapper youth-visual">
                      <div className="feature-visual-indicator"></div>
                      <div className="feature-visual-glow"></div>
                      <div className="feature-visual-icon">
                        <FontAwesomeIcon icon={faUsers} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className={`feature-panel ${activeTab === 1 ? 'active' : ''}`} data-feature="scout">
                <div className="feature-grid">
                  <div className="feature-content">
                    <h3 className="feature-title">Scouting Network</h3>
                    <p className="feature-description">Discover promising talents from TFF 1st League and Polish leagues using advanced statistical models and data-driven recommendations.</p>
                    
                    <ul className="feature-list">
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faSearch} /></span>
                        <div className="feature-list-content">
                          <h4>Position-Based Recommendations</h4>
                          <p>AI-powered talent discovery based on specific position requirements.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faUsers} /></span>
                        <div className="feature-list-content">
                          <h4>Early Talent Discovery</h4>
                          <p>Identify promising players before they reach peak market value.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartLine} /></span>
                        <div className="feature-list-content">
                          <h4>Comparative Player Analysis</h4>
                          <p>Side-by-side statistical comparisons of potential recruits.</p>
                        </div>
                      </li>
                    </ul>
                    
                    <div className="feature-action">
                      <button className="feature-btn" onClick={() => navigate('/authentication')}>
                        <span>Try Scouting Network</span>
                        <FontAwesomeIcon icon={faArrowRight} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="feature-visual">
                    <div className="feature-visual-wrapper scout-visual">
                      <div className="feature-visual-indicator"></div>
                      <div className="feature-visual-glow"></div>
                      <div className="feature-visual-icon">
                        <FontAwesomeIcon icon={faLightbulb} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className={`feature-panel ${activeTab === 2 ? 'active' : ''}`} data-feature="match">
                <div className="feature-grid">
                  <div className="feature-content">
                    <h3 className="feature-title">Match Analysis</h3>
                    <p className="feature-description">Generate detailed visual reports of game performance with event tracking and tactical analysis tools.</p>
                    
                    <ul className="feature-list">
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartPie} /></span>
                        <div className="feature-list-content">
                          <h4>Game Performance Visualizations</h4>
                          <p>Heat maps, player movement tracking, and possession analysis.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faFutbol} /></span>
                        <div className="feature-list-content">
                          <h4>Match Event Tracking</h4>
                          <p>Detailed recording of key game events with video integration.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartLine} /></span>
                        <div className="feature-list-content">
                          <h4>Historical Data Comparisons</h4>
                          <p>Compare current match performance against historical patterns.</p>
                        </div>
                      </li>
                    </ul>
                    
                    <div className="feature-action">
                      <button className="feature-btn" onClick={() => navigate('/authentication')}>
                        <span>Try Match Analysis</span>
                        <FontAwesomeIcon icon={faArrowRight} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="feature-visual">
                    <div className="feature-visual-wrapper match-visual">
                      <div className="feature-visual-indicator"></div>
                      <div className="feature-visual-glow"></div>
                      <div className="feature-visual-icon">
                        <FontAwesomeIcon icon={faFutbol} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className={`feature-panel ${activeTab === 3 ? 'active' : ''}`} data-feature="viz">
                <div className="feature-grid">
                  <div className="feature-content">
                    <h3 className="feature-title">Performance Visualization</h3>
                    <p className="feature-description">Interactive charts and comparative statistics across different seasons for in-depth talent tracking and analysis.</p>
                    
                    <ul className="feature-list">
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartPie} /></span>
                        <div className="feature-list-content">
                          <h4>Dynamic Interactive Charts</h4>
                          <p>Customizable data visualizations for in-depth performance analysis.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartLine} /></span>
                        <div className="feature-list-content">
                          <h4>Performance Trend Analysis</h4>
                          <p>Identify development patterns and performance trajectories.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faUsers} /></span>
                        <div className="feature-list-content">
                          <h4>Coaching Staff Interpretations</h4>
                          <p>Data-driven insights for coaching decision support.</p>
                        </div>
                      </li>
                    </ul>
                    
                    <div className="feature-action">
                      <button className="feature-btn" onClick={() => navigate('/authentication')}>
                        <span>Try Performance Visualization</span>
                        <FontAwesomeIcon icon={faArrowRight} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="feature-visual">
                    <div className="feature-visual-wrapper viz-visual">
                      <div className="feature-visual-indicator"></div>
                      <div className="feature-visual-glow"></div>
                      <div className="feature-visual-icon">
                        <FontAwesomeIcon icon={faChartPie} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className={`feature-panel ${activeTab === 4 ? 'active' : ''}`} data-feature="transfer">
                <div className="feature-grid">
                  <div className="feature-content">
                    <h3 className="feature-title">Transfer Strategy</h3>
                    <p className="feature-description">Optimize transfer decisions through historical data analysis and financial alignment tools for budget-conscious clubs.</p>
                    
                    <ul className="feature-list">
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartLine} /></span>
                        <div className="feature-list-content">
                          <h4>Historical Transfer Analysis</h4>
                          <p>Understand market trends and player valuation patterns.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faBullseye} /></span>
                        <div className="feature-list-content">
                          <h4>Risk Assessment Tools</h4>
                          <p>Evaluate performance consistency and injury history before recruitment.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartPie} /></span>
                        <div className="feature-list-content">
                          <h4>Value Optimization Models</h4>
                          <p>Identify players with the best performance-to-cost ratio.</p>
                        </div>
                      </li>
                    </ul>
                    
                    <div className="feature-action">
                      <button className="feature-btn" onClick={() => navigate('/authentication')}>
                        <span>Try Transfer Strategy</span>
                        <FontAwesomeIcon icon={faArrowRight} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="feature-visual">
                    <div className="feature-visual-wrapper transfer-visual">
                      <div className="feature-visual-indicator"></div>
                      <div className="feature-visual-glow"></div>
                      <div className="feature-visual-icon">
                        <FontAwesomeIcon icon={faBullseye} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className={`feature-panel ${activeTab === 5 ? 'active' : ''}`} data-feature="prediction">
                <div className="feature-grid">
                  <div className="feature-content">
                    <h3 className="feature-title">Score Prediction</h3>
                    <p className="feature-description">Machine learning models that predict match outcomes based on historical data and player performance metrics.</p>
                    
                    <ul className="feature-list">
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faBrain} /></span>
                        <div className="feature-list-content">
                          <h4>ML Prediction Models</h4>
                          <p>AI-powered algorithms trained on extensive match history data.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faUsers} /></span>
                        <div className="feature-list-content">
                          <h4>Optimal Lineup Suggestions</h4>
                          <p>Data-driven team composition recommendations for specific opponents.</p>
                        </div>
                      </li>
                      <li className="feature-list-item">
                        <span className="feature-list-icon"><FontAwesomeIcon icon={faChartPie} /></span>
                        <div className="feature-list-content">
                          <h4>Strategic Decision Support</h4>
                          <p>Outcome probabilities for different tactical approaches.</p>
                        </div>
                      </li>
                    </ul>
                    
                    <div className="feature-action">
                      <button className="feature-btn" onClick={() => navigate('/authentication')}>
                        <span>Try Score Prediction</span>
                        <FontAwesomeIcon icon={faArrowRight} />
                      </button>
                    </div>
                  </div>
                  
                  <div className="feature-visual">
                    <div className="feature-visual-wrapper prediction-visual">
                      <div className="feature-visual-indicator"></div>
                      <div className="feature-visual-glow"></div>
                      <div className="feature-visual-icon">
                        <FontAwesomeIcon icon={faBrain} />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="features-cta">
            <div className="features-cta-content">
              <h3>Ready to Transform Your Club's Performance?</h3>
              <p>Experience all six powerful modules with our comprehensive platform.</p>
              <button className="features-cta-button" onClick={() => navigate('/authentication')}>
                <span>Start Free Trial</span>
                <FontAwesomeIcon icon={faArrowRight} />
              </button>
            </div>
          </div>
        </div>
      </section>        
      
      {/* Product Section - Enhanced with professional styling and interactive animations */}
      <section className={`landing-product ${isVisible.product ? 'visible' : ''}`} id="product">
        <div className="section-background">
          <div className="product-bg-gradient"></div>
          <div className="bg-dots"></div>
          <div className="geometric-patterns"></div>
        </div>
        
        <div className="product-animated-elements">
          <div className="floating-element-product chart-product">
            <FontAwesomeIcon icon={faChartPie} className="element-icon" />
            <div className="element-glow"></div>
          </div>
          <div className="floating-element-product ball-product">
            <FontAwesomeIcon icon={faFutbol} className="element-icon" />
            <div className="element-glow"></div>
          </div>
          <div className="floating-element-product stats-product">
            <FontAwesomeIcon icon={faChartLine} className="element-icon" />
            <div className="element-glow"></div>
          </div>
          <div className="floating-element-product brain-product">
            <FontAwesomeIcon icon={faBrain} className="element-icon" />
            <div className="element-glow"></div>
          </div>
          <div className="floating-element-product shield-product">
            <FontAwesomeIcon icon={faShieldAlt} className="element-icon" />
            <div className="element-glow"></div>
          </div>
        </div>
        
        <div className="landing-product-content">
          <div className="product-header">
            <span className="product-eyebrow">Our Solutions</span>
            <h2 className="landing-section-title">Why Choose <span className="product-title-highlight">TYFOR</span>?</h2>
            <div className="section-title-underline"></div>
            <p className="product-subtitle">Our platform empowers football clubs with cutting-edge solutions that transform operations and drive exceptional results on and off the pitch</p>
          </div>
          
          <div className="landing-product-grid">
            <div className="landing-product-benefits">
              <div className="landing-benefit">
                <div className="landing-benefit-icon">
                  <FontAwesomeIcon icon={faChartLine} />
                  <div className="icon-glow"></div>
                </div>
                <div className="landing-benefit-text">
                  <h3>Data-Driven Decisions</h3>                  <p>Transform raw data into actionable insights that drive strategic player development and acquisition choices through technology integration.</p>
                  <div className="benefit-progress-bar">
                    <div className="progress-value">0%</div>
                  </div>
                </div>
              </div>
              
              <div className="landing-benefit">
                <div className="landing-benefit-icon">
                  <FontAwesomeIcon icon={faRunning} />
                  <div className="icon-glow"></div>
                </div>
                <div className="landing-benefit-text">
                  <h3>Enhanced Youth Development</h3>
                  <p>Monitor physical, conditional, and endurance metrics of academy players with detailed graphical representations, enabling coaches to track development without expensive equipment.</p>
                  <div className="benefit-progress-bar">
                    <div className="progress-value">0%</div>
                  </div>
                </div>
              </div>
              
              <div className="landing-benefit">
                <div className="landing-benefit-icon">
                  <FontAwesomeIcon icon={faSearch} />
                  <div className="icon-glow"></div>
                </div>
                <div className="landing-benefit-text">
                  <h3>Advanced Scouting Network</h3>
                  <p>Discover promising talents from TFF 1st League and Polish Extraklasa using position-based recommendations and data science techniques, reducing reliance on agent recommendations.</p>
                  <div className="benefit-progress-bar">
                    <div className="progress-value">0%</div>
                  </div>
                </div>
              </div>
              
              <div className="landing-benefit">
                <div className="landing-benefit-icon">
                  <FontAwesomeIcon icon={faBullseye} />
                  <div className="icon-glow"></div>
                </div>
                <div className="landing-benefit-text">
                  <h3>Financial Sustainability</h3>
                  <p>Make financially responsible recruitment decisions by identifying talents within budget constraints, helping clubs maintain financial discipline and reduce reliance on external management influences.</p>
                  <div className="benefit-progress-bar">
                    <div className="progress-value">0%</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="product-stats-highlights">
            <div className="product-stat">
              <div className="stat-value">30+</div>
              <div className="stat-label">Anatolian Clubs</div>
            </div>
            <div className="product-stat">
              <div className="stat-value">1.5k+</div>
              <div className="stat-label">Players Tracked</div>
            </div>
            <div className="product-stat">
              <div className="stat-value">50+</div>
              <div className="stat-label">Teams Analyzed</div>
            </div>
          </div>
          
          <div className="product-action">
            <button className="product-cta-button" onClick={() => navigate('/authentication')}>
              <span>Experience the TYFOR Advantage</span>
              <FontAwesomeIcon icon={faArrowRight} className="button-icon" />
              <div className="button-glow"></div>
            </button>
            <p className="product-cta-note">No credit card required • 14-day free trial • Full access</p>
          </div>
        </div>
        </section>
      {/* About Section - Enhanced Professional Design */}
      <section className={`landing-about ${isVisible.about ? 'visible' : ''}`} id="about">
        <div className="about-background">
          <div className="about-bg-gradient"></div>
          <div className="about-bg-patterns"></div>
        </div>
        <div className="landing-about-image">
          <div className="image-glow-about"></div>
          <img src={logoImage} alt="TYFOR Logo" className="landing-about-img" />
          <div className="floating-element-about chart-about">
            <FontAwesomeIcon icon={faChartPie} className="element-icon" />
            <div className="element-glow-about"></div>
          </div>
          <div className="floating-element-about ball-about">
            <FontAwesomeIcon icon={faFutbol} className="element-icon" />
            <div className="element-glow-about"></div>
          </div>
          <div className="floating-element-about stats-about">
            <FontAwesomeIcon icon={faChartLine} className="element-icon" />
            <div className="element-glow-about"></div>
          </div>
        </div>
        <div className="landing-about-content">
          <div className="about-header">
            <h2 className="landing-section-title">About TYFOR</h2>
            <div className="section-title-underline"></div>
          </div>
          <div className="about-achievements">
            <div className="achievement-item">
              <div className="achievement-icon">
                <FontAwesomeIcon icon={faUsers} />
              </div>
              <div className="achievement-value">1,500+</div>
              <div className="achievement-label">Players Analyzed</div>
            </div>
            <div className="achievement-item">
              <div className="achievement-icon">
                <FontAwesomeIcon icon={faFutbol} />
              </div>
              <div className="achievement-value">30</div>
              <div className="achievement-label">Anatolian Clubs</div>
            </div>
            <div className="achievement-item">
              <div className="achievement-icon">
                <FontAwesomeIcon icon={faChartLine} />
              </div>
              <div className="achievement-value">95%</div>
              <div className="achievement-label">Analytics Accuracy</div>
            </div>
          </div>
          <div className="about-description">
            <p className="landing-about-text">
              TYFOR (<strong>T</strong>echnology for <strong>Y</strong>outh in <strong>F</strong>ootball <strong>O</strong>perations <strong>R</strong>esearch) 
              addresses significant challenges in talent development and recruitment faced by Anatolian football clubs. Formerly known 
              our platform integrates technology with data-driven approaches to transform football operations.
            </p>
            <p className="landing-about-text">
              Anatolian clubs face unique challenges: limited financial resources, insufficient infrastructure, and restricted access 
              to advanced technologies. This technological gap has led to growing disparities in competitiveness, where promising talents 
              are frequently lost to wealthier clubs.
            </p>
            <p className="landing-about-text highlight-text">
              Our mission is to provide systematic youth talent development and data-driven scouting processes, reducing 
              clubs' dependence on player agents. We integrate six powerful modules:
            </p>
            <div className="module-list">
              <span className="module-item"><strong>Youth Talent Development</strong></span>
              <span className="module-item"><strong>Scouting Network</strong></span>
              <span className="module-item"><strong>Performance Visualization</strong></span>
              <span className="module-item"><strong>Transfer Strategy</strong></span>
              <span className="module-item"><strong>Match Analysis</strong></span>
              <span className="module-item"><strong>Match Score Prediction</strong></span>
            </div>
            <p className="landing-about-text">
              Developed as a Senior Design Project by Ali Rıza Ercan, TYFOR combines advanced data analytics, machine learning 
              algorithms, and visualization techniques to process player and match data from the Turkish First League and 
              Polish Extraklasa, enabling Anatolian clubs to achieve sustainable talent development and efficient 
              resource management in professional football.
            </p>
          </div>
          <div className="landing-about-buttons">
            <button className="landing-primary-button" onClick={() => navigate('/authentication')}>
              <span>Try TYFOR Now</span>
              <FontAwesomeIcon icon={faArrowRight} className="button-icon" />
            </button>
          </div>
        </div>
      </section>      
      
      {/* Technology Innovation Section - Updated with better styling */}
      <section id="tech" className={`landing-tech ${isVisible.tech ? 'visible' : ''}`}>
        <div className="tech-background">
          <div className="tech-bg-shape"></div>
        </div>
        <div className="tech-container">
          <div className="tech-header">
            <h2>Data-Driven Football Innovation</h2>
            <p>Our cutting-edge platform leverages advanced technologies to revolutionize football operations for clubs across Turkey</p>
          </div>
          <div className="tech-grid">
            <div className="tech-card">
              <div className="tech-card-icon">
                <FontAwesomeIcon icon={faDatabase} />
              </div>
              <h3>Advanced Data Science</h3>
              <p>Our platform employs sophisticated machine learning models and statistical analysis techniques to transform vast quantities of football data into actionable insights for clubs with limited technical resources.</p>
            </div>
            
            <div className="tech-card">
              <div className="tech-card-icon">
                <FontAwesomeIcon icon={faChartPie} />
              </div>
              <h3>Interactive Visualizations</h3>
              <p>Comprehensive data visualization tools provide dynamic interactive charts and comparative statistics that enable tracking player development and match performance across different seasons with unprecedented clarity.</p>
            </div>
            
            <div className="tech-card">
              <div className="tech-card-icon">
                <FontAwesomeIcon icon={faBrain} />
              </div>
              <h3>AI-Powered Predictions</h3>
              <p>Proprietary machine learning algorithms analyze historical data from Turkish and Polish leagues to predict match outcomes with high accuracy, offering strategic decision support for optimal lineup selections.</p>
            </div>
            
            <div className="tech-card">
              <div className="tech-card-icon">
                <FontAwesomeIcon icon={faFutbol} />
              </div>
              <h3>Comprehensive Analysis</h3>
              <p>State-of-the-art video analysis tools track player movements, events, and tactical approaches during matches, providing insights that were previously only available to top-tier clubs with significant financial resources.</p>
            </div>
          </div>
        </div>
      </section>      
      
      {/* Testimonials Section - Professional Redesign */}
      <section className={`landing-testimonials ${isVisible.testimonials ? 'visible' : ''}`} ref={testimonialsRef} id="testimonials">
        <div className="testimonial-bg">
          <div className="testimonial-overlay"></div>
        </div>
        
        <div className="testimonial-floating-elements">
          <div className="testimonial-element quote-element">
            <FontAwesomeIcon icon={faQuoteRight} />
          </div>
          <div className="testimonial-element star-element">
            <FontAwesomeIcon icon={faStar} />
          </div>
        </div>
        
        <div className="testimonial-container">
          <div className="testimonial-header">
            <h2>What Our Partners Say</h2>
            <p>Success stories from Turkish football clubs achieving remarkable results with TYFOR</p>
          </div>
          
          <div className="testimonial-slider">
            <div className={`testimonial-card ${activeTestimonial === 0 ? 'active' : ''}`}>
              <div className="testimonial-quote">"TYFOR has completely transformed our youth development process. We can now track player progress with scientific precision and make data-driven decisions that help us identify and nurture talent much earlier. This system has given us capabilities we previously thought were only available to top European clubs."</div>
              <div className="testimonial-author">
                <div className="testimonial-author-avatar">
                  <FontAwesomeIcon icon={faUser} />
                </div>
                <div className="testimonial-author-info">
                  <div className="testimonial-author-name">Technical Director</div>
                  <div className="testimonial-author-title">Eskişehirspor Youth Academy</div>
                </div>
              </div>
            </div>
            
            <div className={`testimonial-card ${activeTestimonial === 1 ? 'active' : ''}`}>
              <div className="testimonial-quote">"The scouting network module has revolutionized how we discover talent. We've identified promising players that perfectly fit our system and budget constraints. As an Anatolian club with limited resources, TYFOR gives us the competitive edge we need in the modern football landscape."</div>
              <div className="testimonial-author">
                <div className="testimonial-author-avatar">
                  <FontAwesomeIcon icon={faUser} />
                </div>
                <div className="testimonial-author-info">
                  <div className="testimonial-author-name">Recruitment Manager</div>
                  <div className="testimonial-author-title">Bursaspor FC</div>
                </div>
              </div>
            </div>
            
            <div className={`testimonial-card ${activeTestimonial === 2 ? 'active' : ''}`}>
              <div className="testimonial-quote">"The match analysis capabilities have completely transformed our preparation process. Our coaching staff now has access to insights and statistical patterns that were previously invisible to us. We've improved our tactical approach and player development based on TYFOR's comprehensive analytics."</div>
              <div className="testimonial-author">
                <div className="testimonial-author-avatar">
                  <FontAwesomeIcon icon={faUser} />
                </div>
                <div className="testimonial-author-info">
                  <div className="testimonial-author-name">Head Coach</div>
                  <div className="testimonial-author-title">Leading Anatolian Premier League Club</div>
                </div>
              </div>
            </div>
          </div>
          
          <div className="testimonial-controls">
            <div className="testimonial-dots">
              <span 
                className={`dot ${activeTestimonial === 0 ? 'active' : ''}`} 
                onClick={() => setActiveTestimonial(0)}
              ></span>
              <span 
                className={`dot ${activeTestimonial === 1 ? 'active' : ''}`}
                onClick={() => setActiveTestimonial(1)}
              ></span>
              <span 
                className={`dot ${activeTestimonial === 2 ? 'active' : ''}`}
                onClick={() => setActiveTestimonial(2)}
              ></span>
            </div>
            
            <div className="testimonial-arrows">
              <button className="arrow-btn" onClick={() => setActiveTestimonial((activeTestimonial - 1 + 3) % 3)}>
                <FontAwesomeIcon icon={faChevronLeft} />
              </button>
              <button className="arrow-btn" onClick={() => setActiveTestimonial((activeTestimonial + 1) % 3)}>
                <FontAwesomeIcon icon={faChevronRight} />
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Call-to-Action Section - Updated with better styling */}
      <section className="landing-cta-section">
        <div className="cta-overlay"></div>
        <div className="cta-container">
          <h2 className="cta-title">Ready to Revolutionize Your Football Club?</h2>
          <p className="cta-subtitle">Be among the first clubs to transform your talent development, scouting operations, and strategic decision-making with TYFOR's innovative platform.</p>
          
          <div className="cta-features-grid">
            <div className="cta-feature">
              <FontAwesomeIcon icon={faChartLine} className="cta-icon" />
              <h3>Data-Driven Decisions</h3>
              <p>Transform raw match and player data into actionable insights that drive strategic choices</p>
            </div>
            <div className="cta-feature">
              <FontAwesomeIcon icon={faUsers} className="cta-icon" />
              <h3>Youth Development</h3>
              <p>Monitor physical, conditional, and endurance metrics with detailed visualizations</p>
            </div>
            <div className="cta-feature">
              <FontAwesomeIcon icon={faFutbol} className="cta-icon" />
              <h3>Advanced Scouting</h3>
              <p>Discover promising talents that fit within your budget constraints and team needs</p>
            </div>
          </div>
          
          <div className="cta-action">
            <button className="cta-button" onClick={() => navigate('/authentication')}>
              Start Your Free 14-Day Trial
              <FontAwesomeIcon icon={faArrowRight} className="cta-button-icon" />
            </button>
            <p className="cta-note">No credit card required • Full platform access • Cancel anytime</p>
          </div>
          
        </div>
      </section>
            
      {/* Contact Section with Custom Footer */}      
      <section className={`landing-contact ${isVisible.contact ? 'visible' : ''}`} id="contact">
        <div className="contact-background">
          <div className="contact-bg-overlay"></div>
          <div className="contact-bg-pattern"></div>
        </div>
        
        <div className="contact-container">
          <div className="contact-content">
            <div className="contact-info">
              <h2 className="contact-title">Get in Touch</h2>
              <p className="contact-description">
                Have questions about TYFOR or want to see how our platform can benefit your club?
                Reach out to our team for more information, demonstrations, or partnership opportunities.
              </p>
              
              <div className="contact-methods">
                <div className="contact-method">
                  <div className="contact-icon">
                    <FontAwesomeIcon icon={faEnvelope} />
                  </div>
                  <div className="contact-text">
                    <h4>Email Us</h4>
                    <a href="mailto:info.tyfor@gmail.com">info.tyfor@gmail.com</a>
                  </div>
                </div>
                
                <div className="contact-method">
                  <div className="contact-icon">
                    <FontAwesomeIcon icon={faPhone} />
                  </div>
                  <div className="contact-text">
                    <h4>Call Us</h4>
                    <a href="tel:+905342402651">+90 534 240 2651</a>
                  </div>
                </div>
                
                <div className="contact-method">
                  <div className="contact-icon">
                    <FontAwesomeIcon icon={faMapMarkerAlt} />
                  </div>
                  <div className="contact-text">
                    <h4>Visit Us</h4>
                    <p>Turkey</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="contact-form-container">
              <form className="contact-form">
                <h3 className="form-title">Send us a message</h3>
                
                <div className="form-group">
                  <label htmlFor="name">Full Name</label>
                  <input type="text" id="name" name="name" placeholder="Your name" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="email">Email Address</label>
                  <input type="email" id="email" name="email" placeholder="Your email" required />
                </div>
                
                <div className="form-group">
                  <label htmlFor="subject">Subject</label>
                  <input type="text" id="subject" name="subject" placeholder="Subject" />
                </div>
                
                <div className="form-group">
                  <label htmlFor="message">Message</label>
                  <textarea id="message" name="message" rows="5" placeholder="Your message" required></textarea>
                </div>
                
                <button type="submit" className="form-submit-btn">
                  <span>Send Message</span>
                  <FontAwesomeIcon icon={faPaperPlane} />
                </button>
              </form>
            </div>
          </div>
        </div>
          {/* Enhanced Professional Footer */}
        <div className="landing-footer">
          <div className="landing-footer-content">
            <div className="landing-footer-info">
              <div className="landing-footer-brand">
                <img src={logoImage} alt="TYFOR Logo" className="landing-footer-logo" />
                <div className="landing-footer-brand-text">
                  <h3>TYFOR</h3>
                  <p>Technology for Youth in Football Operations Research</p>
                </div>
              </div>
              <p className="landing-footer-description">                Empowering football clubs with cutting-edge data analytics and AI-driven 
                talent development solutions. Be at the forefront of football innovation with our advanced platform.
              </p>
              <div className="landing-footer-contact-info">
                <div className="footer-contact-item">
                  <FontAwesomeIcon icon={faEnvelope} className="footer-icon" />
                  <span>info.tyfor@gmail.com</span>
                </div>
                <div className="footer-contact-item">
                  <FontAwesomeIcon icon={faPhone} className="footer-icon" />
                  <span>+90 534 240 2651</span>
                </div>
              </div>
            </div>
            
            <div className="landing-footer-sections">
              <div className="landing-footer-section">
                <h4>Platform</h4>
                <ul>
                  <li><a href="#features">Features</a></li>
                  <li><a href="#product">Solutions</a></li>
                  <li><a href="#about">About Us</a></li>
                  <li><a href="#testimonials">Testimonials</a></li>
                  <li><a href="#contact">Contact</a></li>
                </ul>
              </div>
              
              <div className="landing-footer-section">
                <h4>Solutions</h4>
                <ul>
                  <li><a href="#features">Youth Development</a></li>
                  <li><a href="#features">Scouting Network</a></li>
                  <li><a href="#features">Match Analysis</a></li>
                  <li><a href="#features">Transfer Strategy</a></li>
                </ul>
              </div>
              
              <div className="landing-footer-section">
                <h4>Legal</h4>
                <ul>
                  <li><a href="#" onClick={() => navigate('/privacy')}>Privacy Policy</a></li>
                  <li><a href="#" onClick={() => navigate('/terms')}>Terms of Service</a></li>
                  <li><a href="#" onClick={() => navigate('/data-policy')}>Data Policy</a></li>
                </ul>
              </div>
            </div>
          </div>
          
          <div className="landing-footer-social-container">
            <p className="landing-social-title">Follow TYFOR</p>
            <div className="landing-footer-social">
              <a href="https://twitter.com/tyfor" target="_blank" rel="noopener noreferrer" aria-label="Twitter">
                <FontAwesomeIcon icon={faTwitter} />
              </a>
              <a href="https://linkedin.com/company/tyfor" target="_blank" rel="noopener noreferrer" aria-label="LinkedIn">
                <FontAwesomeIcon icon={faLinkedinIn} />
              </a>
              <a href="https://instagram.com/tyfor" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
                <FontAwesomeIcon icon={faInstagram} />
              </a>
            </div>
          </div>
          
          <div className="landing-footer-bottom">
            <p>© {new Date().getFullYear()} TYFOR. All rights reserved.</p>
            <p>Designed & Developed by <span className="developer-name">Ali Rıza Ercan</span></p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;
