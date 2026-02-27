<template>
  <div class="canvas">
    <Navbar title="Dashboard" />
    <div style="padding:24px;max-width:1100px;width:100%;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Activité récente (tous utilisateurs)</h3>
        <svg :width="chartW" :height="chartH">
          <g v-for="(v,i) in data1" :key="i">
            <rect :x="10 + i*(barW+barGap)" :y="chartH - 10 - (v*scale)" :width="barW" :height="v*scale" fill="#5294E2" />
          </g>
        </svg>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Taux objectifs terminés (global)</h3>
        <svg :width="chartW" :height="chartH">
          <polyline :points="linePoints" fill="none" stroke="#E79A0F" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
        </svg>
      </section>

      <section style="grid-column:1 / -1;background:#fff;padding:16px;border-radius:8px;">
        <h3>Résumé global</h3>
        <div style="display:flex;gap:12px">
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Utilisateurs<br/><strong>{{ summary.utilisateurs }}</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Activités<br/><strong>{{ summary.activites }}</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Calories consommées<br/><strong>{{ summary.caloriesConsommees }}</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Objectifs terminés<br/><strong>{{ summary.valides }}</strong></div>
        </div>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Répartition des objectifs</h3>
        <svg :width="pieW" :height="pieH" viewBox="0 0 200 200">
          <circle cx="100" cy="100" r="80" fill="none" stroke="#ddd" stroke-width="40" />
          <path v-for="(slice, idx) in pieSlices" :key="idx" :d="slice.d" :fill="slice.color" />
          <text x="100" y="100" text-anchor="middle" dominant-baseline="middle" font-weight="bold" font-size="20">{{ totalObjectives }}</text>
        </svg>
        <div style="margin-top:12px;font-size:12px">
          <div v-for="t in typeData" :key="t.label" style="display:flex;align-items:center;gap:6px;margin-bottom:4px">
            <span :style="`background:${t.color};display:inline-block;width:12px;height:12px;border-radius:2px`"></span>
            <span>{{ t.label }}: {{ t.value }}</span>
          </div>
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
  date_activite: string
  calories_depensees: number
}

interface Objectif {
  type_objectif: string
  date_debut: string
  statut: string
}

interface Consommation {
  calories_calculees?: number
}

interface Metrique {
  id_utilisateur: number
}

interface Utilisateur {
  id_utilisateur: number
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const chartW = 480
    const chartH = 180
    const barW = 32
    const barGap = 8
    const pieW = 160
    const pieH = 160

    const data1 = ref<number[]>([])
    const data2 = ref<number[]>([])
    const summary = ref({
      valides: 0,
      enCours: 0,
      refuses: 0,
      utilisateurs: 0,
      activites: 0,
      caloriesConsommees: 0
    })
    const objectifTypeCounts = ref<Record<string, number>>({})
    const totalObjectives = ref(0)

    const maxV = computed(() => Math.max(...data1.value, 1))
    const scale = computed(() => (chartH - 20) / maxV.value)

    const colors = ['#5294E2', '#E79A0F', '#27AE60', '#E74C3C', '#8E44AD', '#16A085']

    const normalizeStatus = (status: string) => {
      const s = (status || '').toLowerCase()
      if (s.includes('term')) return 'termine'
      if (s.includes('cours') || s.includes('actif')) return 'encours'
      return 'autre'
    }

    const getLastDays = (count: number) => {
      const days: Date[] = []
      const now = new Date()
      for (let i = count - 1; i >= 0; i--) {
        const d = new Date(now)
        d.setDate(now.getDate() - i)
        d.setHours(0, 0, 0, 0)
        days.push(d)
      }
      return days
    }

    const sameDay = (a: Date, b: Date) => {
      return a.getFullYear() === b.getFullYear() && a.getMonth() === b.getMonth() && a.getDate() === b.getDate()
    }

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

    onMounted(() => {
      const loadDashboard = async () => {
        const token = auth.getToken()
        if (!token) return

        try {
          const [activites, objectifs, utilisateurs, consommations, metriques] = await Promise.all([
            fetchJson('/activites/', token) as Promise<Activite[]>,
            fetchJson('/objectifs/', token) as Promise<Objectif[]>,
            fetchJson('/utilisateurs/', token) as Promise<Utilisateur[]>,
            fetchJson('/consommations/', token) as Promise<Consommation[]>,
            fetchJson('/metriques-sante/', token) as Promise<Metrique[]>
          ])

          const last7Days = getLastDays(7)

          data1.value = last7Days.map((day) => {
            return Math.round(
              activites
                .filter((a) => {
                  const d = new Date(a.date_activite)
                  return sameDay(d, day)
                })
                .reduce((sum, a) => sum + (a.calories_depensees || 0), 0)
            )
          })

          const objectifsByStatus = objectifs.reduce(
            (acc, objectif) => {
              const normalized = normalizeStatus(objectif.statut)
              acc[normalized] += 1
              return acc
            },
            { termine: 0, encours: 0, autre: 0 }
          )

          summary.value = {
            valides: objectifsByStatus.termine,
            enCours: objectifsByStatus.encours,
            refuses: objectifsByStatus.autre,
            utilisateurs: utilisateurs.length,
            activites: activites.length,
            caloriesConsommees: Math.round(consommations.reduce((sum, c) => sum + (c.calories_calculees || 0), 0))
          }

          data2.value = last7Days.map((day) => {
            const started = objectifs.filter((o) => new Date(o.date_debut).getTime() <= day.getTime())
            if (!started.length) return 0
            const completed = started.filter((o) => normalizeStatus(o.statut) === 'termine').length
            return Math.round((completed / started.length) * 100)
          })

          const typeCounts = objectifs.reduce((acc: Record<string, number>, objectif) => {
            const label = objectif.type_objectif || 'Non défini'
            acc[label] = (acc[label] || 0) + 1
            return acc
          }, {})

          objectifTypeCounts.value = typeCounts
          totalObjectives.value = objectifs.length

          if (!objectifs.length) {
            totalObjectives.value = metriques.length ? new Set(metriques.map(m => m.id_utilisateur)).size : utilisateurs.length
          }
        } catch {
          data1.value = [0, 0, 0, 0, 0, 0, 0]
          data2.value = [0, 0, 0, 0, 0, 0, 0]
          summary.value = { valides: 0, enCours: 0, refuses: 0, utilisateurs: 0, activites: 0, caloriesConsommees: 0 }
          objectifTypeCounts.value = {}
          totalObjectives.value = 0
        }
      }

      loadDashboard()
    })

    const typeData = computed(() => {
      const entries = Object.entries(objectifTypeCounts.value)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 6)

      return entries.map(([label, value], idx) => ({
        label,
        value,
        color: colors[idx % colors.length]
      }))
    })

    function polarToCartesian(centerX: number, centerY: number, radius: number, angleInDegrees: number) {
      const angleInRadians = (angleInDegrees - 90) * Math.PI / 180.0
      return {
        x: centerX + (radius * Math.cos(angleInRadians)),
        y: centerY + (radius * Math.sin(angleInRadians))
      }
    }

    function describeArc(x: number, y: number, radius: number, startAngle: number, endAngle: number) {
      const start = polarToCartesian(x, y, radius, endAngle)
      const end = polarToCartesian(x, y, radius, startAngle)
      const largeArc = endAngle - startAngle <= 180 ? "0" : "1"
      return [
        "M", x, y,
        "L", start.x, start.y,
        "A", radius, radius, 0, largeArc, 0, end.x, end.y,
        "Z"
      ].join(" ")
    }

    const pieSlices = computed(() => {
      const total = typeData.value.reduce((sum, type) => sum + type.value, 0) || 1
      const center = 100
      const radius = 80
      let startAngle = 0
      const slices: any[] = []

      for (const t of typeData.value) {
        const percentage = (t.value / total) * 100
        const endAngle = startAngle + (percentage * 3.6)
        slices.push({
          d: describeArc(center, center, radius, startAngle, endAngle),
          color: t.color
        })
        startAngle = endAngle
      }

      return slices
    })

    const linePoints = computed(() => {
      const max2 = Math.max(...data2.value, 1)
      const s = (chartH - 20) / max2
      return data2.value.map((v, i) => `${10 + i * (barW + barGap)} , ${chartH - 10 - v * s}`).join(' ')
    })

    return { data1, chartW, chartH, barW, barGap, scale, linePoints, summary, pieW, pieH, typeData, pieSlices, totalObjectives }
  }
})
</script>
