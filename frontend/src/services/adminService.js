import { API_URL } from './api'

export const USAR_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false'

const cooperativasIniciales = [
  {
    id: 1,
    nombre: 'Cooperativa Panamericana Internacional',
    ruc: '1790012345001',
    telefono: '02-250-1122',
    correo: 'operaciones@panamericana.ec',
    terminalBase: 'Quito - Quitumbe',
    colorPrimario: '#1e3a8a',
    activa: true,
  },
  {
    id: 2,
    nombre: 'Flota Imbabura',
    ruc: '1090054321001',
    telefono: '06-295-0333',
    correo: 'contacto@flotaimbabura.ec',
    terminalBase: 'Ibarra / Quito',
    colorPrimario: '#0f766e',
    activa: true,
  },
  {
    id: 3,
    nombre: 'Transportes Baños',
    ruc: '1890098765001',
    telefono: '03-274-0415',
    correo: 'info@transportesbanos.ec',
    terminalBase: 'Ambato / Baños / Puyo',
    colorPrimario: '#b45309',
    activa: true,
  },
]

const busesIniciales = [
  {
    id: 1,
    numeroDisco: 'DISCO-14',
    placa: 'PAA-1420',
    cooperativaId: 1,
    cooperativaNombre: 'Cooperativa Panamericana Internacional',
    tipoServicio: 'Ejecutivo',
    plantillaAsientos: '2x2 Estándar (40 asientos)',
    capacidadTotal: 40,
    estado: 'OPERATIVO',
  },
  {
    id: 2,
    numeroDisco: 'DISCO-08',
    placa: 'IAA-0832',
    cooperativaId: 2,
    cooperativaNombre: 'Flota Imbabura',
    tipoServicio: 'Normal',
    plantillaAsientos: '2x2 Clásico (44 asientos)',
    capacidadTotal: 44,
    estado: 'OPERATIVO',
  },
  {
    id: 3,
    numeroDisco: 'DISCO-25',
    placa: 'TAA-2519',
    cooperativaId: 3,
    cooperativaNombre: 'Transportes Baños',
    tipoServicio: 'Ejecutivo',
    plantillaAsientos: '2x2 Estándar (40 asientos)',
    capacidadTotal: 40,
    estado: 'MANTENIMIENTO',
  },
]

const rutasIniciales = [
  {
    id: 1,
    origen: 'Quito',
    destino: 'Ambato',
    distanciaKm: 140,
    duracionEstimada: '02h45m',
    tarifaBase: 4.5,
    frecuenciaHora: '06:30',
    diasOperacion: 'Lunes a Domingo',
    busAsignado: 'DISCO-14 (PAA-1420)',
    activa: true,
  },
  {
    id: 2,
    origen: 'Ambato',
    destino: 'Puyo',
    distanciaKm: 102,
    duracionEstimada: '02h30m',
    tarifaBase: 3.75,
    frecuenciaHora: '08:00',
    diasOperacion: 'Lunes a Domingo',
    busAsignado: 'DISCO-25 (TAA-2519)',
    activa: true,
  },
  {
    id: 3,
    origen: 'Quito',
    destino: 'Guayaquil',
    distanciaKm: 420,
    duracionEstimada: '08h00m',
    tarifaBase: 12.0,
    frecuenciaHora: '21:30',
    diasOperacion: 'Lunes a Domingo',
    busAsignado: 'DISCO-08 (IAA-0832)',
    activa: true,
  },
]

let memoriaCooperativas = [...cooperativasIniciales]
let memoriaBuses = [...busesIniciales]
let memoriaRutas = [...rutasIniciales]

export async function obtenerCooperativas() {
  if (USAR_MOCKS) {
    return [...memoriaCooperativas]
  }
  const resp = await fetch(`${API_URL}/api/v1/cooperativas`)
  if (!resp.ok) throw new Error('No se pudieron consultar las cooperativas.')
  return resp.json()
}

export async function guardarCooperativaService(datos) {
  if (USAR_MOCKS) {
    if (datos.id) {
      memoriaCooperativas = memoriaCooperativas.map((item) =>
        item.id === datos.id ? { ...datos } : item
      )
      return datos
    }
    const nueva = { ...datos, id: Date.now() }
    memoriaCooperativas.push(nueva)
    return nueva
  }
  const metodo = datos.id ? 'PUT' : 'POST'
  const url = datos.id
    ? `${API_URL}/api/v1/cooperativas/${datos.id}`
    : `${API_URL}/api/v1/cooperativas`
  const resp = await fetch(url, {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  if (!resp.ok) throw new Error('Error al guardar la cooperativa.')
  return resp.json()
}

export async function obtenerBuses() {
  if (USAR_MOCKS) {
    return [...memoriaBuses]
  }
  const resp = await fetch(`${API_URL}/api/v1/buses`)
  if (!resp.ok) throw new Error('No se pudieron consultar los buses.')
  return resp.json()
}

export async function guardarBusService(datos) {
  if (USAR_MOCKS) {
    if (datos.id) {
      memoriaBuses = memoriaBuses.map((item) =>
        item.id === datos.id ? { ...datos } : item
      )
      return datos
    }
    const nuevo = { ...datos, id: Date.now() }
    memoriaBuses.push(nuevo)
    return nuevo
  }
  const metodo = datos.id ? 'PUT' : 'POST'
  const url = datos.id
    ? `${API_URL}/api/v1/buses/${datos.id}`
    : `${API_URL}/api/v1/buses`
  const resp = await fetch(url, {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  if (!resp.ok) throw new Error('Error al guardar la unidad.')
  return resp.json()
}

export async function obtenerRutasYFrecuencias() {
  if (USAR_MOCKS) {
    return [...memoriaRutas]
  }
  const resp = await fetch(`${API_URL}/api/v1/rutas`)
  if (!resp.ok) throw new Error('No se pudieron consultar las rutas.')
  return resp.json()
}

export async function guardarRutaYFrecuenciaService(datos) {
  if (USAR_MOCKS) {
    if (datos.id) {
      memoriaRutas = memoriaRutas.map((item) =>
        item.id === datos.id ? { ...datos } : item
      )
      return datos
    }
    const nueva = { ...datos, id: Date.now() }
    memoriaRutas.push(nueva)
    return nueva
  }
  const metodo = datos.id ? 'PUT' : 'POST'
  const url = datos.id
    ? `${API_URL}/api/v1/rutas/${datos.id}`
    : `${API_URL}/api/v1/rutas`
  const resp = await fetch(url, {
    method: metodo,
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(datos),
  })
  if (!resp.ok) throw new Error('Error al guardar la ruta y frecuencia.')
  return resp.json()
}