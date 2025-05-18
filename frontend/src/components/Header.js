import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { getCurrentUser, logout, getUserSettings, updateUserSettings, changePassword } from '../services/auth';
import { getNotifications, markNotificationRead } from '../services/notifications';
import defaultTeamLogo from '../assets/images/default_team_logo.png';
import TYFORLogo from '../assets/images/TYFOR.png';
import '../styles/Header.css';

const Header = () => {
  const navigate = useNavigate();
  const [currentTime, setCurrentTime] = useState(new Date());
  const headerRef = useRef(null);
  const [user, setUser] = useState(getCurrentUser());
  const [showNotifications, setShowNotifications] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [settingsError, setSettingsError] = useState(null);
  const [settingsSuccess, setSettingsSuccess] = useState(null);
  const [settingsForm, setSettingsForm] = useState({
    firstname: user?.firstname || '',
    lastname: user?.lastname || '',
    email: user?.email || ''
  });
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [passwordError, setPasswordError] = useState(null);
  const [passwordSuccess, setPasswordSuccess] = useState(null);
  const [isChangingPassword, setIsChangingPassword] = useState(false);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const notificationsData = await getNotifications();
        setNotifications(notificationsData);
        setUnreadCount(notificationsData.filter(n => !n.read).length);
      } catch (error) {
        console.error('Error fetching notifications:', error);
      }
    };    // İlk yüklemede bildirimleri al
    fetchNotifications();

    // Her 2 dakikada bir bildirimleri güncelle
    const notificationInterval = setInterval(fetchNotifications, 120000);

    // Kullanıcı bilgilerini localStorage'dan tekrar al
    const userInterval = setInterval(() => {
      const currentUser = getCurrentUser();
      if (JSON.stringify(currentUser) !== JSON.stringify(user)) {
        setUser(currentUser);
      }
    }, 60000);

    return () => {
      clearInterval(notificationInterval);
      clearInterval(userInterval);
    };
  }, [user]);
  // Load user settings
  useEffect(() => {
    const loadUserSettings = async () => {
      try {
        const settings = await getUserSettings();
        setSettingsForm({
          firstname: settings.account.firstname || '',
          lastname: settings.account.lastname || '',
          email: settings.notifications.email || ''
        });
      } catch (error) {
        console.error('Error loading settings:', error);
        setSettingsError('Failed to load settings');
      }
    };

    if (user) {
      loadUserSettings();
      
      // Settings sadece görünür olduğunda yenile
      let settingsInterval;
      if (showSettings) {
        settingsInterval = setInterval(loadUserSettings, 300000); // 5 dakikada bir
      }
      return () => {
        if (settingsInterval) {
          clearInterval(settingsInterval);
        }
      };
    }
  }, [user, showSettings]);

  const handleLogout = async () => {
    await logout();
    navigate('/authentication');
  };

  const handleNotificationClick = async (notification) => {
    if (!notification.read) {
      try {
        await markNotificationRead(notification.id);
        // Bildirimleri yenile
        const updatedNotifications = notifications.map(n =>
          n.id === notification.id ? { ...n, read: true } : n
        );
        setNotifications(updatedNotifications);
        setUnreadCount(prev => prev - 1);
      } catch (error) {
        console.error('Error marking notification as read:', error);
      }
    }
  };

  const handleNotificationsClick = () => {
    setShowNotifications(!showNotifications);
    setShowSettings(false);
    setShowPasswordModal(false);
  };

  const handleSettingsClick = () => {
    setShowSettings(!showSettings);
    setShowNotifications(false);
    setShowPasswordModal(false);
  };

  const handlePasswordModalClick = () => {
    setShowPasswordModal(true);
    setShowSettings(false);
    setShowNotifications(false);
  };

  const handleSettingsChange = (field, value) => {
    setSettingsForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleSettingsSubmit = async (e) => {
    e?.preventDefault();
    setSettingsError(null);
    setSettingsSuccess(null);

    try {
      if (!settingsForm.firstname || !settingsForm.lastname) {
        setSettingsError('First name and last name are required');
        return;
      }

      const settings = {
        account: {
          firstname: settingsForm.firstname,
          lastname: settingsForm.lastname
        },
        notifications: {
          email: settingsForm.email
        }
      };

      const response = await updateUserSettings(settings);
      
      if (response.message) {
        setSettingsSuccess(response.message);
      } else {
        setSettingsSuccess('Settings updated successfully');
      }

      // Update local user data
      const currentUser = getCurrentUser();
      const updatedUser = {
        ...currentUser,
        firstname: settingsForm.firstname,
        lastname: settingsForm.lastname,
        email: settingsForm.email
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));
      setUser(updatedUser);

    } catch (error) {
      console.error('Settings update error:', error);
      setSettingsError(error.message || 'Failed to update settings. Please try again.');
    }
  };

  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setPasswordError(null);
    setPasswordSuccess(null);
    setIsChangingPassword(true);

    try {
      if (passwordForm.newPassword !== passwordForm.confirmPassword) {
        setPasswordError('New passwords do not match');
        return;
      }

      await changePassword(user.id, passwordForm.newPassword);
      setPasswordSuccess('Password changed successfully');
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setShowPasswordModal(false);
    } catch (error) {
      setPasswordError(error.message || 'Failed to change password');
    } finally {
      setIsChangingPassword(false);
    }
  };

  const handlePasswordFormChange = (field, value) => {
    setPasswordForm(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (    <header ref={headerRef} className="header">
    <div className="header-content">
      <div className="left-section">
        <button className="tyfor-logo-button" onClick={() => navigate('/dashboard')}>
          <img src={TYFORLogo} alt="TYFOR Logo" className="tyfor-logo" />
        </button>
        <div className="team-logo-section">
          <img 
            src={user?.team?.logo || defaultTeamLogo}
            alt={user?.team?.name || 'Team Logo'} 
            onError={(e) => {e.target.src = defaultTeamLogo}}
            className="team-logo"
          />
        </div>
        <div className="team-info">
          {user?.team && (
            <>
              <h3 className="team-name">{user.team.name}</h3>
              <span className="league-name">{user.team.league}</span>
            </>
          )}
        </div>
      </div>

      <div className="center-section">
        <div className="user-info">
          <h2 className="user-name">{user?.firstname} {user?.lastname}</h2>
          <div className="user-meta">
            <span className="role-badge">{user?.role}</span>
            <span className="time">{currentTime.toLocaleTimeString()}</span>
          </div>
        </div>
      </div>

      <div className="right-section">
        <div className="user-status">
          <div className="status-indicator online"></div>
          <span>Active</span>
        </div>
        <div className="divider"></div>          <div style={{ position: 'relative' }}>
          <button className="action-button notifications" onClick={handleNotificationsClick}>
            <i className="notification-icon"></i>
            {unreadCount > 0 && <span className="notification-badge">{unreadCount}</span>}
          </button>
        </div>
        <div style={{ position: 'relative' }}>
          <button className="action-button settings" onClick={handleSettingsClick}>
            <i className="settings-icon"></i>
          </button>
        </div>
        <button className="logout-button" onClick={handleLogout}>
          <i className="logout-icon"></i>
          <span>Logout</span>
        </button>

        {/* Dropdown Overlays */}
        {(showNotifications || showSettings) && (
          <div className="dropdown-overlay" onClick={() => {
            setShowNotifications(false);
            setShowSettings(false);
          }}></div>
        )}

        {/* Notifications Dropdown */}
        {showNotifications && (
          <div className="notifications-dropdown">
            <div className="notifications-header">
              <h3>Notifications</h3>
              <button className="close-button" onClick={() => setShowNotifications(false)}>×</button>
            </div>
            <div className="notifications-list">
              {notifications.length === 0 ? (
                <div className="no-notifications">No notifications</div>
              ) : (
                notifications.map(notification => (
                  <div
                    key={notification.id}
                    className={`notification-item ${notification.read ? 'read' : 'unread'}`}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <p className="notification-message">{notification.message}</p>
                    <span className="notification-time">
                      {new Date(notification.created_at).toLocaleString()}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        )}          {/* Settings Dropdown */}
        {showSettings && (
          <div className="settings-dropdown">
            <div className="settings-header">
              <h3>Settings</h3>
              <button className="close-button" onClick={() => setShowSettings(false)}>×</button>
            </div>
            <div className="settings-content">
              <div className="settings-tabs">
                <div className="settings-section profile-section">
                  <div className="section-header">
                    <i className="profile-icon"></i>
                    <h4>Profile Settings</h4>
                  </div>
                  <form onSubmit={handleSettingsSubmit} className="settings-form">
                    <div className="form-row">
                      <div className="form-group">
                        <label>First Name</label>
                        <input
                          type="text"
                          value={settingsForm.firstname}
                          onChange={(e) => handleSettingsChange('firstname', e.target.value)}
                          placeholder="First Name"
                          className="settings-input"
                        />
                      </div>
                      <div className="form-group">
                        <label>Last Name</label>
                        <input
                          type="text"
                          value={settingsForm.lastname}
                          onChange={(e) => handleSettingsChange('lastname', e.target.value)}
                          placeholder="Last Name"
                          className="settings-input"
                        />
                      </div>
                    </div>
                    <div className="form-group">
                      <label>Email Notifications</label>
                      <input
                        type="email"
                        value={settingsForm.email}
                        onChange={(e) => handleSettingsChange('email', e.target.value)}
                        placeholder="Email for notifications"
                        className="settings-input"
                      />
                    </div>
                  </form>
                </div>

                <div className="settings-section security-section">
                  <div className="section-header">
                    <i className="security-icon"></i>
                    <h4>Security Settings</h4>
                  </div>
                  <div className="security-info">                      <div className="security-row">
                      <div className="security-item">
                        <span className="security-label">
                          <i className="login-icon"></i>
                          Last Login
                        </span>
                        <span className="security-value">
                          {user?.last_login 
                            ? new Date(user.last_login).toLocaleString('tr-TR', {
                                year: 'numeric',
                                month: '2-digit',
                                day: '2-digit',
                                hour: '2-digit',
                                minute: '2-digit',
                                hour12: false
                              })
                            : 'First time login'
                          }
                        </span>
                      </div>
                      <div className="security-item login-attempts">
                        <span className="security-label">
                          <i className="warning-icon"></i>
                          Login Attempts
                        </span>                          <span className={`security-value ${user?.wrong_login_attempt > 0 ? 'warning' : 'success'}`}>
                          {user?.wrong_login_attempt > 0 
                            ? `${user.wrong_login_attempt} failed attempts`
                            : 'No failed attempts'
                          }
                        </span>
                      </div>
                    </div>
                    {user?.wrong_login_attempt > 0 && (
                      <div className="security-item warning">
                        <span className="security-label">
                          <i className="warning-icon"></i>
                          Failed Attempts
                        </span>
                        <span className="security-value warning">{user.wrong_login_attempt}</span>
                      </div>
                    )}
                  </div>
                  <button
                    className="security-button change-password-btn"
                    onClick={handlePasswordModalClick}
                  >
                    <i className="password-icon"></i>
                    Change Password
                  </button>
                </div>
              </div>

              <div className="settings-footer">
                {settingsError && (
                  <div className="settings-error">
                    <i className="error-icon"></i>
                    {settingsError}
                  </div>
                )}
                {settingsSuccess && (
                  <div className="settings-success">
                    <i className="success-icon"></i>
                    {settingsSuccess}
                  </div>
                )}
                <button
                  className="primary-button save-settings-btn"
                  onClick={handleSettingsSubmit}
                >
                  <i className="save-icon"></i>
                  Save Changes
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Password Modal */}
        {showPasswordModal && (
          <div className="settings-dropdown">
            <div className="settings-header">
              <h3>Change Password</h3>
              <button className="close-button" onClick={() => setShowPasswordModal(false)}>×</button>
            </div>
            <div className="settings-content">
              <form onSubmit={handlePasswordChange} className="settings-form">
                <div className="form-group">
                  <label htmlFor="currentPassword">Current Password</label>
                  <input
                    type="password"
                    id="currentPassword"
                    value={passwordForm.currentPassword}
                    onChange={(e) => handlePasswordFormChange('currentPassword', e.target.value)}
                    placeholder="Enter current password"
                    className="settings-input"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="newPassword">New Password</label>
                  <input
                    type="password"
                    id="newPassword"
                    value={passwordForm.newPassword}
                    onChange={(e) => handlePasswordFormChange('newPassword', e.target.value)}
                    placeholder="Enter new password"
                    className="settings-input"
                    required
                  />
                </div>
                
                <div className="form-group">
                  <label htmlFor="confirmPassword">Confirm New Password</label>
                  <input
                    type="password"
                    id="confirmPassword"
                    value={passwordForm.confirmPassword}
                    onChange={(e) => handlePasswordFormChange('confirmPassword', e.target.value)}
                    placeholder="Confirm new password"
                    className="settings-input"
                    required
                  />
                </div>

                {passwordError && (
                  <div className="settings-error">
                    <i className="error-icon"></i>
                    {passwordError}
                  </div>
                )}
                
                {passwordSuccess && (
                  <div className="settings-success">
                    <i className="success-icon"></i>
                    {passwordSuccess}
                  </div>
                )}

                <div className="settings-footer">
                  <button
                    type="submit"
                    className="primary-button save-settings-btn"
                    disabled={isChangingPassword}
                  >
                    <i className="save-icon"></i>
                    {isChangingPassword ? 'Changing...' : 'Change Password'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  </header>
  );
};

export default Header;
