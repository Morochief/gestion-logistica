// src/utils/auth.js
import api from "../api/api";

const TOKEN_KEY = "access_token";
const REFRESH_TOKEN_KEY = "refresh_token";
const USER_KEY = "user_data";

// Función para hacer login y guardar tokens
export function login(accessToken, refreshToken, userData) {
  localStorage.setItem(TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
  localStorage.setItem(USER_KEY, JSON.stringify(userData));

  // Configurar interceptor para refresh automático
  setupTokenRefresh();
}

// Función para hacer logout
export function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
}

// Obtener access token
export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

// Obtener refresh token
export function getRefreshToken() {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

// Obtener datos del usuario
export function getUser() {
  const userData = localStorage.getItem(USER_KEY);
  return userData ? JSON.parse(userData) : null;
}

// Verificar si está logueado
export function isLoggedIn() {
  const token = getToken();
  if (!token) return false;

  try {
    // Verificar si el token no ha expirado
    const payload = JSON.parse(atob(token.split('.')[1]));
    const currentTime = Date.now() / 1000;
    return payload.exp > currentTime;
  } catch (error) {
    return false;
  }
}

// Verificar si el usuario tiene un rol específico
export function hasRole(role) {
  const user = getUser();
  return user && user.rol === role;
}

// Verificar si es administrador
export function isAdmin() {
  return hasRole('admin');
}

// Refrescar token automáticamente
export async function refreshToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    logout();
    return false;
  }

  try {
    const response = await api.post('/auth/refresh', {
      refresh_token: refreshToken
    });

    if (response.status === 200) {
      const data = response.data;

      // Actualizar solo el access token
      localStorage.setItem(TOKEN_KEY, data.access_token);

      // Configurar nuevo interceptor
      setupTokenRefresh();

      return true;
    }
  } catch (error) {
    console.error('Error refreshing token:', error);
  }

  // Si falla, hacer logout
  logout();
  return false;
}

// Configurar interceptor para refresh automático de tokens
function setupTokenRefresh() {
  // Remover interceptor anterior si existe
  if (api.interceptors.request.handlers.length > 1) {
    api.interceptors.request.handlers.pop();
  }

  // Agregar interceptor para incluir token en requests
  api.interceptors.request.use((config) => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  });

  // Agregar interceptor para manejar respuestas con token expirado
  api.interceptors.response.use(
    (response) => response,
    async (error) => {
      const originalRequest = error.config;

      if (error.response?.status === 401 && !originalRequest._retry) {
        originalRequest._retry = true;

        const refreshed = await refreshToken();
        if (refreshed) {
          // Reintentar la request original con el nuevo token
          const newToken = getToken();
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
          return api(originalRequest);
        }
      }

      return Promise.reject(error);
    }
  );
}

// Inicializar configuración de tokens al cargar la aplicación
export function initializeAuth() {
  if (isLoggedIn()) {
    setupTokenRefresh();
  }
}
