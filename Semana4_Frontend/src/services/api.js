/**
 * Configuración de Axios
 * ✅ CORREGIDO: Con interceptores para manejar tokens y errores globalmente
 */
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:5000/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// ✅ Interceptor de requests - Agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// ✅ Interceptor de responses - Manejo consistente de errores
api.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    // Manejar errores de autenticación
    if (error.response?.status === 401) {
      // Token inválido o expirado
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // Redirigir a login si no estamos ya ahí
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    }
    
    // ✅ CRÍTICO: Crear un mensaje de error consistente
    const errorMessage = error.response?.data?.error 
      || error.response?.data?.message 
      || error.message 
      || 'Error desconocido'
    
    // Rechazar con mensaje formateado
    return Promise.reject(new Error(errorMessage))
  }
)

export default api
export { api }  // También exportar como named export
