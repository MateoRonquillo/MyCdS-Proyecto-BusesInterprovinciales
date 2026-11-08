<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { destinoCatalogo, SECCIONES_ADMIN, SECCIONES_COOPERATIVA } from '../../router/catalogos'
import PanelLayout from '../../components/panel/PanelLayout.vue'
import AppModal from '../../components/ui/AppModal.vue'
import AppIcon from '../../components/ui/AppIcon.vue'
import { useAuthStore } from '../../stores/auth'
import { request } from '../../services/http'
import { useDestinosStore } from '../../stores/destinos'
const props=defineProps({catalogo:{type:String,default:'buses'}})
const auth=useAuthStore(), destinos=useDestinosStore(), route=useRoute(), router=useRouter()
const admin=computed(()=>auth.rolFront==='ADMINISTRADOR')
const opciones=computed(()=>admin.value?SECCIONES_ADMIN:SECCIONES_COOPERATIVA)
const titulos={cooperativas:'Cooperativas',buses:admin.value?'Flota de transporte':'Mi flota',rutas:'Rutas y recorridos',frecuencias:'Frecuencias',jornadas:'Hoja de trabajo',configuracion:'Identidad del servicio'}
const descripciones={cooperativas:'Organiza las cooperativas que forman parte del servicio.',buses:'Unidades, características y distribución de asientos.',rutas:'Itinerarios claros, con tiempos y paradas intermedias.',frecuencias:'Conecta cada ruta con un bus, horario y tarifa.',jornadas:'Planifica las salidas y los días de parada de cada unidad.',configuracion:'Una identidad consistente en todos los puntos de contacto.'}
const seccionValida=v=>opciones.value.includes(v)?v:props.catalogo
const tab=ref(seccionValida(route.query.seccion)), items=ref([]), error=ref(''), aviso=ref(''), cargando=ref(false), ocupado=ref(false)
const edicion=ref(null), form=ref({}), paradas=ref([]), modal=ref(false), confirmar=ref(null), errorForm=ref(''), errorApoyo=ref(''), buscar=ref(''), pagina=ref(1)
const relaciones=ref({cooperativas:[],buses:[],rutas:[],frecuencias:[]}), geografia=ref([])
const hoy=new Date().toLocaleDateString('en-CA',{timeZone:'America/Guayaquil'}), fecha=ref(hoy)
const campos={
 cooperativas:[['nombre','Nombre'],['logo_url','URL del logo','url'],['color_principal','Color de identidad','color'],['activo','Cooperativa activa','checkbox']],
 buses:[['placa','Placa'],['numero_disco','Número de disco'],['cooperativa_id','Cooperativa','relacion'],['capacidad_asientos','Capacidad de asientos','number'],['chasis','Marca del chasis'],['carroceria','Marca de la carrocería'],['fotografia_url','URL de la fotografía','url'],['asientos_vip','Asientos VIP (separados por coma)'],['activo','Bus activo','checkbox']],
 rutas:[['origen','Ciudad de origen','ciudad'],['destino','Ciudad de destino','ciudad'],['duracion_estimada_horas','Duración del recorrido (horas)','number'],['activo','Ruta activa','checkbox']],
 frecuencias:[['ruta_id','Ruta','relacion'],['bus_id','Bus asignado','relacion'],['hora_salida','Hora de salida','time'],['precio','Tarifa completa (USD)','number'],['resolucion_ant','Referencia de resolución ANT'],['activo','Frecuencia activa','checkbox']],
 jornadas:[['fecha','Fecha de trabajo','date'],['bus_id','Bus','relacion'],['frecuencia_id','Frecuencia (vacío = día de parada)','relacion']],
 configuracion:[['nombre','Nombre del servicio'],['logo_url','URL del logo','url'],['color_principal','Color principal','color'],['soporte','Contacto de soporte'],['redes_sociales','Redes sociales']],
}
const visibles=computed(()=>campos[tab.value]||[])
const filtrados=computed(()=>items.value.filter(item=>Object.values(item).some(v=>String(v??'').toLowerCase().includes(buscar.value.toLowerCase()))))
const paginas=computed(()=>Math.max(1,Math.ceil(filtrados.value.length/8)))
const filas=computed(()=>filtrados.value.slice((pagina.value-1)*8,pagina.value*8))
watch(buscar,()=>pagina.value=1)
watch(()=>form.value.bus_id,()=>{if(tab.value==='jornadas'&&form.value.frecuencia_id&&!opcionesCampo('frecuencia_id').some(f=>f.id===Number(form.value.frecuencia_id)))form.value.frecuencia_id=''})
function nombreRelacion(tipo,id){return relaciones.value[tipo]?.find(v=>v.id===id)?.nombre||`#${id}`}
function opcionesCampo(key){
 const tabla={cooperativa_id:'cooperativas',bus_id:'buses',ruta_id:'rutas',frecuencia_id:'frecuencias'}[key]
 return (relaciones.value[tabla]||[]).filter(v=>key!=='frecuencia_id'||!form.value.bus_id||v.bus_id===Number(form.value.bus_id)).map(v=>({...v,nombre:v.nombre||`${nombreRelacion('rutas',v.ruta_id)} · ${v.hora_salida?.slice(0,5)}`}))
}
let secuencia=0
async function cargar(){const n=++secuencia;cargando.value=true;error.value='';pagina.value=1
 try{const datos=await request(`/${tab.value}${tab.value==='jornadas'?`?fecha=${fecha.value}`:''}`);if(n!==secuencia)return;items.value=tab.value==='configuracion'?[datos]:datos}
 catch(e){if(n===secuencia){error.value=e.message;items.value=[]}}finally{if(n===secuencia)cargando.value=false}
}
async function cargarRelaciones(){relaciones.value=await request('/panel/opciones')}
async function cargarApoyos(){
 errorApoyo.value=''
 const resultados=await Promise.allSettled([cargarRelaciones(),request('/ubicaciones')])
 if(resultados[1].status==='fulfilled')geografia.value=resultados[1].value.provincias
 errorApoyo.value=resultados.filter(r=>r.status==='rejected').map(r=>r.reason.message).join(' ')
}
onMounted(async()=>{await cargarApoyos();await cargar()})
watch(tab,()=>{buscar.value='';aviso.value='';modal.value=false;cargar()})
watch([()=>props.catalogo,()=>route.query.seccion],()=>{tab.value=seccionValida(route.query.seccion||props.catalogo)})
function cambiarTab(op){
 return router.push(destinoCatalogo(auth.rolFront,op))
}
function nuevo(item=null){
 edicion.value=item?.id??null;errorForm.value=''
 form.value=Object.fromEntries(visibles.value.map(([key,,type])=>[key,item?.[key]??(type==='checkbox'?true:type==='color'?'#185a4d':'')]))
 if(tab.value==='buses'&&!admin.value&&!form.value.cooperativa_id)form.value.cooperativa_id=relaciones.value.cooperativas[0]?.id||''
 if(tab.value==='jornadas')form.value.fecha=item?.fecha||fecha.value
 paradas.value=(item?.paradas||[]).map(p=>({ciudad:p.ciudad,minutos:p.minutos,proporcion_tarifa:p.proporcion_tarifa}))
 modal.value=true
}
function ciudadValida(valor){return geografia.value.some(p=>p.ciudades.some(c=>c.valor===valor||c.alias.includes(valor)))}
async function guardar(){if(ocupado.value)return;ocupado.value=true;errorForm.value=''
 try{const datos=Object.fromEntries(visibles.value.map(([key,,type])=>[key,['number','relacion'].includes(type)?(form.value[key]===''?null:Number(form.value[key])):type==='url'?(form.value[key]||null):form.value[key]]))
 if(tab.value==='rutas')datos.paradas=paradas.value.map(p=>({ciudad:p.ciudad,minutos:Number(p.minutos),proporcion_tarifa:Number(p.proporcion_tarifa)}))
 const singleton=tab.value==='configuracion'
 await request(`/${tab.value}${edicion.value&&!singleton?`/${edicion.value}`:''}`,{method:singleton||edicion.value?'PUT':'POST',body:JSON.stringify(datos)})
 destinos.cargado=false;modal.value=false;aviso.value='Los cambios se guardaron correctamente.';await Promise.all([cargar(),cargarApoyos()])
 }catch(e){errorForm.value=e.message}finally{ocupado.value=false}
}
async function eliminar(){ocupado.value=true;errorForm.value='';try{await request(`/${tab.value}/${confirmar.value.id}`,{method:'DELETE'});destinos.cargado=false;confirmar.value=null;aviso.value=tab.value==='jornadas'?'Jornada eliminada.':'Registro desactivado. El historial se conserva.';await cargar()}catch(e){errorForm.value=e.message}finally{ocupado.value=false}}
function principal(item){return item.nombre||item.placa||(tab.value==='rutas'?`${item.origen} → ${item.destino}`:tab.value==='frecuencias'?nombreRelacion('rutas',item.ruta_id):nombreRelacion('buses',item.bus_id))}
function detalle(item){return tab.value==='buses'?`${nombreRelacion('cooperativas',item.cooperativa_id)} · Disco ${item.numero_disco}`:tab.value==='frecuencias'?`${nombreRelacion('buses',item.bus_id)} · ${item.resolucion_ant||'Sin referencia ANT'}`:tab.value==='rutas'?`${item.paradas?.length||0} paradas intermedias`:tab.value==='jornadas'?item.fecha:item.soporte||item.logo_url||'Identidad de la cooperativa'}
</script>
<template><PanelLayout :titulo="titulos[tab]" :descripcion="descripciones[tab]" etiqueta="Gestión de la operación">
<template #acciones><button class="btn-primary" :disabled="cargando||!!errorApoyo" @click="nuevo(tab==='configuracion'?items[0]:null)"><AppIcon :name="tab==='configuracion'?'settings':'building'" :size="17"/>{{ tab==='configuracion'?'Editar identidad':'Nuevo registro' }}</button></template>
<nav class="tabs" aria-label="Catálogos de la operación"><button v-for="op in opciones" :key="op" class="tab" :aria-pressed="tab===op" @click="cambiarTab(op)">{{ titulos[op] }}</button></nav>
<div v-if="errorApoyo" class="alert error" role="alert">No se pudieron cargar las opciones de los formularios. {{ errorApoyo }} <button class="btn-quiet" @click="cargarApoyos">Reintentar opciones</button></div>
<div v-if="aviso" class="alert success" role="status">{{ aviso }}</div><div v-if="error" class="alert error" role="alert">{{ error }} <button class="btn-quiet" @click="cargar">Reintentar</button></div>
<div class="toolbar"><div class="search-control"><AppIcon name="search" :size="17"/><input v-model="buscar" class="control" :aria-label="`Buscar en ${titulos[tab]}`" placeholder="Buscar en los registros…"></div><div class="toolbar-controls"><label v-if="tab==='jornadas'" class="form-field">Fecha de trabajo<input v-model="fecha" type="date" @change="fecha&&cargar()"></label><span class="small muted">{{ filtrados.length }} registros</span><button class="icon-button" :disabled="cargando" aria-label="Actualizar registros" @click="cargar"><AppIcon name="refresh"/></button></div></div>
<p v-if="tab==='jornadas'" class="small muted">Una salida por bus y día. Registra una jornada sin frecuencia para indicar un día de parada.</p>
<section class="card"><div v-if="cargando" class="loading-state" role="status">Cargando registros…</div><div v-else-if="!filtrados.length" class="empty-state"><AppIcon name="search" :size="32"/><h3>{{ buscar?'No hay coincidencias':'Todavía no hay registros' }}</h3><p>{{ buscar?'Prueba con otro nombre o placa.':'Crea el primer registro para comenzar.' }}</p></div>
<div v-else class="table-scroll"><table class="data-table"><thead><tr><th>{{ tab==='buses'?'Unidad':'Registro' }}</th><th>Información</th><th>{{ tab==='jornadas'?'Asignación':'Estado' }}</th><th>Acciones</th></tr></thead><tbody><tr v-for="item in filas" :key="item.id"><td><strong>{{ principal(item) }}</strong><small>{{ detalle(item) }}</small></td><td><template v-if="tab==='buses'"><strong>{{ item.capacidad_asientos }} asientos</strong><small>{{ item.chasis||'Chasis sin registrar' }} · {{ item.carroceria||'Carrocería sin registrar' }}</small></template><template v-else-if="tab==='frecuencias'"><strong class="numeric">{{ item.hora_salida?.slice(0,5) }}</strong><small>USD {{ item.precio.toFixed(2) }}</small></template><template v-else-if="tab==='rutas'"><strong>{{ item.duracion_estimada_horas }} horas</strong><small>{{ item.paradas?.map(p=>p.ciudad).join(' · ')||'Recorrido directo' }}</small></template><template v-else-if="tab==='jornadas'"><strong>{{ item.frecuencia_id?`${relaciones.frecuencias.find(f=>f.id===item.frecuencia_id)?.hora_salida?.slice(0,5)||'Frecuencia #'+item.frecuencia_id}`:'Día de parada' }}</strong></template><template v-else><span class="color-swatch" :style="{background:item.color_principal||'#185a4d'}"></span>{{ item.color_principal||'Sin color' }}</template></td><td><span class="status-badge" :class="item.activo===false?'danger':'success'"><i></i>{{ tab==='jornadas'?(item.frecuencia_id?'Salida asignada':'Parada'):item.activo===false?'Inactivo':'Activo' }}</span></td><td><div class="table-actions"><button v-if="tab!=='jornadas'" class="btn-secondary" :disabled="!!errorApoyo" @click="nuevo(item)">Editar</button><button v-if="tab!=='configuracion'&&item.activo!==false" class="btn-quiet" @click="confirmar=item;errorForm=''">{{ tab==='jornadas'?'Eliminar':'Desactivar' }}</button></div></td></tr></tbody></table></div></section>
<div v-if="paginas>1" class="toolbar" style="margin-top:16px"><span class="small muted">Página {{ pagina }} de {{ paginas }}</span><div class="toolbar-controls"><button class="btn-secondary" :disabled="pagina===1" @click="pagina--">Anterior</button><button class="btn-secondary" :disabled="pagina===paginas" @click="pagina++">Siguiente</button></div></div>
<AppModal :abierto="modal" :titulo="`${edicion?'Editar':'Crear'} · ${titulos[tab]}`" :ocupado="ocupado" ancho @cerrar="modal=false"><form @submit.prevent="guardar"><div v-if="errorForm" class="alert error" role="alert">{{ errorForm }}</div><div class="form-grid"><template v-for="[key,label,type] in visibles" :key="key"><label v-if="type==='checkbox'" class="check-label full-width"><input v-model="form[key]" type="checkbox">{{ label }}</label><label v-else class="form-field">{{ label }}
<select v-if="type==='relacion'" v-model="form[key]" :required="key!=='frecuencia_id'"><option value="" :disabled="key!=='frecuencia_id'">{{ key==='frecuencia_id'?'Día de parada (sin frecuencia)':'Seleccionar…' }}</option><option v-for="op in opcionesCampo(key)" :key="op.id" :value="op.id">{{ op.nombre }}</option></select>
<select v-else-if="type==='ciudad'" v-model="form[key]" required><option value="" disabled>Seleccionar ciudad</option><option v-if="form[key]&&!ciudadValida(form[key])" :value="form[key]">{{ form[key] }} (registro anterior)</option><optgroup v-for="prov in geografia" :key="prov.id" :label="prov.nombre"><option v-for="c in prov.ciudades" :key="c.id" :value="c.alias.includes(form[key])?form[key]:c.valor">{{ c.nombre }}</option></optgroup></select>
<input v-else v-model="form[key]" :type="type||'text'" :min="type==='number'?'0.01':key==='fecha'?hoy:undefined" :step="type==='number'?'any':undefined" :required="!['logo_url','fotografia_url','chasis','carroceria','asientos_vip','soporte','redes_sociales'].includes(key)">
<small v-if="key==='asientos_vip'">Ejemplo: 1,2,3,4. Los demás asientos se consideran normales.</small><small v-if="key==='resolucion_ant'">Registra la referencia del documento revisado por la cooperativa.</small></label></template>
<div v-if="tab==='rutas'" class="full-width"><div class="toolbar"><h3 style="font-size:13px;margin:0">Paradas intermedias</h3><button type="button" class="btn-secondary" @click="paradas.push({ciudad:'',minutos:'',proporcion_tarifa:''})">Añadir parada</button></div><div v-for="(p,i) in paradas" :key="i" class="stop-row"><label class="form-field">Ciudad<select v-model="p.ciudad" required><option value="" disabled>Seleccionar</option><option v-if="p.ciudad&&!ciudadValida(p.ciudad)" :value="p.ciudad">{{ p.ciudad }}</option><optgroup v-for="prov in geografia" :key="prov.id" :label="prov.nombre"><option v-for="c in prov.ciudades" :key="c.id" :value="c.alias.includes(p.ciudad)?p.ciudad:c.valor">{{ c.nombre }}</option></optgroup></select></label><label class="form-field">Minutos desde origen<input v-model="p.minutos" type="number" min="1" required></label><label class="form-field">Proporción de tarifa<input v-model="p.proporcion_tarifa" type="number" min="0.001" max="0.999" step="0.001" required><small>0.25 equivale al 25% acumulado.</small></label><button class="btn-quiet" type="button" :aria-label="`Quitar parada ${i+1}`" @click="paradas.splice(i,1)">Quitar</button></div><p v-if="!paradas.length" class="small muted">Sin paradas: recorrido directo.</p></div>
<div class="form-actions full-width"><button type="button" class="btn-secondary" :disabled="ocupado" @click="modal=false">Cancelar</button><button class="btn-primary" :disabled="ocupado">{{ ocupado?'Guardando…':'Guardar cambios' }}</button></div></div></form></AppModal>
<AppModal :abierto="!!confirmar" :titulo="tab==='jornadas'?'Eliminar jornada':'Desactivar registro'" :ocupado="ocupado" @cerrar="confirmar=null"><p class="muted">{{ tab==='jornadas'?'Se retirará esta asignación de la hoja de trabajo.':'El registro dejará de estar disponible para nuevas operaciones. Su historial se conservará.' }}</p><p v-if="errorForm" class="alert error" role="alert">{{ errorForm }}</p><div class="form-actions"><button class="btn-secondary" :disabled="ocupado" @click="confirmar=null">Volver</button><button class="btn-danger" :disabled="ocupado" @click="eliminar">{{ ocupado?'Procesando…':'Confirmar' }}</button></div></AppModal>
</PanelLayout></template>
<style scoped>.color-swatch{display:inline-block;width:13px;height:13px;border:1px solid var(--border);border-radius:3px;vertical-align:-2px;margin-right:8px}.stop-row{display:grid;grid-template-columns:1.4fr 1fr 1fr auto;gap:12px;margin-bottom:16px;border:1px solid var(--border);border-radius:6px;padding:14px}.stop-row .btn-quiet{align-self:start;margin-top:20px}@media(max-width:760px){.stop-row{grid-template-columns:1fr}.stop-row .btn-quiet{margin:0}}</style>
