<script setup>
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
function cerrarSesion() {
  auth.logout()
  router.push('/login')
}

defineProps({
  rol: {
    type: String,
    default: 'ADMINISTRADOR'
  }
})

const enlacesNavegacion = [
  { nombre: 'Dashboard Admin', ruta: '/admin', seccion: 'ADMIN' },
  { nombre: 'Cooperativas (M02)', ruta: '/admin/cooperativas', seccion: 'ADMIN' },
  { nombre: 'Buses y Plantillas (M03)', ruta: '/admin/buses', seccion: 'ADMIN' },
  { nombre: 'Rutas y Frecuencias (M04)', ruta: '/admin/rutas', seccion: 'ADMIN' },
  { nombre: 'Panel Oficinista (M08)', ruta: '/oficinista', seccion: 'OFICINA' },
  { nombre: 'Aprobación de Pagos (M06)', ruta: '/oficinista/pagos', seccion: 'OFICINA' },
  { nombre: 'Ventas Presenciales', ruta: '/oficinista/ventas', seccion: 'OFICINA' }
]
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <h2>Pasajes EC</h2>
      <small>Panel de Control ({{ rol }})</small>
    </div>

    <nav class="sidebar-nav">
      <ul>
        <li v-for="item in enlacesNavegacion" :key="item.ruta">
          <a :href="item.ruta" class="nav-link">
            <span class="section-pill">{{ item.seccion }}</span>
            <span>{{ item.nombre }}</span>
          </a>
        </li>
      </ul>
    </nav>

    <button type="button" class="btn-salir" @click="cerrarSesion">Cerrar sesión</button>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  background-color: #0f172a;
  color: #f8fafc;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 1rem;
}
.sidebar-brand {
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #334155;
}
.sidebar-brand h2 {
  margin: 0;
  font-size: 1.25rem;
}
.sidebar-brand small {
  color: #94a3b8;
}
.sidebar-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  color: #cbd5e1;
  text-decoration: none;
  border-radius: 6px;
  margin-bottom: 0.35rem;
  font-size: 0.9rem;
}
.nav-link:hover {
  background-color: #1e293b;
  color: #ffffff;
}
.section-pill {
  font-size: 0.65rem;
  background: #334155;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
}
.btn-salir {
  margin-top: auto;
  padding: 10px 14px;
  border: 1px solid #334155;
  border-radius: 8px;
  background: transparent;
  color: #f8fafc;
  font-weight: 600;
}
.btn-salir:hover {
  background: #1e293b;
}
</style>