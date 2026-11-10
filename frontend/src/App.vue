<script setup>
import { onMounted, onBeforeUnmount } from 'vue'
import { useTemaStore } from './stores/tema'
import { useAppStore } from './stores/app'
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { SESION_EXPIRADA } from './services/sesion'
const app = useAppStore()
const auth = useAuthStore()
const router = useRouter()
const tema = useTemaStore()
tema.iniciar()
function expirarSesion() {
  const destino = router.currentRoute.value.fullPath
  auth.logout()
  if (router.currentRoute.value.name !== 'login') {
    router.replace({ name: 'login', query: { redirect: destino, sesion: 'expirada' } })
  }
}
onBeforeUnmount(() => {
  tema.detener()
  window.removeEventListener(SESION_EXPIRADA, expirarSesion)
})
onMounted(() => {
  window.addEventListener(SESION_EXPIRADA, expirarSesion)
  app.cargar()
})
</script>
<template><RouterView /></template>
