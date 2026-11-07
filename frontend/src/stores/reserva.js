import { defineStore } from 'pinia'

const CLAVE = 'reserva-borrador'
const nuevoPasajero = () => ({ nombres: '', cedula: '', correo: '', tipo: 'GENERAL', asiento: null })
const leer = () => {
  try {
    return JSON.parse(sessionStorage.getItem(CLAVE)) || {}
  } catch {
    return {}
  }
}

export const useReservaStore = defineStore('reserva', {
  state: () => ({ viaje: null, pasajeros: [], creadas: [], ...leer() }),

  actions: {
    iniciar(viaje) {
      this.viaje = { ...viaje }
      this.pasajeros = [nuevoPasajero()]
      this.creadas = []
      this.guardar()
    },
    fijarCantidad(n) {
      while (this.pasajeros.length < n) this.pasajeros.push(nuevoPasajero())
      if (this.pasajeros.length > n) this.pasajeros.splice(n)
    },
    guardar() {
      sessionStorage.setItem(CLAVE, JSON.stringify({ viaje: this.viaje, pasajeros: this.pasajeros, creadas: this.creadas }))
    },
    limpiar() {
      this.viaje = null
      this.pasajeros = []
      this.creadas = []
      sessionStorage.removeItem(CLAVE)
    },
  },
})