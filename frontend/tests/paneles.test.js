import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { nextTick } from 'vue'
import { readFileSync } from 'node:fs'
const css = readFileSync('src/design-system.css', 'utf8')
import { request, descargar } from '../src/services/http'
import { useAuthStore } from '../src/stores/auth'
import { useTemaStore } from '../src/stores/tema'
import { useDestinosStore } from '../src/stores/destinos'
import ThemePicker from '../src/components/ui/ThemePicker.vue'
import SelectorDestino from '../src/components/cliente/SelectorDestino.vue'
import AdminSidebar from '../src/components/admin/AdminSidebar.vue'
import Venta from '../src/views/oficinista/VentaPresencialView.vue'
import Compras from '../src/views/cliente/ComprasView.vue'
import Abordaje from '../src/views/personal/AbordajeView.vue'
vi.mock('../src/services/http',()=>({request:vi.fn(),descargar:vi.fn(),leerImagen:vi.fn(async()=> 'data:image/png;base64,imagen')}))
const wrappers=[]
const stubLink={props:['to'],template:'<a :href="typeof to===\'string\'?to:to?.path"><slot/></a>'}
function montar(componente,options={}){const w=mount(componente,{global:{plugins:[createPinia()],mocks:{$route:{fullPath:'/'}},stubs:{RouterLink:stubLink}},attachTo:document.body,...options});wrappers.push(w);return w}
function boton(w,texto){return w.findAll('button').find(b=>b.text().includes(texto))}
const viaje={id:1,fecha:'2030-01-01',origen:'Quito',destino:'Cuenca',origen_orden:0,destino_orden:2,hora_salida:'08:00',hora_llegada:'16:00',precio:20,asientos_disponibles:5,cooperativa:{nombre:'Cooperativa Test'},numero_disco:'01',placa:'AAA-0001',asientos_vip:[1]}
beforeEach(()=>{vi.clearAllMocks();localStorage.clear();document.documentElement.removeAttribute('data-theme');setActivePinia(createPinia());request.mockResolvedValue([])})
afterEach(()=>{wrappers.splice(0).forEach(w=>w.unmount());document.body.innerHTML=''})

describe('Tema y destinos por provincia',()=>{
 it('aplica, persiste y recupera la preferencia sin depender del servidor',async()=>{
  const meta=document.createElement('meta');meta.name='theme-color';document.head.appendChild(meta)
  const w=montar(ThemePicker);const store=useTemaStore();store.iniciar()
  await w.get('select').setValue('oscuro')
  expect(document.documentElement.dataset.theme).toBe('oscuro');expect(meta.content).toBe('#0d1117');expect(localStorage.getItem('pasajes-tema')).toBe('oscuro')
  await w.get('select').setValue('claro');expect(document.documentElement.dataset.theme).toBe('claro');expect(meta.content).toBe('#f4f5f1')
  store.oscuroSistema=true;await w.get('select').setValue('sistema');expect(document.documentElement.dataset.theme).toBe('oscuro');store.detener();meta.remove()
 })
 it('filtra ciudades por provincia y limpia destinos sin conexión al cambiar origen',async()=>{
  request.mockResolvedValue({ciudades:[{valor:'Quito',ciudad:'Quito',provincia_id:'17',provincia:'Pichincha'},{valor:'Cuenca',ciudad:'Cuenca',provincia_id:'01',provincia:'Azuay'},{valor:'Loja',ciudad:'Loja',provincia_id:'11',provincia:'Loja'}],conexiones:[{origen:'Quito',destino:'Cuenca'},{origen:'Cuenca',destino:'Loja'}]})
  const w=montar(SelectorDestino,{props:{modelValue:'',etiqueta:'Destino',origen:'Quito'}});await flushPromises()
  const [prov,ciudad]=w.findAll('select');expect(prov.text()).toContain('Azuay');expect(prov.text()).not.toContain('Pichincha')
  await prov.setValue('01');expect(ciudad.text()).toContain('Cuenca');expect(ciudad.text()).not.toContain('Loja')
  await ciudad.setValue('Cuenca');expect(w.emitted('update:modelValue').at(-1)).toEqual(['Cuenca'])
  await w.setProps({modelValue:'Cuenca',origen:'Cuenca'});await nextTick();expect(w.emitted('update:modelValue').at(-1)).toEqual([''])
 })
})

describe('Navegación por rol',()=>{
 for(const [rol,permitido,prohibido] of [['admin','Configuración',null],['cooperativa','Mi flota','Venta presencial'],['oficinista','Nueva venta','Configuración'],['chofer','Control de abordaje','Mi flota'],['ayudante','Control de abordaje','Revisión de pagos']]){
  it(`ofrece los accesos correspondientes a ${rol}`,async()=>{
   const w=montar(AdminSidebar);const auth=useAuthStore();auth.usuario={nombre:'Prueba',correo:'test@example.test',rol};auth.token='token';await nextTick()
   expect(w.text()).toContain(permitido);if(prohibido)expect(w.text()).not.toContain(prohibido)
  })
 }
})

describe('Venta presencial',()=>{
 it('calcula en servidor y reintenta exactamente la misma venta si se pierde la respuesta',async()=>{
  let intentos=0
  request.mockImplementation(async(path,options)=>{
   if(path==='/destinos')return {ciudades:[{valor:'Quito',ciudad:'Quito',provincia_id:'17',provincia:'Pichincha'},{valor:'Cuenca',ciudad:'Cuenca',provincia_id:'01',provincia:'Azuay'}],conexiones:[{origen:'Quito',destino:'Cuenca'}]}
   if(path.startsWith('/viajes?'))return {items:[viaje]}
   if(path.startsWith('/reservas/disponibilidad/'))return {capacidad_total:5,asientos_ocupados:[3]}
   if(path==='/tarifas/calcular')return {total:20,descuento_total:0}
   if(path==='/ventas/presencial'){intentos++;if(intentos===1)throw new TypeError('Conexión interrumpida');return {reserva_id:5,pago_id:2,precio:20,asiento:2,estado:'CONFIRMADA'}}
   return []
  })
  const w=montar(Venta);await flushPromises()
  // Los selectores se cubren en su prueba; se emiten ciudades válidas al buscador.
  const selects=w.findAllComponents(SelectorDestino)
  selects[0].vm.$emit('update:modelValue','Quito');selects[1].vm.$emit('update:modelValue','Cuenca');await nextTick()
  await w.get('form').trigger('submit');await flushPromises();await boton(w,'Elegir viaje').trigger('click');await flushPromises()
  expect(w.find('button[aria-label="Asiento 3, normal, ocupado"]').attributes('disabled')).toBeDefined()
  await w.get('button[aria-label="Asiento 2, normal, libre"]').trigger('click');await boton(w,'Continuar con el pasajero').trigger('click')
  const inputs=w.findAll('input');await inputs[0].setValue('Pasajero Prueba');await inputs[1].setValue('1710034065')
  await w.get('form').trigger('submit');await flushPromises();expect(w.text()).toContain('Conexión interrumpida');expect(w.text()).toContain('Reintentar la misma venta')
  await w.get('form').trigger('submit');await flushPromises();expect(w.text()).toContain('Venta completada')
  const llamadas=request.mock.calls.filter(([path])=>path==='/ventas/presencial');expect(llamadas).toHaveLength(2);expect(llamadas[0][1].body).toBe(llamadas[1][1].body)
  expect(request.mock.calls.some(([path])=>path==='/pagos'||path==='/reservas')).toBe(false)
 })
})

describe('Revisión de pagos y acceso',()=>{
 it('reinicia el respaldo de descuento y el motivo entre pagos distintos',async()=>{
  const reservas=[1,2].map(id=>({reserva_id:id,pasajero_nombre:`Pasajero ${id}`,precio:10,tipo_pasajero:'ADULTO_MAYOR',estado:'PAGO_EN_REVISION',origen:'Quito',destino:'Cuenca',fecha_viaje:'2030-01-01',hora_salida:'08:00',asiento:id}))
  request.mockImplementation(async path=>path==='/reservas/historial'?reservas:path==='/pagos'?[1,2].map(id=>({id,reserva_id:id,monto:10,estado:'PENDIENTE',metodo_pago:'TRANSFERENCIA'})):[])
  const w=montar(Compras,{props:{oficina:true,vistaInicial:'pagos'}});await flushPromises();await w.findAll('button').filter(b=>b.text()==='Revisar pago')[0].trigger('click');await nextTick()
  const dialog=w.findAll('dialog').find(d=>d.attributes('open')!==undefined);await dialog.get('input[type=checkbox]').setValue(true);await dialog.get('textarea').setValue('Motivo del primer pago')
  await dialog.get('button[aria-label="Cerrar diálogo"]').trigger('click');await w.findAll('button').filter(b=>b.text()==='Revisar pago')[1].trigger('click');await nextTick()
  const segundo=w.findAll('dialog').find(d=>d.attributes('open')!==undefined);expect(segundo.get('input[type=checkbox]').element.checked).toBe(false);expect(segundo.get('textarea').element.value).toBe('');expect(boton(segundo,'Aprobar y emitir boleto').attributes('disabled')).toBeDefined()
 })
 it('verifica primero el código y registra el abordaje solo al confirmarlo',async()=>{
  request.mockImplementation(async path=>path==='/panel/opciones'?{frecuencias:[],rutas:[],buses:[]}:path.startsWith('/panel/manifiesto')?[]:path==='/boletos/validar'?{reserva_id:8,pasajero:'Pasajero Prueba',asiento:4,tipo_pasajero:'GENERAL',origen:'Quito',destino:'Cuenca',bus:'01'}:path==='/boletos/abordar'?{reserva_id:8,pasajero:'Pasajero Prueba',asiento:4}:[])
  const w=montar(Abordaje);await flushPromises();await w.get('input[autocomplete=off]').setValue(JSON.stringify({tipo:'boleto-interprovincial',codigo:'codigo-valido-123456789012345'}));await w.get('form').trigger('submit');await flushPromises()
  expect(w.text()).toContain('Boleto válido para hoy');expect(request.mock.calls.some(([p])=>p==='/boletos/abordar')).toBe(false)
  await boton(w,'Confirmar abordaje').trigger('click');await flushPromises();expect(w.text()).toContain('Acceso registrado');expect(request.mock.calls.filter(([p])=>p==='/boletos/abordar')).toHaveLength(1)
 })
})

describe('Gestión de catálogos',()=>{
 it('permite elegir cooperativa y ruta por nombre sin introducir IDs',async()=>{
  const {createRouter,createMemoryHistory}=await import('vue-router')
  const {default:Operacion}=await import('../src/views/admin/OperacionView.vue')
  const pinia=createPinia(),auth=useAuthStore(pinia)
  auth.usuario={nombre:'Admin',correo:'admin@example.test',rol:'admin'};auth.token='token'
  const router=createRouter({history:createMemoryHistory(),routes:[{path:'/admin/buses',component:{template:'<div></div>'}},{path:'/operacion',component:{template:'<div></div>'}}]})
  await router.push('/admin/buses');await router.isReady()
  request.mockImplementation(async path=>path==='/panel/opciones'?{cooperativas:[{id:10,nombre:'Cooperativa Test'}],buses:[{id:20,nombre:'01 · AAA-0001',cooperativa_id:10}],rutas:[{id:30,nombre:'Quito → Cuenca'}],frecuencias:[]}:path==='/ubicaciones'?{provincias:[]}:[])
  const w=montar(Operacion,{props:{catalogo:'buses'},global:{plugins:[pinia,router],stubs:{RouterLink:stubLink}}});await flushPromises()
  await boton(w,'Nuevo registro').trigger('click');await nextTick()
  const dialog=w.findAll('dialog').find(d=>d.attributes('open')!==undefined)
  expect(dialog.get('select').text()).toContain('Cooperativa Test')
  expect(dialog.text()).not.toContain('ID de cooperativa')
  await dialog.get('button[aria-label="Cerrar diálogo"]').trigger('click')
  await w.findAll('button.tab').find(b=>b.text()==='Frecuencias').trigger('click');await flushPromises()
  expect(router.currentRoute.value.fullPath).toBe('/operacion?seccion=frecuencias')
  await boton(w,'Nuevo registro').trigger('click');await nextTick()
  const frecuencia=w.findAll('dialog').find(d=>d.attributes('open')!==undefined)
  expect(frecuencia.findAll('select')[0].text()).toContain('Quito → Cuenca')
  expect(frecuencia.findAll('select')[1].text()).toContain('AAA-0001')
 })
})


it('mantiene contraste de texto AA en los colores base de ambos temas',()=>{
 function luminancia(hex){if(hex.length===4)hex='#'+hex.slice(1).split('').map(c=>c+c).join('');const valores=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16)/255).map(c=>c<=.04045?c/12.92:((c+.055)/1.055)**2.4);return valores.reduce((v,c,i)=>v+c*[.2126,.7152,.0722][i],0)}
 const temas=[css.slice(0,css.indexOf(':root[data-theme')),css.slice(css.indexOf(':root[data-theme'),css.indexOf('body{'))]
 for(const tema of temas){const valores=Object.fromEntries([...tema.matchAll(/--([\w-]+):(#[0-9a-f]{3,6})/g)].map(m=>[m[1],m[2]]));for(const [texto,fondo] of [['text','surface'],['muted','surface'],['muted','canvas'],['brand','surface'],['success','success-bg'],['warning','warning-bg'],['danger','danger-bg']]){const [oscuro,claro]=[luminancia(valores[texto]),luminancia(valores[fondo])].sort((a,b)=>a-b);expect((claro+.05)/(oscuro+.05)).toBeGreaterThanOrEqual(4.5)}}
})
