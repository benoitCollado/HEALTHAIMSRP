<template>
  <div class="canvas">
    <Navbar :title="flux?.nom || 'Flux'" />
    <div style="padding:24px;max-width:1000px;margin:0 auto;">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <h2>{{ flux?.nom }}</h2>
          <div style="display:flex;gap:8px;align-items:center">
            <button v-if="isEncours" @click="validerFlux">Valider</button>
            <button @click="toggleEdit">{{ editMode ? 'Annuler' : 'Modifier' }}</button>
            <button @click="refuserFlux" style="background:#f39c12;color:#fff">Refuser</button>
          </div>
        </div> 
      <p>{{ flux?.description }}</p>

      <div style="display:flex;gap:16px;margin-bottom:16px;">
        <div style="padding:12px;background:#fff;border-radius:6px;flex:1">
          <strong>% exploitable</strong>
          <div style="font-size:24px">{{ flux?.stats?.exploitablePct }}%</div>
        </div>
        <div style="padding:12px;background:#fff;border-radius:6px;flex:1">
          <strong>Lignes</strong>
          <div style="font-size:20px">{{ flux?.stats?.rows }}</div>
        </div>
        <div style="padding:12px;background:#fff;border-radius:6px;flex:1">
          <strong>Dernier run</strong>
          <div style="font-size:14px">{{ flux?.stats?.lastRun }}</div>
        </div>
      </div>

      <div style="display:flex;gap:20px">
        <div style="flex:1;background:#fff;padding:12px;border-radius:6px">
          <h3>Requêtes pré-définies</h3>
          <div v-for="(q, i) in flux?.sampleQueries || []" :key="i" style="margin-bottom:8px">
            <button @click="runQuery(q.query)">{{ q.name }}</button>
          </div> 
          <div v-if="lastQueryResult" style="margin-top:12px">
            <strong>Résultat (simulé):</strong>
            <pre style="background:#f4f4f4;padding:8px;border-radius:4px">{{ lastQueryResult }}</pre>
          </div>
        </div>

        <div style="flex:1;background:#fff;padding:12px;border-radius:6px">
          <h3>Informations</h3>
          <table style="width:100%;border-collapse:collapse">
            <tbody>
              <tr v-for="(v,k) in infoRows" :key="k"><td style="padding:6px;font-weight:600">{{ k }}</td><td style="padding:6px">{{ v }}</td></tr>
            </tbody>
          </table>
        </div>
      </div>

      <div style="margin-top:16px;background:#fff;padding:12px;border-radius:6px">
        <h3>Fichier (Aperçu Excel-like)</h3>
        <div v-if="isEncours">
          <p style="font-size:13px;color:#666">Aperçu limité pour les flux en cours</p>
          <table style="width:100%;border-collapse:collapse">
            <thead><tr><th style="text-align:left;padding:8px">Clé</th><th style="text-align:left;padding:8px">Valeur</th></tr></thead>
            <tbody>
              <tr v-for="(r, idx) in flux?.tableData || []" :key="idx"><td style="padding:8px">{{ r.cle }}</td><td style="padding:8px">{{ r.valeur }}</td></tr>
            </tbody>
          </table>
        </div>
        <div v-else>
          <div style="margin-bottom:8px">
            <button @click="toggleEdit">{{ editMode ? 'Enregistrer' : 'Éditer le fichier' }}</button>
          </div>
          <div v-if="!editMode">
            <table style="width:100%;border-collapse:collapse;table-layout:fixed">
              <thead>
                <tr>
                  <th v-for="(h, idx) in csvHeaders" :key="idx" style="padding:8px;border-bottom:1px solid #eee;text-align:left">{{ h }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rIdx) in csvRows" :key="rIdx">
                  <td v-for="(cell, cIdx) in row" :key="cIdx" style="padding:6px;border-bottom:1px solid #f6f6f6;overflow:hidden;text-overflow:ellipsis">{{ cell }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div v-else>
            <textarea v-model="csvEditor" style="width:100%;height:260px;font-family:monospace;padding:8px"></textarea>
            <div style="margin-top:8px;display:flex;gap:8px">
              <button @click="saveCsv">Enregistrer</button>
              <button @click="cancelEdit">Annuler</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="flux?.comment" style="margin-top:16px;background:#fff;padding:12px;border-radius:6px">
        <h3>Commentaire</h3>
        <div>{{ flux.comment }}</div>
      </div>

      <div v-if="flux?.errors" style="margin-top:16px;background:#fff;padding:12px;border-radius:6px">
        <h3>Erreurs détectées</h3>
        <ul>
          <li v-for="(e,i) in flux.errors" :key="i">{{ e }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import { mockFluxData } from '../data/mockApiData'

export default defineComponent({
  components: { Navbar },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const id = (route.params.id as string) || ''

    const flux = ref<any | null>(null)
    function findFlux() {
      flux.value = [...mockFluxData.valides, ...mockFluxData.encours, ...mockFluxData.refuses].find((f:any)=>f.id===id) || null
    }
    findFlux()

    const lastQueryResult = ref<string | null>(null)
    const editMode = ref(false)
    const csvEditor = ref('')

    const isEncours = computed(() => mockFluxData.encours.some((f:any)=>f.id===id))

    function runQuery(q: string) {
      lastQueryResult.value = `Résultat simulé pour: ${q}\nLignes: ${Math.floor(Math.random()*10)+1}`
    }

    const infoRows = computed(() => ({
      id: flux.value?.id,
      nom: flux.value?.nom,
      description: flux.value?.description,
      'exploitable %': flux.value?.stats?.exploitablePct,
      lignes: flux.value?.stats?.rows,
      'dernier run': flux.value?.stats?.lastRun,
      taille: flux.value?.fileSize || '-'
    }))

    const csvSource = computed(() => flux.value?.csvContent ?? '')
    const csvRows = computed(() => {
      if (!csvSource.value) return []
      return csvSource.value.split('\n').filter(r=>r.trim().length>0).map(r=>r.split(',').map(c=>c.trim()))
    })
    const csvHeaders = computed(() => {
      const rows = csvRows.value
      if (!rows.length) return []
      return rows[0]
    })

    function toggleEdit() {
      if (!editMode.value) {
        // enter edit mode
        csvEditor.value = flux.value?.csvContent || generateCsvFromTable(flux.value?.tableData || [])
        editMode.value = true
        return
      }
      // if already in edit mode, save
      saveCsv()
    }

    function generateCsvFromTable(tableData: any[]) {
      if (!tableData || !tableData.length) return ''
      // convert array of objects to CSV (headers are keys of first row)
      const headers = Object.keys(tableData[0])
      const lines = [headers.join(',')]
      for (const r of tableData) {
        lines.push(headers.map(h=>String(r[h] ?? '')).join(','))
      }
      return lines.join('\n')
    }

    function saveCsv() {
      if (!flux.value) return
      flux.value.csvContent = csvEditor.value
      // update tableData as array of objects
      const rows = csvEditor.value.split('\n').filter(r=>r.trim().length>0).map(r=>r.split(',').map(c=>c.trim()))
      if (rows.length>0) {
        const headers = rows[0]
        const data = rows.slice(1).map(r=>{
          const obj:any = {}
          for (let i=0;i<headers.length;i++) obj[headers[i]] = r[i] ?? ''
          return obj
        })
        flux.value.tableData = data
      }
      editMode.value = false
    }

    function cancelEdit() {
      editMode.value = false
      csvEditor.value = ''
    }

    function validerFlux() {
      if (!flux.value) return
      const idx = mockFluxData.encours.findIndex((f:any)=>f.id===flux.value.id)
      if (idx !== -1) {
        const obj = mockFluxData.encours.splice(idx,1)[0]
        obj.comment = obj.comment || ''
        mockFluxData.valides.push(obj)
      }
      router.push('/gestion-des-flux')
    }

    function refuserFlux() {
      if (!flux.value) return
      const comment = prompt('Commentaire (optionnel) pour le refus:') || ''
      const errors = prompt('Liste d\'erreurs (séparées par ; ) (optionnel):') || ''
      // remove from encours or valides
      let idx = mockFluxData.encours.findIndex((f:any)=>f.id===flux.value.id)
      if (idx !== -1) {
        const obj = mockFluxData.encours.splice(idx,1)[0]
        obj.comment = comment
        obj.errors = errors ? errors.split(';').map((s:string)=>s.trim()) : []
        mockFluxData.refuses.push(obj)
      } else {
        idx = mockFluxData.valides.findIndex((f:any)=>f.id===flux.value.id)
        if (idx !== -1) {
          const obj = mockFluxData.valides.splice(idx,1)[0]
          obj.comment = comment
          obj.errors = errors ? errors.split(';').map((s:string)=>s.trim()) : []
          mockFluxData.refuses.push(obj)
        }
      }
      router.push('/gestion-des-flux')
    }


    return { flux, lastQueryResult, runQuery, infoRows, isEncours, editMode, csvEditor, csvRows, csvHeaders, toggleEdit, saveCsv, cancelEdit, validerFlux, refuserFlux }
  }
})
</script>
