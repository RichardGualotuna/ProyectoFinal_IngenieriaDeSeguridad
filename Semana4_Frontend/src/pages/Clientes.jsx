
import { useState, useEffect } from 'react'
import { Container, Table, Button, Modal, Form, Alert, Badge, Spinner } from 'react-bootstrap'
import { clienteService } from '../services/services'

const Clientes = () => {
  const [clientes, setClientes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  
  const [showModal, setShowModal] = useState(false)
  const [editingCliente, setEditingCliente] = useState(null)
  const [formData, setFormData] = useState({
    tipo_identificacion: 'CEDULA',
    identificacion: '',
    razon_social: '',
    nombres: '',
    apellidos: '',
    direccion: '',
    telefono: '',
    email: ''
  })

  useEffect(() => {
    loadClientes()
  }, [])

  const loadClientes = async () => {
    try {
      setLoading(true)
      setError('')
      
      const data = await clienteService.getAll()
      
      if (Array.isArray(data)) {
        setClientes(data)
      } else {
        console.warn('Respuesta inesperada:', data)
        setClientes([])
      }
    } catch (err) {
      console.error('Error cargando clientes:', err)
      setError('Error al cargar clientes: ' + err.message)
      setClientes([])
    } finally {
      setLoading(false)
    }
  }

  const handleShowModal = (cliente = null) => {
    if (cliente) {
      setEditingCliente(cliente)
      setFormData({
        tipo_identificacion: cliente.tipo_identificacion,
        identificacion: cliente.identificacion,
        razon_social: cliente.razon_social || '',
        nombres: cliente.nombres || '',
        apellidos: cliente.apellidos || '',
        direccion: cliente.direccion || '',
        telefono: cliente.telefono || '',
        email: cliente.email || ''
      })
    } else {
      setEditingCliente(null)
      setFormData({
        tipo_identificacion: 'CEDULA',
        identificacion: '',
        razon_social: '',
        nombres: '',
        apellidos: '',
        direccion: '',
        telefono: '',
        email: ''
      })
    }
    setShowModal(true)
    setError('')
  }

  const handleCloseModal = () => {
    setShowModal(false)
    setEditingCliente(null)
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
      if (editingCliente) {
        await clienteService.update(editingCliente.id, formData)
        setSuccess('Cliente actualizado exitosamente')
      } else {
        await clienteService.create(formData)
        setSuccess('Cliente creado exitosamente')
      }

      handleCloseModal()
      loadClientes()
      
      setTimeout(() => setSuccess(''), 3000)
    } catch (err) {
      console.error('Error guardando cliente:', err)
      setError('Error al guardar cliente: ' + err.message)
    }
  }

  const handleDelete = async (id, identificacion) => {
    if (window.confirm(`¿Está seguro de eliminar el cliente con identificación "${identificacion}"?`)) {
      try {
        setError('')
        setSuccess('')
        
        await clienteService.delete(id)
        setSuccess('Cliente eliminado exitosamente')
        loadClientes()
        
        setTimeout(() => setSuccess(''), 3000)
      } catch (err) {
        console.error('Error eliminando cliente:', err)
        setError('Error al eliminar cliente: ' + err.message)
      }
    }
  }

  if (loading) {
    return (
      <Container className="py-4 text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Cargando...</span>
        </Spinner>
        <p className="mt-2">Cargando clientes...</p>
      </Container>
    )
  }

  return (
    <Container className="py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2>
          <i className="bi bi-person-vcard me-2"></i>
          Gestión de Clientes
        </h2>
        <Button variant="success" onClick={() => handleShowModal()}>
          <i className="bi bi-plus-circle me-1"></i>
          Nuevo Cliente
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

      <Alert variant="info">
        <i className="bi bi-shield-lock me-2"></i>
        <strong>Seguridad:</strong> Los datos sensibles (nombres, dirección, teléfono, email) están cifrados con AES-256-GCM en la base de datos.
      </Alert>

      {clientes.length === 0 ? (
        <Alert variant="info">
          No hay clientes registrados. Crea el primero haciendo clic en "Nuevo Cliente".
        </Alert>
      ) : (
        <Table striped bordered hover responsive>
          <thead>
            <tr>
              <th>ID</th>
              <th>Tipo ID</th>
              <th>Identificación</th>
              <th>Nombres</th>
              <th>Email</th>
              <th>Teléfono</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            {clientes.map((cliente) => (
              <tr key={cliente.id}>
                <td>{cliente.id}</td>
                <td>
                  <Badge bg="secondary">{cliente.tipo_identificacion}</Badge>
                </td>
                <td><strong>{cliente.identificacion}</strong></td>
                <td>
                  {cliente.tipo_identificacion === 'RUC' 
                    ? cliente.razon_social 
                    : `${cliente.nombres} ${cliente.apellidos}`
                  }
                </td>
                <td>{cliente.email}</td>
                <td>{cliente.telefono}</td>
                <td>
                  <Badge bg={cliente.activo ? 'success' : 'secondary'}>
                    {cliente.activo ? 'Activo' : 'Inactivo'}
                  </Badge>
                </td>
                <td>
                  <Button
                    variant="outline-primary"
                    size="sm"
                    className="me-2"
                    onClick={() => handleShowModal(cliente)}
                  >
                    <i className="bi bi-pencil"></i>
                  </Button>
                  
                  <Button
                    variant="outline-danger"
                    size="sm"
                    onClick={() => handleDelete(cliente.id, cliente.identificacion)}
                  >
                    <i className="bi bi-trash"></i>
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      )}

      {/* Modal para crear/editar cliente */}
      <Modal show={showModal} onHide={handleCloseModal} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            {editingCliente ? 'Editar Cliente' : 'Nuevo Cliente'}
          </Modal.Title>
        </Modal.Header>
        
        <Form onSubmit={handleSubmit}>
          <Modal.Body>
            {error && <Alert variant="danger">{error}</Alert>}
            
            <Form.Group className="mb-3">
              <Form.Label>Tipo de Identificación *</Form.Label>
              <Form.Select
                name="tipo_identificacion"
                value={formData.tipo_identificacion}
                onChange={handleChange}
                required
              >
                <option value="CEDULA">Cédula (10 dígitos)</option>
                <option value="RUC">RUC (13 dígitos)</option>
                <option value="PASAPORTE">Pasaporte</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Identificación *</Form.Label>
              <Form.Control
                type="text"
                name="identificacion"
                value={formData.identificacion}
                onChange={handleChange}
                required
                placeholder="Número de identificación"
              />
            </Form.Group>

            {formData.tipo_identificacion === 'RUC' && (
              <Form.Group className="mb-3">
                <Form.Label>Razón Social *</Form.Label>
                <Form.Control
                  type="text"
                  name="razon_social"
                  value={formData.razon_social}
                  onChange={handleChange}
                  placeholder="Nombre de la empresa"
                />
              </Form.Group>
            )}

            {formData.tipo_identificacion !== 'RUC' && (
              <>
                <Form.Group className="mb-3">
                  <Form.Label>Nombres</Form.Label>
                  <Form.Control
                    type="text"
                    name="nombres"
                    value={formData.nombres}
                    onChange={handleChange}
                    placeholder="Nombres completos"
                  />
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Apellidos</Form.Label>
                  <Form.Control
                    type="text"
                    name="apellidos"
                    value={formData.apellidos}
                    onChange={handleChange}
                    placeholder="Apellidos completos"
                  />
                </Form.Group>
              </>
            )}

            <Form.Group className="mb-3">
              <Form.Label>
                Dirección
                <i className="bi bi-shield-lock-fill text-warning ms-2" title="Dato cifrado"></i>
              </Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                name="direccion"
                value={formData.direccion}
                onChange={handleChange}
                placeholder="Dirección completa"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>
                Teléfono
                <i className="bi bi-shield-lock-fill text-warning ms-2" title="Dato cifrado"></i>
              </Form.Label>
              <Form.Control
                type="tel"
                name="telefono"
                value={formData.telefono}
                onChange={handleChange}
                placeholder="0987654321"
              />
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>
                Email
                <i className="bi bi-shield-lock-fill text-warning ms-2" title="Dato cifrado"></i>
              </Form.Label>
              <Form.Control
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="cliente@ejemplo.com"
              />
            </Form.Group>
          </Modal.Body>
          
          <Modal.Footer>
            <Button variant="secondary" onClick={handleCloseModal}>
              Cancelar
            </Button>
            <Button variant="success" type="submit">
              {editingCliente ? 'Actualizar' : 'Crear'}
            </Button>
          </Modal.Footer>
        </Form>
      </Modal>
    </Container>
  )
}

export default Clientes
