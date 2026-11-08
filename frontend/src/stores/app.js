import { defineStore } from 'pinia'
import { request } from '../services/http'
export const useAppStore = defineStore('app', {
  state: () => ({ nombre: 'Pasajes EC', logo_url: null, color_principal: '#146d83', soporte: '', redes_sociales: '' }),
  actions: {
    async cargar() {
      try {
        const datos = await request('/configuracion')
        Object.assign(this, datos)
        document.documentElement.style.setProperty('--color-primario', this.color_principal)
        document.title = this.nombre
      } catch { /* Mantiene la identidad local si el servidor no está disponible. */ }
    },
  },
})
