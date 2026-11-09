// Adaptadores del catálogo persistente. Los datos usan el contrato snake_case de la API.
import { request } from './http'
export const obtenerCooperativas = () => request('/cooperativas')
export const obtenerBuses = () => request('/buses')
export const obtenerRutasYFrecuencias = () => request('/rutas')
const guardar = (ruta, datos) => {
  const { id, ...payload } = datos
  return request(`${ruta}${id ? `/${id}` : ''}`, { method: id ? 'PUT' : 'POST', body: JSON.stringify(payload) })
}
export const guardarCooperativaService = datos => guardar('/cooperativas', datos)
export const guardarBusService = datos => guardar('/buses', datos)
export const guardarRutaYFrecuenciaService = datos => guardar('/rutas', datos)
