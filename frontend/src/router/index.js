import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../components/cliente/PublicLayout.vue'
import adminRoutes from './admin.routes.js'
import { useAuthStore } from '../stores/auth'
import { destinoCatalogo } from './catalogos'

const routes = [
  {
    path: '/',
    component: PublicLayout,
    children: [
      {
        path: '',
        name: 'inicio',
        component: () => import('../views/cliente/InicioView.vue'),
      },
      {
        path: 'viajes',
        name: 'viajes',
        component: () => import('../views/cliente/ViajesView.vue'),
      },
      {
        path: 'login',
        name: 'login',
        component: () => import('../views/cliente/LoginView.vue'),
      },
      { path: 'compras', name: 'compras', component: () => import('../views/cliente/ComprasView.vue'), meta: { requiresAuth: true, role: 'CLIENTE' } },
      { path: 'registro', component: () => import('../views/cliente/RegistroView.vue') },
      {
        path: 'reservar',
        name: 'reservar',
        component: () => import('../views/cliente/ReservaView.vue'),
        meta: { requiresAuth: true, role: 'CLIENTE' },
      },
      { path: 'mis-reservas', redirect: { name: 'compras' } },
    ],
  },
  ...adminRoutes,
  { path: '/cooperativa', component: () => import('../views/panel/ResumenView.vue'), meta: { requiresAuth: true, role: 'COOPERATIVA' } },
  { path: '/operacion', component: () => import('../views/admin/OperacionView.vue'), meta: { requiresAuth: true, role: 'COOPERATIVA' } },
  { path: '/abordaje/ventas', component: () => import('../views/oficinista/VentaPresencialView.vue'), props: { porAsignacion: true }, meta: { requiresAuth: true, ventaAsignada: true } },
  { path: '/abordaje', component: () => import('../views/personal/AbordajeView.vue'), meta: { requiresAuth: true, role: 'PERSONAL' } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

export function crearRouter(historial = createWebHistory()) {
const router = createRouter({
  history: historial,
  routes,
})

router.beforeEach((to) => {
  const auth = useAuthStore()
  const esPersonal = auth.estaAutenticado && auth.rolFront !== 'CLIENTE'

  if (to.meta.requiresAuth) {
    if (!auth.estaAutenticado) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    const permitido =
      !to.meta.role ||
      auth.rolFront === to.meta.role ||
      auth.rolFront === 'ADMINISTRADOR'
    if (!permitido || (to.meta.ventaAsignada && !['chofer', 'ayudante'].includes(auth.usuario?.rol))) return auth.rutaInicio
    if (to.path === '/operacion') {
      const destino = destinoCatalogo(auth.rolFront, to.query.seccion)
      if (router.resolve(destino).fullPath !== to.fullPath) {
        return typeof destino === 'string' ? { path: destino, replace: true } : { ...destino, replace: true }
      }
    }
    return
  }

  if (esPersonal) return auth.rutaInicio

  if (to.name === 'login' && auth.estaAutenticado) return auth.rutaInicio
})

return router
}

export default crearRouter()