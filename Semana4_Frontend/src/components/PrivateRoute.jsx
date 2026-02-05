/**
 * Componente de Ruta Privada
 */
import { Navigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import { Spinner, Container } from 'react-bootstrap'

const PrivateRoute = ({ children, requireAdmin = false }) => {
  const { isAuthenticated, isAdmin, loading } = useAuth()

  if (loading) {
    return (
      <Container className="text-center py-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
      </Container>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  if (requireAdmin && !isAdmin()) {
    return <Navigate to="/" replace />
  }

  return children
}

export default PrivateRoute
