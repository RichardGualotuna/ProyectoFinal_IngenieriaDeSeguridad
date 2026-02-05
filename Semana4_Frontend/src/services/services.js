/**
 * Servicios de API
 * ✅ CORREGIDO: Con manejo consistente de respuestas del backend
 */
import api from './api'

// ============================================================================
// AUTH SERVICE
// ============================================================================
export const authService = {
  async login(username, password) {
    const response = await api.post('/auth/login', { username, password })
    
    // ✅ CRÍTICO: Guardar token y usuario si el login es exitoso
    if (response.data.success && response.data.data?.token) {
      localStorage.setItem('token', response.data.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.data.user))
    }
    
    return response.data
  },

  async logout() {
    try {
      await api.post('/auth/logout')
    } finally {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
    }
  },

  async getCurrentUser() {
    const response = await api.get('/auth/me')
    return response.data.data || response.data
  },

  getStoredUser() {
    const user = localStorage.getItem('user')
    return user ? JSON.parse(user) : null
  },

  getToken() {
    return localStorage.getItem('token')
  },

  isAuthenticated() {
    return !!this.getToken()
  },

  isAdmin() {
    const user = this.getStoredUser()
    return user?.rol === 'ADMIN'
  }
}

// ============================================================================
// USER SERVICE
// ============================================================================
export const userService = {
  async getAll(params = {}) {
    const response = await api.get('/users', { params })
    
    // ✅ CRÍTICO: Manejar estructura de respuesta del backend
    if (response.data.success && response.data.data) {
      return response.data.data.users || []
    }
    
    return response.data.users || []
  },

  async getById(id) {
    const response = await api.get(`/users/${id}`)
    return response.data.data || response.data
  },

  async create(userData) {
    const response = await api.post('/users', userData)
    return response.data
  },

  async update(id, userData) {
    const response = await api.put(`/users/${id}`, userData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/users/${id}`)
    return response.data
  }
}

// ============================================================================
// CLIENTE SERVICE
// ============================================================================
export const clienteService = {
  async getAll(params = {}) {
    const response = await api.get('/clientes', { params })
    
    // ✅ CRÍTICO: Manejar estructura de respuesta del backend
    if (response.data.success && response.data.data) {
      return response.data.data.clientes || []
    }
    
    return response.data.clientes || []
  },

  async getById(id) {
    const response = await api.get(`/clientes/${id}`)
    return response.data.data || response.data
  },

  async create(clienteData) {
    const response = await api.post('/clientes', clienteData)
    return response.data
  },

  async update(id, clienteData) {
    const response = await api.put(`/clientes/${id}`, clienteData)
    return response.data
  },

  async delete(id) {
    const response = await api.delete(`/clientes/${id}`)
    return response.data
  }
}

// ============================================================================
// HELPERS
// ============================================================================

/**
 * Extraer mensaje de error de respuesta
 */
export const getErrorMessage = (error) => {
  if (error.response?.data?.error) {
    return error.response.data.error
  }
  if (error.response?.data?.message) {
    return error.response.data.message
  }
  if (error.message) {
    return error.message
  }
  return 'Error desconocido'
}

/**
 * Formatear fecha
 */
export const formatDate = (dateString) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('es-EC')
}

/**
 * Formatear moneda
 */
export const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-EC', {
    style: 'currency',
    currency: 'USD'
  }).format(amount)
}
