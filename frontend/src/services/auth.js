import { API_URL } from './api'

export async function iniciarSesion(correo, password) {
  let respuesta
  try {
    respuesta = await fetch(`${API_URL}/api/v1/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ correo, password }),
    })
  } catch {
    throw new Error('No se pudo conectar con el servidor. Intenta más tarde.')
  }

  const datos = await respuesta.json().catch(() => ({}))
  if (!respuesta.ok) {
    throw new Error(
      typeof datos.detail === 'string' ? datos.detail : 'Revisa los datos ingresados.',
    )
  }
  return datos
}