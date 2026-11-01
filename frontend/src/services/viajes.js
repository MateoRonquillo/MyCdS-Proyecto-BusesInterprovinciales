import { API_URL } from './api'
import { generarViajesMock } from './viajesMock'

export const USAR_MOCKS = import.meta.env.VITE_USE_MOCKS !== 'false'

const PAUSA_SIMULADA_MS = 450

export async function buscarViajes({ origen, destino, fecha }) {
  if (USAR_MOCKS) {
    await new Promise((resolve) => setTimeout(resolve, PAUSA_SIMULADA_MS))
    return generarViajesMock({ origen, destino, fecha })
  }

  const params = new URLSearchParams({ origen, destino, fecha })
  let respuesta
  try {
    respuesta = await fetch(`${API_URL}/api/v1/viajes?${params}`)
  } catch {
    throw new Error('No se pudo conectar con el servidor. Intenta nuevamente.')
  }
  if (!respuesta.ok) {
    throw new Error('No se pudieron consultar los viajes en este momento.')
  }
  return respuesta.json()
}