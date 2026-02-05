/**
 * Aplicación Principal
 * 
 */
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import PrivateRoute from './components/PrivateRoute'
import Navbar from './components/Navbar'

// Páginas
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import Usuarios from './pages/Usuarios'
import Clientes from './pages/Clientes'
import Facturas from './pages/Facturas'
import VerificarFactura from './pages/VerificarFactura'

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Routes>
          {/* Rutas públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/verificar/:hash?" element={<VerificarFactura />} />

          {/* Rutas privadas */}
          <Route
            path="/*"
            element={
              <PrivateRoute>
                <>
                  <Navbar />
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    
                    {/* Solo admin puede ver usuarios */}
                    <Route 
                      path="/usuarios" 
                      element={
                        <PrivateRoute requireAdmin={true}>
                          <Usuarios />
                        </PrivateRoute>
                      } 
                    />
                    
                    <Route path="/clientes" element={<Clientes />} />
                    <Route path="/facturas" element={<Facturas />} />
                    
                    {/* Ruta por defecto */}
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </>
              </PrivateRoute>
            }
          />
        </Routes>
      </AuthProvider>
    </BrowserRouter>
  )
}

export default App
