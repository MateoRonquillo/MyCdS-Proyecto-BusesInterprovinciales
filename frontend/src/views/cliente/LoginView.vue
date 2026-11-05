<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const correo = ref('')
const password = ref('')
const verClave = ref(false)
const cargando = ref(false)
const error = ref('')

async function enviar() {
  error.value = ''
  if (!correo.value.trim() || !password.value) {
    error.value = 'Ingresa tu correo y tu contraseña.'
    return
  }
  cargando.value = true
  try {
    await auth.login(correo.value.trim(), password.value)
    router.push(route.query.redirect || auth.rutaInicio)
  } catch (e) {
    error.value = e.message
  } finally {
    cargando.value = false
  }
}
</script>

<template>
  <section class="login-pagina">
    <form class="login-tarjeta" @submit.prevent="enviar" novalidate>
      <span class="login-icono" aria-hidden="true">↗</span>
      <h1>Iniciar sesión</h1>
      <p class="login-sub">Ingresa para comprar y gestionar tus pasajes.</p>

      <p v-if="error" class="login-error" role="alert">{{ error }}</p>

      <label for="correo">Correo electrónico</label>
      <input
        id="correo"
        v-model="correo"
        type="email"
        autocomplete="email"
        placeholder="tucorreo@ejemplo.com"
        :disabled="cargando"
      />

      <label for="password">Contraseña</label>
      <div class="campo-clave">
        <input
          id="password"
          v-model="password"
          :type="verClave ? 'text' : 'password'"
          autocomplete="current-password"
          placeholder="Tu contraseña"
          :disabled="cargando"
        />
        <button type="button" class="ver-clave" @click="verClave = !verClave">
          {{ verClave ? 'Ocultar' : 'Ver' }}
        </button>
      </div>

      <button class="login-boton" type="submit" :disabled="cargando">
        {{ cargando ? 'Ingresando…' : 'Ingresar' }}
      </button>
    </form>
  </section>
</template>

<style scoped>
.login-pagina {
  display: grid;
  place-items: center;
  padding: 56px 22px;
  min-height: 60vh;
}
.login-tarjeta {
  width: min(420px, 100%);
  background: var(--color-superficie);
  border: 1px solid var(--color-borde);
  border-radius: var(--radio);
  padding: 34px 30px;
  box-shadow: 0 10px 40px #0e37401a;
}
.login-icono {
  display: grid;
  place-items: center;
  width: 46px;
  height: 46px;
  margin-bottom: 14px;
  border-radius: 13px;
  background: var(--color-azul);
  color: #fff;
  font-size: 28px;
  font-weight: 800;
}
h1 {
  margin-bottom: 4px;
  color: var(--color-navy);
  font-size: 26px;
}
.login-sub {
  color: var(--color-texto-suave);
  margin-bottom: 20px;
}
label {
  display: block;
  font-weight: 600;
  font-size: 14px;
  margin: 14px 0 6px;
}
input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--color-borde);
  border-radius: 10px;
  background: #fff;
  color: var(--color-texto);
}
input:focus {
  outline: 2px solid var(--color-azul-vivo);
  border-color: transparent;
}
.campo-clave {
  position: relative;
}
.campo-clave input {
  padding-right: 76px;
}
.ver-clave {
  position: absolute;
  right: 8px;
  top: 50%;
  transform: translateY(-50%);
  border: 0;
  background: none;
  color: var(--color-azul);
  font-weight: 600;
  font-size: 13px;
}
.login-boton {
  width: 100%;
  margin-top: 24px;
  padding: 13px;
  border: 0;
  border-radius: 10px;
  background: var(--color-navy);
  color: #fff;
  font-weight: 700;
}
.login-boton:hover:not(:disabled) {
  background: var(--color-navy-hover);
}
.login-boton:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.login-error {
  background: #fdecec;
  color: #a12626;
  border: 1px solid #f3c2c2;
  padding: 10px 12px;
  border-radius: 10px;
  font-size: 14px;
  margin-bottom: 4px;
}
</style>