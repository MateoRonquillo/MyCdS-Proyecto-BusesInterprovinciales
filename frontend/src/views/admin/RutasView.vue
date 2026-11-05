<script setup>
import { ref, onMounted } from 'vue'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'
import {
  obtenerRutasYFrecuencias,
  guardarRutaYFrecuenciaService,
} from '../../services/adminService'

const rutas = ref([])
const mostrarModal = ref(false)
const modoEdicion = ref(false)
const errorValidacion = ref('')

const formulario = ref({
  id: null,
  origen: '',
  destino: '',
  distanciaKm: 100,
  duracionEstimada: '02h30m',
  tarifaBase: 5.0,
  frecuenciaHora: '07:00',
  diasOperacion: 'Lunes a Domingo',
  busAsignado: 'DISCO-14 (PAA-1420)',
  activa: true,
})

onMounted(async () => {
  rutas.value = await obtenerRutasYFrecuencias()
})

function abrirNuevaRuta() {
  modoEdicion.value = false
  errorValidacion.value = ''
  formulario.value = {
    id: null,
    origen: '',
    destino: '',
    distanciaKm: 120,
    duracionEstimada: '03h00m',
    tarifaBase: 5.0,
    frecuenciaHora: '08:00',
    diasOperacion: 'Lunes a Domingo',
    busAsignado: 'DISCO-14 (PAA-1420)',
    activa: true,
  }
  mostrarModal.value = true
}

function editarRuta(ruta) {
  modoEdicion.value = true
  errorValidacion.value = ''
  formulario.value = { ...ruta }
  mostrarModal.value = true
}

async function guardarRuta() {
  if (!formulario.value.origen.trim() || !formulario.value.destino.trim()) {
    errorValidacion.value = 'El origen y el destino son obligatorios.'
    return
  }
  if (
    formulario.value.origen.trim().toLowerCase() ===
    formulario.value.destino.trim().toLowerCase()
  ) {
    errorValidacion.value = 'La ciudad de origen y destino no pueden ser iguales.'
    return
  }

  await guardarRutaYFrecuenciaService({
    ...formulario.value,
    tarifaBase: Number(formulario.value.tarifaBase),
    distanciaKm: Number(formulario.value.distanciaKm),
  })
  rutas.value = await obtenerRutasYFrecuencias()
  mostrarModal.value = false
}
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="ADMINISTRADOR" />

    <main class="admin-main">
      <header class="page-header">
        <div>
          <span class="module-pill">Módulo M05 / M06</span>
          <h1>Rutas Interprovinciales y Frecuencias</h1>
          <p class="subtitle">
            Configuración de trayectos origen-destino, tarifas base y programación de horarios de salida.
          </p>
        </div>
        <button class="btn-primary" @click="abrirNuevaRuta">
          + Crear Ruta y Frecuencia
        </button>
      </header>

      <section class="table-card">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Trayecto (Origen → Destino)</th>
              <th>Distancia / Duración</th>
              <th>Frecuencia (Salida)</th>
              <th>Unidad Asignada</th>
              <th>Tarifa Base</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="ruta in rutas" :key="ruta.id">
              <td>
                <strong>{{ ruta.origen }} → {{ ruta.destino }}</strong>
              </td>
              <td>{{ ruta.distanciaKm }} km · {{ ruta.duracionEstimada }}</td>
              <td>{{ ruta.frecuenciaHora }} ({{ ruta.diasOperacion }})</td>
              <td>{{ ruta.busAsignado }}</td>
              <td>${{ Number(ruta.tarifaBase).toFixed(2) }}</td>
              <td>
                <button class="btn-sm" @click="editarRuta(ruta)">Editar</button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <div v-if="mostrarModal" class="modal-backdrop">
        <div class="modal-box">
          <h2>{{ modoEdicion ? 'Editar Ruta y Frecuencia' : 'Nueva Ruta y Frecuencia' }}</h2>
          <p v-if="errorValidacion" class="alert-error">{{ errorValidacion }}</p>

          <form @submit.prevent="guardarRuta" class="admin-form">
            <div class="form-grid-2">
              <div class="form-row">
                <label>Ciudad de Origen *</label>
                <input
                  v-model="formulario.origen"
                  type="text"
                  placeholder="Ej: Quito"
                  required
                />
              </div>
              <div class="form-row">
                <label>Ciudad de Destino *</label>
                <input
                  v-model="formulario.destino"
                  type="text"
                  placeholder="Ej: Ambato"
                  required
                />
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-row">
                <label>Distancia (km)</label>
                <input v-model="formulario.distanciaKm" type="number" min="1" />
              </div>
              <div class="form-row">
                <label>Duración estimada</label>
                <input
                  v-model="formulario.duracionEstimada"
                  type="text"
                  placeholder="02h45m"
                />
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-row">
                <label>Hora de salida (Frecuencia)</label>
                <input v-model="formulario.frecuenciaHora" type="time" />
              </div>
              <div class="form-row">
                <label>Tarifa base (USD)</label>
                <input
                  v-model="formulario.tarifaBase"
                  type="number"
                  step="0.25"
                  min="0.5"
                />
              </div>
            </div>

            <div class="form-row">
              <label>Unidad asignada</label>
              <input
                v-model="formulario.busAsignado"
                type="text"
                placeholder="DISCO-14 (PAA-1420)"
              />
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn-secondary"
                @click="mostrarModal = false"
              >
                Cancelar
              </button>
              <button type="submit" class="btn-primary">Guardar ruta</button>
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
.form-row input {
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