/* frontend/src/services/notifications.js */
import { authApi } from './auth';

export const getNotifications = async () => {
  try {
    const response = await authApi.get('/notifications');
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const markNotificationRead = async (notificationId) => {
  try {
    const response = await authApi.put(`/notifications/${notificationId}/read`);
    return response.data;
  } catch (error) {
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};

export const sendBroadcastNotification = async (message) => {
  try {
    // Get token directly for logging purposes
    const token = localStorage.getItem('token');
    console.log('Token available before broadcast:', !!token);
    
    const response = await authApi.post('/admin/notifications/broadcast', { message });
    return response.data;
  } catch (error) {
    // Enhanced error logging
    console.error('Broadcast notification error:', error);
    
    if (error.response) {
      console.error('Error status:', error.response.status);
      console.error('Error data:', error.response.data);
      
      if (error.response.status === 403) {
        throw { message: 'You do not have admin privileges to send broadcast notifications.' };
      }
    }
    
    throw error.response ? error.response.data : { message: 'Network error' };
  }
};
