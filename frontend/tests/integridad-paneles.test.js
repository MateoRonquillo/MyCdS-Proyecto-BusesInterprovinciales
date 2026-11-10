import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { createMemoryHistory, createRouter } from 'vue-router'
import { readFileSync } from 'node:fs'
import { useAuthStore } from '../src/stores/auth'
import { crearRouter } from '../src/router'
import { request } from '../src/services/http'
import { SESION_EXPIRADA } from '../src/services/sesion'
import Resumen from '../src/views/panel/ResumenView.vue'
import Operacion from '../src/views/admin/OperacionView.vue'
import App from '../src/App.vue'
vi.mock('../src/services/http', () => ({ request: vi.fn(), descargar: vi.fn(), leerImagen: vi.fn() }))
const wrappers=[]
const Link={props:['to'],template:'<a><slot/></a>'}
const vacio={template:'<div>Panel</div>'}
function usuario(rol='admin') {
  const pinia=createPinia();setActivePinia(pinia)
  const auth=useAuthStore(pinia)
  auth.usuario={nombre:'Operador',correo:'operador@example.test',rol};auth.token='token-vigente'
  localStorage.setItem('token',auth.token);localStorage.setItem('usuario',JSON.stringify(auth.usuario))
  return {pinia,auth}
}
function montar(component,pinia,router){
  const w=mount(component,{attachTo:document.body,global:{plugins:router?[pinia,router]:[pinia],mocks:router?{}:{$route:{fullPath:'/admin'}},stubs:{RouterLink:Link}}})
  wrappers.push(w);return w
}
beforeEach(()=>{vi.clearAllMocks();localStorage.clear();request.mockResolvedValue([])})
afterEach(()=>{wrappers.splice(0).forEach(w=>w.unmount());document.body.innerHTML='';vi.unstubAllGlobals()})

it('usa superficies oscuras grafito y acentos azules, con estados semánticos separados',()=>{
  const css=readFileSync('src/design-system.css','utf8')
  const oscuro=css.slice(css.indexOf(':root[data-theme=oscuro]'),css.indexOf('body{'))
  const colores=Object.fromEntries([...oscuro.matchAll(/--([\w-]+):(#[0-9a-f]{6})/g)].map(m=>[m[1],m[2]]))
  for(const nombre of ['canvas','surface','surface-soft','surface-hover','sidebar','brand','brand-soft']){
    const hex=colores[nombre]
    const [r,g,b]=[1,3,5].map(i=>parseInt(hex.slice(i,i+2),16))
    expect(b).toBeGreaterThan(g);expect(g).toBeGreaterThanOrEqual(r)
  }
  expect(colores['success-bg']).not.toBe(colores['surface'])
})

describe('Integridad de rutas por rol',()=>{
 const casos=[
  ['admin',['/admin','/admin/cooperativas','/admin/buses','/admin/rutas','/operacion?seccion=frecuencias','/operacion?seccion=jornadas','/operacion?seccion=configuracion','/oficinista/ventas','/oficinista/pagos','/abordaje'],null],
  ['cooperativa',['/cooperativa','/operacion?seccion=buses','/operacion?seccion=frecuencias','/operacion?seccion=jornadas'],'/oficinista/ventas'],
  ['oficinista',['/oficinista','/oficinista/ventas','/oficinista/reservas','/oficinista/pagos'],'/admin'],
  ['chofer',['/abordaje'],'/oficinista/ventas'],['ayudante',['/abordaje'],'/admin'],
  ['cliente',['/compras','/reservar'],'/admin'],
 ]
 for(const [rol,permitidas,prohibida] of casos){
  it(`resuelve todos los paneles y rechaza accesos ajenos para ${rol}`,async()=>{
   const {auth}=usuario(rol),router=crearRouter(createMemoryHistory())
   for(const path of permitidas){await router.push(path);expect(router.currentRoute.value.fullPath).toBe(path)}
   if(prohibida){await router.push(prohibida);expect(router.currentRoute.value.fullPath).toBe(auth.rutaInicio)}
  })
 }
 it('normaliza catálogos para mantener URL y menú alineados',async()=>{
  const {auth}=usuario(),router=crearRouter(createMemoryHistory())
  await router.push('/operacion?seccion=rutas');expect(router.currentRoute.value.path).toBe('/admin/rutas')
  await router.push('/operacion?seccion=inexistente');expect(router.currentRoute.value.path).toBe('/admin/buses')
  auth.usuario.rol='cooperativa'
  await router.push('/operacion?seccion=configuracion');expect(router.currentRoute.value.fullPath).toBe('/operacion?seccion=buses')
 })
 it('envía al login sin sesión y conserva el destino solicitado',async()=>{
  setActivePinia(createPinia());const router=crearRouter(createMemoryHistory())
  await router.push('/oficinista/pagos')
  expect(router.currentRoute.value.name).toBe('login');expect(router.currentRoute.value.query.redirect).toBe('/oficinista/pagos')
 })
})

it('no oculta fallos de opciones del catálogo al terminar de cargar la tabla',async()=>{
 const {pinia}=usuario()
 const router=createRouter({history:createMemoryHistory(),routes:[{path:'/admin/buses',component:vacio}]})
 await router.push('/admin/buses')
 let fallar=true
 request.mockImplementation(async path=>{
  if(path==='/panel/opciones'){if(fallar)throw new Error('Servicio de opciones no disponible');return {cooperativas:[],buses:[],rutas:[],frecuencias:[]}}
  if(path==='/ubicaciones')return {provincias:[]}
  return []
 })
 const w=montar(Operacion,pinia,router);await flushPromises()
 expect(w.get('[role=alert]').text()).toContain('Servicio de opciones no disponible')
 const nuevo=()=>w.findAll('button').find(b=>b.text().includes('Nuevo registro'))
 expect(nuevo().attributes('disabled')).toBeDefined()
 fallar=false;await w.findAll('button').find(b=>b.text()==='Reintentar opciones').trigger('click');await flushPromises()
 expect(w.find('[role=alert]').exists()).toBe(false);expect(nuevo().attributes('disabled')).toBeUndefined()
})

it('mantiene el resumen de la última fecha aunque una consulta anterior termine después',async()=>{
 const {pinia}=usuario();let primera
 const datos=n=>({buses_activos:n,frecuencias_activas:0,reservas:0,pagos_por_revisar:0,salidas:[]})
 request.mockImplementationOnce(()=>new Promise(resolve=>{primera=resolve})).mockResolvedValue(datos(9))
 const w=montar(Resumen,pinia);await w.get('input[type=date]').setValue('2030-01-02');await w.get('input[type=date]').trigger('change');await flushPromises()
 expect(w.findAll('.metric-value')[0].text()).toBe('9')
 primera(datos(2));await flushPromises();expect(w.findAll('.metric-value')[0].text()).toBe('9')
})

it('recupera una sesión vencida y no invalida una sesión nueva por una respuesta antigua',async()=>{
 const {pinia,auth}=usuario()
 const router=createRouter({history:createMemoryHistory(),routes:[{path:'/panel',component:vacio},{path:'/login',name:'login',component:vacio}]})
 await router.push('/panel');montar(App,pinia,router);await flushPromises()
 const http=await vi.importActual('../src/services/http')
 let responder
 vi.stubGlobal('fetch',vi.fn(()=>new Promise(resolve=>{responder=resolve})))
 const antigua=http.request('/protegido').catch(e=>e)
 localStorage.setItem('token','token-nuevo');auth.token='token-nuevo'
 responder({ok:false,status:401,json:async()=>({})});await antigua;await flushPromises()
 expect(auth.token).toBe('token-nuevo');expect(router.currentRoute.value.path).toBe('/panel')
 vi.stubGlobal('fetch',vi.fn(async()=>({ok:false,status:401,json:async()=>({})})))
 await expect(http.request('/protegido')).rejects.toMatchObject({status:401});await flushPromises()
 expect(auth.estaAutenticado).toBe(false);expect(localStorage.getItem('token')).toBeNull()
 expect(router.currentRoute.value.name).toBe('login');expect(router.currentRoute.value.query.redirect).toBe('/panel')
 expect(router.currentRoute.value.query.sesion).toBe('expirada')
})
