<script setup>
import { ref, computed, onMounted } from 'vue'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'
import {
  obtenerCooperativas,
  guardarCooperativaService,
} from '../../services/adminService'

const cooperativas = ref([])
const filtroTexto = ref('')
const filtroEstado = ref('TODOS')
const mostrarFormulario = ref(false)
const modoEdicion = ref(false)
const mensajeExito = ref('')
const errorValidacion = ref('')

const formulario = ref({
  id: null,
  nombre: '',
  ruc: '',
  telefono: '',
  correo: '',
  terminalBase: '',
  colorPrimario: '#1e3a8a',
  activa: true,
})

onMounted(async () => {
  cooperativas.value = await obtenerCooperativas()
})

const cooperativasFiltradas = computed(() => {
  return cooperativas.value.filter((coop) => {
    const coincideTexto =
      coop.nombre.toLowerCase().includes(filtroTexto.value.toLowerCase()) ||
      coop.ruc.includes(filtroTexto.value) ||
      coop.terminalBase.toLowerCase().includes(filtroTexto.value.toLowerCase())

    const coincideEstado =
      filtroEstado.value === 'TODOS' ||
      (filtroEstado.value === 'ACTIVA' && coop.activa) ||
      (filtroEstado.value === 'INACTIVA' && !coop.activa)

    return coincideTexto && coincideEstado
  })
})

function abrirNuevaCooperativa() {
  modoEdicion.value = false
  errorValidacion.value = ''
  formulario.value = {
    id: null,
    nombre: '',
    ruc: '',
    telefono: '',
    correo: '',
    terminalBase: '',
    colorPrimario: '#1e3a8a',
    activa: true,
  }
  mostrarFormulario.value = true
}

function editarCooperativa(coop) {
  modoEdicion.value = true
  errorValidacion.value = ''
  formulario.value = { ...coop }
  mostrarFormulario.value = true
}

async function guardarCooperativa() {
  if (!formulario.value.nombre.trim() || !formulario.value.ruc.trim()) {
    errorValidacion.value = 'El nombre de la cooperativa y el RUC son obligatorios.'
    return
  }
  if (!/^\d{13}$/.test(formulario.value.ruc.trim())) {
    errorValidacion.value = 'El RUC debe contener exactamente 13 dígitos numéricos.'
    return
  }

  await guardarCooperativaService({ ...formulario.value })
  cooperativas.value = await obtenerCooperativas()
  mostrarFormulario.value = false
  mensajeExito.value = modoEdicion.value
    ? 'Cooperativa actualizada correctamente.'
    : 'Nueva cooperativa registrada exitosamente.'
  setTimeout(() => {
    mensajeExito.value = ''
  }, 3500)
}

async function alternarEstadoCooperativa(coop) {
  const actualizada = { ...coop, activa: !coop.activa }
  await guardarCooperativaService(actualizada)
  cooperativas.value = await obtenerCooperativas()
}
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="ADMINISTRADOR" />

    <main class="admin-main">
      <header class="page-header">
        <div>
          <span class="module-pill">Módulo M02</span>
          <h1>Gestión de Cooperativas</h1>
          <p class="subtitle">
            Registro, edición, estado operativo y personalización básica de cooperativas interprovinciales.
          </p>
        </div>
        <button class="btn-primary" @click="abrirNuevaCooperativa">
          + Registrar Cooperativa
        </button>
      </header>

      <div v-if="mensajeExito" class="alert-success">
        {{ mensajeExito }}
      </div>

      <section class="filters-bar">
        <input
          v-model="filtroTexto"
          type="text"
          class="input-search"
          placeholder="Buscar por nombre, RUC o terminal base..."
        />
        <select v-model="filtroEstado" class="select-filter">
          <option value="TODOS">Todos los estados</option>
          <option value="ACTIVA">Solo activas</option>
          <option value="INACTIVA">Solo inactivas</option>
        </select>
      </section>

      <section class="table-card">
        <table class="admin-table">
          <thead>
            <tr>
              <th>Color</th>
              <th>Cooperativa</th>
              <th>RUC</th>
              <th>Terminal Base</th>
              <th>Contacto</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="coop in cooperativasFiltradas" :key="coop.id">
              <td>
                <span
                  class="color-dot"
                  :style="{ backgroundColor: coop.colorPrimario }"
                ></span>
              </td>
              <td>
                <strong>{{ coop.nombre }}</strong>
              </td>
              <td>{{ coop.ruc }}</td>
              <td>{{ coop.terminalBase }}</td>
              <td>
                <div>{{ coop.telefono }}</div>
                <small class="text-muted">{{ coop.correo }}</small>
              </td>
              <td>
                <span :class="coop.activa ? 'badge-active' : 'badge-inactive'">
                  {{ coop.activa ? 'ACTIVA' : 'INACTIVA' }}
                </span>
              </td>
              <td class="actions-cell">
                <button class="btn-sm" @click="editarCooperativa(coop)">
                  Editar
                </button>
                <button
                  class="btn-sm btn-outline"
                  @click="alternarEstadoCooperativa(coop)"
                >
                  {{ coop.activa ? 'Desactivar' : 'Activar' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>

      <div v-if="mostrarFormulario" class="modal-backdrop">
        <div class="modal-box">
          <h2>{{ modoEdicion ? 'Editar Cooperativa' : 'Registrar Cooperativa' }}</h2>

          <p v-if="errorValidacion" class="alert-error">{{ errorValidacion }}</p>

          <form @submit.prevent="guardarCooperativa" class="admin-form">
            <div class="form-row">
              <label>Nombre comercial *</label>
              <input
                v-model="formulario.nombre"
                type="text"
                placeholder="Ej: Cooperativa Flota Imbabura"
                required
              />
            </div>

            <div class="form-grid-2">
              <div class="form-row">
                <label>RUC (13 dígitos) *</label>
                <input
                  v-model="formulario.ruc"
                  type="text"
                  maxlength="13"
                  placeholder="1790012345001"
                  required
                />
              </div>

              <div class="form-row">
                <label>Teléfono de oficina</label>
                <input
                  v-model="formulario.telefono"
                  type="text"
                  placeholder="02-250-1122"
                />
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-row">
                <label>Correo electrónico</label>
                <input
                  v-model="formulario.correo"
                  type="email"
                  placeholder="contacto@cooperativa.ec"
                />
              </div>

              <div class="form-row">
                <label>Terminal principal</label>
                <input
                  v-model="formulario.terminalBase"
                  type="text"
                  placeholder="Ej: Quito - Quitumbe"
                />
              </div>
            </div>

            <div class="form-grid-2">
              <div class="form-row">
                <label>Color identificativo</label>
                <input v-model="formulario.colorPrimario" type="color" />
              </div>

              <div class="form-row checkbox-row">
                <label>
                  <input v-model="formulario.activa" type="checkbox" />
                  Cooperativa habilitada para venta
                </label>
              </div>
            </div>

            <div class="modal-footer">
              <button
                type="button"
                class="btn-secondary"
                @click="mostrarFormulario = false"
              >
                Cancelar
              </button>
              <button type="submit" class="btn-primary">
                {{ modoEdicion ? 'Guardar cambios' : 'Registrar cooperativa' }}
              </button>
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
.filters-bar {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.25rem;
}
.input-search {
  flex: 1;
  padding: 0.65rem 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}
.select-filter {
  padding: 0.65rem 0.9rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  background: #ffffff;
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
.color-dot {
  display: inline-block;
  width: 18px;
  height: 18px;
  border-radius: 50%;
}
.text-muted {
  color: #64748b;
}
.badge-active {
  background: #dcfce7;
  color: #166534;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
.badge-inactive {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.25rem 0.55rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}
.actions-cell {
  display: flex;
  gap: 0.5rem;
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
  font-size: 0.8rem;
}
.btn-outline {
  background: #ffffff;
  color: #334155;
  border-color: #cbd5e1;
}
.alert-success {
  background: #dcfce7;
  color: #166534;
  padding: 0.75rem 1rem;
  border-radius: 6px;
  margin-bottom: 1rem;
}
.alert-error {
  background: #fee2e2;
  color: #991b1b;
  padding: 0.65rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
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
  max-width: 540px;
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
.form-row input[type='text'],
.form-row input[type='email'] {
  padding: 0.6rem;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
}
.form-grid-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.checkbox-row {
  justify-content: center;
}
.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.75rem;
}
</style>