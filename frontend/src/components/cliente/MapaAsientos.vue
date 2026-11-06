<script setup>
import { computed } from 'vue'

const props = defineProps({
  capacidad: { type: Number, required: true },
  ocupados: { type: Array, default: () => [] },
  seleccionados: { type: Array, default: () => [] },
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
        <button v-else-if="n" type="button" class="asiento" :class="estado(n)" :disabled="estado(n) === 'ocupado'"
          :aria-label="`Asiento ${n}, ${estado(n)}`" :aria-pressed="estado(n) === 'elegido'" @click="emit('alternar', n)">{{ n }}</button>
        <span v-else class="vacio"></span>
      </template>
    </div>
    <div class="leyenda">
      <span><i class="libre"></i>Libre</span><span><i class="elegido"></i>Tu selección</span><span><i class="ocupado"></i>Ocupado</span>
    </div>
  </div>
</template>

<style scoped>
.bus { width: fit-content; margin: 0 auto; padding: 14px 20px 18px; background: #f4f8f9; border: 2px solid #cfe0e4; border-radius: 28px 28px 14px 14px; }
.frente { text-align: right; margin-bottom: 10px; font-size: 11px; color: #788994; }
.fila { display: grid; grid-template-columns: repeat(2, 40px) 28px repeat(2, 40px); gap: 8px; margin-bottom: 8px; }
.asiento { height: 38px; border-radius: 8px 8px 4px 4px; border: 1.5px solid #146d83; background: #fff; color: #146d83; font-size: 12px; font-weight: 700; cursor: pointer; }
.asiento:hover:not(:disabled) { background: #e8f4f3; }
.asiento.elegido { background: #146d83; color: #fff; }
.asiento.ocupado { background: #d5dde0; border-color: #d5dde0; color: #8a979d; cursor: not-allowed; }
.leyenda { display: flex; justify-content: center; gap: 16px; margin-top: 12px; font-size: 11px; color: #697985; }
.leyenda i { display: inline-block; width: 12px; height: 12px; margin-right: 5px; border-radius: 3px; border: 1.5px solid #146d83; vertical-align: -2px; }
.leyenda i.elegido { background: #146d83; }
.leyenda i.ocupado { background: #d5dde0; border-color: #d5dde0; }
</style>