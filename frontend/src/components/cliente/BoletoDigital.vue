<script setup>
import { computed } from 'vue'
import { useAuthStore } from '../../stores/auth'
import { METODOS, obtenerPasajero } from '../../services/compras'
import { etiquetaTipo } from '../../services/reservas'

const props = defineProps({
  item: { type: Object, required: true },
  grupo: { type: Object, required: true },
  qrUrl: { type: String, required: true },
  pago: { type: Object, default: null },
})

const auth = useAuthStore()

const numero = computed(() => String(props.item.reserva_id).padStart(6, '0'))
const hora = computed(() => props.grupo.hora_salida.slice(0, 5))
const fecha = computed(() => {
  const [a, m, d] = props.grupo.fecha_viaje.split('-').map(Number)
  return new Date(a, m - 1, d).toLocaleDateString('es-EC', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
})
const dinero = (n) => `$${Number(n).toFixed(2)}`
const pasajero = computed(() => obtenerPasajero(props.item.reserva_id))
const comprador = computed(() => auth.usuario)
const metodo = computed(() => METODOS.find((m) => m.valor === props.pago?.metodo_pago)?.etiqueta || '')
const imprimir = () => window.print()
const conDescuento = computed(() => props.item.tipo_pasajero !== 'GENERAL')
</script>

<template>
  <div class="boleto-zona">
    <article class="boleto-imprimible ticket" aria-label="Boleto digital">
      <section class="principal">
        <header class="banda">
          <div>
            <span class="marca">↗ RutasEcuador · BOLETO DIGITAL</span>
            <strong>{{ grupo.cooperativa }}</strong>
          </div>
          <span class="numero">N.º {{ numero }}</span>
        </header>

        <div class="trayecto">
          <div><small>Origen</small><b>{{ grupo.origen }}</b></div>
          <span class="flecha" aria-hidden="true"><i></i>→</span>
          <div class="der"><small>Destino</small><b>{{ grupo.destino }}</b></div>
        </div>

        <dl class="datos">
          <div class="amplio"><dt>Fecha</dt><dd class="cap">{{ fecha }}</dd></div>
          <div><dt>Salida</dt><dd>{{ hora }}</dd></div>
          <div><dt>Asiento</dt><dd class="resalta">{{ item.asiento }}</dd></div>
          <div><dt>Bus (disco)</dt><dd>{{ grupo.numero_disco }}</dd></div>
          <div><dt>Tipo de pasajero</dt><dd>{{ etiquetaTipo(item.tipo_pasajero) }}</dd></div>
          <div><dt>Valor pagado</dt><dd>{{ dinero(item.precio) }}</dd></div>
        </dl>

        <div class="personas">
          <div v-if="pasajero">
            <dt>Pasajero</dt>
            <dd>{{ pasajero.nombres }} <small>· C.I. {{ pasajero.cedula }}</small></dd>
          </div>
          <div v-if="comprador">
            <dt>Comprador</dt>
            <dd>{{ comprador.nombre }} <small v-if="comprador.cedula">· C.I. {{ comprador.cedula }}</small></dd>
          </div>
        </div>

        <footer class="pie">
          <span class="sello">✔ Pago aprobado<template v-if="metodo"> · {{ metodo }}</template><template v-if="pago?.referencia"> · comprobante {{ pago.referencia }}</template></span>
          <small v-if="conDescuento">Presenta el documento que respalda tu descuento al abordar.</small>
          <small v-else>Presenta este boleto y tu cédula al abordar.</small>
        </footer>
      </section>

      <aside class="talon">
        <img :src="qrUrl" :alt="`Código QR del asiento ${item.asiento}`" width="170" height="170" />
        <b>Escanea al abordar</b>
        <small>Asiento {{ item.asiento }} · N.º {{ numero }}</small>
        <span class="valido">VÁLIDO</span>
      </aside>
    </article>

    <div class="boleto-acciones">
      <a class="accion" :href="qrUrl" :download="`boleto-${item.reserva_id}.png`">Descargar QR</a>
      <button type="button" class="accion" @click="imprimir">Imprimir boleto</button>
    </div>
  </div>
</template>

<style scoped>
.boleto-zona { margin-top: 12px; display: grid; gap: 10px; }
.ticket { max-width: 100%; display: flex; background: #fff; border-radius: 16px; overflow: hidden; box-shadow: 0 6px 24px #0e37402a; border: 1px solid #cfe0e4; }
.principal { flex: 1; min-width: 0; display: grid; align-content: start; }
.banda { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; padding: 14px 22px; color: #fff; background: linear-gradient(120deg, #0e4f60, #146d83 60%, #2a9aa5); }
.banda strong { display: block; margin-top: 2px; font-size: 20px; }
.marca { font-size: 11px; letter-spacing: .12em; opacity: .85; font-weight: 700; }
.numero { font-weight: 800; background: #ffffff26; padding: 4px 12px; border-radius: 999px; font-size: 13px; white-space: nowrap; }
.trayecto { display: grid; grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr); align-items: center; gap: 14px; padding: 18px 22px 8px; }
.trayecto small, .datos dt, .personas dt { display: block; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: #788994; font-weight: 700; }
.trayecto b { font-size: 26px; color: #1d3547; line-height: 1.1; overflow-wrap: anywhere; }
.der { text-align: right; }
.flecha { display: flex; align-items: center; gap: 6px; color: #146d83; font-size: 22px; font-weight: 800; }
.flecha i { display: block; width: 56px; height: 2px; background: repeating-linear-gradient(90deg, #146d83 0 6px, transparent 6px 10px); }
.datos { margin: 0; padding: 10px 22px 6px; display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px 18px; }
.datos .amplio { grid-column: span 3; }
.datos dd, .personas dd { overflow-wrap: anywhere; margin: 2px 0 0; font-size: 16px; font-weight: 700; color: #1d3547; }
.cap::first-letter { text-transform: uppercase; }
.resalta { font-size: 26px !important; color: #146d83 !important; line-height: 1; }
.personas { display: grid; gap: 8px; margin: 6px 22px 0; padding: 12px 14px; background: #f4f8f9; border-radius: 10px; }
.personas dd small { font-weight: 500; color: #697985; font-size: 13px; }
.pie { display: grid; gap: 4px; padding: 12px 22px 16px; }
.sello { color: #23653f; font-weight: 800; font-size: 13px; }
.pie small { color: #788994; font-size: 12px; }
.talon { position: relative; width: 230px; flex: none; display: grid; justify-items: center; align-content: center; gap: 6px; padding: 20px 16px; background: #f4f8f9; border-left: 2px dashed #b9cdd2; text-align: center; }
.talon::before, .talon::after { content: ''; position: absolute; left: -11px; width: 20px; height: 20px; border-radius: 50%; background: var(--color-fondo, #f7f9f9); border: 1px solid #cfe0e4; }
.talon::before { top: -11px; } .talon::after { bottom: -11px; }
.talon img { background: #fff; padding: 6px; border-radius: 10px; border: 1px solid #cfe0e4; }
.talon b { color: #1d3547; font-size: 14px; }
.talon small { color: #697985; font-size: 12px; }
.valido { margin-top: 4px; padding: 3px 14px; border-radius: 999px; background: #d9f1e3; color: #23653f; font-size: 12px; font-weight: 800; letter-spacing: .1em; }
.boleto-acciones { display: flex; gap: 10px; flex-wrap: wrap; }
.accion { border: 1px solid #146d83; background: #fff; color: #146d83; border-radius: 9px; padding: 9px 18px; font-weight: 800; font-size: 14px; text-decoration: none; display: inline-block; }
.accion:hover { background: #e8f4f3; }
@media (max-width: 680px) {
  .ticket { flex-direction: column; }
  .talon { width: auto; border-left: 0; border-top: 2px dashed #b9cdd2; }
  .talon::before, .talon::after { display: none; }
  .trayecto { gap: 8px; padding: 16px 16px 6px; }
  .trayecto b { font-size: 19px; }
  .flecha i { width: 22px; }
  .banda, .datos, .pie { padding-left: 16px; padding-right: 16px; }
  .personas { margin-left: 16px; margin-right: 16px; }
  .banda { flex-wrap: wrap; }
  .datos { grid-template-columns: 1fr 1fr; } .datos .amplio { grid-column: span 2; }
}
</style>

<style>
@media print {
  body * { visibility: hidden !important; }
  .boleto-imprimible, .boleto-imprimible * { visibility: visible !important; }
  .boleto-imprimible { position: absolute; left: 0; top: 0; width: 100%; box-shadow: none !important; }
}
</style>