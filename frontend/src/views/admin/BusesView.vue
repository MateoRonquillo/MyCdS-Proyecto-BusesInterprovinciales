<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'
import {
  obtenerBuses,
  obtenerCooperativas,
  guardarBusService,
} from '../../services/adminService'

const buses = ref([])
const cooperativas = ref([])
const mostrarModal = ref(false)
const modoEdicion = ref(false)
const errorFormulario = ref('')

const plantillasDisponibles = [
  { nombre: '2x2 Estándar (40 asientos)', capacidad: 40 },
  { nombre: '2x2 Clásico (44 asientos)', capacidad: 44 },
  { nombre: 'Salón Cama 2x1 (32 asientos)', capacidad: 32 },
]

const formulario = ref({
  id: null,
  numeroDisco: '',
  placa: '',
  cooperativaId: 1,
  cooperativaNombre: '',
  tipoServicio: 'Ejecutivo',
  plantillaAsientos: '2x2 Estándar (40 asientos)',
  capacidadTotal: 40,
  estado: 'OPERATIVO',
})

onMounted(async () => {
  buses.value = await obtenerBuses()
  cooperativas.value = await obtenerCooperativas()
})

function actualizarCapacidadSegunPlantilla() {
  const encontrada = plantillasDisponibles.find(
    (p) => p.nombre === formulario.value.plantillaAsientos
  )
  if (encontrada) {
    formulario.value.capacidadTotal = encontrada.capacidad
  }
}

function abrirNuevoBus() {
  modoEdicion.value = false
  errorFormulario.value = ''
  const primeraCoop = cooperativas.value[0] || { id: 1, nombre: 'General' }
  formulario.value = {
    id: null,
    numeroDisco: '',
    placa: '',
    cooperativaId: primeraCoop.id,
    cooperativaNombre: primeraCoop.nombre,
    tipoServicio: 'Ejecutivo',
    plantillaAsientos: '2x2 Estándar (40 asientos)',
    capacidadTotal: 40,
    estado: 'OPERATIVO',
  }
  mostrarModal.value = true
}

function editarBus(bus) {
  modoEdicion.value = true
  errorFormulario.value = ''
  formulario.value = { ...bus }
  mostrarModal.value = true
}

async function guardarBus() {
  if (!formulario.value.numeroDisco.trim() || !formulario.value.placa.trim()) {
    errorFormulario.value = 'El número de disco y la placa son obligatorios.'
    return
  }
  const coopSeleccionada = cooperativas.value.find(
    (c) => Number(c.id) === Number(formulario.value.cooperativaId)
  )
  if (coopSeleccionada) {
    formulario.value.cooperativaNombre = coopSeleccionada.nombre
  }

  await guardarBusService({ ...formulario.value })
  buses.value = await obtenerBuses()
  mostrarModal.value = false
}
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="ADMINISTRADOR" />

    <main class="admin-main">
      <header class="page-header">
        <div>
          <span class="module-pill">Módulo M03 / M04</span>
          <h1>Flota de Buses y Plantillas de Asientos</h1>
          <p class="subtitle">
            Administración de unidades, asignación a cooperativas y configuración de capacidad.
          </p>
        </div>
        <button class="btn-primary" @click="abrirNuevoBus">+ Registrar Bus</button>
      </header>

      <section class="table-card">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Disco</th>
              <th>Placa</th>
              <th>Cooperativa</th>
              <th>Servicio</th>
              <th>Plantilla / Capacidad</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="bus in buses" :key="bus.id">
              <td><strong>{{ bus.numeroDisco }}</strong></td>
              <td>{{ bus.placa }}</td>
              <td>{{ bus.cooperativaNombre }}</td>
              <td>{{ bus.tipoServicio }}</td>
              <td>{{ bus.plantillaAsientos }} ({{ bus.capacidadTotal }} asientos)</td>
              <td>
                <span
                  :class="bus.estado === 'OPERATIVO' ? 'badge-ok' : 'badge-warn'"
                >
                  {{ bus.estado }}
                </span>
              </td>
              <td>
                <button class="btn-sm" @click="editarBus(bus)">Editar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <div v-if="mostrarModal" class="modal-backdrop">
        <div class="modal-box">
          <h2>{{ modoEdicion ? 'Editar Unidad' : 'Registrar Nueva Unidad' }}</h2>
          <p v-if="errorFormulario" class="alert-error">{{ errorFormulario }}</p>

          <form @submit.prevent="guardarBus" class="admin-form">
            <div class="form-grid-2">
              <div class="form-row">
                <label>Número de Disco *</label>
                <input
                  v-model="formulario.numeroDisco"
                  type="text"
                  placeholder="Ej: DISCO-30"
                  required
                />
              </div>
              <div class="form-row">
                <label>Placa *</label>
                <input
                  v-model="formulario.placa"
                  type="text"
                  placeholder="Ej: PAA-4512"
                  required
                />
              </div>
            </div>

            <div class="form-row">
              <label>Cooperativa asignada</label>
              <select v-model="formulario.cooperativaId">
                <option
                  v-for="coop in cooperativas"
                  :key="coop.id"
                  :value="coop.id"
                >
                  {{ coop.nombre }}
                </option>
              </select>
            </div>

            <div class="form-grid-2">
              <div class="form-row">
                <label>Tipo de servicio</label>
                <select v-model="formulario.tipoServicio">
                  <option value="Normal">Normal</option>
                  <option value="Ejecutivo">Ejecutivo</option>
                  <option value="VIP">VIP</option>
                </select>
              </div>

              <div class="form-row">
                <label>Estado de unidad</label>
                <select v-model="formulario.estado">
                  <option value="OPERATIVO">OPERATIVO</option>
                  <option value="MANTENIMIENTO">MANTENIMIENTO</option>
                </select>
              </div>
            </div>

            <div class="form-row">
              <label>Plantilla de distribución de asientos</label>
              <select
                v-model="formulario.plantillaAsientos"
                @change="actualizarCapacidadSegunPlantilla"
              >
                <option
                  v-for="plt in plantillasDisponibles"
                  :key="plt.nombre"
                  :value="plt.nombre"
                >
                  {{ plt.nombre }}
                </option>
              </select>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn-secondary"
                @click="mostrarModal = false"
              >
                Cancelar
              </button>
              <button type="submit" class="btn-primary">Guardar unidad</button>
            </div>
          </form>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f4f6f9;
  font-family: system-ui, -apple-system, sans-serif;
}
.admin-main {
  flex: 1;
  padding: 2rem;
}
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
}
.module-pill {
  font-size: 0.75rem;
  font-weight: 700;
  color: #1d4ed8;
  background: #dbeafe;
  padding: 0.2rem 0.55rem;
  border-radius: 4px;
}
.subtitle {
  color: #64748b;
  margin-top: 0.25rem;
}
.table-card {
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
  overflow-x: auto;
}
.admin-table {
  width: 100%;
  border-collapse: collapse;
}
.admin-table th,
.admin-table td {
  padding: 0.9rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}
.admin-table th {
  background: #f8fafc;
  color: #475569;
  font-size: 0.85rem;
}
.badge-ok {
  background: #dcfce7;
  color: #166534;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
.badge-warn {
  background: #fef3c7;
  color: #92400e;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
.btn-primary {
  background: #1d4ed8;
  color: #ffffff;
  border: none;
  padding: 0.65rem 1.1rem;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.btn-secondary {
  background: #e2e8f0;
  color: #1e293b;
  border: none;
  padding: 0.65rem 1.1rem;
  border-radius: 6px;
  cursor: pointer;
}
.btn-sm {
  background: #eff6ff;
  color: #1d4ed8;
  border: 1px solid #bfdbfe;
  padding: 0.35rem 0.65rem;
  border-radius: 5px;
  cursor: pointer;
}
.alert-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.65rem;
  border-radius: 6px;
}
.modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
}
.modal-box {
  background: #ffffff;
  padding: 1.75rem;
  border-radius: 10px;
  width: 100%;
  max-width: 520px;
}
.admin-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.form-row input,
.form-row select {
  padding: 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}
.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.75rem;
}
</style>