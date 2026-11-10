<script setup>
import { computed } from 'vue'

const props = defineProps({
  capacidad: { type: Number, required: true },
  ocupados: { type: Array, default: () => [] },
  seleccionados: { type: Array, default: () => [] },
  vip: { type: Array, default: () => [] },
  tipo: { type: String, default: '' },
})
const emit = defineEmits(['alternar'])

const filas = computed(() =>
  Array.from({ length: Math.ceil(props.capacidad / 4) }, (_, f) =>
    [1, 2, null, 3, 4].map((c) => (c === null ? null : f * 4 + c)).map((n) => (n && n <= props.capacidad ? n : null)),
  ),
)
const estado = (n) => (props.ocupados.includes(n) ? 'ocupado' : props.seleccionados.includes(n) ? 'elegido' : 'libre')
</script>

<template>
  <div class="bus" role="group" aria-label="Mapa de asientos">
    <div class="frente"><span>Conductor</span></div>
    <div v-for="(fila, i) in filas" :key="i" class="fila">
      <template v-for="(n, j) in fila" :key="j">
        <span v-if="j === 2" class="pasillo" aria-hidden="true"></span>
        <button v-else-if="n" type="button" class="asiento" :class="[estado(n), { vip: vip.includes(n) }]" :disabled="estado(n) === 'ocupado' || (tipo === 'VIP' && !vip.includes(n)) || (tipo === 'NORMAL' && vip.includes(n))"
          :aria-label="`Asiento ${n}, ${vip.includes(n) ? 'VIP' : 'normal'}, ${estado(n)}`" :aria-pressed="estado(n) === 'elegido'" @click="emit('alternar', n)">{{ n }}{{ vip.includes(n) ? '★' : '' }}</button>
        <span v-else class="vacio"></span>
      </template>
    </div>
    <div class="leyenda">
      <span>★ VIP</span><span><i class="libre"></i>Libre</span><span><i class="elegido"></i>Tu selección</span><span><i class="ocupado"></i>Ocupado</span>
    </div>
  </div>
</template>

<style scoped>
.bus { width: fit-content; max-width: 100%; margin: 0 auto; padding: 14px 12px 18px; background: var(--surface-soft); border: 1px solid var(--border); border-radius: 28px 28px 14px 14px; }
.frente { text-align: right; margin-bottom: 10px; font-size: 11px; color: var(--muted); }
.fila { display: grid; grid-template-columns: repeat(2, minmax(30px, 40px)) 18px repeat(2, minmax(30px, 40px)); gap: 6px; margin-bottom: 8px; }
.asiento { height: 42px; border-radius: 8px 8px 4px 4px; border: 1.5px solid var(--brand); background: var(--surface); color: var(--brand); font-size: 12px; font-weight: 700; cursor: pointer; }
.asiento:hover:not(:disabled) { background: var(--brand-soft); }
.asiento.vip { border-color: var(--warning); }
.asiento:disabled:not(.ocupado) { opacity: .3; cursor: not-allowed; }
.asiento.elegido { background: var(--brand); color: var(--surface); }
.asiento.ocupado { background: var(--border); border-color: var(--border); color: var(--muted); cursor: not-allowed; }
.leyenda { display: flex; flex-wrap: wrap; justify-content: center; gap: 10px; margin-top: 12px; font-size: 11px; color: var(--muted); }
.leyenda i { display: inline-block; width: 12px; height: 12px; margin-right: 5px; border-radius: 3px; border: 1.5px solid var(--brand); vertical-align: -2px; }
.leyenda i.elegido { background: var(--brand); }
.leyenda i.ocupado { background: var(--border); border-color: var(--border); }
</style>