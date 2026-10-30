<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
const router = useRouter()
const hoy = new Date().toLocaleDateString('en-CA')
const busqueda = reactive({ origen: '', destino: '', fecha: '' })
const error = ref('')
function buscar() {
  error.value = ''
  if (!busqueda.origen || !busqueda.destino || !busqueda.fecha) {
    error.value = 'Completa el origen, destino y fecha para continuar.'
    return
  }
  if (busqueda.origen.trim().toLowerCase() === busqueda.destino.trim().toLowerCase()) {
    error.value = 'El origen y el destino deben ser diferentes.'
    return
  }
  router.push({ name: 'viajes', query: { origen: busqueda.origen, destino: busqueda.destino, fecha: busqueda.fecha } })
}
</script>

<template>
  <div class="home">
    <section class="hero">
      <div class="hero-art" aria-hidden="true"><div class="art-sun"></div><div class="art-road"></div><div class="art-mountain mountain-one"></div><div class="art-mountain mountain-two"></div><span class="hero-art-label">ECUADOR · EN MOVIMIENTO</span></div>
      <div class="hero-content page-container">
        <span class="eyebrow"><span class="eyebrow-dot"></span> VIAJAR NUNCA FUE TAN SENCILLO</span>
        <h1>Tu próximo destino<br />está <em>más cerca.</em></h1>
      </div>
    </section>

    <section class="search-wrap page-container" aria-labelledby="search-title">
      <div class="search-card">
        <div class="search-header"><div><span class="section-kicker">PLANIFICA TU VIAJE</span><h2 id="search-title">¿A dónde vamos hoy?</h2></div><span class="search-caption">Explora las rutas disponibles</span></div>
        <form class="search-form" @submit.prevent="buscar">
          <label class="field"><span>Origen</span><div class="input-with-icon"><span aria-hidden="true">◎</span><input v-model.trim="busqueda.origen" name="origen" autocomplete="off" placeholder="Ciudad de salida" required /></div></label>
          <label class="field"><span>Destino</span><div class="input-with-icon"><span aria-hidden="true">⌖</span><input v-model.trim="busqueda.destino" name="destino" autocomplete="off" placeholder="¿A dónde viajas?" required /></div></label>
          <label class="field"><span>Fecha de viaje</span><div class="input-with-icon"><span aria-hidden="true">▦</span><input v-model="busqueda.fecha" name="fecha" type="date" :min="hoy" required /></div></label>
          <button class="search-submit" type="submit">Buscar viajes <span aria-hidden="true">→</span></button>
        </form>
        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      </div>
    </section>

    <section class="benefits page-container" aria-labelledby="benefits-title">
      <div class="section-heading"><div><span class="section-kicker">VIAJA CON CONFIANZA</span><h2 id="benefits-title">Tu viaje, de principio a fin</h2></div><p>Diseñamos una experiencia simple para ayudarte a planificar tu siguiente aventura.</p></div>
      <div class="benefit-grid">
        <article class="benefit-card"><span class="benefit-icon">⌕</span><span class="benefit-index">01 / EXPLORA</span><h3>Encuentra tu ruta</h3><p>Explora opciones entre ciudades y provincias desde un mismo lugar.</p></article>
        <article class="benefit-card"><span class="benefit-icon">▤</span><span class="benefit-index">02 / ORGANIZA</span><h3>Planifica a tu ritmo</h3><p>Ten a mano la información necesaria para decidir cómo viajar.</p></article>
        <article class="benefit-card"><span class="benefit-icon">✓</span><span class="benefit-index">03 / VIAJA</span><h3>Disfruta el camino</h3><p>Una experiencia pensada para que lo importante sea tu destino.</p></article>
      </div>
    </section>
    <section class="bottom-cta page-container"><div><span class="section-kicker">COMIENZA AQUÍ</span><h2>El Ecuador te espera.</h2><p>Empieza explorando nuestras rutas interprovinciales.</p></div><RouterLink class="button-white" to="/viajes">Explorar viajes <span aria-hidden="true">→</span></RouterLink></section>
  </div>
</template>
