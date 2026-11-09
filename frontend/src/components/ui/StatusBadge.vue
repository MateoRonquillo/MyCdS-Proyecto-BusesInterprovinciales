<script setup>
import { computed } from 'vue'
const props = defineProps({ estado: String })
const etiquetas = { PENDIENTE: 'Pendiente de pago', PAGO_EN_REVISION:'Pago en revisión', CONFIRMADA:'Confirmada', PAGADA:'Pagada', CANCELADA:'Cancelada', EXPIRADA:'Expirada', APROBADO:'Aprobado', RECHAZADO:'Rechazado', ABORDADO:'A bordo', POR_ABORDAR:'Por abordar' }
const tono = computed(() => ['CONFIRMADA','APROBADO','ABORDADO','PAGADA'].includes(props.estado) ? 'success' : ['CANCELADA','EXPIRADA','RECHAZADO'].includes(props.estado) ? 'danger' : 'pending')
</script>
<template><span class="status-badge" :class="tono"><i></i>{{ etiquetas[estado] || estado }}</span></template>
