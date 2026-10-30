<script setup>
import { computed } from 'vue'
import TarjetaViaje from './TarjetaViaje.vue'
import { useViajesStore } from '../../stores/viajes'

const store = useViajesStore()
const emit = defineEmits(['reintentar'])

const titulo = computed(() => {
  const n = store.viajesFiltrados.length
  return `${n} viaje${n === 1 ? '' : 's'} disponible${n === 1 ? '' : 's'}`
})
const fechaLarga = computed(() => {
  if (!store.consulta) return ''
  const [a, m, d] = store.consulta.fecha.split('-').map(Number)
  const texto = new Date(a, m - 1, d).toLocaleDateString('es-EC', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  return texto.charAt(0).toUpperCase() + texto.slice(1)
})
const sinCoincidencias = computed(() => store.resultados.length > 0 && store.viajesFiltrados.length === 0)
</script>

<template>
  <section class="lista" aria-live="polite" :aria-busy="store.estado === 'cargando'">
    <!-- Inicial -->
    <div v-if="store.estado === 'inicial'" class="aviso">
      <div class="aviso-icono" aria-hidden="true">↗</div>
      <span class="section-kicker">RESULTADOS</span>
      <h2>Tu próxima aventura comienza aquí</h2>
      <p>Ingresa el origen, el destino y la fecha para ver los horarios, cooperativas y asientos disponibles.</p>
    </div>

    <!-- Cargando -->
    <div v-else-if="store.estado === 'cargando'" class="esqueletos" role="status">
      <span class="sr-only">Buscando viajes…</span>
      <div v-for="n in 3" :key="n" class="esqueleto"></div>
    </div>

    <!-- Error -->
    <div v-else-if="store.estado === 'error'" class="aviso error" role="alert">
      <div class="aviso-icono" aria-hidden="true">!</div>
      <h2>No pudimos cargar los viajes</h2>
      <p>{{ store.error }}</p>
      <button class="accion" type="button" @click="emit('reintentar')">Reintentar</button>
    </div>

    <!-- Sin viajes para la ruta -->
    <div v-else-if="store.resultados.length === 0" class="aviso">
      <div class="aviso-icono" aria-hidden="true">∅</div>
      <h2>No hay viajes para esta ruta</h2>
      <p>No encontramos salidas de {{ store.consulta.origen }} a {{ store.consulta.destino }} el {{ fechaLarga }}. Prueba con otra fecha o revisa los nombres de las ciudades.</p>
    </div>

    <!-- Resultados -->
    <template v-else>
      <header class="lista-cab">
        <div>
          <span class="section-kicker">{{ store.consulta.origen.toUpperCase() }} → {{ store.consulta.destino.toUpperCase() }}</span>
          <h2>{{ titulo }}</h2>
          <p class="fecha">{{ fechaLarga }}</p>
        </div>
        <span v-if="store.datosSimulados" class="demo" title="El backend aún no expone /api/v1/viajes">Datos de demostración</span>
      </header>

      <div v-if="sinCoincidencias" class="aviso">
        <h2>Ningún viaje coincide con los filtros</h2>
        <p>Hay {{ store.resultados.length }} viajes para esta ruta. Ajusta o limpia los filtros para verlos.</p>
        <button class="accion" type="button" @click="store.limpiarFiltros()">Limpiar filtros</button>
      </div>
      <ul v-else class="viajes">
        <li v-for="v in store.viajesFiltrados" :key="v.id"><TarjetaViaje :viaje="v" /></li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.lista { min-width: 0; }
.lista-cab { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.lista-cab h2 { font-size: 24px; letter-spacing: -.04em; margin: 6px 0 2px; }
.fecha { margin: 0; font-size: 13px; color: #697985; }
.demo { font-size: 10px; font-weight: 800; letter-spacing: .08em; text-transform: uppercase; color: #8a5a10; background: #fdf1dc; border: 1px solid #f0d9ab; padding: 5px 10px; border-radius: 30px; white-space: nowrap; }
.viajes { list-style: none; margin: 0; padding: 0; display: grid; gap: 12px; }
.aviso { display: flex; flex-direction: column; align-items: center; text-align: center; justify-content: center; min-height: 340px; padding: 27px; background: radial-gradient(circle at 50% 28%, #eef9f7, #fff 60%); border: 1px solid var(--color-borde); border-radius: 12px; }
.aviso-icono { width: 76px; height: 76px; display: grid; place-items: center; border-radius: 50%; background: #dfefef; color: #197790; font-size: 40px; margin-bottom: 14px; }
.aviso h2 { font-size: 21px; letter-spacing: -.04em; margin: 8px 0 10px; }
.aviso p { color: #728591; font-size: 13px; max-width: 430px; margin: 0 0 14px; }
.aviso.error { background: #fff8f8; border-color: #f0d4d4; }
.aviso.error .aviso-icono { background: #f7dede; color: #a22e32; }
.accion { background: #146d83; color: #fff; border: 0; border-radius: 7px; padding: 10px 22px; font-size: 12px; font-weight: 800; }
.accion:hover { background: #10556d; }
.esqueletos { display: grid; gap: 12px; }
.esqueleto { height: 110px; border-radius: 12px; background: linear-gradient(90deg, #eef3f3 25%, #f8fbfb 50%, #eef3f3 75%); background-size: 200% 100%; animation: brillo 1.2s infinite linear; }
@keyframes brillo { to { background-position: -200% 0; } }
.sr-only { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0 0 0 0); white-space: nowrap; }
@media (prefers-reduced-motion: reduce) { .esqueleto { animation: none; } }
@media (max-width: 620px) { .lista-cab { flex-direction: column; } }
</style>