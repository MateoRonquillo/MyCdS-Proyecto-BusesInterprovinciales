<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAppStore } from '../../stores/app'
import { useAuthStore } from '../../stores/auth'

const app = useAppStore()
const auth = useAuthStore()
const router = useRouter()
const menuAbierto = ref(false)

function salir() {
  auth.logout()
  menuAbierto.value = false
  router.push('/')
}
</script>

<template>
  <div class="layout-publico">
    <header class="site-header">
      <div class="site-topline">Rutas interprovinciales · Ecuador <span>Tu próximo destino comienza aquí</span></div>
      <div class="header-inner">
        <RouterLink to="/" class="brand" @click="menuAbierto = false" :aria-label="`${app.nombre} - Inicio`">
          <span class="brand-symbol" aria-hidden="true">↗</span>
          <span class="brand-text">Rutas<span>Ecuador</span><small>Viaja más fácil</small></span>
        </RouterLink>
        <button class="menu-toggle" type="button" :aria-expanded="menuAbierto" aria-controls="nav-publica" @click="menuAbierto = !menuAbierto">
          <span aria-hidden="true">☰</span> Menú
        </button>
        <nav id="nav-publica" class="site-nav" :class="{ abierta: menuAbierto }" aria-label="Navegación principal">
          <RouterLink to="/" @click="menuAbierto = false">Inicio</RouterLink>
          <RouterLink to="/viajes" @click="menuAbierto = false">Buscar viajes</RouterLink>

          <template v-if="auth.estaAutenticado">
            <span class="nav-usuario">Hola, {{ auth.usuario.nombre.split(' ')[0] }}</span>
            <button type="button" class="nav-salir" @click="salir">Salir</button>
          </template>
          <RouterLink v-else to="/login" @click="menuAbierto = false">Ingresar</RouterLink>

          <RouterLink class="nav-cta" to="/viajes" @click="menuAbierto = false">Explorar rutas <span aria-hidden="true">→</span></RouterLink>
        </nav>
      </div>
    </header>
    <main id="contenido" class="public-main"><RouterView /></main>
    <footer class="site-footer">
      <div class="footer-inner">
        <div><strong>↗ RutasEcuador</strong><p>Una mejor forma de planificar tus viajes por Ecuador.</p></div>
        <div class="footer-links"><RouterLink to="/">Inicio</RouterLink><RouterLink to="/viajes">Buscar viajes</RouterLink></div>
      </div>
      <div class="footer-bottom">Sistema de Gestión y Venta de Pasajes Interprovinciales del Ecuador · Proyecto académico</div>
    </footer>
  </div>
</template>

<style scoped>
.nav-usuario {
  font-size: 15px;
  font-weight: 600;
  color: var(--color-navy);
}
.nav-salir {
  font-size: 15px;
  border: 1px solid var(--color-borde);
  background: #fff;
  color: var(--color-navy);
  padding: 8px 16px;
  border-radius: 10px;
  font-weight: 600;
}
.nav-salir:hover {
  background: var(--color-fondo);
}
</style>