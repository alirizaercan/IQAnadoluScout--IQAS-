// frontend/src/services/auth.js

import axios from 'axios';

const API_URL = 'http://localhost:5056/api/auth';

// Create axios instance with common headers
export const authApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000  // 10 second timeout
});

// Add token to headers if it exists
authApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
      
      // For admin routes, add extra logging
      if (config.url.includes('/admin/')) {
        console.log(`Request to admin route: ${config.url}`);
        console.log(`Token added to headers: ${!!token}`);
        
        // Check if user is admin
        try {
          const user = JSON.parse(localStorage.getItem('user'));
          console.log(`Current user is admin: ${user?.is_admin}`);
          
          // If this is an admin endpoint but user isn't admin, log warning
          if (!user?.is_admin) {
            console.warn('Warning: Non-admin user attempting to access admin endpoint');
          }
        } catch (e) {
          console.error('Error checking user admin status:', e);
        }
      }
    } else {
      console.warn(`No token available for request to: ${config.url}`);
    }
    return config;
  },
  error => {
    console.error('Request interceptor error:', error);
    return Promise.reject(error);
  }
);

// Add response interceptor for better error handling
authApi.interceptors.response.use(
  response => response,
  error => {
    console.error('API Error:', error?.response?.data || error.message);
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/authentication';
    }
    throw error.response?.data || { message: 'Network error. Please check your connection.' };
  }
);

export const login = async (credentials) => {
  try {
    const response = await authApi.post('/login', credentials);
    if (response.data.token) {
      localStorage.setItem('token', response.data.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

export const createAdmin = async (adminData) => {
  try {
    const response = await authApi.post('/admin/create', adminData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const createUser = async (userData) => {
  try {
    const response = await authApi.post('/admin/create-user', userData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const getTeams = async () => {
  try {
    const response = await authApi.get('/admin/teams');
    return response.data.teams;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const getUsers = async () => {
  try {
    const response = await authApi.get('/admin/users');
    return response.data.users;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const deleteUser = async (userId) => {
  try {
    const response = await authApi.delete(`/admin/users/${userId}`);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const isAuthenticated = () => {
  return localStorage.getItem('token') !== null;
};

export const isAdmin = () => {
  const user = JSON.parse(localStorage.getItem('user'));
  return user && user.is_admin === true;
};

export const changePassword = async (userId, newPassword) => {
  try {
    const response = await authApi.post('/change-password', {
      user_id: userId,
      new_password: newPassword
    });
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const getCurrentUser= () => {
  return JSON.parse(localStorage.getItem('user'));
};

export const getUserSettings = async () => {
  try {
    const response = await authApi.get('/settings');
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const updateUserSettings = async (settings) => {
  try {
    const response = await authApi.put('/settings', settings);
    
    // Update local storage with new user data
    if (response.data.success) {
      const currentUser = JSON.parse(localStorage.getItem('user')) || {};
      const updatedUser = {
        ...currentUser,
        firstname: settings.account.firstname,
        lastname: settings.account.lastname,
        email: settings.notifications.email
      };
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
    
    return response.data;
  } catch (error) {
    console.error('Settings update error:', error);
    throw error.response?.data || { message: 'Failed to update settings. Please try again.' };
  }
};