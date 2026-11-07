import { API_URL } from './api'
import { ApiError, pedir } from './reservas'

export const ESTADOS = {
  PENDIENTE: { etiqueta: 'Pendiente de pago', tono: 'aviso' },
  PAGO_EN_REVISION: { etiqueta: 'Pago en revisión', tono: 'info' },
  PAGADA: { etiqueta: 'Pagada', tono: 'ok' },
  CONFIRMADA: { etiqueta: 'Confirmada', tono: 'ok' },
  CANCELADA: { etiqueta: 'Cancelada', tono: 'malo' },
  EXPIRADA: { etiqueta: 'Expirada', tono: 'malo' },
}

export const METODOS = [
  { valor: 'DEPOSITO', etiqueta: 'Depósito' },
  { valor: 'TRANSFERENCIA', etiqueta: 'Transferencia' },
  { valor: 'EFECTIVO', etiqueta: 'Efectivo (en oficina)' },
]

export const obtenerHistorial = () => pedir('/reservas/historial')
export const obtenerPagos = () => pedir('/pagos')
export const cancelarReserva = (id) => pedir(`/reservas/${id}`, { method: 'DELETE' })

export const registrarPago = (reservaId, metodo, monto, referencia) =>
  pedir('/pagos', {
    method: 'POST',
    body: JSON.stringify({ reserva_id: reservaId, metodo_pago: metodo, monto, referencia: referencia || null }),
  })

export async function obtenerQr(reservaId) {
  const token = localStorage.getItem('token')
  let r
  try {
    r = await fetch(`${API_URL}/api/v1/boletos/${reservaId}/qr`, {
      headers: token ? { Authorization: `Bearer ${token}` } : {},
    })
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. Intenta nuevamente.', 0)
  }
  if (!r.ok) {
    const datos = await r.json().catch(() => ({}))
    throw new ApiError(
      r.status === 401 ? 'Tu sesión expiró. Inicia sesión nuevamente.' : datos.error?.message || 'No se pudo cargar el boleto.',
      r.status,
    )
  }
  return URL.createObjectURL(await r.blob())
}

export const CLAVE_PASAJEROS = 'pasajeros-por-reserva'

const leerPasajeros = () => {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_PASAJEROS)) || {}
  } catch {
    return {}
  }
}

export function guardarPasajeros(reservas, pasajeros) {
  const mapa = leerPasajeros()
  reservas.forEach((r, i) => {
    if (pasajeros[i]) mapa[r.id] = { nombres: pasajeros[i].nombres, cedula: pasajeros[i].cedula }
  })
  try {
    localStorage.setItem(CLAVE_PASAJEROS, JSON.stringify(mapa))
  } catch {
  }
}

export const obtenerPasajero = (reservaId) => leerPasajeros()[reservaId] || null