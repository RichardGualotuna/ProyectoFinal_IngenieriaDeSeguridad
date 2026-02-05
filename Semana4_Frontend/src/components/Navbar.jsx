/**
 * Componente de Navbar
 */
import { Link, useNavigate } from 'react-router-dom'
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap'
import { useAuth } from '../contexts/AuthContext'

const NavbarComponent = () => {
  const { user, logout, isAdmin } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
      <Container>
        <Navbar.Brand as={Link} to="/">
          <i className="bi bi-receipt me-2"></i>
          Facturación Electrónica
        </Navbar.Brand>
        
        <Navbar.Toggle aria-controls="navbar-nav" />
        
        <Navbar.Collapse id="navbar-nav">
          <Nav className="me-auto">
            <Nav.Link as={Link} to="/">
              <i className="bi bi-house-door me-1"></i>
              Dashboard
            </Nav.Link>
            
            {isAdmin() && (
              <Nav.Link as={Link} to="/usuarios">
                <i className="bi bi-people me-1"></i>
                Usuarios
              </Nav.Link>
            )}
            
            <Nav.Link as={Link} to="/clientes">
              <i className="bi bi-person-vcard me-1"></i>
              Clientes
            </Nav.Link>
            
            <Nav.Link as={Link} to="/facturas">
              <i className="bi bi-file-earmark-text me-1"></i>
              Facturas
            </Nav.Link>

            <Nav.Link href="/verificar" target="_blank">
              <i className="bi bi-qr-code me-1"></i>
              Verificar QR
            </Nav.Link>
          </Nav>
          
          <Nav>
            <NavDropdown 
              title={
                <>
                  <i className="bi bi-person-circle me-1"></i>
                  {user?.nombres} {user?.apellidos}
                </>
              } 
              id="user-dropdown"
              align="end"
            >
              <NavDropdown.Item disabled>
                <small className="text-muted">
                  {user?.email}<br />
                  Rol: {user?.rol}
                </small>
              </NavDropdown.Item>
              <NavDropdown.Divider />
              <NavDropdown.Item onClick={handleLogout}>
                <i className="bi bi-box-arrow-right me-1"></i>
                Cerrar Sesión
              </NavDropdown.Item>
            </NavDropdown>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  )
}

export default NavbarComponent
