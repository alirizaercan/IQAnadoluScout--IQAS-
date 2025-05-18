/* frontend/src/pages/AuthenticationPage.js */
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AuthenticationPage.css';
import { login, changePassword } from '../services/auth';
import logoImage from '../assets/images/TYFOR_auth.gif';
import userIcon from '../assets/images/user_icon.png';

const AuthenticationPage = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
  });
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [userId, setUserId] = useState(null);

  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prevState) => ({
      ...prevState,
      [name]: value,
    }));
  };
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match!');
      return;
    }
    
    try {      console.log('Sending password change request...');
      const data = await changePassword(userId, newPassword);
      console.log('Password change successful:', data);
      setShowPasswordModal(false);
      setError(null);
      
      // Successful password change
      if (data.user?.is_admin) {
        console.log('Navigating to admin...');
        navigate('/admin');
      } else {
        console.log('Navigating to dashboard...');
        navigate('/dashboard');
      }
    } catch (error) {
      console.error('Password change failed:', error);
      setError(error.message || 'Failed to change password');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      const response = await login(formData);
      setUserId(response.user.id);
      
      // Eğer kullanıcı access key ile giriş yaptıysa şifre değiştirme modalını göster
      if (response.user.needs_password_change) {
        setShowPasswordModal(true);
      } else {
        if (response.user.is_admin) {
          navigate('/admin');
        } else {
          navigate('/dashboard');
        }
      }
    } catch (error) {
      setError(error.message || 'Failed to login. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-container">
        <div className="logo-section">
          <img src={logoImage} alt="TYFOR Logo" className="logo" />
        </div>
        
        <div className="form-section">
          <div className="form-card">
            <div className="avatar-container">
              <div className="logo-overlay"></div>
              <img src={userIcon} alt="Avatar" className="avatar" />
            </div>
            
            <h2>Welcome Back</h2>
            <p className="subtitle">Sign in to your account</p>
            
            <form onSubmit={handleSubmit}>
              {error && (
                <div className="error-message">
                  <i className="error-icon">!</i>
                  <span>{error}</span>
                </div>
              )}
              
              <div className="form-group">
                <label htmlFor="username">Username or Access Key</label>
                <div className="input-wrapper">
                  <i className="input-icon user-icon"></i>
                  <input
                    type="text"
                    id="username"
                    name="username"
                    value={formData.username}
                    onChange={handleChange}
                    placeholder="Enter your username or access key"
                    required
                  />
                </div>
              </div>
              
              <div className="form-group">
                <label htmlFor="password">Password</label>
                <div className="input-wrapper">
                  <i className="input-icon password-icon"></i>
                  <input
                    type="password"
                    id="password"
                    name="password"
                    value={formData.password}
                    onChange={handleChange}
                    placeholder="Enter your password"
                  />
                </div>
              </div>
              
              <div className="button-container">
                <button 
                  type="submit" 
                  className="submit-button" 
                  disabled={loading}
                >
                  {loading ? (
                    <span className="loading-spinner"></span>
                  ) : (
                    'Sign In'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {showPasswordModal && (
        <div className="modal-overlay">
          <div className="password-modal">
            <h3>Set Your New Password</h3>
            <p>Please set a new password for your account.</p>
            
            <form onSubmit={handlePasswordChange}>
              <div className="form-group">
                <label htmlFor="newPassword">New Password</label>
                <input
                  type="password"
                  id="newPassword"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="Enter new password"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Confirm new password"
                  required
                />
              </div>
              
              <div className="button-container">
                <button type="submit" className="submit-button">
                  Set Password
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AuthenticationPage;