export const TEMAS = ['sistema', 'claro', 'oscuro']
export const normalizarTema = tema => TEMAS.includes(tema) ? tema : 'sistema'
export const resolverTema = (tema, oscuro) => tema === 'oscuro' || (normalizarTema(tema) === 'sistema' && oscuro) ? 'oscuro' : 'claro'
