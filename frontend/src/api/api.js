// frontend/src/api/api.js
import axios from "axios";

const api = axios.create({
  // ✅ CORREGIDO: Sin el /api al final porque los blueprints ya lo tienen
  baseURL: process.env.REACT_APP_API_URL || "http://localhost:5000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export default api;