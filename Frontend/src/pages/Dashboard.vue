<template>
  <div class="canvas">
    <Navbar title="Dashboard" />
    <div style="padding:24px;max-width:1100px;width:100%;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <section v-if="error" style="grid-column:1 / -1;background:#fff3f3;padding:16px;border-radius:8px;color:#b42318;">
        {{ error }}
      </section>

      <section v-if="loading" style="grid-column:1 / -1;background:#fff;padding:16px;border-radius:8px;">
        Chargement des données globales...
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Top 3 exercices</h3>
        <div v-if="!topExercises.length" style="color:#667085">Aucune activité disponible.</div>
        <div v-else>
          <div v-for="item in topExercises" :key="item.label" style="margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:14px">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
            <div style="height:10px;background:#e9eef5;border-radius:999px;overflow:hidden">
              <div :style="`height:100%;width:${exerciseBarPercent(item.value)}%;background:#5294E2`"></div>
            </div>
          </div>
        </div>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Top 3 aliments</h3>
        <div v-if="!topAliments.length" style="color:#667085">Aucune consommation disponible.</div>
        <div v-else>
          <div v-for="item in topAliments" :key="item.label" style="margin-bottom:12px">
            <div style="display:flex;justify-content:space-between;margin-bottom:4px;font-size:14px">
              <span>{{ item.label }}</span>
              <strong>{{ item.value }}</strong>
            </div>
            <div style="height:10px;background:#f8eddb;border-radius:999px;overflow:hidden">
              <div :style="`height:100%;width:${foodBarPercent(item.value)}%;background:#E79A0F`"></div>
            </div>
          </div>
        </div>
      </section>

      <section style="grid-column:1 / -1;background:#fff;padding:16px;border-radius:8px;">
        <h3>Moyennes utilisateurs</h3>
        <div style="display:flex;gap:12px">
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Taille moyenne<br/><strong>{{ stats.tailleMoyenne }} cm</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Poids moyen<br/><strong>{{ stats.poidsMoyen }} kg</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Âge moyen<br/><strong>{{ stats.ageMoyen }} ans</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Exos / utilisateur<br/><strong>{{ stats.exosMoyensParUtilisateur }}</strong></div>
        </div>
      </section>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import { auth } from '../services/auth'
import { API_BASE_URL } from '../config'

interface Activite {
  id_exercice: number
}

interface Consommation {
  id_aliment: number
}

interface Exercice {
  id_exercice: number
  nom_exercice: string
}

interface Aliment {
  id_aliment: number
  nom_aliment: string
}

interface Utilisateur {
  id_utilisateur: number
  age: number
  taille_cm: number
  poids_kg: number
}

interface RankedItem {
  label: string
  value: number
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const loading = ref(false)
    const error = ref('')
    const topExercises = ref<RankedItem[]>([])
    const topAliments = ref<RankedItem[]>([])
    const stats = ref({
      tailleMoyenne: '0.0',
      poidsMoyen: '0.0',
      ageMoyen: '0.0',
      exosMoyensParUtilisateur: '0.00'
    })

    const fetchJson = async (endpoint: string, token: string) => {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
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

    const toTopThree = (countMap: Record<number, number>, labelMap: Map<number, string>): RankedItem[] => {
      return Object.entries(countMap)
        .map(([id, value]) => ({
          label: labelMap.get(Number(id)) || `ID ${id}`,
          value
        }))
        .sort((a, b) => b.value - a.value)
        .slice(0, 3)
    }

    const exerciseMax = computed(() => Math.max(...topExercises.value.map(item => item.value), 1))
    const foodMax = computed(() => Math.max(...topAliments.value.map(item => item.value), 1))

    const exerciseBarPercent = (value: number) => Math.max(5, Math.round((value / exerciseMax.value) * 100))
    const foodBarPercent = (value: number) => Math.max(5, Math.round((value / foodMax.value) * 100))

    onMounted(() => {
      const loadDashboard = async () => {
        const token = auth.getToken()
        if (!token) return

        try {
          loading.value = true
          error.value = ''

          const [activites, utilisateurs, consommations, exercices, aliments] = await Promise.all([
            fetchJson('/activites/', token) as Promise<Activite[]>,
            fetchJson('/utilisateurs/', token) as Promise<Utilisateur[]>,
            fetchJson('/consommations/', token) as Promise<Consommation[]>,
            fetchJson('/exercices/', token) as Promise<Exercice[]>,
            fetchJson('/aliments/', token) as Promise<Aliment[]>
          ])

          const exerciceNameById = new Map(exercices.map(item => [item.id_exercice, item.nom_exercice]))
          const alimentNameById = new Map(aliments.map(item => [item.id_aliment, item.nom_aliment]))

          const exerciceCountMap = activites.reduce((acc: Record<number, number>, activity) => {
            acc[activity.id_exercice] = (acc[activity.id_exercice] || 0) + 1
            return acc
          }, {})

          const alimentCountMap = consommations.reduce((acc: Record<number, number>, consommation) => {
            acc[consommation.id_aliment] = (acc[consommation.id_aliment] || 0) + 1
            return acc
          }, {})

          topExercises.value = toTopThree(exerciceCountMap, exerciceNameById)
          topAliments.value = toTopThree(alimentCountMap, alimentNameById)

          const userCount = utilisateurs.length
          const totalHeight = utilisateurs.reduce((sum, user) => sum + (user.taille_cm || 0), 0)
          const totalWeight = utilisateurs.reduce((sum, user) => sum + (user.poids_kg || 0), 0)
          const totalAge = utilisateurs.reduce((sum, user) => sum + (user.age || 0), 0)

          stats.value = {
            tailleMoyenne: userCount ? (totalHeight / userCount).toFixed(1) : '0.0',
            poidsMoyen: userCount ? (totalWeight / userCount).toFixed(1) : '0.0',
            ageMoyen: userCount ? (totalAge / userCount).toFixed(1) : '0.0',
            exosMoyensParUtilisateur: userCount ? (activites.length / userCount).toFixed(2) : '0.00'
          }
        } catch {
          topExercises.value = []
          topAliments.value = []
          stats.value = {
            tailleMoyenne: '0.0',
            poidsMoyen: '0.0',
            ageMoyen: '0.0',
            exosMoyensParUtilisateur: '0.00'
          }
          error.value = 'Impossible de charger les données globales du dashboard.'
        } finally {
          loading.value = false
        }
      }

      loadDashboard()
    })

    return { loading, error, topExercises, topAliments, stats, exerciseBarPercent, foodBarPercent }
  }
})
</script>
