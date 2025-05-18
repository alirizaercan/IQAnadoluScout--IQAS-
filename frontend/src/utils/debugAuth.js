// frontend/src/utils/debugAuth.js
import { authApi } from '../services/auth';

// Check if the current user's token is valid and has admin privileges
export const checkAdminAuth = async () => {
  try {
    console.log('Testing admin authentication...');
    
    // Get current token and user data from localStorage
    const token = localStorage.getItem('token');
    const user = JSON.parse(localStorage.getItem('user'));
    
    console.log('Token exists:', !!token);
    console.log('User data:', user);
    
    if (!token) {
      return {
        success: false,
        message: 'No token found in localStorage'
      };
    }
    
    // Test the auth using our debug endpoint
    const response = await authApi.get('/admin/test-auth');
    console.log('Auth test response:', response.data);
    
    return {
      success: true,
      data: response.data,
      localUser: user
    };
  } catch (error) {
    console.error('Auth test error:', error);
    return {
      success: false,
      message: error.response ? 
        `Error ${error.response.status}: ${JSON.stringify(error.response.data)}` :
        'Network error connecting to admin auth test endpoint'
    };
  }
};
