<script setup>
import PanelLayout from '../../components/panel/PanelLayout.vue'
import ComprasView from '../cliente/ComprasView.vue'
</script>
<template><PanelLayout titulo="Revisión de pagos" descripcion="Una bandeja de comprobantes para validar, resolver y emitir boletos."><ComprasView oficina vista-inicial="pagos"/></PanelLayout></template>
