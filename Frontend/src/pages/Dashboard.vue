<template>
  <div class="canvas" role="main" aria-label="Tableau de bord d'administration">
    <Navbar title="Dashboard" />
    <div id="main-content" class="dashboard-container">
      <div v-if="loading" class="loading" role="status" aria-live="polite">
        Chargement des indicateurs...
      </div>
      <div v-if="error" class="error" role="alert">
        {{ error }}
      </div>

      <template v-if="data && !loading">
        <!-- Qualité des données -->
        <section class="card" aria-labelledby="qualite-title">
          <h2 id="qualite-title">Qualité des données</h2>
          <div class="kpi-grid">
            <div class="kpi" aria-label="Score de qualité">
              <span class="kpi-value">{{ data.qualite_donnees.score_pct }}%</span>
              <span class="kpi-label">Score qualité</span>
            </div>
            <div class="kpi" aria-label="Total anomalies">
              <span class="kpi-value">{{ data.qualite_donnees.total_anomalies }}</span>
              <span class="kpi-label">Anomalies</span>
            </div>
            <div class="kpi" aria-label="Objectifs refusés">
              <span class="kpi-value">{{ data.qualite_donnees.objectifs_refuses }}</span>
              <span class="kpi-label">Objectifs refusés</span>
            </div>
            <div class="kpi" aria-label="Consommations invalides">
              <span class="kpi-value">{{ data.qualite_donnees.consommations_invalides }}</span>
              <span class="kpi-label">Consommations invalides</span>
            </div>
            <div class="kpi" aria-label="Métriques aberrantes">
              <span class="kpi-value">{{ data.qualite_donnees.metriques_aberrantes }}</span>
              <span class="kpi-label">Métriques aberrantes</span>
            </div>
          </div>
        </section>

        <!-- Progression utilisateurs -->
        <section class="card" aria-labelledby="users-title">
          <h2 id="users-title">Progression utilisateurs</h2>
          <div class="kpi-grid">
            <div class="kpi" aria-label="Total utilisateurs">
              <span class="kpi-value">{{ data.progression_utilisateurs.total }}</span>
              <span class="kpi-label">Total</span>
            </div>
            <div class="kpi" aria-label="Nouveaux utilisateurs 7 jours">
              <span class="kpi-value">{{ data.progression_utilisateurs.nouveaux_7j }}</span>
              <span class="kpi-label">Nouveaux (7j)</span>
            </div>
            <div class="kpi" aria-label="Nouveaux utilisateurs 30 jours">
              <span class="kpi-value">{{ data.progression_utilisateurs.nouveaux_30j }}</span>
              <span class="kpi-label">Nouveaux (30j)</span>
            </div>
          </div>
        </section>

        <!-- Tendances nutrition -->
        <section class="card" aria-labelledby="nutrition-title">
          <h2 id="nutrition-title">Tendances nutrition</h2>
          <div class="kpi-grid">
            <div class="kpi" aria-label="Total consommations">
              <span class="kpi-value">{{ data.tendances_nutrition.total_consommations }}</span>
              <span class="kpi-label">Consommations</span>
            </div>
            <div class="kpi" aria-label="Consommations 7 derniers jours">
              <span class="kpi-value">{{ data.tendances_nutrition.consommations_7j }}</span>
              <span class="kpi-label">Derniers 7j</span>
            </div>
            <div class="kpi" aria-label="Calories moyennes">
              <span class="kpi-value">{{ data.tendances_nutrition.calories_moyennes }}</span>
              <span class="kpi-label">Cal. moyennes</span>
            </div>
          </div>
        </section>

        <!-- Tendances activité -->
        <section class="card" aria-labelledby="activite-title">
          <h2 id="activite-title">Tendances activité</h2>
          <div class="kpi-grid">
            <div class="kpi" aria-label="Total activités">
              <span class="kpi-value">{{ data.tendances_activite.total_activites }}</span>
              <span class="kpi-label">Activités</span>
            </div>
            <div class="kpi" aria-label="Activités 7 derniers jours">
              <span class="kpi-value">{{ data.tendances_activite.activites_7j }}</span>
              <span class="kpi-label">Derniers 7j</span>
            </div>
            <div class="kpi" aria-label="Durée totale en minutes">
              <span class="kpi-value">{{ formatDuree(data.tendances_activite.duree_totale_minutes) }}</span>
              <span class="kpi-label">Durée totale</span>
            </div>
          </div>
        </section>

        <!-- Objectifs -->
        <section class="card" aria-labelledby="objectifs-title">
          <h2 id="objectifs-title">Objectifs</h2>
          <div class="kpi-grid">
            <div class="kpi" aria-label="Objectifs validés">
              <span class="kpi-value">{{ data.objectifs.valides }}</span>
              <span class="kpi-label">Validés</span>
            </div>
            <div class="kpi" aria-label="Objectifs en cours">
              <span class="kpi-value">{{ data.objectifs.encours }}</span>
              <span class="kpi-label">En cours</span>
            </div>
            <div class="kpi" aria-label="Objectifs refusés">
              <span class="kpi-value">{{ data.objectifs.refuses }}</span>
              <span class="kpi-label">Refusés</span>
            </div>
            <div class="kpi" aria-label="Taux de validation">
              <span class="kpi-value">{{ data.objectifs.taux_validation_pct }}%</span>
              <span class="kpi-label">Taux validation</span>
            </div>
          </div>
        </section>

        <!-- KPIs business -->
        <section class="card" aria-labelledby="kpis-title">
          <h2 id="kpis-title">KPIs business</h2>
          <div class="kpi-grid">
            <div class="kpi" aria-label="Utilisateurs actifs 30 jours">
              <span class="kpi-value">{{ data.kpis_business.utilisateurs_actifs_30j }}</span>
              <span class="kpi-label">Utilisateurs actifs (30j)</span>
            </div>
            <div class="kpi" aria-label="Données santé total">
              <span class="kpi-value">{{ data.kpis_business.donnees_sante_total }}</span>
              <span class="kpi-label">Données santé</span>
            </div>
          </div>
        </section>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import { getDashboard, type DashboardData } from '../services/adminApi'

export default defineComponent({
  components: { Navbar },
  setup() {
    const data = ref<DashboardData | null>(null)
    const loading = ref(true)
    const error = ref('')

    const formatDuree = (minutes: number) => {
      if (minutes < 60) return `${minutes} min`
      const h = Math.floor(minutes / 60)
      const m = minutes % 60
      return m ? `${h}h ${m}min` : `${h}h`
    }

    onMounted(async () => {
      try {
        loading.value = true
        error.value = ''
        data.value = await getDashboard()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors du chargement du tableau de bord.'
        data.value = null
      } finally {
        loading.value = false
      }
    })

    return { data, loading, error, formatDuree }
  }
})
</script>

<style scoped>
.dashboard-container {
  padding: 24px;
  max-width: 1100px;
  width: 100%;
  margin: 0 auto;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.card h2 {
  font-size: 1rem;
  margin: 0 0 12px 0;
  color: #2f4b66;
}

.kpi-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.kpi {
  flex: 1;
  min-width: 80px;
  padding: 12px;
  background: #f7f9fc;
  border-radius: 6px;
}

.kpi-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #2f4b66;
}

.kpi-label {
  font-size: 0.85rem;
  color: #5a6c7d;
}

.loading, .error {
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
</style>
