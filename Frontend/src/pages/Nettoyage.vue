<template>
  <div class="canvas">
    <Navbar title="Nettoyage" />
    <div style="padding:24px;max-width:900px;width:100%;margin:0 auto">
      <div style="background:#fff;padding:16px;border-radius:8px;">
      <h3>Nettoyage</h3>
      <p>Liste des éléments nécessitant un nettoyage / reconciliation.</p>
      <table style="width:100%;border-collapse:collapse">
        <thead><tr><th style="text-align:left">ID</th><th>Type</th><th></th></tr></thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.type }}</td>
            <td><button @click="clean(r)">Nettoyer</button></td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue'
import Navbar from '../components/Navbar.vue'

export default defineComponent({
  components: { Navbar },
  setup() {
    const state = reactive({ rows: [ {id:'N-1', type:'Incohérence date'}, {id:'N-2', type:'Doublon'}, {id:'N-3', type:'Manque info'} ] })
    function clean(r:any){
      state.rows = state.rows.filter((x:any)=>x.id!==r.id)
    }
    return { ...state, clean }
  }
})
</script>
