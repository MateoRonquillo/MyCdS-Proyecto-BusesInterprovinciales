export const adminRoutes = [
  {
    path: '/admin',
    name: 'admin-dashboard',
    component: () => import('../views/admin/AdminDashboardView.vue'),
    meta: { requiresAuth: true, role: 'ADMINISTRADOR' },
  },
  {
    path: '/admin/cooperativas',
    name: 'admin-cooperativas',
    component: () => import('../views/admin/CooperativasView.vue'),
    meta: { requiresAuth: true, role: 'ADMINISTRADOR' },
  },
  {
    path: '/admin/buses',
    name: 'admin-buses',
    component: () => import('../views/admin/BusesView.vue'),
    meta: { requiresAuth: true, role: 'ADMINISTRADOR' },
  },
  {
    path: '/admin/rutas',
    name: 'admin-rutas',
    component: () => import('../views/admin/RutasView.vue'),
    meta: { requiresAuth: true, role: 'ADMINISTRADOR' },
  },
  {
    path: '/oficinista',
    name: 'oficinista-dashboard',
    component: () => import('../views/oficinista/OficinistaDashboardView.vue'),
    meta: { requiresAuth: true, role: 'OFICINISTA' },
  },
]

export default adminRoutes