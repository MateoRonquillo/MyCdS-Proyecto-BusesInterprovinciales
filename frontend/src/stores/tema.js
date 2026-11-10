import { defineStore } from 'pinia'
import { normalizarTema, resolverTema } from '../utils/tema'
let medios, escuchar
export const useTemaStore = defineStore('tema', {
  state: () => ({ preferencia: 'sistema', oscuroSistema: false }),
  getters: { efectivo: s => resolverTema(s.preferencia, s.oscuroSistema) },
  actions: {
    aplicar() { document.documentElement.dataset.theme = this.efectivo; document.documentElement.style.colorScheme = this.efectivo === 'oscuro' ? 'dark' : 'light'; document.querySelector('meta[name="theme-color"]')?.setAttribute('content', this.efectivo === 'oscuro' ? '#0d1117' : '#f4f5f1') },
    elegir(tema) {
      this.preferencia = normalizarTema(tema)
      try { localStorage.setItem('pasajes-tema', this.preferencia) } catch { /* La selección sigue funcionando sin almacenamiento. */ }
      this.aplicar()
    },
    iniciar() {
      try { this.preferencia = normalizarTema(localStorage.getItem('pasajes-tema')) } catch { this.preferencia = 'sistema' }
      medios = window.matchMedia('(prefers-color-scheme: dark)')
      this.oscuroSistema = medios.matches
      escuchar = e => { this.oscuroSistema = e.matches; this.aplicar() }
      medios.addEventListener('change', escuchar)
      this.aplicar()
    },
    detener() { medios?.removeEventListener('change', escuchar) },
  },
})
