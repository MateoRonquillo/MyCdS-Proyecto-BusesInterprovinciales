<script setup>
import { computed } from 'vue'
import { useViajesStore, FRANJAS, ORDENES } from '../../stores/viajes'

const store = useViajesStore()
const habilitado = computed(() => store.estado === 'listo' && store.resultados.length > 0)

const precioActual = computed({
  get: () => store.filtros.precioMax ?? store.precioMaximo,
  set: (valor) => { store.filtros.precioMax = Number(valor) },
})
</script>

<template>
  <section class="filtros-card" aria-labelledby="filtros-titulo">
    <div class="filtros-head">
      <h2 id="filtros-titulo">Filtrar resultados</h2>
      <button v-if="store.filtrosActivos" class="filtros-limpiar" type="button" @click="store.limpiarFiltros()">
        Limpiar ({{ store.filtrosActivos }})
      </button>
    </div>

    <p v-if="!habilitado" class="filtros-ayuda">Realiza una búsqueda para poder filtrar por cooperativa, horario y precio.</p>

    <fieldset class="filtros-grupo" :disabled="!habilitado">
      <label class="filtros-campo">
        Ordenar por
        <select v-model="store.filtros.orden">
          <option v-for="o in ORDENES" :key="o.valor" :value="o.valor">{{ o.etiqueta }}</option>
        </select>
      </label>

      <label class="filtros-campo">
        Cooperativa
        <select v-model="store.filtros.cooperativa">
          <option value="">Todas</option>
          <option v-for="c in store.cooperativas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
        </select>
      </label>

      <div class="filtros-campo" role="group" aria-labelledby="franja-etiqueta">
        <span id="franja-etiqueta">Horario de salida</span>
        <div class="franjas">
          <label v-for="f in FRANJAS" :key="f.valor" class="franja" :class="{ activa: store.filtros.franjas.includes(f.valor) }">
            <input v-model="store.filtros.franjas" type="checkbox" :value="f.valor" />
            <strong>{{ f.etiqueta }}</strong>
            <small>{{ f.rango }}</small>
          </label>
        </div>
      </div>

      <label class="filtros-campo">
        <span class="precio-linea">Precio máximo <output>${{ Number(precioActual).toFixed(2) }}</output></span>
        <input
          v-model="precioActual"
          type="range"
          :min="store.precioMinimo"
          :max="store.precioMaximo"
          step="0.5"
        />
      </label>

      <label class="filtros-check">
        <input v-model="store.filtros.soloDisponibles" type="checkbox" />
        Ocultar viajes sin asientos
      </label>
    </fieldset>
  </section>
</template>

<style scoped>
.filtros-card { background: #fff; border: 1px solid var(--color-borde); border-radius: 12px; padding: 22px 27px 26px; }
.filtros-head { display: flex; justify-content: space-between; align-items: center; gap: 10px; margin-bottom: 14px; }
.filtros-head h2 { font-size: 16px; margin: 0; }
.filtros-limpiar { background: none; border: 0; color: #176d84; font-size: 12px; font-weight: 700; text-decoration: underline; padding: 0; }
.filtros-ayuda { font-size: 11px; color: #788994; background: #f3f7f7; padding: 10px 12px; border-radius: 7px; margin: 0 0 14px; }
.filtros-grupo { border: 0; margin: 0; padding: 0; display: grid; gap: 18px; min-width: 0; }
.filtros-grupo:disabled { opacity: .5; }
.filtros-campo { display: flex; flex-direction: column; gap: 7px; font-size: 12px; font-weight: 800; color: #4a6070; }
.filtros-campo select { height: 42px; border: 1px solid #dce6e9; border-radius: 7px; padding: 0 10px; background: #f9fbfb; color: #273f4d; font-size: 12px; }
.franjas { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.franja { position: relative; display: flex; flex-direction: column; border: 1px solid #dce6e9; border-radius: 8px; padding: 9px 10px; background: #f9fbfb; cursor: pointer; font-weight: 500; }
.franja input { position: absolute; opacity: 0; inset: 0; cursor: pointer; }
.franja strong { font-size: 12px; color: #273f4d; }
.franja small { font-size: 10px; color: #788994; }
.franja.activa { border-color: #146d83; background: #e8f4f3; }
.franja:focus-within { outline: 3px solid #efb65e; outline-offset: 2px; }
.precio-linea { display: flex; justify-content: space-between; }
.precio-linea output { color: #146d83; }
.filtros-campo input[type='range'] { accent-color: #146d83; width: 100%; }
.filtros-check { display: flex; align-items: center; gap: 9px; font-size: 12px; font-weight: 700; color: #4a6070; }
.filtros-check input { width: 16px; height: 16px; accent-color: #146d83; }
</style>