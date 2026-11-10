<script setup>
import { useTemaStore } from '../../stores/tema'
const tema = useTemaStore()
</script>
<template><label class="theme-picker"><span>Tema</span><select aria-label="Tema del sistema" :value="tema.preferencia" @change="tema.elegir($event.target.value)"><option value="sistema">Sistema</option><option value="claro">Claro</option><option value="oscuro">Oscuro</option></select></label></template>
<style scoped>.theme-picker{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--muted)}.theme-picker select{min-height:36px;padding:6px 25px 6px 10px;background:var(--surface);border:1px solid var(--border);color:var(--text);border-radius:6px;font:inherit}</style>
