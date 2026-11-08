<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import GrupoViaje from '../../components/cliente/GrupoViaje.vue'
import { useAuthStore } from '../../stores/auth'
import { obtenerHistorial, obtenerPagos } from '../../services/compras'
import { USAR_MOCKS } from '../../services/viajes'

const auth = useAuthStore()
const router = useRouter()

const reservas = ref([])
const pagos = ref([])
const estado = ref('cargando') // cargando | listo | error
const error = ref('')
const filtro = ref('todas')

const FILTROS = [
  { valor: 'todas', etiqueta: 'Todas', estados: null },
  { valor: 'pagar', etiqueta: 'Por pagar', estados: ['PENDIENTE'] },
  { valor: 'revision', etiqueta: 'En revisión', estados: ['PAGO_EN_REVISION'] },
  { valor: 'boletos', etiqueta: 'Con boleto', estados: ['CONFIRMADA', 'PAGADA'] },
  { valor: 'cerradas', etiqueta: 'Canceladas', estados: ['CANCELADA', 'EXPIRADA'] },
]

// Pago más reciente de cada reserva (la API los devuelve del más nuevo al más antiguo)
const pagoPorReserva = computed(() => {
  const mapa = new Map()
  pagos.value.forEach((p) => { if (!mapa.has(p.reserva_id)) mapa.set(p.reserva_id, p) })
  return mapa
})

const cuenta = (f) => (f.estados ? reservas.value.filter((r) => f.estados.includes(r.estado)).length : reservas.value.length)

// Un grupo = un viaje (frecuencia + fecha) con los asientos reservados en él
const grupos = computed(() => {
  const f = FILTROS.find((x) => x.valor === filtro.value)
  const mapa = new Map()
  reservas.value
    .filter((r) => !f.estados || f.estados.includes(r.estado))
    .forEach((r) => {
      const clave = `${r.frecuencia_id}|${r.fecha_viaje}`
      if (!mapa.has(clave)) mapa.set(clave, { clave, ...r, items: [] })
      mapa.get(clave).items.push(r)
    })
  mapa.forEach((g) => g.items.sort((a, b) => a.asiento - b.asiento))
  return [...mapa.values()]
})

function sesionExpirada() {
  auth.logout({ expirada: true })
  router.push({ name: 'login', query: { redirect: '/mis-reservas' } })
}

async function cargar() {
  if (USAR_MOCKS) return (estado.value = 'listo')
  estado.value = 'cargando'
  error.value = ''
  try {
    ;[reservas.value, pagos.value] = await Promise.all([obtenerHistorial(), obtenerPagos()])
    estado.value = 'listo'
  } catch (e) {
    if (e.status === 401) return sesionExpirada()
    error.value = e.message
    estado.value = 'error'
  }
}

onMounted(cargar)
</script>

<template>
  <div class="mis page-container">
    <div class="page-heading">
      <RouterLink class="breadcrumb" to="/viajes">← Buscar más viajes</RouterLink>
      <span class="section-kicker">TU HISTORIAL</span>
      <h1>Mis reservas</h1>
      <p>Revisa el estado de tus pagos y descarga tus boletos.</p>
    </div>

    <p v-if="USAR_MOCKS" class="aviso">
      Estás en modo simulado. Para ver tus reservas reales, usa <code>VITE_USE_MOCKS_CLIENTE=false</code> en <code>frontend/.env</code>.
    </p>

    <template v-else>
      <div v-if="estado === 'listo' && reservas.length" class="filtros" role="group" aria-label="Filtrar reservas">
        <button v-for="f in FILTROS" :key="f.valor" type="button" :class="{ activo: filtro === f.valor }" @click="filtro = f.valor">
          {{ f.etiqueta }} <span>{{ cuenta(f) }}</span>
        </button>
      </div>

      <p v-if="estado === 'cargando'" class="vacio">Cargando tus reservas…</p>

      <div v-else-if="estado === 'error'" class="vacio">
        <p>{{ error }}</p>
        <button class="btn" type="button" @click="cargar">Reintentar</button>
      </div>

      <div v-else-if="!reservas.length" class="vacio">
        <p>Aún no tienes reservas.</p>
        <RouterLink class="btn" to="/viajes">Buscar viajes</RouterLink>
      </div>

      <p v-else-if="!grupos.length" class="vacio">No hay reservas en esta categoría.</p>

      <div v-else class="lista">
        <GrupoViaje v-for="g in grupos" :key="g.clave" :grupo="g" :pagos="pagoPorReserva" @cambio="cargar" @sesion-expirada="sesionExpirada" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.mis { max-width: 900px; }
.lista { display: grid; gap: 16px; }
.filtros { display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px; }
.filtros button { border: 1px solid #cfdadd; background: #fff; color: #1d3547; border-radius: 999px; padding: 7px 14px; font-size: 13px; font-weight: 700; }
.filtros button span { margin-left: 4px; color: #788994; }
.filtros button.activo { background: #146d83; border-color: #146d83; color: #fff; }
.filtros button.activo span { color: #d6ebe8; }
.vacio { text-align: center; padding: 48px 16px; color: #697985; background: #fff; border: 1px solid var(--color-borde); border-radius: 14px; display: grid; gap: 14px; justify-items: center; }
.aviso { background: #fff3d6; color: #6b4d00; border: 1px solid #f0d58a; padding: 12px 16px; border-radius: 10px; font-size: 14px; }
.btn { background: #146d83; color: #fff; border: 0; border-radius: 9px; padding: 10px 20px; font-weight: 800; text-decoration: none; display: inline-block; }
</style>