/**
 * Página de Login
 */
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Container, Card, Form, Button, Alert } from 'react-bootstrap'
import { useAuth } from '../contexts/AuthContext'

const Login = () => {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      await login(username, password)
      navigate('/')
    } catch (err) {
      setError(err.message || 'Error al iniciar sesión')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
      <Card style={{ width: '100%', maxWidth: '400px' }}>
        <Card.Body>
          <div className="text-center mb-4">
            <i className="bi bi-receipt" style={{ fontSize: '3rem', color: '#0d6efd' }}></i>
            <h3 className="mt-2">Facturación Electrónica</h3>
            <p className="text-muted">Iniciar Sesión</p>
          </div>

          {error && <Alert variant="danger" dismissible onClose={() => setError('')}>{error}</Alert>}

          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Usuario</Form.Label>
              <Form.Control
                type="text"
                placeholder="Ingrese su usuario"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                disabled={loading}
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Contraseña</Form.Label>
              <Form.Control
                type="password"
                placeholder="Ingrese su contraseña"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                disabled={loading}
              />
            </Form.Group>

            <Button 
              variant="primary" 
              type="submit" 
              className="w-100"
              disabled={loading}
            >
              {loading ? 'Iniciando sesión...' : 'Iniciar Sesión'}
            </Button>
          </Form>

          <div className="mt-3 text-center">
            <small className="text-muted">
              Usuario por defecto: <strong>admin</strong><br />
              Contraseña: <strong>Admin123!</strong>
            </small>
          </div>
        </Card.Body>
      </Card>
    </Container>
  )
}

export default Login
