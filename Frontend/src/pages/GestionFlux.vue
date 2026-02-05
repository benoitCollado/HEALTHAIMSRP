<template>
  <div class="canvas">
    <Navbar title="Gestion des flux" />
    <div style="padding:24px;max-width:1100px;width:100%;margin:0 auto;display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px">
      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Validés</h3>
        <ul>
          <li v-for="item in valides" :key="item.id">{{ item.id }} - {{ item.nom }}</li>
        </ul>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>En cours</h3>
        <ul>
          <li v-for="item in encours" :key="item.id">
            {{ item.id }} - {{ item.nom }}
            <div style="margin-top:6px"><button @click="valider(item)">Valider</button> <button @click="refuser(item)">Refuser</button></div>
          </li>
        </ul>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Refusés</h3>
        <ul>
          <li v-for="item in refuses" :key="item.id">{{ item.id }} - {{ item.nom }}</li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive } from 'vue'
import Navbar from '../components/Navbar.vue'

export default defineComponent({
  components: { Navbar },
  setup() {
    const state = reactive({
      valides: [ {id: 'F-101', nom: 'Flux A'}, {id:'F-102', nom:'Flux B'} ],
      encours: [ {id: 'F-201', nom: 'Flux C'}, {id:'F-202', nom:'Flux D'} ],
      refuses: [ {id: 'F-301', nom: 'Flux X'} ]
    })

    function valider(item: any) {
      state.valides.push(item)
      state.encours = state.encours.filter((i:any)=>i.id!==item.id)
    }
    function refuser(item: any) {
      state.refuses.push(item)
      state.encours = state.encours.filter((i:any)=>i.id!==item.id)
    }

    return { ...state, valider, refuser }
  }
})
</script>
