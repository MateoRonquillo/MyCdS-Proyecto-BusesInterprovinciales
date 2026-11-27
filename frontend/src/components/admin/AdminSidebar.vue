<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { useAppStore } from '../../stores/app'
import AppIcon from '../ui/AppIcon.vue'
const auth = useAuthStore(), app = useAppStore()
const props = defineProps({ abierta: Boolean })
const emit = defineEmits(['cerrar'])
const enlaces = computed(() => {
  if (auth.rolFront === 'PERSONAL') return [
    {nombre:'Control de abordaje', ruta:'/abordaje', icono:'scan'},
    {nombre:'Emitir boleto de mi ruta', ruta:'/abordaje/ventas', icono:'ticket'},
  ]
  if (auth.rolFront === 'OFICINISTA') return [
    {nombre:'Resumen',ruta:'/oficinista',icono:'overview'}, {nombre:'Nueva venta',ruta:'/oficinista/ventas',icono:'ticket'},
    {nombre:'Reservas y boletos',ruta:'/oficinista/reservas',icono:'route'}, {nombre:'Revisión de pagos',ruta:'/oficinista/pagos',icono:'wallet'},
  ]
  if (auth.rolFront === 'COOPERATIVA') return [
    {nombre:'Resumen',ruta:'/cooperativa',icono:'overview'}, {nombre:'Mi flota',ruta:'/operacion?seccion=buses',icono:'bus'},
    {nombre:'Frecuencias',ruta:'/operacion?seccion=frecuencias',icono:'route'}, {nombre:'Hoja de trabajo',ruta:'/operacion?seccion=jornadas',icono:'calendar'},
  ]
  return [
    {nombre:'Resumen',ruta:'/admin',icono:'overview'}, {nombre:'Cooperativas',ruta:'/admin/cooperativas',icono:'building'},
    {nombre:'Flota',ruta:'/admin/buses',icono:'bus'}, {nombre:'Rutas',ruta:'/admin/rutas',icono:'route'},
    {nombre:'Frecuencias',ruta:'/operacion?seccion=frecuencias',icono:'calendar'},
    {nombre:'Hoja de trabajo',ruta:'/operacion?seccion=jornadas',icono:'calendar'},
    {nombre:'Venta presencial',ruta:'/oficinista/ventas',icono:'ticket'},
    {nombre:'Reservas y pagos',ruta:'/oficinista/pagos',icono:'wallet'}, {nombre:'Abordaje',ruta:'/abordaje',icono:'scan'},
    {nombre:'Configuración',ruta:'/operacion?seccion=configuracion',icono:'settings'},
  ]
})
</script>
<template>
<div v-if="abierta" class="sidebar-scrim" @click="emit('cerrar')"></div>
<aside class="sidebar" :class="{ abierta }">
<RouterLink :to="auth.rutaInicio" class="panel-brand" @click="emit('cerrar')"><span class="brand-mark"><AppIcon name="route" :size="25"/></span><span>{{ app.nombre }}<small>Operaciones · Ecuador</small></span></RouterLink>
<p class="nav-caption">ESPACIO DE TRABAJO</p>
<nav aria-label="Navegación del panel"><RouterLink v-for="item in enlaces" :key="item.ruta" :to="item.ruta" class="panel-nav-link" :class="{ actual: $route.fullPath === item.ruta }" @click="emit('cerrar')"><AppIcon :name="item.icono"/><span>{{ item.nombre }}</span></RouterLink></nav>
<div class="sidebar-note"><span class="live-dot"></span><div>Una operación conectada<small>Viajes, ventas y acceso en un lugar.</small></div></div>
<div class="sidebar-user"><span class="avatar">{{ auth.usuario?.nombre?.slice(0, 1) }}</span><div><strong>{{ auth.usuario?.nombre }}</strong><small>{{ auth.usuario?.correo }}</small></div></div>
<RouterLink class="panel-nav-link signout" to="/login" @click="auth.logout()"><AppIcon name="logout"/>Cerrar sesión</RouterLink>
</aside>
</template>
