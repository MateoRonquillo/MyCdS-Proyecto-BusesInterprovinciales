<script setup>
import { computed, onMounted, ref } from 'vue'
import { useAuthStore } from '../../stores/auth'
import PanelLayout from '../../components/panel/PanelLayout.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import { request } from '../../services/http'
const auth = useAuthStore(), datos = ref(null), error = ref(''), cargando = ref(true)
const fecha = ref(new Date().toLocaleDateString('en-CA',{timeZone:'America/Guayaquil'}))
const oficina = computed(() => auth.rolFront === 'OFICINISTA')
const titulo = computed(() => oficina.value ? 'Cada viaje, bien coordinado.' : auth.rolFront === 'COOPERATIVA' ? 'Tu flota, en perspectiva.' : 'Una visión de la operación.')
const metricas = computed(() => !datos.value ? [] : oficina.value ? [
  ['Boletos confirmados',datos.value.boletos_confirmados,'ticket','Para la fecha seleccionada'],['Pagos por revisar',datos.value.pagos_por_revisar,'wallet','Todas las fechas'],['Importe confirmado',`$${datos.value.importe_confirmado.toFixed(2)}`,'wallet','Reservas confirmadas del día'],['Pasajeros a bordo',datos.value.abordados,'scan','Accesos registrados'],
] : [['Buses activos',datos.value.buses_activos,'bus','Flota disponible en el catálogo'],['Salidas habilitadas',datos.value.frecuencias_activas,'route','Para la fecha seleccionada'],['Reservas del día',datos.value.reservas,'ticket','Todos los estados'],['Pagos por revisar',datos.value.pagos_por_revisar,'wallet','Todas las fechas']])
const acciones = computed(() => oficina.value ? [
  ['Nueva venta','Asientos, pasajero y cobro en efectivo','/oficinista/ventas','ticket'],['Revisar pagos','Validar comprobantes y emitir boletos','/oficinista/pagos','wallet'],['Reservas y boletos','Consultar estados y descargar documentos','/oficinista/reservas','route'],
] : auth.rolFront === 'COOPERATIVA' ? [
  ['Gestionar mi flota','Unidades y distribución de asientos','/operacion?seccion=buses','bus'],['Organizar salidas','Frecuencias de tu cooperativa','/operacion?seccion=frecuencias','route'],['Planificar el día','Asignaciones y días de parada','/operacion?seccion=jornadas','calendar'],
] : [['Administrar cooperativas','Identidad y estado de operación','/admin/cooperativas','building'],['Gestionar frecuencias','Rutas, horarios y tarifas','/operacion?seccion=frecuencias','route'],['Supervisar ventas','Comprobantes y boletos pendientes','/oficinista/pagos','wallet'],['Configurar el servicio','Marca y canales de atención','/operacion?seccion=configuracion','settings']])
let ultimaConsulta=0
async function cargar(){
 if(!fecha.value)return
 const consulta=++ultimaConsulta;cargando.value=true;error.value=''
 try{const respuesta=await request(`/panel/resumen?fecha=${fecha.value}`);if(consulta===ultimaConsulta)datos.value=respuesta}
 catch(e){if(consulta===ultimaConsulta)error.value=e.message}
 finally{if(consulta===ultimaConsulta)cargando.value=false}
}
onMounted(cargar)
</script>
<template><PanelLayout :titulo="titulo" descripcion="Información real para tomar decisiones, atender a los pasajeros y preparar la próxima salida.">
<template #acciones><label class="form-field"><span class="sr-only">Fecha del resumen</span><input v-model="fecha" type="date" aria-label="Fecha del resumen" @change="cargar"></label><button class="icon-button" :disabled="cargando" aria-label="Actualizar resumen" @click="cargar"><AppIcon name="refresh"/></button></template>
<div v-if="error" class="alert error" role="alert">{{ error }} <button class="btn-quiet" @click="cargar">Reintentar</button></div>
<div v-if="cargando" class="loading-state" role="status">Consultando la operación…</div>
<template v-else-if="datos"><div class="metric-grid"><article v-for="[label,valor,icono,detalle] in metricas" :key="label" class="card metric-card"><AppIcon class="metric-icon" :name="icono"/><span class="metric-label">{{ label }}</span><strong class="metric-value">{{ valor }}</strong><p class="metric-foot">{{ detalle }}</p></article></div>
<div class="section-grid"><section class="card"><div class="card-heading"><div><h2>Salidas del día</h2><p>Horarios y asientos con reserva en algún tramo.</p></div><span class="small muted">{{ datos.salidas.length }} salidas</span></div>
<div v-if="!datos.salidas.length" class="empty-state"><AppIcon name="calendar" :size="32"/><h3>No hay salidas habilitadas</h3><p>Consulta otra fecha o revisa la hoja de trabajo.</p></div>
<div v-else class="table-scroll"><table class="data-table"><thead><tr><th>Recorrido</th><th>Salida</th><th>Bus</th><th>Ocupación por asiento</th></tr></thead><tbody><tr v-for="s in datos.salidas" :key="s.id"><td><strong>{{ s.ruta }}</strong><small>Desde ${{ s.precio.toFixed(2) }} · tarifa completa</small></td><td class="numeric">{{ s.hora.slice(0,5) }}</td><td>{{ s.bus }}</td><td><span class="small numeric">{{ s.asientos_con_reserva }} / {{ s.capacidad }}</span><div class="progress-bar"><span :style="{width:`${s.asientos_con_reserva/s.capacidad*100}%`}"></span></div></td></tr></tbody></table></div></section>
<div class="stack"><section class="card"><div class="card-heading"><h2>Accesos de trabajo</h2></div><div class="action-list"><RouterLink v-for="[label,detalle,ruta,icono] in acciones" :key="ruta" :to="ruta" class="action-link"><AppIcon :name="icono"/><span><strong>{{ label }}</strong><small>{{ detalle }}</small></span><AppIcon name="arrow" :size="16"/></RouterLink></div></section><div class="card card-body"><p class="eyebrow-label">Una atención consistente</p><h3 style="font-size:17px;font-weight:550">Todo listo para el siguiente viaje.</h3><p class="small muted" style="margin:0">Revisa los pagos, confirma las asignaciones y mantén a tu equipo informado antes de cada salida.</p></div></div></div></template>
</PanelLayout></template>
