import axios from 'axios';
import { getAuthBase, isElectron } from './config';
import { getAccessToken, setAccessToken } from './tokenStore';

// Create an Axios instance
const api = axios.create({
  baseURL: 'http://localhost:8000', // Update this based on the active backend URL
  withCredentials: true,
});

// Request interceptor to attach access token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor to handle 401s and token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      
      try {
        const authBase = getAuthBase();
        
        // Attempt to get a new access token using cookies
        const response = await axios.post(`${authBase}/refresh`, {}, {
          withCredentials: true,
        });
        
        const { access_token } = response.data;
        
        setAccessToken(access_token);
        
        // Update header and retry original request
        originalRequest.headers.Authorization = `Bearer ${access_token}`;
        return api(originalRequest);
        
      } catch (refreshError) {
        // If refresh fails (e.g. refresh token expired), clear everything and redirect
        setAccessToken(null);
        localStorage.removeItem('refresh_token');
        // Electron uses HashRouter where all routes are prefix-mapped under '#/'.
        // Redirecting via pathname (window.location.href) changes the base URL index structure and breaks
        // subsequent hash routing navigation. We must use window.location.hash for Electron redirects.
        if (isElectron) {
          window.location.hash = '#/login';
        } else {
          window.location.href = '/login';
        }
        return Promise.reject(refreshError);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api;
