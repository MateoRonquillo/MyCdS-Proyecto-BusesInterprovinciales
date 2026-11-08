export const SECCIONES_ADMIN = ['cooperativas', 'buses', 'rutas', 'frecuencias', 'jornadas', 'configuracion']
export const SECCIONES_COOPERATIVA = ['buses', 'frecuencias', 'jornadas']
const RUTAS_ADMIN = { cooperativas: '/admin/cooperativas', buses: '/admin/buses', rutas: '/admin/rutas' }

export function destinoCatalogo(rol, seccion) {
  const permitidas = rol === 'ADMINISTRADOR' ? SECCIONES_ADMIN : SECCIONES_COOPERATIVA
  const elegida = permitidas.includes(seccion) ? seccion : 'buses'
  return rol === 'ADMINISTRADOR' && RUTAS_ADMIN[elegida]
    ? RUTAS_ADMIN[elegida]
    : { path: '/operacion', query: { seccion: elegida } }
}
