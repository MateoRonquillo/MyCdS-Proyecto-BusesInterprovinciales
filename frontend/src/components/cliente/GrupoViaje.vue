<script setup>
import { computed, onBeforeUnmount, ref } from 'vue'
import BoletoDigital from './BoletoDigital.vue'
import { ESTADOS, METODOS, cancelarReserva, obtenerQr, registrarPago } from '../../services/compras'
import { etiquetaTipo } from '../../services/reservas'

const props = defineProps({
  grupo: { type: Object, required: true },
  pagos: { type: Object, required: true },
})
const emit = defineEmits(['cambio', 'sesion-expirada'])

const mostrarPago = ref(false)
const metodo = ref('DEPOSITO')
const referencia = ref('')
const enviando = ref(false)
const error = ref('')
const qr = ref({ reservaId: null, url: '', cargando: false, error: '' })

const pendientes = computed(() => props.grupo.items.filter((i) => i.estado === 'PENDIENTE'))
const activos = computed(() => props.grupo.items.filter((i) => !['CANCELADA', 'EXPIRADA'].includes(i.estado)))
const confirmados = computed(() => activos.value.filter((i) => ['CONFIRMADA', 'PAGADA'].includes(i.estado)))
const enRevision = computed(() => activos.value.filter((i) => i.estado === 'PAGO_EN_REVISION'))
const totalCompra = computed(() => activos.value.reduce((a, i) => a + i.precio, 0))
const total = computed(() => pendientes.value.reduce((a, i) => a + i.precio, 0))
const dinero = (n) => `$${Number(n).toFixed(2)}`
const fecha = computed(() => {
  const [a, m, d] = props.grupo.fecha_viaje.split('-').map(Number)
  return new Date(a, m - 1, d).toLocaleDateString('es-EC', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
})
const hora = computed(() => props.grupo.hora_salida.slice(0, 5))

const referenciaComun = computed(() => {
  const refs = new Set(enRevision.value.map((i) => props.pagos.get(i.reserva_id)?.referencia).filter(Boolean))
  return enRevision.value.length > 1 && refs.size === 1 ? [...refs][0] : ''
})

const resumen = computed(() => {
  const n = activos.value.length
  if (!n) return null
  const conf = confirmados.value.length
  const rev = enRevision.value.length
  const pen = pendientes.value.length
  const plural = n === 1 ? '' : 's'
  const importe = dinero(totalCompra.value)
  const ref = referenciaComun.value ? ` · comprobante ${referenciaComun.value}` : ''
  if (conf === n) return { tono: 'ok', texto: `Compra completa: ${n} boleto${plural} confirmado${plural} · ${importe}` }
  if (conf > 0) return { tono: 'info', texto: `${conf} de ${n} boletos confirmados · ${importe}. Los demás siguen en revisión o por pagar.` }
  if (rev === n) return { tono: 'info', texto: `Tu pago de ${importe} está en revisión (${n} asiento${plural}${ref}). Recibirás los boletos cuando se apruebe.` }
  if (pen === n) return { tono: 'aviso', texto: `Compra de ${importe} pendiente de pago (${n} asiento${plural}).` }
  return { tono: 'info', texto: `Compra de ${importe}: ${rev} en revisión y ${pen} por pagar.` }
})

function falla(e) {
  if (e.status === 401) return emit('sesion-expirada')
  error.value = e.message
}

async function pagar() {
  error.value = ''
  if (metodo.value !== 'EFECTIVO' && !referencia.value.trim()) {
    error.value = 'Ingresa el número de comprobante del depósito o la transferencia.'
    return
  }
  enviando.value = true
  try {
    for (const item of pendientes.value) {
      await registrarPago(item.reserva_id, metodo.value, item.precio, referencia.value.trim())
    }
    mostrarPago.value = false
    referencia.value = ''
  } catch (e) {
    falla(e)
  } finally {
    enviando.value = false
    emit('cambio')
  }
}

async function cancelar(item) {
  if (!window.confirm(`¿Cancelar el asiento ${item.asiento}? Quedará libre para otros pasajeros.`)) return
  error.value = ''
  try {
    await cancelarReserva(item.reserva_id)
    emit('cambio')
  } catch (e) {
    falla(e)
  }
}

function soltarQr() {
  if (qr.value.url) URL.revokeObjectURL(qr.value.url)
  qr.value = { reservaId: null, url: '', cargando: false, error: '' }
}

async function verBoleto(item) {
  if (qr.value.reservaId === item.reserva_id) return soltarQr()
  soltarQr()
  qr.value = { reservaId: item.reserva_id, url: '', cargando: true, error: '' }
  try {
    qr.value.url = await obtenerQr(item.reserva_id)
  } catch (e) {
    if (e.status === 401) return emit('sesion-expirada')
    qr.value.error = e.message
  } finally {
    qr.value.cargando = false
  }
}

onBeforeUnmount(soltarQr)
</script>

<template>
  <article class="grupo">
    <header>
      <div>
        <span class="ruta">{{ grupo.origen }} → {{ grupo.destino }}</span>
        <small>{{ grupo.cooperativa }} · Bus {{ grupo.numero_disco }}</small>
      </div>
      <div class="cuando"><b>{{ hora }}</b><small>{{ fecha }}</small></div>
    </header>

    <p v-if="resumen" class="resumen" :class="resumen.tono">{{ resumen.texto }}</p>

    <ul class="filas">
      <li v-for="item in grupo.items" :key="item.reserva_id">
        <div class="fila">
          <span class="asiento">Asiento {{ item.asiento }}</span>
          <span class="tipo">{{ etiquetaTipo(item.tipo_pasajero) }}</span>
          <span class="precio">{{ dinero(item.precio) }}</span>
          <span class="estado" :class="ESTADOS[item.estado]?.tono">{{ ESTADOS[item.estado]?.etiqueta || item.estado }}</span>
          <span class="acciones-fila">
            <button v-if="item.estado === 'CONFIRMADA'" type="button" class="link" @click="verBoleto(item)">
              {{ qr.reservaId === item.reserva_id ? 'Ocultar boleto' : 'Ver boleto' }}
            </button>
            <button v-if="item.estado === 'PENDIENTE'" type="button" class="link peligro" @click="cancelar(item)">Cancelar</button>
          </span>
        </div>
        <p v-if="item.estado === 'PENDIENTE' && pagos.get(item.reserva_id)?.estado === 'RECHAZADO'" class="rechazo">
          Tu pago fue rechazado: {{ pagos.get(item.reserva_id).motivo_rechazo }}. Puedes volver a intentarlo.
        </p>
        <p v-else-if="item.estado === 'PAGO_EN_REVISION' && !referenciaComun" class="nota">
          Pago enviado
          <template v-if="pagos.get(item.reserva_id)?.referencia">(comprobante {{ pagos.get(item.reserva_id).referencia }})</template>.
          El oficinista lo está revisando.
        </p>

        <template v-if="qr.reservaId === item.reserva_id">
          <p v-if="qr.cargando" class="nota">Cargando boleto…</p>
          <p v-else-if="qr.error" class="rechazo">{{ qr.error }}</p>
          <BoletoDigital v-else :item="item" :grupo="grupo" :qr-url="qr.url" :pago="pagos.get(item.reserva_id)" />
        </template>
      </li>
    </ul>

    <footer v-if="pendientes.length">
      <template v-if="!mostrarPago">
        <span>Por pagar: <b>{{ dinero(total) }}</b> ({{ pendientes.length }} asiento{{ pendientes.length === 1 ? '' : 's' }})</span>
        <button type="button" class="btn" @click="mostrarPago = true">Registrar pago</button>
      </template>
      <form v-else class="pago" @submit.prevent="pagar">
        <label>Método de pago
          <select v-model="metodo"><option v-for="m in METODOS" :key="m.valor" :value="m.valor">{{ m.etiqueta }}</option></select>
        </label>
        <label v-if="metodo !== 'EFECTIVO'">Número de comprobante
          <input v-model.trim="referencia" maxlength="100" autocomplete="off" placeholder="Ej. 123456789" />
        </label>
        <p class="nota">Total a pagar: <b>{{ dinero(total) }}</b>. Un oficinista revisará tu pago para confirmar los boletos.</p>
        <div class="botones">
          <button type="button" class="btn sec" :disabled="enviando" @click="mostrarPago = false">Cancelar</button>
          <button type="submit" class="btn" :disabled="enviando">{{ enviando ? 'Enviando…' : 'Enviar pago' }}</button>
        </div>
      </form>
    </footer>
    <p v-if="error" class="rechazo" role="alert">{{ error }}</p>
  </article>
</template>

<style scoped>
.grupo > *, .filas > li { min-width: 0; }
.grupo { background: #fff; border: 1px solid var(--color-borde); border-radius: 14px; padding: 18px 22px; display: grid; gap: 12px; }
header { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
header small, .cuando small { display: block; color: #788994; font-size: 12px; }
.ruta { font-size: 17px; font-weight: 800; color: #1d3547; }
.cuando { text-align: right; }
.cuando b { font-size: 18px; color: #146d83; }
.filas { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; }
.filas > li { background: #f4f8f9; border-radius: 10px; padding: 10px 14px; }
.fila { display: grid; grid-template-columns: 110px 1fr 70px 150px auto; gap: 10px; align-items: center; font-size: 14px; }
.asiento { font-weight: 700; }
.precio { font-weight: 700; }
.estado { justify-self: start; padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 700; }
.estado.aviso { background: #fff3d6; color: #8a6100; }
.estado.info { background: #e1eefb; color: #1b5a99; }
.estado.ok { background: #d9f1e3; color: #23653f; }
.estado.malo { background: #fdecec; color: #a12626; }
.acciones-fila { display: flex; gap: 12px; justify-content: flex-end; }
.link { border: 0; background: none; color: #146d83; font-weight: 700; font-size: 13px; padding: 0; }
.link.peligro { color: #a12626; }
.resumen { margin: 0; padding: 10px 14px; border-radius: 10px; font-size: 14px; font-weight: 600; }
.resumen.ok { background: #d9f1e3; color: #23653f; }
.resumen.info { background: #e1eefb; color: #1b5a99; }
.resumen.aviso { background: #fff3d6; color: #8a6100; }
.nota { margin: 8px 0 0; font-size: 13px; color: #697985; }
.rechazo { margin: 8px 0 0; font-size: 13px; color: #a12626; }
footer { display: flex; justify-content: space-between; align-items: center; gap: 12px; flex-wrap: wrap; padding-top: 12px; border-top: 1px solid var(--color-borde); }
.pago { width: 100%; display: grid; gap: 12px; }
.pago label { display: grid; gap: 5px; font-size: 13px; font-weight: 600; color: #1d3547; }
.pago input, .pago select { padding: 10px 12px; border: 1px solid #cfdadd; border-radius: 9px; background: #fff; margin: 0; width: 100%; box-sizing: border-box; }
.botones { display: flex; justify-content: flex-end; gap: 10px; }
.btn { background: #146d83; color: #fff; border: 0; border-radius: 9px; padding: 10px 18px; font-weight: 800; text-decoration: none; display: inline-block; }
.btn:disabled { opacity: .6; cursor: progress; }
.btn.sec { background: #fff; color: #146d83; border: 1px solid #146d83; }
@media (max-width: 720px) { .fila { grid-template-columns: 1fr 1fr; } .acciones-fila { justify-content: flex-start; } }
</style>