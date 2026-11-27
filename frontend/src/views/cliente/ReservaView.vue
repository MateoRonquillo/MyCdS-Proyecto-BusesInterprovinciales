<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import MapaAsientos from '../../components/cliente/MapaAsientos.vue'
import { useAuthStore } from '../../stores/auth'
import { useReservaStore } from '../../stores/reserva'
import { guardarPasajeros } from '../../services/compras'
import { MAX_PASAJEROS, TIPOS_PASAJERO, calcularTarifa, crearReservas, obtenerDisponibilidad } from '../../services/reservas'
import { validarCedula, validarCorreo, validarNombres } from '../../utils/validaciones'

const auth = useAuthStore()
const reserva = useReservaStore()
const router = useRouter()

const paso = ref(1)
const errores = ref([])
const aviso = ref('')
const cargando = ref(false)
const disp = ref({ capacidad: 0, ocupados: [] })
const tarifa = ref(null)
const tipoAsiento = ref('')
watch(tipoAsiento, () => { reserva.pasajeros.forEach(p => p.asiento = null) })
const finalizada = ref(false)

const libres = computed(() => (disp.value.capacidad ? disp.value.capacidad - disp.value.ocupados.length : MAX_PASAJEROS))
const maxPasajeros = computed(() => Math.max(1, Math.min(MAX_PASAJEROS, libres.value)))
const seleccionados = computed(() => reserva.pasajeros.map((p) => p.asiento).filter(Boolean))
const etiquetaTipo = (v) => TIPOS_PASAJERO.find((t) => t.valor === v)?.etiqueta || v
// La cédula del comprador viene de su cuenta: se muestra bloqueada y no se revalida
const cedulaCuenta = computed(() => auth.usuario?.cedula || '')
const dinero = (n) => `$${Number(n).toFixed(2)}`

function manejarError(e) {
  if (e.status === 401) {
    auth.logout({ expirada: true })
    router.push({ name: 'login', query: { redirect: '/reservar' } })
    return
  }
  aviso.value = e.message
}

async function cargarDisponibilidad() {
  try {
    disp.value = await obtenerDisponibilidad(reserva.viaje)
    reserva.pasajeros.forEach((p) => { if (disp.value.ocupados.includes(p.asiento)) p.asiento = null })
  } catch (e) {
    manejarError(e)
  }
}

onMounted(async () => {
  if (!reserva.viaje) return router.replace({ name: 'viajes' })
  if (auth.usuario && !auth.usuario.cedula) await auth.refrescarUsuario()
  const comprador = reserva.pasajeros[0]
  if (comprador && auth.usuario) {
    if (!comprador.nombres) comprador.nombres = auth.usuario.nombre
    if (!comprador.correo) comprador.correo = auth.usuario.correo
    // La cédula de la cuenta siempre manda sobre lo que quedó en el borrador
    if (auth.usuario.cedula) comprador.cedula = auth.usuario.cedula
  }
  await cargarDisponibilidad()
})
watch(() => reserva.pasajeros, () => reserva.guardar(), { deep: true })

function cambiarCantidad(delta) {
  const n = Math.min(maxPasajeros.value, Math.max(1, reserva.pasajeros.length + delta))
  reserva.fijarCantidad(n)
}

function validarPasajeros() {
  const vistas = new Set()
  errores.value = reserva.pasajeros.map((p, i) => {
    const e = {}
    if (!validarNombres(p.nombres)) e.nombres = 'Ingresa nombres y apellidos válidos.'
    if (!validarCedula(p.cedula)) e.cedula = 'Cédula ecuatoriana inválida (10 dígitos).'
    else if (vistas.has(p.cedula)) e.cedula = 'Esta cédula ya está en otro pasajero.'
    if (!validarCorreo(p.correo)) e.correo = 'Correo electrónico inválido.'
    vistas.add(p.cedula)
    return e
  })
  return errores.value.every((e) => Object.keys(e).length === 0)
}

function irAAsientos() {
  aviso.value = ''
  if (validarPasajeros()) paso.value = 2
  else aviso.value = 'Revisa los campos marcados antes de continuar.'
}

function alternar(n) {
  aviso.value = ''
  const dueno = reserva.pasajeros.find((p) => p.asiento === n)
  if (dueno) { dueno.asiento = null; return }
  const libre = reserva.pasajeros.find((p) => !p.asiento)
  if (!libre) { aviso.value = 'Ya elegiste un asiento para cada pasajero. Toca uno elegido para cambiarlo.'; return }
  libre.asiento = n
}

async function irAResumen() {
  aviso.value = ''
  if (seleccionados.value.length < reserva.pasajeros.length) { aviso.value = 'Elige un asiento para cada pasajero.'; return }
  cargando.value = true
  try {
    tarifa.value = await calcularTarifa(reserva.viaje, reserva.pasajeros.map((p) => p.tipo))
    paso.value = 3
  } catch (e) {
    manejarError(e)
  } finally {
    cargando.value = false
  }
}

async function confirmar() {
  aviso.value = ''
  cargando.value = true
  try {
    reserva.creadas = await crearReservas(reserva.viaje, reserva.pasajeros)
    guardarPasajeros(reserva.creadas, reserva.pasajeros)
    reserva.guardar()
    finalizada.value = true
  } catch (e) {
    if (e.status === 409) {
      reserva.pasajeros.forEach((p) => (p.asiento = null))
      paso.value = 2
      await cargarDisponibilidad()
      aviso.value = 'Alguno de los asientos acaba de ser ocupado. Elige nuevamente.'
    } else manejarError(e)
  } finally {
    cargando.value = false
  }
}

function terminar() {
  reserva.limpiar()
  router.push({ name: 'inicio' })
}
</script>

<template>
  <div v-if="reserva.viaje" class="reserva page-container">
    <div class="page-heading">
      <RouterLink class="breadcrumb" to="/viajes">← Volver a los viajes</RouterLink>
      <span class="section-kicker">{{ reserva.viaje.origen.toUpperCase() }} → {{ reserva.viaje.destino.toUpperCase() }}</span>
      <h1>Reserva tu viaje</h1>
      <p>{{ reserva.viaje.cooperativa?.nombre }} · {{ reserva.viaje.fecha }} · salida {{ reserva.viaje.hora_salida }}</p>
    </div>

    <!-- Reserva creada -->
    <section v-if="finalizada" class="tarjeta exito">
      <h2>¡Reserva creada!</h2>
      <p>Tus asientos quedaron reservados con estado <strong>pendiente de pago</strong>. Puedes registrar el pago y descargar tus boletos desde Mis compras.</p>
      <ul class="lista-resumen">
        <li v-for="(p, i) in reserva.pasajeros" :key="i"><span>{{ p.nombres }} · asiento {{ p.asiento }}</span><b>{{ dinero(reserva.creadas[i]?.precio ?? 0) }}</b></li>
      </ul>
      <RouterLink class="btn" to="/compras">Continuar al pago</RouterLink><button class="btn sec" type="button" @click="terminar">Comprar otro boleto</button>
    </section>

    <template v-else>
      <ol class="pasos" aria-label="Progreso de la reserva">
        <li :class="{ activo: paso === 1, hecho: paso > 1 }">1. Pasajeros</li>
        <li :class="{ activo: paso === 2, hecho: paso > 2 }">2. Asientos</li>
        <li :class="{ activo: paso === 3 }">3. Resumen</li>
      </ol>
      <p v-if="aviso" class="aviso" role="alert">{{ aviso }}</p>

      <!-- Paso 1 -->
      <section v-if="paso === 1" class="tarjeta">
        <div class="cantidad">
          <span>Cantidad de pasajeros</span>
          <button type="button" aria-label="Quitar pasajero" :disabled="reserva.pasajeros.length <= 1" @click="cambiarCantidad(-1)">−</button>
          <b>{{ reserva.pasajeros.length }}</b>
          <button type="button" aria-label="Agregar pasajero" :disabled="reserva.pasajeros.length >= maxPasajeros" @click="cambiarCantidad(1)">+</button>
        </div>
        <fieldset v-for="(p, i) in reserva.pasajeros" :key="i" class="pasajero">
          <legend>{{ i === 0 ? 'Pasajero 1 (comprador)' : `Pasajero ${i + 1}` }}</legend>
          <label>Nombres y apellidos
            <input v-model.trim="p.nombres" autocomplete="off" :class="{ malo: errores[i]?.nombres }" />
            <small v-if="errores[i]?.nombres">{{ errores[i].nombres }}</small>
          </label>
          <label>Cédula
            <input v-model.trim="p.cedula" inputmode="numeric" maxlength="10" autocomplete="off" :readonly="i === 0 && !!cedulaCuenta" :class="{ malo: errores[i]?.cedula }" />
            <small v-if="i === 0 && cedulaCuenta" class="nota">Tomada de tu cuenta.</small>
            <small v-if="errores[i]?.cedula">{{ errores[i].cedula }}</small>
          </label>
          <label>Correo electrónico
            <input v-model.trim="p.correo" type="email" autocomplete="off" :class="{ malo: errores[i]?.correo }" />
            <small v-if="errores[i]?.correo">{{ errores[i].correo }}</small>
          </label>
          <label>Tipo de pasajero
            <select v-model="p.tipo">
              <option v-for="t in TIPOS_PASAJERO" :key="t.valor" :value="t.valor">{{ t.etiqueta }}{{ t.descuento ? ` (${t.descuento}% desc.)` : '' }}</option>
            </select>
            <small v-if="p.tipo !== 'GENERAL'" class="nota">El chofer verificará el documento que respalda el descuento al abordar.</small>
          </label>
        </fieldset>
        <button class="btn" type="button" @click="irAAsientos">Continuar a asientos →</button>
      </section>

      <!-- Paso 2 -->
      <section v-else-if="paso === 2" class="tarjeta">
        <p class="ayuda">VIP: {{ reserva.viaje.asientos_vip?.join(', ') || 'No disponibles' }}. Los demás asientos son normales.</p>
        <p class="ayuda">Elige {{ reserva.pasajeros.length }} asiento{{ reserva.pasajeros.length === 1 ? '' : 's' }}. Se asignan a los pasajeros en orden.</p>
        <label>Tipo de asiento<select v-model="tipoAsiento"><option value="">Todos</option><option>NORMAL</option><option>VIP</option></select></label>
        <MapaAsientos :vip="reserva.viaje.asientos_vip || []" :tipo="tipoAsiento" :capacidad="disp.capacidad" :ocupados="disp.ocupados" :seleccionados="seleccionados" @alternar="alternar" />
        <ul class="lista-resumen">
          <li v-for="(p, i) in reserva.pasajeros" :key="i"><span>{{ p.nombres }}</span><b>{{ p.asiento ? `Asiento ${p.asiento}` : 'Sin asiento' }}</b></li>
        </ul>
        <div class="acciones">
          <button class="btn sec" type="button" @click="paso = 1">← Pasajeros</button>
          <button class="btn" type="button" :disabled="cargando" @click="irAResumen">{{ cargando ? 'Calculando…' : 'Ver resumen →' }}</button>
        </div>
      </section>

      <!-- Paso 3 -->
      <section v-else class="tarjeta">
        <table class="tabla">
          <thead><tr><th>Pasajero</th><th>Asiento</th><th>Tipo</th><th>Descuento</th><th>Total</th></tr></thead>
          <tbody>
            <tr v-for="(p, i) in reserva.pasajeros" :key="i">
              <td>{{ p.nombres }}<small>{{ p.cedula }}</small></td><td>{{ p.asiento }}</td><td>{{ etiquetaTipo(p.tipo) }}</td>
              <td>{{ tarifa.detalle[i].descuento ? `−${dinero(tarifa.detalle[i].descuento)}` : '—' }}</td><td>{{ dinero(tarifa.detalle[i].total) }}</td>
            </tr>
          </tbody>
        </table>
        <dl class="totales">
          <div><dt>Subtotal</dt><dd>{{ dinero(tarifa.subtotal) }}</dd></div>
          <div><dt>Descuentos</dt><dd>−{{ dinero(tarifa.descuento_total) }}</dd></div>
          <div class="total"><dt>Total a pagar</dt><dd>{{ dinero(tarifa.total) }}</dd></div>
        </dl>
        <div class="acciones">
          <button class="btn sec" type="button" @click="paso = 2">← Asientos</button>
          <button class="btn" type="button" :disabled="cargando" @click="confirmar">{{ cargando ? 'Reservando…' : 'Confirmar reserva' }}</button>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.reserva { max-width: 820px; }
.pasos { display: flex; gap: 8px; list-style: none; padding: 0; margin: 0 0 16px; }
.pasos li { flex: 1; text-align: center; padding: 10px; border-radius: 10px; background: var(--surface-soft); color: var(--muted); font-size: 13px; font-weight: 700; }
.pasos li.activo { background: var(--brand); color: var(--surface); }
.pasos li.hecho { background: var(--brand-soft); color: var(--brand); }
.tarjeta { background: var(--surface); border: 1px solid var(--color-borde); border-radius: 14px; padding: 24px; display: grid; gap: 18px; }
.aviso { background: var(--danger-bg); color: var(--danger); border: 1px solid var(--border); padding: 10px 14px; border-radius: 10px; font-size: 14px; }
.cantidad { display: flex; align-items: center; gap: 14px; font-weight: 600; color: var(--text); }
.cantidad span { margin-right: auto; }
.cantidad button { width: 34px; height: 34px; border-radius: 50%; border: 1px solid var(--brand); background: var(--surface); color: var(--brand); font-size: 18px; }
.cantidad button:disabled { opacity: .4; cursor: not-allowed; }
.pasajero { border: 1px solid var(--color-borde); border-radius: 12px; padding: 14px 18px 18px; display: grid; grid-template-columns: 1fr 1fr; gap: 12px 16px; align-items: start; }
.pasajero legend { padding: 0 8px; font-weight: 700; color: var(--brand); }
.pasajero label { display: grid; align-content: start; gap: 5px; margin: 0; font-size: 13px; font-weight: 600; color: var(--text); }
.pasajero input, .pasajero select { margin: 0; width: 100%; box-sizing: border-box; padding: 10px 12px; border: 1px solid var(--border); border-radius: 9px; background: var(--surface); }
.pasajero input[readonly] { background: var(--surface-soft); color: var(--muted); }
.pasajero input.malo { border-color: var(--danger); }
.pasajero small { font-weight: 400; color: var(--danger); }
.pasajero small.nota { color: var(--muted); }
.ayuda { color: var(--muted); }
.lista-resumen { list-style: none; padding: 0; margin: 0; display: grid; gap: 8px; }
.lista-resumen li { display: flex; justify-content: space-between; padding: 10px 14px; background: var(--surface-soft); border-radius: 9px; font-size: 14px; }
.acciones { display: flex; justify-content: space-between; gap: 12px; }
.btn { background: var(--brand); color: var(--surface); border: 0; border-radius: 9px; padding: 12px 22px; font-weight: 800; }
.btn:hover:not(:disabled) { background: var(--brand-hover); }
.btn:disabled { opacity: .6; cursor: progress; }
.btn.sec { background: var(--surface); color: var(--brand); border: 1px solid var(--brand); }
.tabla { width: 100%; border-collapse: collapse; font-size: 14px; }
.tabla th { text-align: left; font-size: 12px; color: var(--muted); padding: 8px; border-bottom: 1px solid var(--color-borde); }
.tabla td { padding: 10px 8px; border-bottom: 1px solid var(--surface-soft); }
.tabla td small { display: block; color: var(--muted); font-size: 11px; }
.totales { margin: 0; display: grid; gap: 6px; justify-self: end; min-width: 240px; }
.totales div { display: flex; justify-content: space-between; gap: 24px; }
.totales dt { color: var(--muted); }
.totales dd { margin: 0; font-weight: 700; }
.totales .total { font-size: 18px; padding-top: 8px; border-top: 1px solid var(--color-borde); color: var(--brand); }
.exito h2 { color: var(--success); }
@media (max-width: 640px) { .pasajero { grid-template-columns: 1fr; } .tabla { font-size: 12px; } }
</style>