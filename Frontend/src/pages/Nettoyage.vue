<template>
  <div class="canvas">
    <Navbar title="Nettoyage" />
    <div style="padding:24px;max-width:900px;width:100%;margin:0 auto">
      <div style="background:#fff;padding:16px;border-radius:8px;">
      <h3>Nettoyage</h3>
      <p>Liste des éléments nécessitant un nettoyage / reconciliation.</p>
      <div v-if="loading" style="padding:12px;background:#f5f7fa;border-radius:6px;color:#2f4b66;margin-bottom:12px">
        Chargement des éléments depuis la base...
      </div>
      <div v-if="error" style="padding:12px;background:#ffebee;border-radius:6px;color:#c62828;margin-bottom:12px">
        {{ error }}
      </div>
      <table v-if="rows.length" style="width:100%;border-collapse:collapse">
        <thead><tr><th style="text-align:left">ID</th><th>Type</th><th></th></tr></thead>
        <tbody>
          <tr v-for="r in rows" :key="r.id">
            <td>{{ r.id }}</td>
            <td>{{ r.type }}</td>
            <td><button @click="clean(r)">Nettoyer</button></td>
          </tr>
        </tbody>
      </table>
      <div v-else-if="!loading" style="padding:12px;background:#f5f7fa;border-radius:6px;color:#666">
        Aucun élément à nettoyer pour le moment.
      </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, reactive, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import { auth } from '../services/auth'

interface NettoyageRow {
  id: string
  type: string
}

interface Objectif {
  id_objectif: number
  type_objectif: string
  description: string
  date_debut: string
  date_fin: string
  statut: string
}

interface Consommation {
  id_consommation: number
  calories_calculees: number
  quantite_g: number
}

interface Metrique {
  id_metrique: number
  date_mesure: string
  poids_kg?: number
  frequence_cardiaque?: number
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const state = reactive({
      rows: [] as NettoyageRow[],
      loading: false,
      error: ''
    })

    const fetchJson = async (endpoint: string, token: string) => {
      const response = await fetch(`http://localhost:8000${endpoint}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        throw new Error(`Erreur ${response.status} sur ${endpoint}`)
      }

      return response.json()
    }

    const loadRows = async () => {
      const token = auth.getToken()
      if (!token) {
        state.error = 'Token absent, impossible de charger les données de nettoyage.'
        return
      }

      try {
        state.loading = true
        state.error = ''

        const [objectifs, consommations, metriques] = await Promise.all([
          fetchJson('/objectifs/', token) as Promise<Objectif[]>,
          fetchJson('/consommations/', token) as Promise<Consommation[]>,
          fetchJson('/metriques-sante/', token) as Promise<Metrique[]>
        ])

        const rows: NettoyageRow[] = []

        objectifs.forEach((objectif) => {
          const status = (objectif.statut || '').toLowerCase()
          if (status.includes('refus') || status.includes('rejet')) {
            rows.push({
              id: `OBJ-${objectif.id_objectif}`,
              type: `Objectif refusé (${objectif.type_objectif})`
            })
          }

          if (!objectif.description || !objectif.description.trim()) {
            rows.push({
              id: `OBJ-${objectif.id_objectif}-DESC`,
              type: 'Objectif sans description'
            })
          }
        })

        consommations.forEach((consommation) => {
          if (consommation.calories_calculees <= 0 || consommation.quantite_g <= 0) {
            rows.push({
              id: `CONSO-${consommation.id_consommation}`,
              type: 'Consommation avec calories/quantité invalides'
            })
          }
        })

        metriques.forEach((metrique) => {
          const heartRate = metrique.frequence_cardiaque ?? 0
          const poids = metrique.poids_kg ?? 0
          if (heartRate > 220 || heartRate < 30) {
            rows.push({
              id: `MET-${metrique.id_metrique}-FC`,
              type: 'Métrique avec fréquence cardiaque incohérente'
            })
          }
          if (poids > 350 || poids < 20) {
            rows.push({
              id: `MET-${metrique.id_metrique}-POIDS`,
              type: 'Métrique avec poids incohérent'
            })
          }
        })

        state.rows = rows
      } catch (err) {
        state.error = err instanceof Error ? err.message : 'Erreur lors du chargement nettoyage.'
      } finally {
        state.loading = false
      }
    }
    
    function clean(r: NettoyageRow) {
      state.rows = state.rows.filter((x) => x.id !== r.id)
    }

    onMounted(() => {
      loadRows()
    })

    return { ...state, clean }
  }
})
</script>
