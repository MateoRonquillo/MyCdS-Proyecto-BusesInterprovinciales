import { defineStore } from 'pinia'
import { buscarViajes, USAR_MOCKS } from '../services/viajes'

export const FRANJAS = [
  { valor: 'madrugada', etiqueta: 'Madrugada', rango: '00:00 – 05:59', desde: 0, hasta: 360 },
  { valor: 'manana', etiqueta: 'Mañana', rango: '06:00 – 11:59', desde: 360, hasta: 720 },
  { valor: 'tarde', etiqueta: 'Tarde', rango: '12:00 – 17:59', desde: 720, hasta: 1080 },
  { valor: 'noche', etiqueta: 'Noche', rango: '18:00 – 23:59', desde: 1080, hasta: 1440 },
]

export const ORDENES = [
  { valor: 'hora', etiqueta: 'Hora de salida' },
  { valor: 'precio', etiqueta: 'Menor precio' },
  { valor: 'duracion', etiqueta: 'Menor duración' },
]

const filtrosIniciales = () => ({
  cooperativa: '',
  franjas: [],
  precioMax: null,
  soloDisponibles: false,
  orden: 'hora',
})

const aMinutos = (hora) => {
  const [h, m] = hora.split(':').map(Number)
  return h * 60 + m
}

export const useViajesStore = defineStore('viajes', {
  state: () => ({
    consulta: null,
    resultados: [],
    estado: 'inicial',
    error: '',
    filtros: filtrosIniciales(),
    datosSimulados: USAR_MOCKS,
  }),

  getters: {
    cooperativas: (state) => {
      const mapa = new Map()
      state.resultados.forEach((v) => mapa.set(v.cooperativa.id, v.cooperativa.nombre))
      return [...mapa].map(([id, nombre]) => ({ id, nombre })).sort((a, b) => a.nombre.localeCompare(b.nombre))
    },
    precioMinimo: (state) => (state.resultados.length ? Math.floor(Math.min(...state.resultados.map((v) => v.precio))) : 0),
    precioMaximo: (state) => (state.resultados.length ? Math.ceil(Math.max(...state.resultados.map((v) => v.precio))) : 0),
    filtrosActivos(state) {
      const f = state.filtros
      return [f.cooperativa !== '', f.franjas.length > 0, f.precioMax !== null && f.precioMax < this.precioMaximo, f.soloDisponibles].filter(Boolean).length
    },
    viajesFiltrados(state) {
      const f = state.filtros
      const rangos = FRANJAS.filter((x) => f.franjas.includes(x.valor))
      const lista = state.resultados.filter((v) => {
        if (f.cooperativa !== '' && v.cooperativa.id !== Number(f.cooperativa)) return false
        if (f.soloDisponibles && v.asientos_disponibles <= 0) return false
        if (f.precioMax !== null && v.precio > f.precioMax) return false
        if (rangos.length) {
          const min = aMinutos(v.hora_salida)
          if (!rangos.some((r) => min >= r.desde && min < r.hasta)) return false
        }
        return true
      })
      const criterios = {
        hora: (a, b) => aMinutos(a.hora_salida) - aMinutos(b.hora_salida),
        precio: (a, b) => a.precio - b.precio || aMinutos(a.hora_salida) - aMinutos(b.hora_salida),
        duracion: (a, b) => a.duracion_min - b.duracion_min || aMinutos(a.hora_salida) - aMinutos(b.hora_salida),
      }
      return [...lista].sort(criterios[f.orden] || criterios.hora)
    },
  },

  actions: {
    limpiarFiltros() {
      this.filtros = { ...filtrosIniciales(), precioMax: this.precioMaximo || null }
    },
    async buscar(consulta) {
      this.consulta = { ...consulta }
      this.estado = 'cargando'
      this.error = ''
      try {
        const { items } = await buscarViajes(consulta)
        if (this.consulta.origen !== consulta.origen || this.consulta.destino !== consulta.destino || this.consulta.fecha !== consulta.fecha) return
        this.resultados = items
        this.limpiarFiltros()
        this.estado = 'listo'
      } catch (e) {
        this.resultados = []
        this.error = e.message
        this.estado = 'error'
      }
    },
  },
})