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
import { defineComponent, reactive, computed, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import { useRouter } from 'vue-router'
import { auth } from '../services/auth'
import { API_BASE_URL } from '../config'

interface Objectif {
  id_objectif: number
  type_objectif: string
  description: string
  date_debut: string
  date_fin: string
  statut: string
  id_utilisateur: number
}

interface FluxItem {
  id: number
  nom: string
  description: string
  comment?: string
  errors?: string[]
  fileSize?: string
  stats?: {
    rows: number
    exploitablePct: number
    lastRun: string
  }
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const state = reactive({
      valides: [] as FluxItem[],
      encours: [] as FluxItem[],
      refuses: [] as FluxItem[]
    })
    const router = useRouter()

    const normalizeStatus = (status: string) => {
      const s = (status || '').toLowerCase()
      if (s.includes('term') || s.includes('valid')) return 'valide'
      if (s.includes('cours') || s.includes('actif')) return 'encours'
      if (s.includes('refus') || s.includes('rejet')) return 'refuse'
      return 'refuse'
    }

    const mapObjectifToFlux = (objectif: Objectif): FluxItem => ({
      id: objectif.id_objectif,
      nom: `Objectif ${objectif.type_objectif}`,
      description: objectif.description,
      stats: {
        rows: 1,
        exploitablePct: normalizeStatus(objectif.statut) === 'valide' ? 100 : normalizeStatus(objectif.statut) === 'encours' ? 70 : 30,
        lastRun: objectif.date_fin || objectif.date_debut
      },
      fileSize: '-',
      comment: normalizeStatus(objectif.statut) === 'refuse' ? `Statut: ${objectif.statut}` : ''
    })

    async function fetchObjectifs() {
      const token = auth.getToken()
      if (!token) return

      const response = await fetch(`${API_BASE_URL}/objectifs/`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) return

      const objectifs = (await response.json()) as Objectif[]
      const mapped = objectifs.map(mapObjectifToFlux)

      state.valides = mapped.filter(item => {
        const target = objectifs.find(o => o.id_objectif === item.id)
        return target ? normalizeStatus(target.statut) === 'valide' : false
      })

      state.encours = mapped.filter(item => {
        const target = objectifs.find(o => o.id_objectif === item.id)
        return target ? normalizeStatus(target.statut) === 'encours' : false
      })

      state.refuses = mapped.filter(item => {
        const target = objectifs.find(o => o.id_objectif === item.id)
        return target ? normalizeStatus(target.statut) === 'refuse' : false
      })
    }

    const recentValides = computed(() => {
      return [...state.valides].slice(-5).reverse()
    })

    onMounted(() => {
      fetchObjectifs()
    })

    return { ...state, recentValides, router }
  }
})
</script>

<style scoped>
.open-btn{background:#0078d4;color:#fff;padding:6px 10px;border-radius:6px;text-decoration:none}
.open-btn:hover{opacity:0.9}
.clickable-item{cursor:pointer;padding:10px;border-radius:6px}
.clickable-item:hover{background:#f6f9ff}
</style>
