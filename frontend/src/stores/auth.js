import { defineStore } from 'pinia'
import { iniciarSesion } from '../services/auth'

const leerUsuario = () => {
  try {
    return JSON.parse(localStorage.getItem('usuario')) || null
  } catch {
    return null
  }
}

const ROL_FRONT = { admin: 'ADMINISTRADOR', oficinista: 'OFICINISTA' }

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    usuario: leerUsuario(),
  }),

  getters: {
    estaAutenticado: (s) => !!s.token && !!s.usuario,
    rolFront: (s) => ROL_FRONT[s.usuario?.rol] || 'CLIENTE',
    rutaInicio() {
      if (this.rolFront === 'ADMINISTRADOR') return '/admin'
      if (this.rolFront === 'OFICINISTA') return '/oficinista'
      return '/'
    },
  },

  actions: {
    async login(correo, password) {
      const { access_token, usuario } = await iniciarSesion(correo, password)
      this.token = access_token
      this.usuario = usuario
      localStorage.setItem('token', access_token)
      localStorage.setItem('usuario', JSON.stringify(usuario))
    },
    logout() {
      this.token = ''
      this.usuario = null
      localStorage.removeItem('token')
      localStorage.removeItem('usuario')
      localStorage.removeItem('pasajeros-por-reserva')
    },
  },
})