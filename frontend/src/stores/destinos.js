import { defineStore } from 'pinia'
import { request } from '../services/http'
export const useDestinosStore = defineStore('destinos', {
  state:()=>({ ciudades:[],conexiones:[],cargado:false,cargando:false,error:'' }),
  actions:{
    async cargar(){
      if(this.cargado || this.cargando)return
      this.cargando=true;this.error=''
      try{const datos=await request('/destinos');this.ciudades=datos.ciudades;this.conexiones=datos.conexiones;this.cargado=true}
      catch(e){this.error=e.message}finally{this.cargando=false}
    },
  },
})
