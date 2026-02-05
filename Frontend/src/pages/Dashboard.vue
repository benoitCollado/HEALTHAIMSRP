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
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed } from 'vue'
import Navbar from '../components/Navbar.vue'

export default defineComponent({
  components: { Navbar },
  setup() {
    const data1 = [12, 20, 8, 16, 24, 18, 22]
    const data2 = [40,50,55,60,58,64,70]
    const chartW = 480
    const chartH = 180
    const barW = 32
    const barGap = 8
    const maxV = Math.max(...data1)
    const scale = (chartH - 20) / maxV

    const linePoints = computed(() => {
      const max2 = Math.max(...data2)
      const s = (chartH - 20) / max2
      return data2.map((v,i) => `${10 + i*(barW+barGap)} , ${chartH - 10 - v*s}`).join(' ')
    })

    const summary = { valides: 124, enCours: 32, refuses: 8 }

    return { data1, chartW, chartH, barW, barGap, scale, linePoints, summary }
  }
})
</script>
