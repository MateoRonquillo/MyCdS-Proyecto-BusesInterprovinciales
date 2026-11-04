<script setup>
import { ref } from 'vue'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'

const reservasPendientes = ref([
  { id: 'RES-1001', pasajero: 'Carlos Mendoza', total: 4.50 },
  { id: 'RES-1004', pasajero: 'Ana Torres', total: 15.00 }
])

const formulario = ref({
  reservaId: '',
  metodoPago: 'Efectivo',
  numeroComprobante: '',
  monto: null
})

const mensajeExito = ref('')
const errorValidacion = ref('')

function registrarPago() {
  if (!formulario.value.reservaId) {
    errorValidacion.value = 'Debe seleccionar una reserva pendiente.'
    return
  }
  if (formulario.value.metodoPago !== 'Efectivo' && !formulario.value.numeroComprobante.trim()) {
    errorValidacion.value = 'El número de comprobante es obligatorio para depósitos y transferencias.'
    return
  }

  // Simulación de guardado
  errorValidacion.value = ''
  mensajeExito.value = `Pago registrado exitosamente para la reserva ${formulario.value.reservaId}. Estado actualizado a PAGO EN REVISIÓN.`
  
  // Limpiar formulario
  setTimeout(() => {
    reservasPendientes.value = reservasPendientes.value.filter(r => r.id !== formulario.value.reservaId)
    formulario.value = { reservaId: '', metodoPago: 'Efectivo', numeroComprobante: '', monto: null }
    mensajeExito.value = ''
  }, 3000)
}
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="OFICINISTA" />

    <main class="admin-main">
      <header class="page-header">
        <div>
          <span class="module-pill">Módulo M06</span>
          <h1>Carga de Comprobantes</h1>
          <p class="subtitle">
            Registro de pagos en efectivo, depósitos o transferencias para reservas pendientes.
          </p>
        </div>
      </header>

      <div class="form-container">
        <div v-if="mensajeExito" class="alert-success">{{ mensajeExito }}</div>
        <p v-if="errorValidacion" class="alert-error">{{ errorValidacion }}</p>

        <form @submit.prevent="registrarPago" class="admin-form">
          <div class="form-row">
            <label>Seleccionar Reserva Pendiente *</label>
            <select v-model="formulario.reservaId" required>
              <option value="" disabled>Seleccione una reserva...</option>
              <option v-for="res in reservasPendientes" :key="res.id" :value="res.id">
                {{ res.id }} - {{ res.pasajero }} (${{ res.total.toFixed(2) }})
              </option>
            </select>
          </div>

          <div class="form-grid-2">
            <div class="form-row">
              <label>Método de Pago *</label>
              <select v-model="formulario.metodoPago">
                <option value="Efectivo">Efectivo (Ventanilla)</option>
                <option value="Deposito">Depósito Bancario</option>
                <option value="Transferencia">Transferencia</option>
              </select>
            </div>
            
            <div class="form-row">
              <label>Monto Recibido (USD) *</label>
              <input v-model="formulario.monto" type="number" step="0.25" min="1" placeholder="Ej: 4.50" required />
            </div>
          </div>

          <div class="form-row" v-if="formulario.metodoPago !== 'Efectivo'">
            <label>Número de Comprobante / Transacción *</label>
            <input v-model="formulario.numeroComprobante" type="text" placeholder="Ej: 0987654321" />
          </div>

          <div class="modal-footer">
            <button type="submit" class="btn-primary">Registrar Pago</button>
          </div>
        </form>
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-layout { display: flex; min-height: 100vh; background-color: #f8fafc; font-family: system-ui, -apple-system, sans-serif; }
.admin-main { flex: 1; padding: 2rem; }
.page-header { margin-bottom: 1.5rem; }
.module-pill { font-size: 0.75rem; font-weight: 700; color: #0f766e; background: #ccfbf1; padding: 0.2rem 0.55rem; border-radius: 4px; }
.subtitle { color: #64748b; margin-top: 0.25rem; }
.form-container { background: #ffffff; padding: 2rem; border-radius: 8px; border: 1px solid #e2e8f0; max-width: 700px; }
.admin-form { display: flex; flex-direction: column; gap: 1.25rem; }
.form-row { display: flex; flex-direction: column; gap: 0.35rem; }
.form-row input, .form-row select { padding: 0.65rem; border: 1px solid #cbd5e1; border-radius: 6px; }
.form-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.modal-footer { display: flex; justify-content: flex-end; margin-top: 1rem; }
.btn-primary { background: #0f766e; color: #ffffff; border: none; padding: 0.75rem 1.25rem; border-radius: 6px; font-weight: 600; cursor: pointer; }
.alert-success { background: #dcfce7; color: #166534; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; }
.alert-error { background: #fee2e2; color: #991b1b; padding: 0.75rem 1rem; border-radius: 6px; margin-bottom: 1rem; }
</style>