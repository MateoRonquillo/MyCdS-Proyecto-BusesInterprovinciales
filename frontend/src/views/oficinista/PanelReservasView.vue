<script setup>
import { ref } from 'vue'
import AdminSidebar from '../../components/admin/AdminSidebar.vue'

// Datos simulados (Mocks) hasta que I1 (Mateo) termine la API de reservas
const reservas = ref([
  {
    id: 'RES-1001',
    pasajero: 'Carlos Mendoza',
    ruta: 'Quito → Ambato',
    fechaViaje: '2026-11-05 06:30',
    asiento: '12',
    total: 4.50,
    estado: 'PENDIENTE'
  },
  {
    id: 'RES-1002',
    pasajero: 'Lucía Vargas',
    ruta: 'Ambato → Puyo',
    fechaViaje: '2026-11-06 08:00',
    asiento: '04',
    total: 3.75,
    estado: 'PAGO_EN_REVISION'
  },
  {
    id: 'RES-1003',
    pasajero: 'Mario Cifuentes',
    ruta: 'Quito → Guayaquil',
    fechaViaje: '2026-11-10 21:30',
    asiento: '15',
    total: 12.00,
    estado: 'CONFIRMADA'
  }
])
</script>

<template>
  <div class="admin-layout">
    <AdminSidebar rol="OFICINISTA" />

    <main class="admin-main">
      <header class="page-header">
        <div>
          <span class="module-pill">Módulo M08-A</span>
          <h1>Gestión de Reservas</h1>
          <p class="subtitle">
            Bandeja central para consultar reservas de clientes y sus estados de pago.
          </p>
        </div>
      </header>

      <section class="table-card">
        <table class="admin-table">
          <thead>
            <tr>
              <th>ID Reserva</th>
              <th>Pasajero</th>
              <th>Trayecto y Fecha</th>
              <th>Asiento</th>
              <th>Total</th>
              <th>Estado</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="reserva in reservas" :key="reserva.id">
              <td><strong>{{ reserva.id }}</strong></td>
              <td>{{ reserva.pasajero }}</td>
              <td>
                <div>{{ reserva.ruta }}</div>
                <small class="text-muted">{{ reserva.fechaViaje }}</small>
              </td>
              <td>Nº {{ reserva.asiento }}</td>
              <td>${{ reserva.total.toFixed(2) }}</td>
              <td>
                <span :class="{
                  'badge-warn': reserva.estado === 'PENDIENTE',
                  'badge-info': reserva.estado === 'PAGO_EN_REVISION',
                  'badge-ok': reserva.estado === 'CONFIRMADA'
                }">
                  {{ reserva.estado.replace(/_/g, ' ') }}
                </span>
              </td>
              <td>
                <button class="btn-sm" :disabled="reserva.estado !== 'PENDIENTE'">
                  Gestionar Pago
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </main>
  </div>
</template>

<style scoped>
.admin-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f8fafc;
  font-family: system-ui, -apple-system, sans-serif;
}
.admin-main {
  flex: 1;
  padding: 2rem;
}
.page-header {
  margin-bottom: 1.5rem;
}
.module-pill {
  font-size: 0.75rem;
  font-weight: 700;
  color: #0f766e;
  background: #ccfbf1;
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
.admin-table th, .admin-table td {
  padding: 0.9rem 1rem;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
}
.admin-table th {
  background: #f8fafc;
  color: #475569;
  font-size: 0.85rem;
}
.text-muted {
  color: #64748b;
}
.badge-warn {
  background: #fef3c7; color: #92400e; padding: 0.25rem 0.55rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
}
.badge-info {
  background: #e0f2fe; color: #0369a1; padding: 0.25rem 0.55rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
}
.badge-ok {
  background: #dcfce7; color: #166534; padding: 0.25rem 0.55rem; border-radius: 4px; font-size: 0.75rem; font-weight: 600;
}
.btn-sm {
  background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; padding: 0.35rem 0.65rem; border-radius: 5px; cursor: pointer;
}
.btn-sm:disabled {
  background: #f1f5f9; color: #94a3b8; border-color: #e2e8f0; cursor: not-allowed;
}
</style>