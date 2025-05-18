import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/AdminPanelPage.css';
import { createClubUser, getAllTeams, getAllUsers, deleteUserAccount } from '../services/admin';
import { sendBroadcastNotification } from '../services/notifications';
import { logout, getCurrentUser } from '../services/auth';
import { checkToken } from '../utils/tokenChecker';
import { checkAdminAuth } from '../utils/debugAuth';
import userIcon from '../assets/images/user_icon.png';

const AdminPanelPage = () => {
  const navigate = useNavigate();
  
  // Current admin user state
  const [currentAdmin, setCurrentAdmin] = useState(null);

  // Form data for creating new user
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    firstname: '',
    lastname: '',
    role: 'coach', // Default role
    team_id: ''
  });

  // Lists for dropdown options and user management
  const [teams, setTeams] = useState([]);
  const [users, setUsers] = useState([]);
    // UI state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [accessKey, setAccessKey] = useState(null);
  const [activeTab, setActiveTab] = useState('create-user');
  const [confirmDelete, setConfirmDelete] = useState(null);
  const [showNotificationForm, setShowNotificationForm] = useState(false);
  const [notificationMessage, setNotificationMessage] = useState('');
  const [notificationLoading, setNotificationLoading] = useState(false);

  // Fetch current admin, teams and users on component mount
  useEffect(() => {
    const admin = getCurrentUser();
    if (!admin || !admin.is_admin) {
      navigate('/');
      return;
    }
    
    // Verify admin authentication status
    const verifyAdminAuth = async () => {
      const authStatus = await checkAdminAuth();
      console.log('Admin auth verification:', authStatus);
      
      if (!authStatus.success || !authStatus.data?.is_admin) {
        console.error('Admin auth failed:', authStatus.message);
        setError(`Authentication error: ${authStatus.message}. Please try logging out and back in.`);
      }
    };
    
    verifyAdminAuth();
    setCurrentAdmin(admin);
    fetchTeams();
    fetchUsers();
  }, [navigate]);

  // Fetch all teams for dropdown
  const fetchTeams = async () => {
    try {
      const teamsData = await getAllTeams();
      setTeams(teamsData);
      
      // Set default team_id if teams are available
      if (teamsData.length > 0) {
        setFormData(prev => ({ ...prev, team_id: teamsData[0].team_id }));
      }
    } catch (err) {
      setError('Failed to load teams');
      console.error('Error fetching teams:', err);
    }
  };

  // Fetch all users for management
  const fetchUsers = async () => {
    try {
      const usersData = await getAllUsers();
      setUsers(usersData);
    } catch (err) {
      setError('Failed to load users');
      console.error('Error fetching users:', err);
    }
  };

  // Handle form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  // Handle form submission to create new user
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess(null);
    setAccessKey(null);
    
    try {
      const response = await createClubUser(formData);
      setSuccess('User created successfully');
      setAccessKey(response.access_key);
      
      // Reset form
      setFormData({
        username: '',
        email: '',
        firstname: '',
        lastname: '',
        role: 'coach',
        team_id: teams.length > 0 ? teams[0].team_id : ''
      });
      
      // Refresh user list
      fetchUsers();
      
    } catch (err) {
      setError(err.message || 'Failed to create user');
      console.error('Error creating user:', err);
    } finally {
      setLoading(false);
    }
  };

  // Copy access key to clipboard
  const copyAccessKey = () => {
    navigator.clipboard.writeText(accessKey);
    alert('Access key copied to clipboard!');
  };

  // Handle logout
  const handleLogout = () => {    logout();
    navigate('/authentication');
  };

  // Delete user with confirmation
  const handleDeleteUser = async (userId) => {
    if (confirmDelete === userId) {
      try {
        await deleteUserAccount(userId);
        setSuccess('User deleted successfully');
        fetchUsers(); // Refresh user list
        setConfirmDelete(null);
      } catch (err) {
        setError('Failed to delete user');
        console.error('Error deleting user:', err);
      }
    } else {
      setConfirmDelete(userId);
    }
  };

  // Cancel delete confirmation
  const cancelDelete = () => {
    setConfirmDelete(null);
  };  const handleNotificationSubmit = async (e) => {
    e.preventDefault();
    setNotificationLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      // First verify admin authentication
      const authStatus = await checkAdminAuth();
      console.log("Admin auth status before sending notification:", authStatus);
      
      if (!authStatus.success || !authStatus.data?.is_admin) {
        setError('Admin authentication failed. Please log out and log in again.');
        return;
      }
      
      // Proceed with sending notification
      await sendBroadcastNotification(notificationMessage);
      setSuccess('Notification sent successfully to all users');
      setNotificationMessage('');
      setShowNotificationForm(false);
    } catch (err) {
      console.error("Notification error:", err);
      // Provide more detailed error message
      if (err.message && err.message.includes('403')) {
        setError('Permission denied: Your account does not have admin privileges required to send notifications.');
      } else {
        setError(err.message || 'Failed to send notification. Please try again later.');
      }
    } finally {
      setNotificationLoading(false);
    }
  };

  return (
    <div className="admin-panel">
      <header className="admin-header">
        <div className="admin-logo">
          <h1>Admin Panel</h1>
        </div>
        <div className="admin-user">
          <img src={userIcon} alt="Admin" className="admin-avatar"/>
          <span>{currentAdmin?.username || 'Admin'}</span>
          <button className="logout-btn" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <main className="admin-content">
        <div className="admin-sidebar">
          <h2>Navigation</h2>
          <ul>
            <li 
              className={activeTab === 'create-user' ? 'active' : ''}
              onClick={() => {
                setActiveTab('create-user');
                setShowNotificationForm(false);
              }}
            >
              Create User Account
            </li>
            <li 
              className={activeTab === 'manage-users' ? 'active' : ''}
              onClick={() => {
                setActiveTab('manage-users');
                setShowNotificationForm(false);
              }}
            >
              Manage Users
            </li>
            <li 
              className={activeTab === 'send-notification' ? 'active' : ''}
              onClick={() => {
                setActiveTab('send-notification');
                setShowNotificationForm(true);
              }}
            >
              Send Notification
            </li>
          </ul>
        </div>

        <div className="admin-main-content">
          {showNotificationForm && (
            <section className="send-notification-section">
              <h2>Send Notification</h2>
              
              {error && <div className="error-message">{error}</div>}
              {success && <div className="success-message">{success}</div>}
              
              <form onSubmit={handleNotificationSubmit}>
                <div className="form-group">
                  <label htmlFor="message">Message</label>
                  <textarea
                    id="message"
                    name="message"
                    value={notificationMessage}
                    onChange={(e) => setNotificationMessage(e.target.value)}
                    placeholder="Enter notification message"
                    required
                  />
                </div>
                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="create-btn" 
                    disabled={notificationLoading}
                  >
                    {notificationLoading ? 'Sending...' : 'Send Notification'}
                  </button>
                </div>
              </form>
            </section>
          )}

          {activeTab === 'create-user' && (
            <section className="create-user-section">
              <h2>Create Club User Account</h2>
              
              {error && <div className="error-message">{error}</div>}
              {success && !accessKey && <div className="success-message">{success}</div>}
              
              {accessKey && (
                <div className="access-key-box">
                  <h3>User Created Successfully!</h3>
                  <p>Access Key for the new user:</p>
                  <div className="key-display">
                    <code>{accessKey}</code>
                    <button onClick={copyAccessKey}>Copy</button>
                  </div>
                  <p className="key-instructions">
                    Save this key and provide it to the user. They will use this key to log in.
                    This key will not be displayed again.
                  </p>
                </div>
              )}
              
              <form onSubmit={handleSubmit}>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="firstname">First Name</label>
                    <input
                      type="text"
                      id="firstname"
                      name="firstname"
                      value={formData.firstname}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="lastname">Last Name</label>
                    <input
                      type="text"
                      id="lastname"
                      name="lastname"
                      value={formData.lastname}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="username">Username</label>
                    <input
                      type="text"
                      id="username"
                      name="username"
                      value={formData.username}
                      onChange={handleChange}
                      required
                    />
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="email">Email</label>
                    <input
                      type="email"
                      id="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      required
                    />
                  </div>
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="role">Role</label>
                    <select
                      id="role"
                      name="role"
                      value={formData.role}
                      onChange={handleChange}
                      required
                    >
                      <option value="coach">Coach</option>
                      <option value="analyst">Analyst</option>
                      <option value="scout">Scout</option>
                      <option value="manager">Manager</option>
                      <option value="director">Director</option>
                    </select>
                  </div>
                  
                  <div className="form-group">
                    <label htmlFor="team_id">Team</label>
                    <select
                      id="team_id"
                      name="team_id"
                      value={formData.team_id}
                      onChange={handleChange}
                      required
                    >
                      {teams.map(team => (
                        <option key={team.team_id} value={team.team_id}>
                          {team.team_name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="form-actions">
                  <button 
                    type="submit" 
                    className="create-btn" 
                    disabled={loading}
                  >
                    {loading ? 'Creating...' : 'Create User'}
                  </button>
                </div>
              </form>
            </section>
          )}

          {activeTab === 'manage-users' && (
            <section className="manage-users-section">
              <h2>Manage Users</h2>
              
              {error && <div className="error-message">{error}</div>}
              {success && <div className="success-message">{success}</div>}
              
              <table className="users-table">
                <thead>
                  <tr>
                    <th>Username</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Role</th>
                    <th>Team</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.length === 0 && (
                    <tr>
                      <td colSpan="6" className="no-users">No users found</td>
                    </tr>
                  )}
                  
                  {users.map(user => (
                    <tr key={user.id}>
                      <td>{user.username}</td>
                      <td>{`${user.firstname || ''} ${user.lastname || ''}`}</td>
                      <td>{user.email}</td>
                      <td>{user.role || 'N/A'}</td>
                      <td>{user.club || 'N/A'}</td>
                      <td>
                        {confirmDelete === user.id ? (
                          <div className="delete-confirmation">
                            <button 
                              onClick={() => handleDeleteUser(user.id)}
                              className="confirm-delete-btn"
                            >
                              Confirm
                            </button>
                            <button 
                              onClick={cancelDelete}
                              className="cancel-delete-btn"
                            >
                              Cancel
                            </button>
                          </div>
                        ) : (
                          <button 
                            onClick={() => handleDeleteUser(user.id)}
                            className="delete-btn"
                          >
                            Delete
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </section>
          )}
        </div>
      </main>
    </div>
  );
};

export default AdminPanelPage;