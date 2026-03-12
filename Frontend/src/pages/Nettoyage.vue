<template>
  <div class="canvas" role="main" aria-label="Nettoyage et validation des anomalies">
    <Navbar title="Nettoyage" />
    <div id="main-content" class="nettoyage-container">
      <section class="card" aria-labelledby="nettoyage-title">
        <h2 id="nettoyage-title">Nettoyage des anomalies</h2>
        <p id="nettoyage-desc">
          Liste des éléments nécessitant une validation ou une correction. Vous pouvez valider une anomalie (l'accepter telle quelle),
          la corriger, ou exporter les données nettoyées.
        </p>

        <div class="actions-bar">
          <label for="filter-type" class="sr-only">Filtrer par type d'anomalie</label>
          <select
            id="filter-type"
            v-model="filterType"
            aria-label="Filtrer par type d'anomalie"
            @change="loadRows"
          >
            <option value="">Tous les types</option>
            <option value="objectif_refuse">Objectifs refusés</option>
            <option value="consommation_invalide">Consommations invalides</option>
            <option value="metrique_incoherente">Métriques incohérentes</option>
          </select>
          <button
            type="button"
            class="btn btn-primary"
            :disabled="exporting"
            aria-label="Exporter les données nettoyées en CSV"
            @click="doExport"
          >
            {{ exporting ? 'Export en cours...' : 'Exporter les données nettoyées (CSV)' }}
          </button>
        </div>

        <div v-if="loading" class="loading" role="status" aria-live="polite">
          Chargement des anomalies...
        </div>
        <div v-if="error" class="error" role="alert">
          {{ error }}
        </div>
        <div v-if="success" class="success" role="status" aria-live="polite">
          {{ success }}
        </div>

        <div v-if="rows.length && !loading" role="region" aria-labelledby="table-title">
          <h3 id="table-title" class="sr-only">Tableau des anomalies</h3>
          <table class="table" role="table" aria-describedby="table-title">
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Type</th>
                <th scope="col">Description</th>
                <th scope="col">Détail</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="r in rows" :key="r.id">
                <td>{{ r.id }}</td>
                <td>{{ r.type_affichage }}</td>
                <td>{{ r.description }}</td>
                <td>{{ r.detail }}</td>
                <td>
                  <div class="btn-group">
                    <button
                      type="button"
                      class="btn btn-small"
                      :disabled="processing === r.id"
                      :aria-label="`Valider l'anomalie ${r.id}`"
                      @click="valider(r)"
                    >
                      Valider
                    </button>
                    <button
                      type="button"
                      class="btn btn-small btn-warning"
                      :disabled="processing === r.id"
                      :aria-label="`Corriger l'anomalie ${r.id}`"
                      @click="corriger(r)"
                    >
                      Corriger
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-else-if="!loading" class="empty" role="status">
          Aucune anomalie à traiter pour le moment.
        </div>
      </section>
    </div>

    <!-- Modal correction (simple) -->
    <div
      v-if="showCorrectionModal"
      class="modal-overlay"
      role="dialog"
      aria-modal="true"
      aria-labelledby="modal-title"
      aria-describedby="modal-desc"
      @keydown.esc="showCorrectionModal = false"
    >
      <div class="modal">
        <h3 id="modal-title">Corriger l'anomalie</h3>
        <p id="modal-desc">
          Pour les objectifs refusés : le statut sera mis à "Terminé". Pour les consommations et métriques,
          les valeurs aberrantes seront automatiquement corrigées.
        </p>
        <div class="modal-actions">
          <button
            type="button"
            class="btn btn-primary"
            :disabled="processing"
            @click="confirmCorriger"
          >
            Confirmer la correction
          </button>
          <button type="button" class="btn" @click="showCorrectionModal = false">
            Annuler
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import { auth } from '../services/auth'
import {
  getAnomalies,
  validerAnomalie,
  corrigerAnomalie,
  exportDonneesNettoyees,
  type Anomalie
} from '../services/adminApi'

export default defineComponent({
  components: { Navbar },
  setup() {
    const rows = ref<Anomalie[]>([])
    const loading = ref(false)
    const error = ref('')
    const success = ref('')
    const exporting = ref(false)
    const processing = ref<string | null>(null)
    const filterType = ref('')
    const showCorrectionModal = ref(false)
    const anomalyToCorriger = ref<Anomalie | null>(null)

    const loadRows = async () => {
      const token = auth.getToken()
      if (!token) {
        error.value = 'Token absent, impossible de charger les données.'
        return
      }

      try {
        loading.value = true
        error.value = ''
        const res = await getAnomalies(filterType.value || undefined)
        rows.value = res.anomalies
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors du chargement.'
        rows.value = []
      } finally {
        loading.value = false
      }
    }

    const valider = async (r: Anomalie) => {
      try {
        processing.value = r.id
        error.value = ''
        success.value = ''
        await validerAnomalie(r.id)
        success.value = `Anomalie ${r.id} validée.`
        await loadRows()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de la validation.'
      } finally {
        processing.value = null
      }
    }

    const corriger = (r: Anomalie) => {
      anomalyToCorriger.value = r
      showCorrectionModal.value = true
    }

    const confirmCorriger = async () => {
      const r = anomalyToCorriger.value
      if (!r) return

      try {
        processing.value = r.id
        error.value = ''
        success.value = ''
        await corrigerAnomalie(r.id)
        success.value = `Anomalie ${r.id} corrigée.`
        showCorrectionModal.value = false
        anomalyToCorriger.value = null
        await loadRows()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de la correction.'
      } finally {
        processing.value = null
      }
    }

    const doExport = async () => {
      try {
        exporting.value = true
        error.value = ''
        const blob = await exportDonneesNettoyees('all')
        const url = URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = `donnees_nettoyees_${new Date().toISOString().slice(0, 10)}.csv`
        a.click()
        URL.revokeObjectURL(url)
        success.value = 'Export CSV téléchargé.'
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de l\'export.'
      } finally {
        exporting.value = false
      }
    }

    onMounted(() => {
      loadRows()
    })

    return {
      rows,
      loading,
      error,
      success,
      exporting,
      processing,
      filterType,
      showCorrectionModal,
      loadRows,
      valider,
      corriger,
      confirmCorriger,
      doExport
    }
  }
})
</script>

<style scoped>
.nettoyage-container {
  padding: 24px;
  max-width: 900px;
  width: 100%;
  margin: 0 auto;
}

.card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card h2 {
  font-size: 1.25rem;
  margin: 0 0 8px 0;
  color: #2f4b66;
}

#nettoyage-desc {
  margin: 0 0 16px 0;
  color: #5a6c7d;
  font-size: 0.95rem;
}

.actions-bar {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.actions-bar select {
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.95rem;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #ccc;
  background: #fff;
  cursor: pointer;
  font-size: 0.95rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #5294E2;
  color: #fff;
  border-color: #5294E2;
}

.btn-primary:hover:not(:disabled) {
  background: #3d7bc7;
}

.btn-warning {
  background: #f39c12;
  color: #fff;
  border-color: #f39c12;
}

.btn-small {
  padding: 6px 10px;
  font-size: 0.85rem;
}

.btn-group {
  display: flex;
  gap: 8px;
}

.table {
  width: 100%;
  border-collapse: collapse;
}

.table th, .table td {
  padding: 10px 12px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.table th {
  font-weight: 600;
  background: #f7f9fc;
  color: #2f4b66;
}

.table td {
  font-size: 0.9rem;
}

.loading, .error, .success, .empty {
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
}

.loading {
  background: #f5f7fa;
  color: #2f4b66;
}

.error {
  background: #ffebee;
  color: #c62828;
}

.success {
  background: #e8f5e9;
  color: #2e7d32;
}

.empty {
  background: #f5f7fa;
  color: #666;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
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

.modal {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  max-width: 480px;
  width: 90%;
}

.modal h3 {
  margin: 0 0 12px 0;
  font-size: 1.1rem;
}

.modal p {
  margin: 0 0 20px 0;
  color: #5a6c7d;
  font-size: 0.95rem;
}

.modal-actions {
  display: flex;
  gap: 12px;
}
</style>
