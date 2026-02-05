
import { createContext, useState, useContext, useEffect } from 'react'
import { authService } from '../services/services'

const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Verificar si hay usuario almacenado al cargar
    const storedUser = authService.getStoredUser()
    if (storedUser && authService.isAuthenticated()) {
      setUser(storedUser)
    }
    setLoading(false)
  }, [])

  const login = async (username, password) => {
    const response = await authService.login(username, password)
    
    if (response.success && response.data?.user) {
      setUser(response.data.user)
      return response
    }
    
    throw new Error(response.error || 'Error en el login')
  }

  const logout = async () => {
    await authService.logout()
    setUser(null)
  }

  const isAdmin = () => {
    return user?.rol === 'ADMIN'
  }

  const value = {
    user,
    login,
    logout,
    isAuthenticated: !!user,
    isAdmin,
    loading
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth debe usarse dentro de AuthProvider')
  }
  return context
}
