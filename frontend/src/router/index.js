import { createRouter, createWebHistory } from 'vue-router'
import PublicLayout from '../components/cliente/PublicLayout.vue'
import adminRoutes from './admin.routes.js'
import { useAuthStore } from '../stores/auth'

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
      {
        path: 'reservar',
        name: 'reservar',
        component: () => import('../views/cliente/ReservaView.vue'),
        meta: { requiresAuth: true, role: 'CLIENTE' },
      },
      {
        path: 'mis-reservas',
        name: 'mis-reservas',
        component: () => import('../views/cliente/MisReservasView.vue'),
        meta: { requiresAuth: true, role: 'CLIENTE' },
      },
    ],
  },
  ...adminRoutes,
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHistory(),
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
    if (!permitido) return auth.rutaInicio
    return
  }

  if (esPersonal) return auth.rutaInicio

  if (to.name === 'login' && auth.estaAutenticado) return auth.rutaInicio
})

export default router