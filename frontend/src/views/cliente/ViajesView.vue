<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FiltrosViajes from '../../components/cliente/FiltrosViajes.vue'
import ListaViajes from '../../components/cliente/ListaViajes.vue'
import { useViajesStore } from '../../stores/viajes'
import { CIUDADES } from '../../services/viajesMock'
import { normalizar } from '../../utils/texto'

const route = useRoute()
const router = useRouter()
const store = useViajesStore()

const busqueda = reactive({
  origen: String(route.query.origen || ''),
  destino: String(route.query.destino || ''),
  fecha: String(route.query.fecha || ''),
})
const fechaMin = new Date().toLocaleDateString('en-CA')
const errorForm = ref('')

function validar() {
  if (!busqueda.origen || !busqueda.destino || !busqueda.fecha) return 'Completa el origen, destino y fecha para continuar.'
  if (normalizar(busqueda.origen) === normalizar(busqueda.destino)) return 'El origen y el destino deben ser diferentes.'
  if (busqueda.fecha < fechaMin) return 'La fecha de salida no puede ser anterior a hoy.'
  return ''
}

async function consultar() {
  errorForm.value = validar()
  if (errorForm.value) return
  router.replace({ name: 'viajes', query: { origen: busqueda.origen, destino: busqueda.destino, fecha: busqueda.fecha } })
  await store.buscar({ origen: busqueda.origen, destino: busqueda.destino, fecha: busqueda.fecha })
}

function intercambiar() {
  ;[busqueda.origen, busqueda.destino] = [busqueda.destino, busqueda.origen]
}

onMounted(() => {
  if (busqueda.origen && busqueda.destino && busqueda.fecha) consultar()
})
</script>

<template>
  <div class="trips page-container">
    <div class="page-heading">
      <RouterLink class="breadcrumb" to="/">← Volver al inicio</RouterLink>
      <span class="section-kicker">ENCUENTRA TU PRÓXIMO DESTINO</span>
      <h1>Buscar viajes</h1>
      <p>Elige la ciudad de salida, el destino y la fecha en que deseas viajar.</p>
    </div>

    <div class="trips-layout">
      <aside class="trips-side">
        <section class="trips-form-card">
          <div class="trips-card-head">
            <span class="benefit-icon">⌕</span>
            <div><h2>Personaliza tu búsqueda</h2><p>Completa la información de tu viaje.</p></div>
          </div>
          <form class="trips-form" novalidate @submit.prevent="consultar">
            <label class="field">Ciudad de origen
              <input v-model.trim="busqueda.origen" list="lista-ciudades" autocomplete="off" placeholder="Ej. Ambato" required />
            </label>
            <button class="swap" type="button" aria-label="Intercambiar origen y destino" @click="intercambiar">⇅</button>
            <label class="field">Ciudad de destino
              <input v-model.trim="busqueda.destino" list="lista-ciudades" autocomplete="off" placeholder="Ej. Quito" required />
            </label>
            <label class="field">Fecha de salida
              <input v-model="busqueda.fecha" :min="fechaMin" type="date" required />
            </label>
            <datalist id="lista-ciudades"><option v-for="c in CIUDADES" :key="c" :value="c" /></datalist>
            <button class="search-submit" type="submit" :disabled="store.estado === 'cargando'">
              {{ store.estado === 'cargando' ? 'Buscando…' : 'Consultar viajes →' }}
            </button>
          </form>
          <p v-if="errorForm" class="form-error" role="alert">{{ errorForm }}</p>
        </section>
        <FiltrosViajes />
      </aside>

      <ListaViajes @reintentar="consultar" />
    </div>
  </div>
</template>

<style scoped>
.trips-side { display: grid; gap: 18px; align-content: start; }
.swap { justify-self: end; margin: -12px 0 -12px; width: 34px; height: 34px; border-radius: 50%; border: 1px solid #dce6e9; background: #fff; color: #146d83; font-size: 16px; }
.swap:hover { background: #e8f4f3; }
.search-submit:disabled { opacity: .65; cursor: progress; }
</style>