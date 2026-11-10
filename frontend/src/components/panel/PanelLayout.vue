<script setup>
import { computed, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import AdminSidebar from '../admin/AdminSidebar.vue'
import ThemePicker from '../ui/ThemePicker.vue'
import AppIcon from '../ui/AppIcon.vue'
const props = defineProps({ titulo: String, descripcion: String, etiqueta: {type:String, default:'Centro de operaciones'} })
const auth = useAuthStore(), abierta = ref(false)
const rol = computed(() => ({admin:'Administración',cooperativa:'Cooperativa',oficinista:'Oficina de ventas',chofer:'Conducción',ayudante:'Asistencia de viaje'}[auth.usuario?.rol] || 'Operaciones'))
const fecha = new Intl.DateTimeFormat('es-EC', { dateStyle:'long', timeZone:'America/Guayaquil' }).format(new Date())
</script>
<template><div class="panel-shell"><a href="#panel-contenido" class="skip-link">Saltar al contenido</a><AdminSidebar :abierta="abierta" @cerrar="abierta=false"/>
<div class="panel-workspace"><header class="workspace-topbar"><div class="topbar-context"><button class="icon-button mobile-menu" aria-label="Abrir navegación" :aria-expanded="abierta" @click="abierta=!abierta"><AppIcon name="menu"/></button><span class="workspace-role">{{ rol }}</span><span class="topbar-date">{{ fecha }}</span></div><ThemePicker/></header>
<main id="panel-contenido" class="panel-content"><div class="page-intro"><div><p class="eyebrow-label">{{ etiqueta }}</p><h1>{{ titulo }}</h1><p v-if="descripcion" class="intro-description">{{ descripcion }}</p></div><div class="intro-actions"><slot name="acciones"/></div></div><slot/></main>
<footer class="workspace-footer"><span>Pasajes EC · Gestión de transporte</span><span>America/Guayaquil · USD</span></footer></div></div></template>
