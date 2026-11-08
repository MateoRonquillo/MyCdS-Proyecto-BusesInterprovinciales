import { API_URL } from './api'
import { SESION_EXPIRADA } from './sesion'

export async function request(path, options = {}) {
  const token = localStorage.getItem('token')
  let r
  try { r = await fetch(`${API_URL}/api/v1${path}`, {
    ...options,
    headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...options.headers },
  }) } catch { throw new Error('No se pudo conectar con el servidor. Revisa tu conexión e intenta nuevamente.') }
  if (!r.ok) {
    if (r.status === 401 && token && localStorage.getItem('token') === token) {
      window.dispatchEvent(new Event(SESION_EXPIRADA))
    }
    const data = await r.json().catch(() => ({}))
    const detalle = data.error?.details?.[0]?.message?.replace(/^Value error, /, '')
    const mensaje = data.error?.code === 'validation_error' ? `Revisa los datos ingresados.${detalle ? ' ' + detalle : ''}` : data.error?.message || data.detail
    const error = new Error(r.status === 401 ? 'Tu sesión expiró. Vuelve a ingresar para continuar.' : mensaje || 'No se pudo completar la operación.')
    error.status = r.status
    throw error
  }
  if (r.status === 204) return null
  return options.blob ? r.blob() : r.json()
}

export async function descargar(path, nombre) {
  const blob = await request(path, { blob: true })
  const url = URL.createObjectURL(blob)
  const enlace = document.createElement('a')
  enlace.href = url
  enlace.download = nombre
  enlace.click()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

export function leerImagen(archivo) {
  if (!archivo || archivo.size > 2_000_000 || !['image/png', 'image/jpeg'].includes(archivo.type)) {
    return Promise.reject(new Error('Selecciona un comprobante PNG o JPEG de hasta 2 MB.'))
  }
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(reader.result)
    reader.onerror = () => reject(new Error('No se pudo leer la imagen.'))
    reader.readAsDataURL(archivo)
  })
}
