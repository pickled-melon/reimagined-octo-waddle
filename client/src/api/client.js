import axios from 'axios';
import Cookies from 'js-cookie';

const client = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
});

client.interceptors.request.use((config) => {
  const token = Cookies.get('csrftoken');
  if (token) config.headers['X-CSRFToken'] = token;
  return config;
});

export default client;