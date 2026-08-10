import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('[API Error]', error.response?.status, error.response?.data || error.message);
    const detail = error.response?.data?.detail;
    let message = 'An error occurred';
    if (Array.isArray(detail) && detail.length > 0) {
      message = detail[0].msg || JSON.stringify(detail[0]);
    } else if (typeof detail === 'string') {
      message = detail;
    } else if (typeof detail === 'object' && detail !== null) {
      message = detail.msg || JSON.stringify(detail);
    } else if (error.response?.data?.message) {
      message = error.response.data.message;
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

export default api;
