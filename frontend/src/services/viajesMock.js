import { normalizar } from '../utils/texto'

export const CIUDADES = [
  'Ambato', 'Cuenca', 'Esmeraldas', 'Guayaquil', 'Ibarra', 'Latacunga',
  'Loja', 'Machala', 'Manta', 'Portoviejo', 'Quito', 'Riobamba',
  'Santo Domingo', 'Tulcán',
]

const COOPERATIVAS = {
  andina: { id: 1, nombre: 'Andina Express', color_principal: '#166b83' },
  sol: { id: 2, nombre: 'Flota del Sol', color_principal: '#c9892b' },
  austro: { id: 3, nombre: 'Trans Austro', color_principal: '#2f7d4f' },
  cotopaxi: { id: 4, nombre: 'Expreso Cotopaxi', color_principal: '#8a3f64' },
}

const TRAYECTOS = [
  { a: 'Quito', b: 'Ambato', min: 150, precio: 4.0, coops: ['andina', 'cotopaxi'], salidas: ['05:00', '07:30', '10:00', '13:30', '16:00', '19:30'] },
  { a: 'Quito', b: 'Guayaquil', min: 480, precio: 11.5, coops: ['andina', 'sol'], salidas: ['06:00', '09:00', '13:00', '21:30', '23:00'] },
  { a: 'Quito', b: 'Cuenca', min: 540, precio: 13.0, coops: ['austro', 'andina'], salidas: ['07:00', '14:30', '21:00', '22:30'] },
  { a: 'Quito', b: 'Ibarra', min: 150, precio: 3.5, coops: ['cotopaxi', 'sol'], salidas: ['05:30', '08:00', '12:00', '15:30', '18:00'] },
  { a: 'Quito', b: 'Riobamba', min: 210, precio: 5.5, coops: ['cotopaxi', 'andina'], salidas: ['06:30', '09:30', '14:00', '17:30'] },
  { a: 'Cuenca', b: 'Guayaquil', min: 240, precio: 8.0, coops: ['austro', 'sol'], salidas: ['05:30', '08:30', '12:00', '15:00', '18:30'] },
  { a: 'Cuenca', b: 'Loja', min: 270, precio: 8.5, coops: ['austro'], salidas: ['06:00', '11:00', '16:30', '22:00'] },
  { a: 'Ambato', b: 'Riobamba', min: 60, precio: 1.8, coops: ['cotopaxi', 'andina'], salidas: ['06:00', '08:00', '11:00', '14:00', '17:00'] },
  { a: 'Ambato', b: 'Guayaquil', min: 330, precio: 8.0, coops: ['sol', 'andina'], salidas: ['05:15', '10:30', '15:45', '22:15'] },
  { a: 'Guayaquil', b: 'Machala', min: 180, precio: 5.0, coops: ['sol', 'austro'], salidas: ['06:00', '09:30', '13:00', '17:00'] },
  { a: 'Guayaquil', b: 'Manta', min: 240, precio: 6.5, coops: ['sol'], salidas: ['05:45', '10:00', '15:30', '20:00'] },
  { a: 'Quito', b: 'Santo Domingo', min: 180, precio: 4.5, coops: ['andina', 'sol'], salidas: ['06:00', '09:00', '13:30', '17:30'] },
]

const TIPOS_BUS = ['Convencional', 'Semicama', 'Ejecutivo']

function sumarMinutos(hora, minutos) {
  const [h, m] = hora.split(':').map(Number)
  const total = h * 60 + m + minutos
  const hh = Math.floor((total % 1440) / 60)
  const mm = total % 60
  return `${String(hh).padStart(2, '0')}:${String(mm).padStart(2, '0')}`
}

function semilla(texto) {
  let h = 0
  for (const c of texto) h = (h * 31 + c.charCodeAt(0)) >>> 0
  return h
}

function asientos(sem) {
  const mezcla = Math.imul(sem ^ (sem >>> 15), 2246822507) >>> 0
  return mezcla % 7 === 0 ? 0 : (mezcla >>> 8) % 40 + 1
}

function nombreCiudad(valor) {
  return CIUDADES.find((c) => normalizar(c) === normalizar(valor)) || valor
}

export function generarViajesMock({ origen, destino, fecha }) {
  const o = normalizar(origen)
  const d = normalizar(destino)
  const trayecto = TRAYECTOS.find(
    (t) => (normalizar(t.a) === o && normalizar(t.b) === d) || (normalizar(t.a) === d && normalizar(t.b) === o),
  )
  if (!trayecto) return { items: [], total: 0 }

  const items = []
  trayecto.salidas.forEach((hora, i) => {
    const claveCoop = trayecto.coops[i % trayecto.coops.length]
    const sem = semilla(`${trayecto.a}${trayecto.b}${fecha}${hora}`)
    const tipo = TIPOS_BUS[sem % TIPOS_BUS.length]
    const recargo = tipo === 'Ejecutivo' ? 1.25 : tipo === 'Semicama' ? 1.1 : 1
    items.push({
      id: sem,
      cooperativa: { ...COOPERATIVAS[claveCoop], logo_url: null },
      origen: nombreCiudad(origen),
      destino: nombreCiudad(destino),
      fecha,
      hora_salida: hora,
      hora_llegada: sumarMinutos(hora, trayecto.min),
      duracion_min: trayecto.min,
      precio: Math.round(trayecto.precio * recargo * 100) / 100,
      asientos_disponibles: asientos(sem),
      tipo_bus: tipo,
    })
  })
  return { items, total: items.length }
}