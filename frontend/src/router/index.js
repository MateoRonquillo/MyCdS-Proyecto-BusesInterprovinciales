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

  // Rutas protegidas (admin / oficinista)
  if (to.meta.requiresAuth) {
    if (!auth.estaAutenticado) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
    const permitido =
      !to.meta.role ||
      auth.rolFront === to.meta.role ||
      auth.rolFront === 'ADMINISTRADOR' // el admin puede ver ambos paneles
    if (!permitido) return auth.rutaInicio
    return
  }

  // Rutas públicas: el personal interno no las usa, va a su panel
  if (esPersonal) return auth.rutaInicio

  // Un cliente ya logueado no necesita volver al login
  if (to.name === 'login' && auth.estaAutenticado) return auth.rutaInicio
})

export default router