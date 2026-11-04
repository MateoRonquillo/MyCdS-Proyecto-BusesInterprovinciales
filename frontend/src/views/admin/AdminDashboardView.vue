<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'

const modulosAdmin = ref([
  {
    id: 'M02',
    titulo: 'Cooperativas',
    descripcion: 'Registro, edición y estado activo/inactivo de cooperativas interprovinciales.',
    ruta: '/admin/cooperativas',
    estado: 'Operativo',
  },
  {
    id: 'M03',
    titulo: 'Buses y Plantillas',
    descripcion: 'Gestión de unidades, asociación a cooperativas y configuración de asientos.',
    ruta: '/admin/buses',
    estado: 'Operativo',
  },
  {
    id: 'M05 / M06',
    titulo: 'Rutas y Frecuencias',
    descripcion: 'Definición de origen, destino, horarios y asignación de unidades por trayecto.',
    ruta: '/admin/rutas',
    estado: 'Operativo',
  },
])
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="ADMINISTRADOR" />

    <main class="admin-main">
      <header class="admin-header">
        <div>
          <h1>Panel Administrativo</h1>
          <p class="subtitle">
            Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador
          </p>
        </div>
        <span class="badge-rol">Rol: Administrador</span>
      </header>

      <section class="admin-grid">
        <article v-for="modulo in modulosAdmin" :key="modulo.id" class="admin-card">
          <div class="card-header">
            <span class="module-tag">{{ modulo.id }}</span>
            <span class="status-tag">{{ modulo.estado }}</span>
          </div>
          <h2>{{ modulo.titulo }}</h2>
          <p>{{ modulo.descripcion }}</p>
          <RouterLink :to="modulo.ruta" class="card-action-link">
            Administrar módulo →
          </RouterLink>
        </article>
      </section>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f4f6f9;
  font-family: system-ui, -apple-system, sans-serif;
}
.admin-main {
  flex: 1;
  padding: 2rem;
}
.admin-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dce1e7;
}
.subtitle {
  color: #5c677d;
  margin-top: 0.25rem;
}
.badge-rol {
  background-color: #1e3a8a;
  color: #ffffff;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.85rem;
  font-weight: 600;
}
.admin-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1.5rem;
}
.admin-card {
  background: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}
.card-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.module-tag {
  font-weight: 700;
  color: #1d4ed8;
}
.status-tag {
  font-size: 0.8rem;
  color: #166534;
  background: #dcfce7;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-weight: 600;
}
.card-action-link {
  margin-top: auto;
  padding-top: 1rem;
  color: #1d4ed8;
  font-weight: 600;
  text-decoration: none;
}
</style>