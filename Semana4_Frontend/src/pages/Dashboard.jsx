/**
 * Página de Dashboard
 */
import { Container, Row, Col, Card } from 'react-bootstrap'
import { useAuth } from '../contexts/AuthContext'

const Dashboard = () => {
  const { user } = useAuth()

  const cards = [
    {
      title: 'Usuarios',
      icon: 'bi-people',
      color: 'primary',
      link: '/usuarios',
      description: 'Gestionar usuarios del sistema',
      adminOnly: true
    },
    {
      title: 'Clientes',
      icon: 'bi-person-vcard',
      color: 'success',
      link: '/clientes',
      description: 'Gestionar clientes'
    },
    {
      title: 'Facturas',
      icon: 'bi-file-earmark-text',
      color: 'info',
      link: '/facturas',
      description: 'Gestionar facturas electrónicas'
    }
  ]

  return (
    <Container className="py-4">
      <h2 className="mb-4">
        <i className="bi bi-house-door me-2"></i>
        Dashboard
      </h2>

      <Card className="mb-4">
        <Card.Body>
          <h5>Bienvenido, {user?.nombres} {user?.apellidos}</h5>
          <p className="text-muted mb-0">
            Rol: <strong>{user?.rol}</strong> | Email: {user?.email}
          </p>
        </Card.Body>
      </Card>

      <Row>
        {cards
          .filter(card => !card.adminOnly || user?.rol === 'ADMIN')
          .map((card, index) => (
            <Col key={index} md={4} className="mb-4">
              <Card 
                className="h-100 cursor-pointer text-hover-primary"
                onClick={() => window.location.href = card.link}
                style={{ transition: 'transform 0.2s' }}
                onMouseEnter={(e) => e.currentTarget.style.transform = 'scale(1.05)'}
                onMouseLeave={(e) => e.currentTarget.style.transform = 'scale(1)'}
              >
                <Card.Body className="text-center">
                  <i 
                    className={`bi ${card.icon}`} 
                    style={{ fontSize: '3rem', color: `var(--bs-${card.color})` }}
                  ></i>
                  <h5 className="mt-3">{card.title}</h5>
                  <p className="text-muted">{card.description}</p>
                </Card.Body>
              </Card>
            </Col>
          ))}
      </Row>

      <Row>
        <Col>
          <Card>
            <Card.Header>
              <i className="bi bi-shield-lock me-2"></i>
              Seguridad Implementada
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <h6><i className="bi bi-check-circle text-success me-2"></i>Autenticación JWT</h6>
                  <p className="text-muted small">Tokens seguros con expiración de 8 horas</p>
                  
                  <h6><i className="bi bi-check-circle text-success me-2"></i>Cifrado AES-256-GCM</h6>
                  <p className="text-muted small">Datos sensibles de clientes cifrados</p>
                </Col>
                <Col md={6}>
                  <h6><i className="bi bi-check-circle text-success me-2"></i>Firmas Digitales RSA-2048</h6>
                  <p className="text-muted small">Integridad de facturas electrónicas</p>
                  
                  <h6><i className="bi bi-check-circle text-success me-2"></i>Auditoría Completa</h6>
                  <p className="text-muted small">Registro de todas las operaciones</p>
                </Col>
              </Row>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  )
}

export default Dashboard
