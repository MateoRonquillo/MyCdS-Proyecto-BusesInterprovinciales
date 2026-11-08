import { API_URL } from './api'
import { USAR_MOCKS } from './viajes'

export const MAX_PASAJEROS = 10

export const TIPOS_PASAJERO = [
  { valor: 'GENERAL', etiqueta: 'Adulto', descuento: 0 },
  { valor: 'ADULTO_MAYOR', etiqueta: 'Tercera edad', descuento: 50 },
  { valor: 'DISCAPACIDAD', etiqueta: 'Persona con discapacidad', descuento: 50 },
  { valor: 'NINO_ADOLESCENTE', etiqueta: 'Niño o adolescente', descuento: 50 },
  { valor: 'ESTUDIANTE', etiqueta: 'Estudiante', descuento: 50 },
]

export const etiquetaTipo = (valor) => TIPOS_PASAJERO.find((t) => t.valor === valor)?.etiqueta || valor

export class ApiError extends Error {
  constructor(mensaje, status) {
    super(mensaje)
    this.status = status
  }
}

export async function pedir(ruta, opciones = {}) {
  const token = localStorage.getItem('token')
  let r
  try {
    r = await fetch(`${API_URL}/api/v1${ruta}`, {
      ...opciones,
      headers: { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}) },
    })
  } catch {
    throw new ApiError('No se pudo conectar con el servidor. Intenta nuevamente.', 0)
  }
  if (r.status === 204) return null
  const datos = await r.json().catch(() => ({}))
  if (!r.ok) {
    const e = datos.error
    const detalle = e?.details?.[0]?.message?.replace(/^Value error, /, '')
    const msg = e?.code === 'validation_error' ? detalle || 'Revisa los datos ingresados.'
      : e?.message || (typeof datos.detail === 'string' ? datos.detail : 'No se pudo completar la solicitud.')
    throw new ApiError(r.status === 401 ? 'Tu sesión expiró. Inicia sesión nuevamente.' : msg, r.status)
  }
  return datos
}

const reservadasMock = new Set()
const pausa = (ms = 350) => new Promise((res) => setTimeout(res, ms))
const redondear = (n) => Math.round(n * 100) / 100

function ocupadosMock(viaje) {
  const capacidad = 40
  const libres = Math.min(viaje.asientos_disponibles ?? 20, capacidad)
  let s = (viaje.id >>> 0) || 1
  const rnd = () => (s = (Math.imul(s, 1664525) + 1013904223) >>> 0) / 4294967296
  const todos = Array.from({ length: capacidad }, (_, i) => i + 1)
  for (let i = todos.length - 1; i > 0; i--) {
    const j = Math.floor(rnd() * (i + 1))
    ;[todos[i], todos[j]] = [todos[j], todos[i]]
  }
  const propios = todos.slice(0, capacidad - libres)
  const nuevos = [...reservadasMock].filter((k) => k.startsWith(`${viaje.id}|${viaje.fecha}|`)).map((k) => Number(k.split('|')[2]))
  return [...new Set([...propios, ...nuevos])].sort((a, b) => a - b)
}

function tarifaMock(viaje, tipos) {
  const detalle = tipos.map((tipo) => {
    const descuento = tipo === 'GENERAL' ? 0 : redondear(viaje.precio * 0.5)
    return { tipo_pasajero: tipo, precio_unitario: viaje.precio, descuento_porcentaje: tipo === 'GENERAL' ? 0 : 50, descuento, total: redondear(viaje.precio - descuento) }
  })
  return {
    cantidad_pasajeros: tipos.length,
    subtotal: redondear(viaje.precio * tipos.length),
    descuento_total: redondear(detalle.reduce((a, d) => a + d.descuento, 0)),
    total: redondear(detalle.reduce((a, d) => a + d.total, 0)),
    detalle,
  }
}

export async function obtenerDisponibilidad(viaje) {
  if (USAR_MOCKS) {
    await pausa()
    return { capacidad: 40, ocupados: ocupadosMock(viaje) }
  }
  const d = await pedir(`/reservas/disponibilidad/${viaje.id}?fecha=${viaje.fecha}&origen_orden=${viaje.origen_orden ?? 0}${viaje.destino_orden == null ? '' : `&destino_orden=${viaje.destino_orden}`}`)
  return { capacidad: d.capacidad_total, ocupados: d.asientos_ocupados, mapa: d.mapa_asientos }
}

export async function calcularTarifa(viaje, tipos) {
  if (USAR_MOCKS) {
    await pausa(200)
    return tarifaMock(viaje, tipos)
  }
  return pedir('/tarifas/calcular', { method: 'POST', body: JSON.stringify({ frecuencia_id: viaje.id, tipos_pasajero: tipos, origen_orden: viaje.origen_orden ?? 0, destino_orden: viaje.destino_orden }) })
}

export async function crearReservas(viaje, pasajeros) {
  const creadas = []
  try {
    for (const p of pasajeros) {
      if (USAR_MOCKS) {
        await pausa(150)
        const clave = `${viaje.id}|${viaje.fecha}|${p.asiento}`
        if (reservadasMock.has(clave)) throw new ApiError('El asiento ya está reservado para este viaje', 409)
        reservadasMock.add(clave)
        creadas.push({ id: Date.now() + creadas.length, asiento: p.asiento, tipo_pasajero: p.tipo, precio: tarifaMock(viaje, [p.tipo]).total, estado: 'PENDIENTE' })
      } else {
        creadas.push(await pedir('/reservas', {
          method: 'POST',
          body: JSON.stringify({ frecuencia_id: viaje.id, fecha_viaje: viaje.fecha, asiento: p.asiento, tipo_pasajero: p.tipo, pasajero_nombre: p.nombres, pasajero_cedula: p.cedula, origen_orden: viaje.origen_orden ?? 0, destino_orden: viaje.destino_orden }),
        }))
      }
    }
    return creadas
  } catch (e) {
    for (const r of creadas) {
      if (USAR_MOCKS) reservadasMock.delete(`${viaje.id}|${viaje.fecha}|${r.asiento}`)
      else await pedir(`/reservas/${r.id}`, { method: 'DELETE' }).catch(() => {})
    }
    throw e
  }
}