<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { useReservaStore } from '../../stores/reserva'
import { useViajesStore } from '../../stores/viajes'

const props = defineProps({ viaje: { type: Object, required: true } })
const router = useRouter()
const reserva = useReservaStore()
const viajes = useViajesStore()

function seleccionar() {
  reserva.iniciar({ ...props.viaje, fecha: props.viaje.fecha || viajes.consulta?.fecha })
  router.push({ name: 'reservar' })
}

const duracion = computed(() => {
  const h = Math.floor(props.viaje.duracion_min / 60)
  const m = props.viaje.duracion_min % 60
  return m ? `${h} h ${m} min` : `${h} h`
})
const agotado = computed(() => props.viaje.asientos_disponibles <= 0)
const pocos = computed(() => !agotado.value && props.viaje.asientos_disponibles <= 8)
const precio = computed(() => `$${props.viaje.precio.toFixed(2)}`)
const iniciales = computed(() => props.viaje.cooperativa.nombre.split(' ').map((p) => p[0]).slice(0, 2).join(''))
</script>

<template>
  <article class="viaje" :class="{ agotado }" :style="{ '--coop': viaje.cooperativa.color_principal || '#166b83' }">
    <header class="viaje-coop">
      <span class="coop-logo" aria-hidden="true">{{ iniciales }}</span>
      <div>
        <strong>{{ viaje.cooperativa.nombre }}</strong>
        <small>{{ viaje.tipo_bus || viaje.tipo_viaje }}</small>
        <details><summary>Ver bus</summary><p>Disco {{ viaje.numero_disco }} · {{ viaje.placa }}<br>{{ viaje.chasis }} · {{ viaje.carroceria }}<br>Asientos: {{ viaje.tipos_asiento?.join(', ') }}</p><img v-if="viaje.fotografia_url" :src="viaje.fotografia_url" alt="Fotografía del bus" style="max-width:180px" loading="lazy"></details>
      </div>
    </header>

    <div class="viaje-horario" :aria-label="`Sale a las ${viaje.hora_salida} y llega a las ${viaje.hora_llegada}`">
      <div><b>{{ viaje.hora_salida }}</b><span>{{ viaje.origen }}</span></div>
      <div class="viaje-linea" aria-hidden="true"><i></i><small>{{ duracion }}</small></div>
      <div><b>{{ viaje.hora_llegada }}</b><span>{{ viaje.destino }}</span></div>
    </div>

    <footer class="viaje-pie">
      <div class="viaje-precio"><small>Por pasajero</small><strong>{{ precio }}</strong></div>
      <span class="asientos" :class="{ pocos, agotado }">
        {{ agotado ? 'Sin asientos' : `${viaje.asientos_disponibles} asiento${viaje.asientos_disponibles === 1 ? '' : 's'} disponible${viaje.asientos_disponibles === 1 ? '' : 's'}` }}
      </span>
      <button class="reservar" type="button" :disabled="agotado" :title="agotado ? 'No hay asientos disponibles' : 'Reservar este viaje'" @click="seleccionar">
        {{ agotado ? 'Agotado' : 'Seleccionar' }}
      </button>
    </footer>
  </article>
</template>

<style scoped>
.viaje { display: grid; grid-template-columns: 190px 1fr auto; align-items: center; gap: 22px; background: var(--surface); border: 1px solid var(--color-borde); border-left: 5px solid var(--coop); border-radius: 12px; padding: 18px 22px; }
.viaje.agotado { opacity: .7; }
.viaje-coop { display: flex; align-items: center; gap: 11px; min-width: 0; }
.coop-logo { flex-shrink: 0; width: 40px; height: 40px; border-radius: 10px; background: var(--coop); color: #fff; display: grid; place-items: center; font-size: 13px; font-weight: 800; }
.viaje-coop strong { display: block; font-size: 13px; color: var(--text); line-height: 1.25; }
.viaje-coop small { font-size: 11px; color: var(--muted); }
.viaje-horario { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 14px; }
.viaje-horario b { display: block; font-family: var(--font-ui); font-size: 21px; color: var(--text); letter-spacing: -.03em; }
.viaje-horario span { font-size: 11px; color: var(--muted); }
.viaje-horario > div:last-child { text-align: right; }
.viaje-linea { display: flex; flex-direction: column; align-items: center; gap: 4px; min-width: 70px; }
.viaje-linea i { display: block; width: 100%; height: 2px; background: linear-gradient(90deg, var(--coop), #cfe0e4); border-radius: 2px; }
.viaje-linea small { font-size: 10px; color: var(--muted); white-space: nowrap; }
.viaje-pie { display: grid; justify-items: end; gap: 6px; }
.viaje-precio { text-align: right; line-height: 1.1; }
.viaje-precio small { display: block; font-size: 10px; color: var(--muted); }
.viaje-precio strong { font-family: var(--font-ui); font-size: 22px; color: var(--brand); }
.asientos { font-size: 11px; font-weight: 700; color: var(--success); }
.asientos.pocos { color: var(--warning); }
.asientos.agotado { color: var(--danger); }
.reservar { background: var(--brand); color: var(--surface); border: 0; border-radius: 7px; padding: 9px 20px; font-size: 12px; font-weight: 800; }
.reservar:hover:not(:disabled) { background: var(--brand-hover); }
.reservar:disabled { background: var(--border); cursor: not-allowed; }
@media (max-width: 760px) {
  .viaje { grid-template-columns: 1fr; gap: 14px; }
  .viaje-pie { grid-template-columns: 1fr auto; justify-items: start; align-items: center; }
  .viaje-precio { text-align: left; }
  .asientos { grid-column: 1; grid-row: 2; }
  .reservar { grid-column: 2; grid-row: 1 / span 2; }
}
</style>