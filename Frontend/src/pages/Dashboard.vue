<template>
  <div class="canvas">
    <Navbar title="Dashboard" />
    <div style="padding:24px;max-width:1100px;width:100%;margin:0 auto;display:grid;grid-template-columns:1fr 1fr;gap:16px">
      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Activité récente</h3>
        <svg :width="chartW" :height="chartH">
          <g v-for="(v,i) in data1" :key="i">
            <rect :x="10 + i*(barW+barGap)" :y="chartH - 10 - (v*scale)" :width="barW" :height="v*scale" fill="#5294E2" />
          </g>
        </svg>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Taux de validation</h3>
        <svg :width="chartW" :height="chartH">
          <polyline :points="linePoints" fill="none" stroke="#E79A0F" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" />
        </svg>
      </section>

      <section style="grid-column:1 / -1;background:#fff;padding:16px;border-radius:8px;">
        <h3>Résumé</h3>
        <div style="display:flex;gap:12px">
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Validés<br/><strong>{{summary.valides}}</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">En cours<br/><strong>{{summary.enCours}}</strong></div>
          <div style="flex:1;padding:12px;background:#f7f9fc;border-radius:6px">Refusés<br/><strong>{{summary.refuses}}</strong></div>
        </div>
      </section>

      <section style="background:#fff;padding:16px;border-radius:8px;">
        <h3>Répartition par type</h3>
        <svg :width="pieW" :height="pieH" viewBox="0 0 200 200">
          <circle cx="100" cy="100" r="80" fill="none" stroke="#ddd" stroke-width="40" />
          <path v-for="(slice, idx) in pieSlices" :key="idx" :d="slice.d" :fill="slice.color" />
          <text x="100" y="100" text-anchor="middle" dominant-baseline="middle" font-weight="bold" font-size="20">{{ apiData.total }}</text>
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

export default defineComponent({
  components: { Navbar },
  setup() {
    const chartW = 480
    const chartH = 180
    const barW = 32
    const barGap = 8
    const pieW = 160
    const pieH = 160

    // Toutes les données viennent du faux API
    const data1 = ref<number[]>([])
    const data2 = ref<number[]>([])
    const summary = ref({ valides: 0, enCours: 0, refuses: 0 })
    const apiData = ref({ type_a: 0, type_b: 0, type_c: 0, type_d: 0, total: 0 })

    const maxV = computed(() => Math.max(...data1.value, 1))
    const scale = computed(() => (chartH - 20) / maxV.value)

    onMounted(() => {
      // GROS APPEL API FAKE - simule la réponse complète du backend
      const fakeApiResponse = {
        // Activité récente par jour (bar chart)
        activity: [45, 38, 52, 41, 67, 55, 73],
        activityLabels: ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'],
        activityTotal: 371,
        
        // Taux de validation dans le temps (line chart) en %
        validationRate: [68, 71, 75, 78, 82, 79, 85],
        validationRateLabels: ['Semaine 1', 'Semaine 2', 'Semaine 3', 'Semaine 4', 'Semaine 5', 'Semaine 6', 'Semaine 7'],
        validationRateAverage: 77.1,
        
        // Répartition par type de flux
        typeDistribution: {
          type_a: 48,
          type_b: 25,
          type_c: 18,
          type_d: 9,
          total: 100
        },
        
        // Résumé principal
        summary: {
          valides: 287,
          enCours: 54,
          refuses: 12,
          total: 353
        },
        
        // Métriques additionnelles
        metrics: {
          derniere_activite: '32 secondes',
          taux_succes: 81.3,
          taux_erreur: 3.4,
          taux_en_attente: 15.3
        }
      }
      
      // Remplir les données avec la réponse API
      data1.value = fakeApiResponse.activity
      data2.value = fakeApiResponse.validationRate
      apiData.value = fakeApiResponse.typeDistribution
      summary.value = fakeApiResponse.summary
    })

    const typeData = computed(() => {
      const total = apiData.value.total || 1
      return [
        { label: 'Type A', value: apiData.value.type_a, color: '#5294E2' },
        { label: 'Type B', value: apiData.value.type_b, color: '#E79A0F' },
        { label: 'Type C', value: apiData.value.type_c, color: '#27AE60' },
        { label: 'Type D', value: apiData.value.type_d, color: '#E74C3C' }
      ]
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
      const total = apiData.value.total || 1
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

    return { data1, chartW, chartH, barW, barGap, scale, linePoints, summary, pieW, pieH, typeData, apiData, pieSlices }
  }
})
</script>
