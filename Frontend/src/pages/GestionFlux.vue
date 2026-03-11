<template>
  <div class="canvas" role="main" aria-label="Gestion des flux de données ETL">
    <Navbar title="Gestion des flux" />
    <div id="main-content" class="flux-container">
      <div v-if="loading" class="loading" role="status" aria-live="polite">
        Chargement des flux...
      </div>
      <div v-if="error" class="error" role="alert">
        {{ error }}
      </div>
      <div v-if="fluxData && !fluxData.airflow_disponible && !loading" class="warning" role="status">
        Airflow n'est pas disponible. Les flux ETL (import Open Food Facts, export CSV) ne sont pas affichés.
        Vérifiez que les services Airflow sont démarrés.
      </div>

      <!-- CSV intermédiaires : visualisation et validation -->
      <section v-if="!loading" class="card csv-card" aria-labelledby="csv-title">
        <h2 id="csv-title">CSV intermédiaires (à valider avant incorporation)</h2>
        <p class="section-desc">
          Les DAGs Airflow produisent des CSV horodatés. Visualisez, modifiez puis validez pour que incorporation_ml les charge en BDD (import) ou les copie vers ML (export).
        </p>
        <div class="csv-tabs">
          <button
            type="button"
            :class="['tab-btn', { active: csvTab === 'import' }]"
            @click="csvTab = 'import'"
            :aria-pressed="csvTab === 'import'"
          >
            Import (Open Food Facts)
          </button>
          <button
            type="button"
            :class="['tab-btn', { active: csvTab === 'export' }]"
            @click="csvTab = 'export'"
            :aria-pressed="csvTab === 'export'"
          >
            Export (BDD → CSV)
          </button>
        </div>
        <div v-if="csvLoading" class="loading-small">Chargement des CSV...</div>
        <ul v-else class="csv-list" role="list">
          <li
            v-for="item in (csvTab === 'import' ? csvList.import : csvList.export)"
            :key="item.filename"
            class="csv-item"
            role="listitem"
          >
            <span class="csv-name">{{ item.filename }}</span>
            <span class="csv-meta">{{ item.rows }} lignes · {{ item.created_at?.slice(0, 19) }} · {{ item.status }}</span>
            <div class="csv-actions">
              <button type="button" class="btn-sm" @click="openViewer(item)" :disabled="item.status !== 'pending'">
                Voir
              </button>
              <button type="button" class="btn-sm" @click="openEditor(item)" :disabled="item.status !== 'pending'">
                Modifier
              </button>
              <button type="button" class="btn-sm btn-validate" @click="doValidate(item)" :disabled="item.status !== 'pending'">
                Valider
              </button>
              <button type="button" class="btn-sm btn-reject" @click="doReject(item)" :disabled="item.status !== 'pending'">
                Refuser
              </button>
            </div>
          </li>
          <li v-if="(csvTab === 'import' ? csvList.import : csvList.export).length === 0" class="empty">
            Aucun CSV {{ csvTab === 'import' ? 'd\'import' : 'd\'export' }} en attente
          </li>
        </ul>
      </section>

      <!-- Modal visualisation / édition CSV (vue tableau type Excel) -->
      <div v-if="modalCsv" class="modal-overlay" role="dialog" aria-labelledby="modal-title" aria-modal="true" @click.self="closeModal">
        <div class="modal-content modal-content-table">
          <h3 id="modal-title">{{ modalEdit ? 'Modifier le CSV' : 'Visualiser le CSV' }} {{ modalCsv.filename }}</h3>
          <p class="modal-info">{{ csvHeaders.length }} colonnes · {{ csvRows.length }} lignes</p>
          <div class="csv-table-scroll">
            <table class="csv-table" role="grid">
              <thead>
                <tr>
                  <th class="csv-th-num" scope="col">#</th>
                  <th v-for="(col, j) in csvHeaders" :key="j" scope="col">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, i) in csvRows" :key="i">
                  <td class="csv-td-num">{{ i + 1 }}</td>
                  <td v-for="(cell, j) in row" :key="j">
                    <input
                      v-if="modalEdit"
                      v-model="csvRows[i][j]"
                      type="text"
                      class="cell-input"
                      :aria-label="`Ligne ${i + 1}, ${csvHeaders[j] || 'col' + j}`"
                    />
                    <span v-else class="cell-text">{{ cell }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="modal-actions">
            <button v-if="modalEdit" type="button" class="btn-primary" @click="saveCsvEdit">
              Enregistrer
            </button>
            <button type="button" class="btn-secondary" @click="closeModal">
              {{ modalEdit ? 'Annuler' : 'Fermer' }}
            </button>
          </div>
        </div>
      </div>

      <template v-if="fluxData && !loading">
        <!-- Métadonnées des données en base -->
        <section class="card meta-card" aria-labelledby="meta-title">
          <h2 id="meta-title">Données en base (résultat des flux)</h2>
          <div class="meta-grid">
            <div class="meta-item">
              <span class="meta-value">{{ fluxData.flux_metadonnees.consommations.total }}</span>
              <span class="meta-label">Consommations (dernier: {{ fluxData.flux_metadonnees.consommations.dernier_run || '-' }})</span>
            </div>
            <div class="meta-item">
              <span class="meta-value">{{ fluxData.flux_metadonnees.activites.total }}</span>
              <span class="meta-label">Activités (dernier: {{ fluxData.flux_metadonnees.activites.dernier_run || '-' }})</span>
            </div>
            <div class="meta-item">
              <span class="meta-value">{{ fluxData.flux_metadonnees.metriques.total }}</span>
              <span class="meta-label">Métriques (dernier: {{ fluxData.flux_metadonnees.metriques.dernier_run || '-' }})</span>
            </div>
          </div>
        </section>

        <section class="card" aria-labelledby="encours-title">
          <h2 id="encours-title">En cours</h2>
          <p class="section-desc">Flux ETL en cours d'exécution (Airflow)</p>
          <ul class="flux-list" role="list">
            <li
              v-for="item in fluxData.encours"
              :key="item.id"
              class="flux-item"
              role="listitem"
            >
              <div class="flux-link flux-link-static">
                <span class="flux-name">{{ item.nom }}</span>
                <span class="flux-desc">{{ item.description }}</span>
                <span class="flux-stats">Dernier run : {{ item.stats?.lastRun ?? '-' }} · {{ item.statut }}</span>
                <a
                  v-if="item.dag_id"
                  :href="airflowDagUrl(item.dag_id)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-link"
                  :aria-label="`Ouvrir ${item.nom} dans Airflow`"
                >
                  Voir dans Airflow →
                </a>
              </div>
            </li>
            <li v-if="!fluxData.encours.length" class="empty">Aucun flux en cours</li>
          </ul>
        </section>

        <section class="card" aria-labelledby="valides-title">
          <h2 id="valides-title">Réussis récemment</h2>
          <p class="section-desc">Dernières exécutions réussies des flux ETL</p>
          <ul class="flux-list" role="list">
            <li
              v-for="item in recentValides"
              :key="item.id"
              class="flux-item"
              role="listitem"
            >
              <div class="flux-link flux-link-static">
                <span class="flux-name">{{ item.nom }}</span>
                <span class="flux-desc">{{ item.description }}</span>
                <span class="flux-stats">Dernier run : {{ item.stats?.lastRun ?? '-' }}</span>
                <a
                  v-if="item.dag_id"
                  :href="airflowDagUrl(item.dag_id)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-link"
                  :aria-label="`Ouvrir ${item.nom} dans Airflow`"
                >
                  Voir dans Airflow →
                </a>
              </div>
            </li>
            <li v-if="!recentValides.length" class="empty">Aucun flux réussi récemment</li>
          </ul>
        </section>

        <section class="card" aria-labelledby="refuses-title">
          <h2 id="refuses-title">En échec</h2>
          <p class="section-desc">Flux ETL en échec ou sans exécution récente</p>
          <ul class="flux-list" role="list">
            <li
              v-for="item in fluxData.refuses"
              :key="item.id"
              class="flux-item"
              role="listitem"
            >
              <div class="flux-link flux-link-static">
                <span class="flux-name">{{ item.nom }}</span>
                <span class="flux-desc">{{ item.description }}</span>
                <span v-if="item.errors" class="flux-errors">{{ item.errors.join('; ') }}</span>
                <span class="flux-stats">Dernier run : {{ item.stats?.lastRun ?? '-' }}</span>
                <a
                  v-if="item.dag_id"
                  :href="airflowDagUrl(item.dag_id)"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-link"
                  :aria-label="`Ouvrir ${item.nom} dans Airflow pour diagnostiquer`"
                >
                  Voir dans Airflow →
                </a>
              </div>
            </li>
            <li v-if="!fluxData.refuses.length" class="empty">Aucun flux en échec</li>
          </ul>
        </section>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted, onUnmounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import {
  getFlux,
  getFluxCsvList,
  getFluxCsvContent,
  updateFluxCsv,
  validateFluxCsv,
  rejectFluxCsv,
  type FluxData,
  type CsvIntermediaireMeta,
  type FluxCsvListResponse
} from '../services/adminApi'
import { AIRFLOW_UI_URL } from '../config'

export default defineComponent({
  components: { Navbar },
  setup() {
    const fluxData = ref<FluxData | null>(null)
    const loading = ref(true)
    const error = ref('')
    const csvTab = ref<'import' | 'export'>('import')
    const csvList = ref<FluxCsvListResponse>({ import: [], export: [] })
    const csvLoading = ref(false)
    const modalCsv = ref<CsvIntermediaireMeta | null>(null)
    const modalContent = ref('')
    const modalEdit = ref(false)
    const csvHeaders = ref<string[]>([])
    const csvRows = ref<string[][]>([])

    function parseCSV(text: string): { headers: string[]; rows: string[][] } {
      const lines = text.split(/\r?\n/).filter((l) => l.trim() !== '' || l.includes(','))
      if (lines.length === 0) return { headers: [], rows: [] }
      const parseLine = (line: string): string[] => {
        const result: string[] = []
        let current = ''
        let inQuotes = false
        for (let i = 0; i < line.length; i++) {
          const c = line[i]
          if (c === '"') {
            inQuotes = !inQuotes
          } else if (c === ',' && !inQuotes) {
            result.push(current)
            current = ''
          } else {
            current += c
          }
        }
        result.push(current)
        return result
      }
      const headers = parseLine(lines[0])
      const rows = lines.slice(1).map((l) => {
        const cells = parseLine(l)
        while (cells.length < headers.length) cells.push('')
        return cells.slice(0, headers.length)
      })
      return { headers, rows }
    }

    function toCSV(headers: string[], rows: string[][]): string {
      const escape = (v: string) => {
        const s = String(v ?? '')
        if (s.includes(',') || s.includes('"') || s.includes('\n')) {
          return '"' + s.replace(/"/g, '""') + '"'
        }
        return s
      }
      const padRow = (r: string[]) => {
        const arr = [...r]
        while (arr.length < headers.length) arr.push('')
        return arr.slice(0, headers.length)
      }
      return [headers.map(escape).join(','), ...rows.map((r) => padRow(r).map(escape).join(','))].join('\n')
    }

    const recentValides = computed(() => {
      if (!fluxData.value) return []
      return [...fluxData.value.valides].slice(-5).reverse()
    })

    const airflowDagUrl = (dagId: string) => {
      return `${AIRFLOW_UI_URL.replace(/\/$/, '')}/dags/${dagId}/grid`
    }

    async function loadCsvList() {
      csvLoading.value = true
      try {
        csvList.value = await getFluxCsvList()
      } catch {
        csvList.value = { import: [], export: [] }
      } finally {
        csvLoading.value = false
      }
    }

    function loadCsvIntoTable(content: string) {
      const { headers, rows } = parseCSV(content)
      csvHeaders.value = headers
      csvRows.value = rows
    }

    async function openViewer(item: CsvIntermediaireMeta) {
      try {
        const res = await getFluxCsvContent(item.filename)
        loadCsvIntoTable(res.content)
        modalCsv.value = item
        modalEdit.value = false
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur chargement CSV'
      }
    }

    async function openEditor(item: CsvIntermediaireMeta) {
      try {
        const res = await getFluxCsvContent(item.filename)
        loadCsvIntoTable(res.content)
        modalCsv.value = item
        modalEdit.value = true
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur chargement CSV'
      }
    }

    async function saveCsvEdit() {
      if (!modalCsv.value) return
      try {
        const content = toCSV(csvHeaders.value, csvRows.value)
        await updateFluxCsv(modalCsv.value.filename, content)
        closeModal()
        loadCsvList()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur mise à jour CSV'
      }
    }

    function closeModal() {
      modalCsv.value = null
      modalContent.value = ''
      modalEdit.value = false
      csvHeaders.value = []
      csvRows.value = []
    }

    async function doValidate(item: CsvIntermediaireMeta) {
      try {
        await validateFluxCsv(item.filename)
        loadCsvList()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur validation'
      }
    }

    async function doReject(item: CsvIntermediaireMeta) {
      try {
        await rejectFluxCsv(item.filename)
        loadCsvList()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur refus'
      }
    }

    function onKeydown(e: KeyboardEvent) {
      if (e.key === 'Escape' && modalCsv.value) closeModal()
    }

    onMounted(async () => {
      window.addEventListener('keydown', onKeydown)
      try {
        loading.value = true
        error.value = ''
        fluxData.value = await getFlux()
        await loadCsvList()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors du chargement des flux.'
        fluxData.value = null
      } finally {
        loading.value = false
      }
    })

    onUnmounted(() => window.removeEventListener('keydown', onKeydown))

    return {
      fluxData,
      loading,
      error,
      recentValides,
      airflowDagUrl,
      csvTab,
      csvList,
      csvLoading,
      modalCsv,
      modalContent,
      modalEdit,
      csvHeaders,
      csvRows,
      openViewer,
      openEditor,
      saveCsvEdit,
      closeModal,
      doValidate,
      doReject
    }
  }
})
</script>

<style scoped>
.flux-container {
  padding: 24px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.meta-card {
  grid-column: 1 / -1;
}

.meta-grid {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.meta-item {
  padding: 12px 16px;
  background: #f7f9fc;
  border-radius: 6px;
}

.meta-value {
  display: block;
  font-size: 1.25rem;
  font-weight: 700;
  color: #2f4b66;
}

.meta-label {
  font-size: 0.85rem;
  color: #5a6c7d;
}

.card h2 {
  font-size: 1rem;
  margin: 0 0 8px 0;
  color: #2f4b66;
}

.section-desc {
  font-size: 0.9rem;
  color: #5a6c7d;
  margin: 0 0 12px 0;
}

.flux-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.flux-item {
  margin-bottom: 12px;
}

.flux-link, .flux-link-static {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px;
  border-radius: 6px;
  color: inherit;
}

.flux-name {
  font-weight: 600;
  color: #2f4b66;
}

.flux-desc, .flux-stats {
  font-size: 12px;
  color: #666;
}

.flux-errors {
  font-size: 12px;
  color: #a00;
}

.btn-link {
  margin-top: 6px;
  font-size: 0.9rem;
  color: #5294E2;
  text-decoration: none;
}

.btn-link:hover, .btn-link:focus {
  text-decoration: underline;
  outline: 2px solid #5294E2;
  outline-offset: 2px;
}

.empty {
  padding: 12px;
  color: #666;
  font-style: italic;
}

.loading, .error, .warning {
  grid-column: 1 / -1;
  padding: 12px;
  border-radius: 6px;
}

.loading {
  background: #f5f7fa;
  color: #2f4b66;
}

.error {
  background: #ffebee;
  color: #c62828;
}

.warning {
  background: #fff3e0;
  color: #e65100;
}

.csv-card {
  grid-column: 1 / -1;
}

.csv-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 12px;
}

.tab-btn {
  padding: 8px 16px;
  border: 1px solid #ccc;
  background: #f5f5f5;
  border-radius: 4px;
  cursor: pointer;
}

.tab-btn.active {
  background: #5294E2;
  color: #fff;
  border-color: #5294E2;
}

.csv-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.csv-item {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
}

.csv-name {
  font-weight: 600;
  min-width: 200px;
}

.csv-meta {
  font-size: 0.85rem;
  color: #666;
}

.csv-actions {
  display: flex;
  gap: 8px;
  margin-left: auto;
}

.btn-sm {
  padding: 4px 10px;
  font-size: 0.85rem;
  border: 1px solid #ccc;
  background: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.btn-sm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-sm.btn-validate {
  background: #4caf50;
  color: #fff;
  border-color: #4caf50;
}

.btn-sm.btn-reject {
  background: #f44336;
  color: #fff;
  border-color: #f44336;
}

.loading-small {
  padding: 12px;
  color: #666;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  max-width: 90vw;
  max-height: 90vh;
  overflow: auto;
}

.modal-content h3 {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
}

.modal-content-table {
  max-width: 95vw;
  width: 100%;
}

.modal-info {
  font-size: 0.9rem;
  color: #666;
  margin: 0 0 12px 0;
}

.csv-table-scroll {
  overflow: auto;
  max-height: 60vh;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 16px;
}

.csv-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.csv-table th,
.csv-table td {
  border: 1px solid #ddd;
  padding: 6px 8px;
  text-align: left;
  white-space: nowrap;
}

.csv-table thead th {
  background: #2f4b66;
  color: #fff;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.csv-th-num,
.csv-td-num {
  min-width: 40px;
  max-width: 50px;
  text-align: center;
  background: #f5f5f5;
}

.csv-table tbody tr:hover {
  background: #f9f9f9;
}

.cell-input {
  width: 100%;
  min-width: 80px;
  padding: 4px 6px;
  border: 1px solid #ccc;
  border-radius: 2px;
  font-size: 12px;
}

.cell-input:focus {
  outline: 2px solid #5294E2;
  outline-offset: -1px;
}

.cell-text {
  display: block;
  min-width: 60px;
}

.modal-actions {
  display: flex;
  gap: 12px;
  margin-top: 16px;
}

.btn-primary {
  padding: 8px 16px;
  background: #5294E2;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-secondary {
  padding: 8px 16px;
  background: #f5f5f5;
  border: 1px solid #ccc;
  border-radius: 4px;
  cursor: pointer;
}
</style>
