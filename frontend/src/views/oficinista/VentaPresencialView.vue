<script setup>
import { ref, computed } from 'vue'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'

// Estado del flujo de venta
const pasoActual = ref(1) // 1: Viaje, 2: Asientos, 3: Pasajero y Pago

// Mocks temporales para viajes y asientos
const viajesDisponibles = ref([
  { id: 'V-001', ruta: 'Quito → Ambato', hora: '10:30', bus: 'DISCO-14', tarifa: 4.50, disponibles: 12 },
  { id: 'V-002', ruta: 'Quito → Guayaquil', hora: '11:00', bus: 'DISCO-08', tarifa: 12.00, disponibles: 5 },
  { id: 'V-003', ruta: 'Ambato → Puyo', hora: '12:15', bus: 'DISCO-25', tarifa: 3.75, disponibles: 20 }
])

const asientosDisponibles = ref(
  Array.from({ length: 40 }, (_, i) => ({
    numero: i + 1,
    estado: Math.random() > 0.7 ? 'OCUPADO' : 'DISPONIBLE'
  }))
)

// Formularios y selecciones
const viajeSeleccionado = ref(null)
const asientosSeleccionados = ref([])
const datosPasajero = ref({ cedula: '', nombre: '', correo: '' })
const mensajeExito = ref('')

const totalPagar = computed(() => {
  if (!viajeSeleccionado.value) return 0
  return viajeSeleccionado.value.tarifa * asientosSeleccionados.value.length
})

function seleccionarViaje(viaje) {
  viajeSeleccionado.value = viaje
  pasoActual.value = 2
  asientosSeleccionados.value = []
}

function toggleAsiento(asiento) {
  if (asiento.estado === 'OCUPADO') return
  const index = asientosSeleccionados.value.indexOf(asiento.numero)
  if (index === -1) {
    if (asientosSeleccionados.value.length < 5) asientosSeleccionados.value.push(asiento.numero)
  } else {
    asientosSeleccionados.value.splice(index, 1)
  }
}

function irAPago() {
  if (asientosSeleccionados.value.length === 0) return
  pasoActual.value = 3
}

function emitirBoleto() {
  if (!datosPasajero.value.cedula || !datosPasajero.value.nombre) return
  
  mensajeExito.value = `¡Boleto emitido con éxito! (Asientos: ${asientosSeleccionados.value.join(', ')})`
  
  setTimeout(() => {
    // Resetear el flujo para el siguiente cliente en la fila
    pasoActual.value = 1
    viajeSeleccionado.value = null
    asientosSeleccionados.value = []
    datosPasajero.value = { cedula: '', nombre: '', correo: '' }
    mensajeExito.value = ''
  }, 4000)
}
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="OFICINISTA" />

    <main class="admin-main">
      <header class="page-header">
        <div>
          <span class="module-pill">Módulo M13</span>
          <h1>Venta en Ventanilla</h1>
          <p class="subtitle">Emisión rápida de pasajes presenciales, selección de asientos y cobro.</p>
        </div>
      </header>

      <div v-if="mensajeExito" class="alert-success">
        <strong>✓ Operación exitosa:</strong> {{ mensajeExito }}
      </div>

      <div class="wizard-container" v-else>
        <!-- PASO 1: Seleccionar Viaje -->
        <section v-if="pasoActual === 1" class="step-card">
          <h2>1. Próximas Salidas</h2>
          <div class="viajes-grid">
            <div 
              v-for="viaje in viajesDisponibles" 
              :key="viaje.id" 
              class="viaje-item"
              @click="seleccionarViaje(viaje)"
            >
              <div class="viaje-ruta">{{ viaje.ruta }}</div>
              <div class="viaje-detalles">
                <span>🕒 {{ viaje.hora }}</span>
                <span>🚌 {{ viaje.bus }}</span>
              </div>
              <div class="viaje-footer">
                <span class="precio">${{ viaje.tarifa.toFixed(2) }}</span>
                <span class="disponibles">{{ viaje.disponibles }} asientos disp.</span>
              </div>
            </div>
          </div>
        </section>

        <!-- PASO 2: Seleccionar Asientos -->
        <section v-if="pasoActual === 2" class="step-card">
          <div class="step-header">
            <h2>2. Seleccionar Asientos ({{ viajeSeleccionado.ruta }})</h2>
            <button class="btn-outline" @click="pasoActual = 1">Volver</button>
          </div>
          
          <div class="asientos-layout">
            <div class="bus-grid">
              <div 
                v-for="asiento in asientosDisponibles" 
                :key="asiento.numero"
                class="asiento"
                :class="{
                  'ocupado': asiento.estado === 'OCUPADO',
                  'seleccionado': asientosSeleccionados.includes(asiento.numero)
                }"
                @click="toggleAsiento(asiento)"
              >
                {{ asiento.numero }}
              </div>
            </div>
            
            <div class="resumen-panel">
              <h3>Resumen</h3>
              <p><strong>Seleccionados:</strong> {{ asientosSeleccionados.length || 0 }}</p>
              <p><strong>Asientos:</strong> {{ asientosSeleccionados.join(', ') || '-' }}</p>
              <h2 class="total-text">Total: ${{ totalPagar.toFixed(2) }}</h2>
              
              <button 
                class="btn-primary btn-block" 
                :disabled="asientosSeleccionados.length === 0"
                @click="irAPago"
              >
                Continuar con el cobro →
              </button>
            </div>
          </div>
        </section>

        <!-- PASO 3: Pasajero y Emisión -->
        <section v-if="pasoActual === 3" class="step-card">
          <div class="step-header">
            <h2>3. Datos del Pasajero y Emisión</h2>
            <button class="btn-outline" @click="pasoActual = 2">Volver a asientos</button>
          </div>

          <form @submit.prevent="emitirBoleto" class="emision-grid">
            <div class="form-section">
              <div class="form-row">
                <label>Cédula de Identidad *</label>
                <input v-model="datosPasajero.cedula" type="text" maxlength="10" required placeholder="Ej: 1712345678" />
              </div>
              <div class="form-row">
                <label>Nombre Completo *</label>
                <input v-model="datosPasajero.nombre" type="text" required placeholder="Ej: Juan Pérez" />
              </div>
              <div class="form-row">
                <label>Correo (Opcional para factura electrónica)</label>
                <input v-model="datosPasajero.correo" type="email" placeholder="juan@email.com" />
              </div>
            </div>

            <div class="resumen-final-panel">
              <h3>Detalle de Venta</h3>
              <div class="ticket-preview">
                <p><strong>Ruta:</strong> {{ viajeSeleccionado.ruta }}</p>
                <p><strong>Salida:</strong> {{ viajeSeleccionado.hora }}</p>
                <p><strong>Asientos ({{ asientosSeleccionados.length }}):</strong> {{ asientosSeleccionados.join(', ') }}</p>
                <hr>
                <p class="cobro-total">A COBRAR: ${{ totalPagar.toFixed(2) }}</p>
              </div>
              <button type="submit" class="btn-success btn-block">
                Cobrar e Imprimir Boleto
              </button>
            </div>
          </form>
        </section>
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; background-color: #f4f6f9; font-family: system-ui, -apple-system, sans-serif; }
.admin-main { flex: 1; padding: 2rem; }
.page-header { margin-bottom: 1.5rem; }
.module-pill { font-size: 0.75rem; font-weight: 700; color: #b45309; background: #fef3c7; padding: 0.2rem 0.55rem; border-radius: 4px; }
.subtitle { color: #64748b; margin-top: 0.25rem; }
.wizard-container { max-width: 900px; }
.step-card { background: #ffffff; padding: 2rem; border-radius: 8px; border: 1px solid #e2e8f0; }
.step-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1.5rem; }
.step-header h2 { margin: 0; color: #1e293b; }

/* Grid de viajes */
.viajes-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 1rem; }
.viaje-item { border: 1px solid #cbd5e1; border-radius: 8px; padding: 1rem; cursor: pointer; transition: 0.2s; }
.viaje-item:hover { border-color: #0f766e; background-color: #f0fdfa; transform: translateY(-2px); }
.viaje-ruta { font-weight: 700; font-size: 1.1rem; color: #0f172a; margin-bottom: 0.5rem; }
.viaje-detalles { display: flex; justify-content: space-between; color: #475569; font-size: 0.9rem; margin-bottom: 1rem; }
.viaje-footer { display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #e2e8f0; padding-top: 0.75rem; }
.precio { font-weight: 800; color: #0f766e; font-size: 1.1rem; }
.disponibles { font-size: 0.8rem; background: #e0f2fe; color: #0369a1; padding: 0.2rem 0.4rem; border-radius: 4px; }

/* Grid de Asientos */
.asientos-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 2rem; }
.bus-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.75rem; background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 2px dashed #cbd5e1; }
.asiento { background: #ffffff; border: 2px solid #94a3b8; border-radius: 6px; padding: 0.75rem; text-align: center; font-weight: 700; cursor: pointer; user-select: none; transition: 0.2s; }
.asiento:hover:not(.ocupado) { border-color: #0f766e; color: #0f766e; }
.asiento.ocupado { background: #e2e8f0; border-color: #cbd5e1; color: #94a3b8; cursor: not-allowed; }
.asiento.seleccionado { background: #0f766e; border-color: #0f766e; color: #ffffff; }

/* Resumen y Formulario */
.resumen-panel, .resumen-final-panel { background: #f8fafc; padding: 1.5rem; border-radius: 8px; border: 1px solid #e2e8f0; display: flex; flex-direction: column; }
.total-text { color: #0f766e; margin: 1.5rem 0; font-size: 1.5rem; border-bottom: 2px solid #0f766e; padding-bottom: 0.5rem; }
.emision-grid { display: grid; grid-template-columns: 1.5fr 1fr; gap: 2rem; }
.form-section { display: flex; flex-direction: column; gap: 1.25rem; }
.form-row { display: flex; flex-direction: column; gap: 0.35rem; }
.form-row input { padding: 0.75rem; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 1rem; }
.ticket-preview { background: #fff; padding: 1rem; border: 1px dashed #94a3b8; margin-bottom: 1.5rem; border-radius: 4px; }
.ticket-preview p { margin: 0.25rem 0; font-size: 0.95rem; }
.cobro-total { font-weight: 800; font-size: 1.25rem; color: #b45309; margin-top: 0.5rem !important; }

/* Botones y alertas */
.btn-primary { background: #0f766e; color: #ffffff; border: none; padding: 0.75rem; border-radius: 6px; font-weight: 600; cursor: pointer; }
.btn-primary:disabled { background: #94a3b8; cursor: not-allowed; }
.btn-success { background: #15803d; color: #ffffff; border: none; padding: 1rem; border-radius: 6px; font-weight: 700; cursor: pointer; font-size: 1.1rem; transition: 0.2s; }
.btn-success:hover { background: #166534; }
.btn-outline { background: transparent; border: 1px solid #cbd5e1; padding: 0.4rem 0.8rem; border-radius: 6px; cursor: pointer; color: #475569; }
.btn-block { width: 100%; }
.alert-success { background: #dcfce7; color: #166534; padding: 1rem; border-radius: 8px; font-size: 1.1rem; border: 1px solid #bbf7d0; max-width: 900px; }
</style>