<script setup>
import { onMounted, ref, useId, watch } from 'vue'
const props = defineProps({ abierto:Boolean, titulo:String, descripcion:String, ocupado:Boolean, ancho:Boolean })
const emit = defineEmits(['cerrar']), dialogo = ref(null), id = useId()
function sincronizar(){ if(!dialogo.value)return; if(props.abierto && !dialogo.value.open) dialogo.value.showModal(); else if(!props.abierto && dialogo.value.open) dialogo.value.close() }
watch(() => props.abierto, sincronizar)
onMounted(sincronizar)
function cancelar(e){e.preventDefault();if(!props.ocupado)emit('cerrar')}
</script>
<template><dialog ref="dialogo" class="modal" :class="{wide:ancho}" :aria-labelledby="id" @cancel="cancelar" @close="emit('cerrar')"><div class="modal-heading"><div><h2 :id="id">{{ titulo }}</h2><p v-if="descripcion">{{ descripcion }}</p></div><button class="modal-close" :disabled="ocupado" type="button" aria-label="Cerrar diálogo" @click="emit('cerrar')">×</button></div><div class="card-body"><slot/></div></dialog></template>
<style scoped>dialog{padding:0;color:var(--text)}dialog::backdrop{background:var(--overlay);backdrop-filter:blur(3px)}</style>
