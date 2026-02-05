import { useState, useEffect } from 'react';
import { api } from '../services/api';

export default function Facturas() {
  const [facturas, setFacturas] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [productos, setProductos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedFactura, setSelectedFactura] = useState(null);
  const [formData, setFormData] = useState({
    cliente_id: '',
    items: [{ codigo: '', nombre: '', cantidad: 1, precio_unitario: 0, iva_porcentaje: 15 }],
    observaciones: ''
  });

  useEffect(() => {
    loadFacturas();
    loadClientes();
    loadProductos();
  }, []);

  const loadFacturas = async () => {
    try {
      setLoading(true);
      const response = await api.get('/facturas?per_page=100');
      setFacturas(response.data.data?.facturas || response.data.facturas || []);
    } catch (error) {
      console.error('Error cargando facturas:', error);
      alert('Error al cargar facturas');
    } finally {
      setLoading(false);
    }
  };

  const loadClientes = async () => {
    try {
      const response = await api.get('/clientes?per_page=100');
      console.log('Respuesta clientes:', response.data);
      setClientes(response.data.data?.clientes || response.data.clientes || []);
    } catch (error) {
      console.error('Error cargando clientes:', error);
    }
  };

  const loadProductos = () => {
    // Productos de ejemplo hardcodeados (podrían venir de la API)
    setProductos([
      { codigo: 'PROD001', nombre: 'Laptop Dell Inspiron 15', precio_unitario: 1200.00 },
      { codigo: 'PROD002', nombre: 'Mouse Logitech MX Master 3', precio_unitario: 99.99 },
      { codigo: 'PROD003', nombre: 'Teclado Mecánico Corsair K95', precio_unitario: 189.99 },
      { codigo: 'PROD004', nombre: 'Monitor LG UltraWide 34"', precio_unitario: 599.99 },
      { codigo: 'PROD005', nombre: 'Webcam Logitech C920', precio_unitario: 79.99 },
      { codigo: 'SERV001', nombre: 'Consultoría TI (hora)', precio_unitario: 50.00 },
      { codigo: 'SERV002', nombre: 'Desarrollo Web (hora)', precio_unitario: 75.00 },
      { codigo: 'SERV003', nombre: 'Soporte Técnico Mensual', precio_unitario: 150.00 }
    ]);
  };

  const addItem = () => {
    setFormData({
      ...formData,
      items: [...formData.items, { codigo: '', nombre: '', cantidad: 1, precio_unitario: 0, iva_porcentaje: 15 }]
    });
  };

  const removeItem = (index) => {
    const newItems = formData.items.filter((_, i) => i !== index);
    setFormData({ ...formData, items: newItems });
  };

  const updateItem = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index][field] = value;
    
    // Si selecciona un producto, llenar automáticamente
    if (field === 'codigo') {
      const producto = productos.find(p => p.codigo === value);
      if (producto) {
        newItems[index].nombre = producto.nombre;
        newItems[index].precio_unitario = producto.precio_unitario;
      }
    }
    
    setFormData({ ...formData, items: newItems });
  };

  const calcularTotal = () => {
    return formData.items.reduce((total, item) => {
      const subtotal = item.cantidad * item.precio_unitario;
      const iva = subtotal * (item.iva_porcentaje / 100);
      return total + subtotal + iva;
    }, 0);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.cliente_id) {
      alert('Debe seleccionar un cliente');
      return;
    }
    
    if (formData.items.length === 0 || !formData.items[0].codigo) {
      alert('Debe agregar al menos un producto');
      return;
    }

    try {
      await api.post('/facturas', formData);
      alert('✅ Factura creada exitosamente con firma RSA y código QR');
      setShowModal(false);
      setFormData({
        cliente_id: '',
        items: [{ codigo: '', nombre: '', cantidad: 1, precio_unitario: 0, iva_porcentaje: 15 }],
        observaciones: ''
      });
      loadFacturas();
    } catch (error) {
      console.error('Error creando factura:', error);
      alert('❌ Error al crear factura: ' + (error.response?.data?.error || error.message));
    }
  };

  const verDetalle = async (factura) => {
    try {
      const response = await api.get(`/facturas/${factura.id}`);
      setSelectedFactura(response.data);
      setShowDetailModal(true);
    } catch (error) {
      console.error('Error cargando detalle:', error);
      alert('Error al cargar detalle de factura');
    }
  };

  const descargarXML = async (facturaId) => {
    try {
      const response = await api.get(`/facturas/${facturaId}/xml`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `factura_${facturaId}.xml`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error descargando XML:', error);
      alert('Error al descargar XML');
    }
  };

  if (loading) {
    return <div className="flex justify-center items-center h-screen">
      <div className="text-xl">Cargando facturas...</div>
    </div>;
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center gap-2">
            📄 Gestión de Facturas Electrónicas
          </h1>
          <p className="text-gray-600 mt-1">
            Con firma digital RSA-2048, códigos QR y simulación SRI
          </p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          style={{ backgroundColor: '#16a34a' }}
          className="hover:bg-green-700 text-white px-8 py-4 rounded-lg flex items-center gap-3 transition transform hover:scale-105 shadow-xl font-bold text-lg"
        >
          <span className="text-2xl">📝</span> + Nueva Factura
        </button>
      </div>

      {/* Info de seguridad */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6 flex items-start gap-3">
        <span className="text-2xl">🔒</span>
        <div>
          <p className="text-blue-800 font-medium">Seguridad Criptográfica Activa</p>
          <p className="text-blue-600 text-sm">
            Todas las facturas se firman con RSA-2048 + SHA-256, generan QR para verificación pública y simulan autorización SRI
          </p>
        </div>
      </div>

      {/* Tabla de facturas */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Número</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Fecha</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Cliente</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Total</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Estado SRI</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Acciones</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {facturas.length === 0 ? (
              <tr>
                <td colSpan="7" className="px-6 py-12 text-center text-gray-500">
                  <div className="flex flex-col items-center gap-3">
                    <span className="text-5xl">📄</span>
                    <p className="text-lg">No hay facturas registradas</p>
                    <button
                      onClick={() => setShowModal(true)}
                      className="text-green-600 hover:text-green-700 font-medium"
                    >
                      Crear primera factura
                    </button>
                  </div>
                </td>
              </tr>
            ) : (
              facturas.map((factura) => (
                <tr key={factura.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{factura.id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {factura.numero_factura}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(factura.fecha_emision).toLocaleDateString('es-EC')}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {factura.cliente?.nombres} {factura.cliente?.apellidos}
                    <br />
                    <span className="text-xs text-gray-500">{factura.cliente?.identificacion}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-bold text-gray-900">
                    ${parseFloat(factura.total).toFixed(2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800">
                      {factura.estado_sri}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm space-x-2">
                    <button
                      onClick={() => verDetalle(factura)}
                      className="text-blue-600 hover:text-blue-900 font-medium"
                    >
                      👁️ Ver
                    </button>
                    <button
                      onClick={() => descargarXML(factura.id)}
                      className="text-purple-600 hover:text-purple-900 font-medium"
                    >
                      📥 XML
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Modal de crear factura */}
      {showModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">Nueva Factura Electrónica</h2>
                <button
                  onClick={() => setShowModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                {/* Cliente */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Cliente *
                  </label>
                  <select
                    value={formData.cliente_id}
                    onChange={(e) => setFormData({ ...formData, cliente_id: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    required
                  >
                    <option value="">Seleccione un cliente</option>
                    {clientes.map(cliente => (
                      <option key={cliente.id} value={cliente.id}>
                        {cliente.decrypted_data?.nombres} {cliente.decrypted_data?.apellidos} - {cliente.identificacion}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Items */}
                <div>
                  <div className="flex justify-between items-center mb-3">
                    <label className="block text-sm font-medium text-gray-700">
                      Productos/Servicios *
                    </label>
                    <button
                      type="button"
                      onClick={addItem}
                      className="text-green-600 hover:text-green-700 text-sm font-medium"
                    >
                      + Agregar ítem
                    </button>
                  </div>

                  {formData.items.map((item, index) => (
                    <div key={index} className="grid grid-cols-12 gap-3 mb-3 p-3 bg-gray-50 rounded-lg">
                      <div className="col-span-3">
                        <select
                          value={item.codigo}
                          onChange={(e) => updateItem(index, 'codigo', e.target.value)}
                          className="w-full px-2 py-1 text-sm border rounded"
                          required
                        >
                          <option value="">Producto...</option>
                          {productos.map(p => (
                            <option key={p.codigo} value={p.codigo}>{p.codigo}</option>
                          ))}
                        </select>
                      </div>
                      <div className="col-span-4">
                        <input
                          type="text"
                          value={item.nombre}
                          onChange={(e) => updateItem(index, 'nombre', e.target.value)}
                          className="w-full px-2 py-1 text-sm border rounded"
                          placeholder="Descripción"
                          required
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          value={item.cantidad}
                          onChange={(e) => updateItem(index, 'cantidad', parseFloat(e.target.value))}
                          className="w-full px-2 py-1 text-sm border rounded"
                          min="0.01"
                          step="0.01"
                          placeholder="Cant."
                          required
                        />
                      </div>
                      <div className="col-span-2">
                        <input
                          type="number"
                          value={item.precio_unitario}
                          onChange={(e) => updateItem(index, 'precio_unitario', parseFloat(e.target.value))}
                          className="w-full px-2 py-1 text-sm border rounded"
                          min="0"
                          step="0.01"
                          placeholder="Precio"
                          required
                        />
                      </div>
                      <div className="col-span-1">
                        {formData.items.length > 1 && (
                          <button
                            type="button"
                            onClick={() => removeItem(index)}
                            className="text-red-600 hover:text-red-800"
                          >
                            🗑️
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Total */}
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex justify-between items-center">
                    <span className="text-lg font-medium text-gray-700">Total Estimado:</span>
                    <span className="text-2xl font-bold text-green-600">
                      ${calcularTotal().toFixed(2)}
                    </span>
                  </div>
                </div>

                {/* Observaciones */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Observaciones
                  </label>
                  <textarea
                    value={formData.observaciones}
                    onChange={(e) => setFormData({ ...formData, observaciones: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
                    rows="3"
                    placeholder="Notas adicionales..."
                  />
                </div>

                {/* Botones */}
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setShowModal(false)}
                    className="flex-1 px-4 py-2 border-2 border-gray-400 text-gray-700 rounded-lg hover:bg-gray-100 font-medium"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    className="flex-1 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 font-bold shadow-lg"
                    style={{ backgroundColor: '#16a34a', color: 'white' }}
                  >
                    🔐 Crear y Firmar Factura
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Modal de detalle con QR */}
      {showDetailModal && selectedFactura && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-800">
                  Factura {selectedFactura.numero_factura}
                </h2>
                <button
                  onClick={() => setShowDetailModal(false)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>

              <div className="grid grid-cols-2 gap-6">
                {/* Info de factura */}
                <div className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-500">Cliente</p>
                    <p className="font-medium">
                      {selectedFactura.cliente?.nombres} {selectedFactura.cliente?.apellidos}
                    </p>
                    <p className="text-sm text-gray-600">{selectedFactura.cliente?.identificacion}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Fecha Emisión</p>
                    <p className="font-medium">
                      {new Date(selectedFactura.fecha_emision).toLocaleString('es-EC')}
                    </p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Estado SRI</p>
                    <p className="font-medium text-green-600">{selectedFactura.estado_sri}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Autorización SRI</p>
                    <p className="font-mono text-xs">{selectedFactura.num_autorizacion}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-500">Hash SHA-256</p>
                    <p className="font-mono text-xs break-all">{selectedFactura.hash_sha256}</p>
                  </div>
                </div>

                {/* QR Code */}
                <div className="flex flex-col items-center">
                  <p className="text-sm text-gray-500 mb-3">Código QR de Verificación</p>
                  {selectedFactura.qr_image && (
                    <img
                      src={selectedFactura.qr_image}
                      alt="QR Factura"
                      className="w-64 h-64 border-2 border-gray-300 rounded-lg"
                    />
                  )}
                  <p className="text-xs text-gray-500 mt-3 text-center">
                    Escanea para verificar autenticidad
                  </p>
                </div>
              </div>

              {/* Items */}
              <div className="mt-6">
                <h3 className="font-medium mb-3">Detalle de Productos</h3>
                <table className="w-full text-sm">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-3 py-2 text-left">Producto</th>
                      <th className="px-3 py-2 text-right">Cant.</th>
                      <th className="px-3 py-2 text-right">P. Unit.</th>
                      <th className="px-3 py-2 text-right">Total</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {selectedFactura.items?.map((item, idx) => (
                      <tr key={idx}>
                        <td className="px-3 py-2">{item.nombre}</td>
                        <td className="px-3 py-2 text-right">{item.cantidad}</td>
                        <td className="px-3 py-2 text-right">${parseFloat(item.precio_unitario).toFixed(2)}</td>
                        <td className="px-3 py-2 text-right font-medium">
                          ${(item.cantidad * item.precio_unitario).toFixed(2)}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot className="bg-gray-50 font-bold">
                    <tr>
                      <td colSpan="3" className="px-3 py-2 text-right">Total:</td>
                      <td className="px-3 py-2 text-right text-green-600">
                        ${parseFloat(selectedFactura.total).toFixed(2)}
                      </td>
                    </tr>
                  </tfoot>
                </table>
              </div>

              {selectedFactura.observaciones && (
                <div className="mt-4 p-3 bg-gray-50 rounded-lg">
                  <p className="text-sm text-gray-500">Observaciones</p>
                  <p className="text-sm">{selectedFactura.observaciones}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
