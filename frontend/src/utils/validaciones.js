export function validarCedula(cedula = '') {
  if (!/^\d{10}$/.test(cedula)) return false
  const provincia = Number(cedula.slice(0, 2))
  if (provincia < 1 || provincia > 24) return false
  if (Number(cedula[2]) > 5) return false
  const coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
  const suma = coeficientes.reduce((acc, k, i) => {
    let v = Number(cedula[i]) * k
    if (v > 9) v -= 9
    return acc + v
  }, 0)
  return (10 - (suma % 10)) % 10 === Number(cedula[9])
}

export const validarCorreo = (correo = '') => /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(correo.trim())

export const validarNombres = (nombres = '') => nombres.trim().length >= 3 && /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]+$/.test(nombres.trim())