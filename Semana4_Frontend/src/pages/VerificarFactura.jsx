import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

export default function VerificarFactura() {
  const { hash } = useParams();
  const navigate = useNavigate();
  const [verificacion, setVerificacion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [hashInput, setHashInput] = useState(hash || '');

  const verificarFactura = async (hashToVerify) => {
    try {
      setLoading(true);
      setError('');
      setVerificacion(null);
      
      // Limpiar el hash - solo letras y números
      const hashLimpio = hashToVerify.replace(/[^a-fA-F0-9]/g, '');
      
      if (hashLimpio.length !== 64) {
        setError('El hash SHA-256 debe tener exactamente 64 caracteres hexadecimales');
        setLoading(false);
        return;
      }
      
      console.log('Verificando hash:', hashLimpio);
      
      // NO usar JWT - este es un endpoint público
      const response = await fetch(`http://localhost:5000/api/v1/facturas/verificar/${hashLimpio}`);
      const data = await response.json();
      
      console.log('Respuesta verificación:', data);
      setVerificacion(data);
    } catch (err) {
      console.error('Error verificando factura:', err);
      setError('Error al verificar factura. Por favor, intente nuevamente.');
    } finally {
      setLoading(false);
    }
  };

  // Verificar automáticamente si viene hash en la URL
  useEffect(() => {
    if (hash) {
      verificarFactura(hash);
    }
  }, [hash]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (hashInput.trim()) {
      verificarFactura(hashInput.trim());
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8 border-t-4 border-green-500">
          <div className="flex items-center gap-4 mb-3">
            <div className="bg-green-100 p-3 rounded-full">
              <span className="text-4xl">🔍</span>
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                Verificación de Factura Electrónica
              </h1>
              <p className="text-gray-600 mt-1">
                Sistema de verificación pública con firma digital RSA-2048
              </p>
            </div>
          </div>
        </div>

        {/* Formulario de búsqueda */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-gray-700 mb-3">
                Ingrese el Hash SHA-256 de la factura:
              </label>
              <div className="flex gap-3">
                <input
                  type="text"
                  value={hashInput}
                  onChange={(e) => setHashInput(e.target.value)}
                  placeholder="Ejemplo: a56261f19ef8ff4507cfd91483a8ade56342020f31641bddea9f57a4f25780a3"
                  className="flex-1 px-4 py-3 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 font-mono text-sm"
                  required
                  disabled={loading}
                />
                <button
                  type="submit"
                  disabled={loading}
                  style={{ backgroundColor: '#16a34a', color: 'white' }}
                  className="px-8 py-3 font-bold rounded-lg hover:bg-green-700 disabled:bg-gray-400 shadow-lg transform transition hover:scale-105 disabled:transform-none disabled:cursor-not-allowed"
                >
                  {loading ? ' Verificando...' : '✓ Verificar'}
                </button>
              </div>
            </div>
            <div className="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
              <p className="text-sm text-blue-800">
                <span className="font-semibold"> Sugerencia:</span> Puede escanear el código QR de la factura o copiar y pegar el hash manualmente
              </p>
            </div>
          </form>
        </div>

        {/* Loading */}
        {loading && (
          <div className="bg-white rounded-lg shadow-lg p-12 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Verificando autenticidad...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <p className="text-red-800">❌ {error}</p>
          </div>
        )}

        {/* Resultado de verificación */}
        {!loading && verificacion && (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            {/* Estado */}
            <div className={`p-8 text-center ${
              verificacion.valida 
                ? 'bg-gradient-to-r from-green-500 to-green-600' 
                : 'bg-gradient-to-r from-red-500 to-red-600'
            }`}>
              <div className="text-7xl mb-3">
                {verificacion.valida ? '✅' : '❌'}
              </div>
              <h2 className="text-3xl font-bold text-white mb-2">
                {verificacion.valida ? 'FACTURA VÁLIDA' : 'FACTURA INVÁLIDA'}
              </h2>
              <p className="text-white text-lg">
                {verificacion.mensaje}
              </p>
            </div>

            {/* Detalles de la factura */}
            {verificacion.valida && verificacion.factura && (
              <div className="p-8">
                <h3 className="text-2xl font-bold text-gray-800 mb-6">
                  Información de la Factura
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Columna izquierda */}
                  <div className="space-y-4">
                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Número de Factura</p>
                      <p className="text-xl font-bold text-gray-900 font-mono">
                        {verificacion.factura.numero_factura}
                      </p>
                    </div>

                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Cliente</p>
                      <p className="text-lg font-medium text-gray-900">
                        {verificacion.factura.cliente}
                      </p>
                      <p className="text-sm text-gray-600">
                        CI/RUC: {verificacion.factura.identificacion}
                      </p>
                    </div>

                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Fecha de Emisión</p>
                      <p className="text-lg font-medium text-gray-900">
                        {verificacion.factura.fecha_emision}
                      </p>
                    </div>

                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Total</p>
                      <p className="text-2xl font-bold text-green-600">
                        ${verificacion.factura.total.toFixed(2)}
                      </p>
                    </div>
                  </div>

                  {/* Columna derecha */}
                  <div className="space-y-4">
                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Estado SRI</p>
                      <span className="inline-block px-3 py-1 bg-green-100 text-green-800 rounded-full font-medium">
                        {verificacion.factura.estado_sri}
                      </span>
                    </div>

                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Número de Autorización</p>
                      <p className="text-sm font-mono text-gray-700 break-all">
                        {verificacion.factura.num_autorizacion}
                      </p>
                    </div>

                    <div className="border-b pb-3">
                      <p className="text-sm text-gray-500 mb-1">Fecha de Autorización</p>
                      <p className="text-lg font-medium text-gray-900">
                        {verificacion.factura.fecha_autorizacion}
                      </p>
                    </div>

                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-start gap-3">
                        <span className="text-2xl">🔐</span>
                        <div>
                          <p className="font-medium text-blue-900">Firma Digital Válida</p>
                          <p className="text-sm text-blue-700">
                            La firma RSA-2048 ha sido verificada correctamente
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Información técnica */}
                <div className="mt-8 p-4 bg-gray-50 rounded-lg">
                  <details>
                    <summary className="cursor-pointer font-medium text-gray-700 hover:text-gray-900">
                       Ver detalles técnicos
                    </summary>
                    <div className="mt-4 space-y-2 text-sm">
                      <div>
                        <p className="text-gray-500">Hash SHA-256:</p>
                        <p className="font-mono text-xs break-all text-gray-700">{hash}</p>
                      </div>
                      <div className="text-gray-600 mt-3">
                        <p>✓ Algoritmo de firma: RSA-2048 con PSS padding</p>
                        <p>✓ Función hash: SHA-256</p>
                        <p>✓ Integridad del documento: Verificada</p>
                        <p>✓ Autenticidad del emisor: Confirmada</p>
                      </div>
                    </div>
                  </details>
                </div>
              </div>
            )}

            {/* Factura no encontrada */}
            {!verificacion.valida && verificacion.status === 'NO_ENCONTRADA' && (
              <div className="p-8">
                <div className="flex items-start gap-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <span className="text-3xl">⚠️</span>
                  <div>
                    <p className="font-medium text-yellow-900 mb-2">
                      Factura no encontrada en el sistema
                    </p>
                    <p className="text-sm text-yellow-700">
                      El hash proporcionado no corresponde a ninguna factura registrada.
                      Verifique que el código QR o hash sean correctos.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Factura alterada */}
            {!verificacion.valida && verificacion.status === 'ALTERADA' && (
              <div className="p-8">
                <div className="flex items-start gap-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                  <span className="text-3xl">⛔</span>
                  <div>
                    <p className="font-medium text-red-900 mb-2">
                      ¡ADVERTENCIA! Documento alterado
                    </p>
                    <p className="text-sm text-red-700 mb-3">
                      La firma digital no es válida o el contenido del documento ha sido modificado
                      después de su emisión. Esta factura NO debe ser considerada como auténtica.
                    </p>
                    <p className="text-xs text-red-600 font-mono">
                      Posible ataque detectado: Modificación no autorizada del XML o firma comprometida
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Instrucciones */}
        {!loading && !verificacion && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h3 className="font-bold text-lg text-gray-800 mb-4">
               ¿Cómo verificar una factura?
            </h3>
            <div className="space-y-3 text-gray-700">
              <div className="flex items-start gap-3">
                <span className="text-xl">1️⃣</span>
                <p>
                  <strong>Escanea el código QR</strong> de la factura impresa o PDF usando tu smartphone
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">2️⃣</span>
                <p>
                  <strong>O ingresa manualmente</strong> el hash SHA-256 que aparece en la factura
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">3️⃣</span>
                <p>
                  El sistema verificará la <strong>firma digital RSA-2048</strong> y la integridad del documento
                </p>
              </div>
              <div className="flex items-start gap-3">
                <span className="text-xl">4️⃣</span>
                <p>
                  Recibirás confirmación inmediata de la <strong>autenticidad</strong> de la factura
                </p>
              </div>
            </div>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong> Seguridad:</strong> Este sistema utiliza criptografía de clave pública RSA-2048 
                con SHA-256 para garantizar la autenticidad e integridad de las facturas electrónicas.
                Cualquier alteración del documento será detectada automáticamente.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
