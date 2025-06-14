import axios from 'axios';

const API_URL = 'http://localhost:5056/api/auth';

// Create axios instance with common headers
const adminApi = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add token to headers if it exists
adminApi.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Admin account creation (first setup)
export const createAdminAccount = async (adminData) => {
  try {
    const response = await adminApi.post('/admin/create', adminData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

// Create club user account with access key
export const createClubUser = async (userData) => {
  try {
    const response = await adminApi.post('/admin/create-user', userData);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

// Get all football teams for dropdown selection
export const getAllTeams = async () => {
  try {
    const response = await adminApi.get('/admin/teams');
    return response.data.teams;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

// Get all non-admin users
export const getAllUsers = async () => {
  try {
    const response = await adminApi.get('/admin/users');
    return response.data.users;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

// Delete a user account
export const deleteUserAccount = async (userId) => {
  try {
    const response = await adminApi.delete(`/admin/users/${userId}`);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};