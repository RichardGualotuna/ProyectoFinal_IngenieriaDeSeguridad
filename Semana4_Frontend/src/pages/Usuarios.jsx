
import { useState, useEffect } from 'react'
import { Container, Table, Button, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap'
import { userService } from '../services/services'

const Usuarios = () => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [showModal, setShowModal] = useState(false)
  const [editingUser, setEditingUser] = useState(null)
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    email: '',
    nombres: '',
    apellidos: '',
    rol: 'FACTURADOR'
  })

  useEffect(() => {
    loadUsers()
  }, [])

  const loadUsers = async () => {
    try {
      setLoading(true)
      setError('')
      
      //  CRÍTICO: Manejar correctamente la respuesta del backend
      const data = await userService.getAll()
      
      //  CRÍTICO: Asegurar que siempre sea un array
      if (Array.isArray(data)) {
        setUsers(data)
      } else {
        console.warn('Respuesta inesperada:', data)
        setUsers([])
      }
    } catch (err) {
      console.error('Error cargando usuarios:', err)
      setError('Error al cargar usuarios: ' + err.message)
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  const handleShowModal = (user = null) => {
    if (user) {
      // Modo edición
      setEditingUser(user)
      setFormData({
        username: user.username,
        password: '', // No mostrar password en edición
        email: user.email,
        nombres: user.nombres,
        apellidos: user.apellidos,
        rol: user.rol
      })
    } else {
      // Modo creación
      setEditingUser(null)
      setFormData({
        username: '',
        password: '',
        email: '',
        nombres: '',
        apellidos: '',
        rol: 'FACTURADOR'
      })
    }
    setShowModal(true)
    setError('')
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingUser(null)
    setFormData({
      username: '',
      password: '',
      email: '',
      nombres: '',
      apellidos: '',
      rol: 'FACTURADOR'
    })
    setError('')
  }

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setSuccess('')

    try {
      if (editingUser) {
        //  CRÍTICO: Actualizar usuario
        const updateData = { ...formData }
        
        // No enviar password vacío en actualización
        if (!updateData.password) {
          delete updateData.password
        }
        // No enviar username en actualización (no se puede cambiar)
        delete updateData.username
        
        await userService.update(editingUser.id, updateData)
        setSuccess('Usuario actualizado exitosamente')
      } else {
        //  CRÍTICO: Crear nuevo usuario
        await userService.create(formData)
        setSuccess('Usuario creado exitosamente')
      }

      handleCloseModal()
      loadUsers()
      
      // Limpiar mensaje después de 3 segundos
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      console.error('Error guardando usuario:', err)
      setError('Error al guardar usuario: ' + err.message)
    }
  }

  const handleDelete = async (id, username) => {
    if (window.confirm(`¿Está seguro de eliminar el usuario "${username}"?`)) {
      try {
        setError('')
        setSuccess('')
        
        // CRÍTICO: Eliminar usuario
        await userService.delete(id)
        setSuccess('Usuario eliminado exitosamente')
        loadUsers()
        
        setTimeout(() => setSuccess(''), 3000)
      } catch (err) {
        console.error('Error eliminando usuario:', err)
        setError('Error al eliminar usuario: ' + err.message)
      }
    }
  }

  const handleToggleActive = async (user) => {
    try {
      setError('')
      setSuccess('')
      
      //  CRÍTICO: Cambiar estado activo/inactivo
      await userService.update(user.id, { activo: !user.activo })
      setSuccess(`Usuario ${!user.activo ? 'activado' : 'desactivado'} exitosamente`)
      loadUsers()
      
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      console.error('Error cambiando estado:', err)
      setError('Error al cambiar estado: ' + err.message)
    }
  }

  if (loading) {
    return (
      <Container className="py-4 text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
        <p className="mt-2">Cargando usuarios...</p>
      </Container>
    )
  }

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>
          <i className="bi bi-people me-2"></i>
          Gestión de Usuarios
        </h2>
        <Button variant="primary" onClick={() => handleShowModal()}>
          <i className="bi bi-plus-circle me-1"></i>
          Nuevo Usuario
        </Button>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError('')}>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess('')}>
          {success}
        </Alert>
      )}

      {users.length === 0 ? (
        <Alert variant="info">
          No hay usuarios registrados. Crea el primero haciendo clic en "Nuevo Usuario".
        </Alert>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Usuario</th>
              <th>Nombres</th>
              <th>Email</th>
              <th>Rol</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {users.map((user) => (
              <tr key={user.id}>
                <td>{user.id}</td>
                <td><strong>{user.username}</strong></td>
                <td>{user.nombres} {user.apellidos}</td>
                <td>{user.email}</td>
                <td>
                  <Badge bg={
                    user.rol === 'ADMIN' ? 'danger' :
                    user.rol === 'FACTURADOR' ? 'primary' :
                    user.rol === 'CONTADOR' ? 'success' : 'secondary'
                  }>
                    {user.rol}
                  </Badge>
                </td>
                <td>
                  <Badge bg={user.activo ? 'success' : 'secondary'}>
                    {user.activo ? 'Activo' : 'Inactivo'}
                  </Badge>
                </td>
                <td>
                  <Button
                    variant="outline-primary"
                    size="sm"
                    className="me-2"
                    onClick={() => handleShowModal(user)}
                  >
                    <i className="bi bi-pencil"></i>
                  </Button>
                  
                  <Button
                    variant={user.activo ? 'outline-warning' : 'outline-success'}
                    size="sm"
                    className="me-2"
                    onClick={() => handleToggleActive(user)}
                  >
                    <i className={`bi bi-${user.activo ? 'x-circle' : 'check-circle'}`}></i>
                  </Button>
                  
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => handleDelete(user.id, user.username)}
                  >
                    <i className="bi bi-trash"></i>
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Modal para crear/editar usuario */}
      <Modal show={showModal} onHide={handleCloseModal}>
        <Modal.Header closeButton>
          <Modal.Title>
            {editingUser ? 'Editar Usuario' : 'Nuevo Usuario'}
          </Modal.Title>
        </Modal.Header>
        
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            {error && <Alert variant="danger">{error}</Alert>}
            
            <Form.Group className="mb-3">
              <Form.Label>Usuario *</Form.Label>
              <Form.Control
                type="text"
                name="username"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={!!editingUser}
                placeholder="Nombre de usuario único"
              />
              {editingUser && (
                <Form.Text className="text-muted">
                  El nombre de usuario no se puede modificar
                </Form.Text>
              )}
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>
                Contraseña {editingUser ? '(dejar vacío para no cambiar)' : '*'}
              </Form.Label>
              <Form.Control
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required={!editingUser}
                placeholder="Contraseña segura"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Nombres *</Form.Label>
              <Form.Control
                type="text"
                name="nombres"
                value={formData.nombres}
                onChange={handleChange}
                required
                placeholder="Nombres completos"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Apellidos *</Form.Label>
              <Form.Control
                type="text"
                name="apellidos"
                value={formData.apellidos}
                onChange={handleChange}
                required
                placeholder="Apellidos completos"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Email *</Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="correo@ejemplo.com"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Rol *</Form.Label>
              <Form.Select
                name="rol"
                value={formData.rol}
                onChange={handleChange}
                required
              >
                <option value="FACTURADOR">FACTURADOR</option>
                <option value="CONTADOR">CONTADOR</option>
                <option value="AUDITOR">AUDITOR</option>
                <option value="ADMIN">ADMIN</option>
              </Form.Select>
            </Form.Group>
          </Modal.Body>
          
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button variant="primary" type="submit">
              {editingUser ? 'Actualizar' : 'Crear'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  )
}

export default Usuarios
