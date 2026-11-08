<script setup>
defineProps({ name: String, size: { type: Number, default: 20 } })
const trazos = {
  overview: 'M3 3h7v7H3z M14 3h7v7h-7z M3 14h7v7H3z M14 14h7v7h-7z',
  bus: 'M5 17V5a2 2 0 012-2h10a2 2 0 012 2v12H5z M5 10h14 M8 3v7 M16 3v7 M7 17v3 M17 17v3 M8 14h1 M15 14h1',
  route: 'M5 7a2 2 0 100-4 2 2 0 000 4z M19 21a2 2 0 100-4 2 2 0 000 4z M7 5h8a4 4 0 010 8H9a4 4 0 000 8h8',
  ticket: 'M3 6h18v4a2 2 0 000 4v4H3v-4a2 2 0 000-4V6z M15 6v3 M15 11v2 M15 15v3',
  wallet: 'M3 6h17v14H3V6z M3 6V4l14-2v4 M15 11h6v5h-6z',
  building: 'M4 21V3h12v18 M16 9h4v12 M8 7h4 M8 11h4 M8 15h4 M8 21v-3h4v3 M2 21h20',
  calendar: 'M4 5h16v16H4z M8 3v4 M16 3v4 M4 10h16 M8 14h2 M14 14h2 M8 18h2',
  scan: 'M8 3H3v5 M16 3h5v5 M21 16v5h-5 M8 21H3v-5 M3 12h18 M8 8h3v3H8z M14 14h3v3h-3z',
  settings: 'M12 3v3 M12 18v3 M3 12h3 M18 12h3 M5.6 5.6l2.1 2.1 M16.3 16.3l2.1 2.1 M5.6 18.4l2.1-2.1 M16.3 7.7l2.1-2.1 M16 12a4 4 0 11-8 0 4 4 0 018 0z',
  arrow: 'M5 12h14 M13 6l6 6-6 6',
  logout: 'M9 3H4v18h5 M10 12h11 M16 7l5 5-5 5',
  check: 'M5 12l4 4L19 6',
  search: 'M20 20l-5-5 M17 10a7 7 0 11-14 0 7 7 0 0114 0z',
  refresh: 'M20 7V3l-3 3a8 8 0 10 3 10 M20 7h-5',
  menu: 'M4 6h16 M4 12h16 M4 18h16',
}
</script>
<template><svg :width="size" :height="size" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path :d="trazos[name] || trazos.overview"/></svg></template>
