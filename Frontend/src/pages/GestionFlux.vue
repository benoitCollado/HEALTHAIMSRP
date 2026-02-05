<template>
  <div class="canvas">
    <Navbar title="Gestion des flux" />
    <div style="padding:24px;max-width:1200px;width:100%;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>En cours</h3>
        <ul>
          <li v-for="item in encours" :key="item.id" class="clickable-item" @click="router.push(`/flux/${item.id}`)" style="margin-bottom:12px;display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-weight:600">{{ item.id }} - {{ item.nom }}</div>
              <div style="font-size:12px;color:#666">{{ item.description }}</div>
            </div>
            <div style="display:flex;align-items:center;gap:12px">
              <div style="text-align:right;font-size:13px;color:#333">
                <div>{{ item.fileSize || '-' }}</div>
                <div style="font-size:12px;color:#666">{{ item.stats?.rows || '-' }} lignes</div>
              </div>
            </div>
          </li>
        </ul>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Validés récemment</h3>
        <ul>
          <li v-for="item in recentValides" :key="item.id" class="clickable-item" @click="router.push(`/flux/${item.id}`)" style="margin-bottom:8px;display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-weight:600">{{ item.id }} - {{ item.nom }}</div>
              <div v-if="item.comment" style="font-size:12px;color:#666">Commentaire: {{ item.comment }}</div>
            </div>
            <div style="text-align:right">
              <div>{{ item.fileSize || '-' }}</div>
              <div style="font-size:12px;color:#666">{{ item.stats?.rows || '-' }} lignes</div>
            </div>
          </li>
        </ul>
      </section>

      <section style="grid-column:1 / -1;background:#fff;padding:16px;border-radius:8px;">
        <h3>Refusés</h3>
        <ul>
          <li v-for="item in refuses" :key="item.id" class="clickable-item" @click="router.push(`/flux/${item.id}`)" style="margin-bottom:12px;display:flex;align-items:center;justify-content:space-between">
            <div>
              <div style="font-weight:600">{{ item.id }} - {{ item.nom }}</div>
              <div v-if="item.comment" style="font-size:12px;color:#666">Commentaire: {{ item.comment }}</div>
              <div v-if="item.errors" style="font-size:12px;color:#a00">Erreurs: {{ item.errors.join('; ') }}</div>
            </div>
            <div style="text-align:right">
              <div>{{ item.fileSize || '-' }}</div>
              <div style="font-size:12px;color:#666">{{ item.stats?.rows || '-' }} lignes</div>
            </div>
          </li>
        </ul>
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import { mockFluxData } from '../data/mockApiData'
import { useRouter } from 'vue-router'

export default defineComponent({
  components: { Navbar },
  setup() {
    // work on local reactive copies
    const state = reactive({
      valides: [...mockFluxData.valides],
      encours: [...mockFluxData.encours],
      refuses: [...mockFluxData.refuses]
    })
    const router = useRouter()

    const recentValides = computed(() => {
      return state.valides.slice(-5).reverse()
    })

    function refreshLists() {
      state.valides = [...mockFluxData.valides]
      state.encours = [...mockFluxData.encours]
      state.refuses = [...mockFluxData.refuses]
    }

    return { ...state, recentValides, refreshLists, router }
  }
})
</script>

<style scoped>
.open-btn{background:#0078d4;color:#fff;padding:6px 10px;border-radius:6px;text-decoration:none}
.open-btn:hover{opacity:0.9}
.clickable-item{cursor:pointer;padding:10px;border-radius:6px}
.clickable-item:hover{background:#f6f9ff}
</style>
