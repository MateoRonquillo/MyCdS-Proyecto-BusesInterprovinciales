<script setup>
import { computed, onMounted, ref, watch, useId } from 'vue'
import { useDestinosStore } from '../../stores/destinos'
const props=defineProps({modelValue:String,etiqueta:String,origen:String,esOrigen:Boolean,disabled:Boolean})
const emit=defineEmits(['update:modelValue']), store=useDestinosStore(), provincia=ref(''), id=useId()
const disponibles=computed(()=>store.ciudades.filter(c=>props.esOrigen?store.conexiones.some(x=>x.origen===c.valor):props.origen?store.conexiones.some(x=>x.origen===props.origen&&x.destino===c.valor):store.conexiones.some(x=>x.destino===c.valor)))
const provincias=computed(()=>[...new Map(disponibles.value.map(c=>[c.provincia_id,{id:c.provincia_id,nombre:c.provincia}])).values()])
const ciudades=computed(()=>disponibles.value.filter(c=>c.provincia_id===provincia.value))
function sincronizar(){const c=disponibles.value.find(c=>c.valor===props.modelValue);if(c)provincia.value=c.provincia_id;else if(!provincias.value.some(p=>p.id===provincia.value))provincia.value=''}
watch([()=>props.modelValue,disponibles],sincronizar,{immediate:true})
watch(()=>props.origen,()=>{if(props.modelValue&&!disponibles.value.some(c=>c.valor===props.modelValue))emit('update:modelValue','')})
function cambiarProvincia(){emit('update:modelValue','')}
onMounted(()=>store.cargar())
</script>
<template><fieldset class="destination-select"><legend>{{ etiqueta }}</legend><div class="destination-fields"><label :for="`${id}-provincia`">Provincia<select :id="`${id}-provincia`" v-model="provincia" :disabled="disabled||store.cargando||!provincias.length" required @change="cambiarProvincia"><option value="" disabled>{{ store.cargando?'Cargando…':'Selecciona provincia' }}</option><option v-for="p in provincias" :key="p.id" :value="p.id">{{ p.nombre }}</option></select></label><label :for="`${id}-ciudad`">Ciudad<select :id="`${id}-ciudad`" :value="modelValue||''" :disabled="disabled||!provincia" required @change="emit('update:modelValue',$event.target.value)"><option value="" disabled>Selecciona ciudad</option><option v-for="c in ciudades" :key="c.valor" :value="c.valor">{{ c.ciudad }}</option></select></label></div><p v-if="store.error" class="form-error" role="alert">No se pudieron cargar los destinos. <button type="button" class="btn-quiet" @click="store.cargar">Reintentar</button></p><small v-else-if="store.cargado&&!disponibles.length">{{ origen?'No hay conexiones configuradas desde esta ciudad.':'No hay destinos disponibles en el catálogo.' }}</small></fieldset></template>
<style scoped>.destination-select{border:0;padding:0;margin:0;min-width:0}.destination-select legend{font-size:11px;font-weight:700;margin-bottom:8px;color:var(--text)}.destination-fields{display:grid;grid-template-columns:1fr 1fr;gap:8px}.destination-fields label{display:grid;gap:5px;min-width:0;font-size:10px;color:var(--muted)}select{width:100%;height:44px;border:1px solid var(--border);border-radius:6px;padding:0 9px;background:var(--surface-soft);color:var(--text);font-size:11px;text-overflow:ellipsis}.destination-select small{font-size:10px;color:var(--muted)}</style>
