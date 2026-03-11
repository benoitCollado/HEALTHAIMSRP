<template>
  <div class="canvas nav-page">
    <Navbar title="Accueil" />
    <div class="page-content">
      <!-- Admin view: Navigation -->
      <div v-if="isAdmin">
        <h2>Page d'accueil</h2>
        <p>Bienvenue dans le système de gestion des flux</p>
        <div class="nav-grid">
          <router-link to="/dashboard" class="nav-card">
            <div class="nav-icon">📊</div>
            <div>Dashboard</div>
          </router-link>
          <router-link to="/gestion-des-flux" class="nav-card">
            <div class="nav-icon">📋</div>
            <div>Gestion des flux</div>
          </router-link>
          <router-link to="/nettoyage" class="nav-card">
            <div class="nav-icon">🧹</div>
            <div>Nettoyage</div>
          </router-link>
          <router-link to="/test-backend" class="nav-card">
            <div class="nav-icon">🧪</div>
            <div>Test API</div>
          </router-link>
        </div>
      </div>

      <!-- User view: Profile -->
      <div v-else class="user-view">
        <h2>Votre profil</h2>

        <!-- Tab navigation -->
        <div class="user-tabs">
          <button
            v-for="tab in tabs"
            :key="tab.id"
            class="user-tab"
            :class="{ active: activeTab === tab.id }"
            @click="activeTab = tab.id"
          >
            {{ tab.icon }} {{ tab.label }}
            <span v-if="tab.count !== undefined" class="tab-count">{{ tab.count }}</span>
          </button>
        </div>

        <div class="user-panel">
          <div v-if="userLoading" class="user-loading">Chargement des données utilisateur...</div>
          <div v-else-if="userError" class="user-error">{{ userError }}</div>

          <template v-else>

          <!-- Tab: Profil -->
          <div v-if="activeTab === 'profil'" class="user-section">
            <h3>Informations personnelles</h3>
            <div class="user-grid">
              <div class="user-card">
                <div class="user-label">ID utilisateur</div>
                <div class="user-value">{{ userProfile?.id_utilisateur ?? '-' }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Nom d'utilisateur</div>
                <div class="user-value">{{ userProfile?.username || '-' }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Sexe</div>
                <div class="user-value">{{ userProfile?.sexe || '-' }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Âge</div>
                <div class="user-value">{{ userProfile?.age ?? '-' }} ans</div>
              </div>
              <div class="user-card">
                <div class="user-label">Taille</div>
                <div class="user-value">{{ userProfile?.taille_cm ?? '-' }} cm</div>
              </div>
              <div class="user-card">
                <div class="user-label">Poids</div>
                <div class="user-value">{{ userProfile?.poids_kg ?? '-' }} kg</div>
              </div>
              <div class="user-card">
                <div class="user-label">Niveau activité</div>
                <div class="user-value">{{ userProfile?.niveau_activite ?? '-' }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Type abonnement</div>
                <div class="user-value">{{ userProfile?.type_abonnement ?? '-' }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Date d'inscription</div>
                <div class="user-value">{{ formatDate(userProfile?.date_inscription) }}</div>
              </div>
            </div>
          </div>

          <!-- Tab: Santé -->
          <div v-if="activeTab === 'sante'">
            <h3>Mesures santé</h3>
            <div v-if="!userMetrics.length" class="user-empty">Aucune mesure disponible.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Poids</th>
                    <th>FC</th>
                    <th>Sommeil</th>
                    <th>Calories</th>
                    <th>Pas</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="metric in userMetrics" :key="metric.id_metrique">
                    <td>{{ formatDate(metric.date_mesure) }}</td>
                    <td>{{ metric.poids_kg ?? '-' }}</td>
                    <td>{{ metric.frequence_cardiaque ?? '-' }}</td>
                    <td>{{ metric.duree_sommeil_h ?? '-' }}</td>
                    <td>{{ metric.calories_brulees ?? '-' }}</td>
                    <td>{{ metric.pas ?? '-' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Activités -->
          <div v-if="activeTab === 'activites'">
            <h3>Activités physiques</h3>
            <div v-if="!userActivities.length" class="user-empty">Aucune activité enregistrée.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Durée (min)</th>
                    <th>Calories dépensées</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="activity in userActivities" :key="activity.id_activite">
                    <td>{{ formatDate(activity.date_activite) }}</td>
                    <td>{{ activity.duree_minutes }}</td>
                    <td>{{ activity.calories_depensees }} kcal</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Alimentation -->
          <div v-if="activeTab === 'alimentation'">
            <h3>Alimentation</h3>
            <div class="user-grid user-grid-2" style="margin-bottom:16px">
              <div class="user-card">
                <div class="user-label">Calories consommées (total)</div>
                <div class="user-value">{{ totalCaloriesConsumed }} kcal</div>
              </div>
              <div class="user-card">
                <div class="user-label">Consommations enregistrées</div>
                <div class="user-value">{{ userConsumptions.length }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Dernière consommation</div>
                <div class="user-value">{{ lastConsumptionDate }}</div>
              </div>
            </div>
            <div v-if="!userConsumptions.length" class="user-empty">Aucune consommation enregistrée.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Calories</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="c in userConsumptions" :key="c.id_consommation">
                    <td>{{ formatDate(c.date_consommation) }}</td>
                    <td>{{ c.calories_calculees }} kcal</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Objectifs -->
          <div v-if="activeTab === 'objectifs'">
            <h3>Objectifs</h3>
            <div v-if="!userGoals.length" class="user-empty">Aucun objectif enregistré.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Statut</th>
                    <th>Début</th>
                    <th>Fin</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="goal in userGoals" :key="goal.id_objectif">
                    <td>{{ goal.type_objectif }}</td>
                    <td>
                      <span class="goal-status" :class="goal.statut?.toLowerCase().replace(/\s+/g, '-')">
                        {{ goal.statut }}
                      </span>
                    </td>
                    <td>{{ formatDate(goal.date_debut) }}</td>
                    <td>{{ formatDate(goal.date_fin) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Navbar from '../components/Navbar.vue'
import { auth } from '../services/auth'
import { API_BASE_URL } from '../config'

interface UserProfile {
  id_utilisateur: number
  username: string
  age: number
  sexe: string
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  type_abonnement: number
  date_inscription: string
}

interface Metrique {
  id_metrique: number
  date_mesure: string
  poids_kg?: number
  frequence_cardiaque?: number
  duree_sommeil_h?: number
  calories_brulees?: number
  pas?: number
  id_utilisateur: number
}

interface Activite {
  id_activite: number
  date_activite: string
  duree_minutes: number
  calories_depensees: number
  id_utilisateur: number
}

interface Consommation {
  id_consommation: number
  date_consommation: string
  calories_calculees: number
  id_utilisateur: number
}

interface Objectif {
  id_objectif: number
  type_objectif: string
  date_debut: string
  date_fin: string
  statut: string
  id_utilisateur: number
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const router = useRouter()
    const isAdmin = computed(() => auth.isAdmin())
    const userProfile = ref<UserProfile | null>(null)
    const userMetrics = ref<Metrique[]>([])
    const userActivities = ref<Activite[]>([])
    const userConsumptions = ref<Consommation[]>([])
    const userGoals = ref<Objectif[]>([])
    const userLoading = ref(false)
    const userError = ref('')
    const activeTab = ref('profil')

    const tabs = computed(() => [
      { id: 'profil', label: 'Profil', icon: '👤' },
      { id: 'sante', label: 'Santé', icon: '❤️', count: userMetrics.value.length },
      { id: 'activites', label: 'Activités', icon: '🏃', count: userActivities.value.length },
      { id: 'alimentation', label: 'Alimentation', icon: '🍽️', count: userConsumptions.value.length },
      { id: 'objectifs', label: 'Objectifs', icon: '🎯', count: userGoals.value.length }
    ])

    const formatDate = (dateValue?: string) => {
      if (!dateValue) return '-'
      const date = new Date(dateValue)
      if (Number.isNaN(date.getTime())) return '-'
      return date.toLocaleDateString('fr-FR')
    }

    const displayedMetrics = computed(() => userMetrics.value.slice(0, 8))
    const recentActivities = computed(() => userActivities.value.slice(0, 5))

    const activeGoals = computed(() => {
      return userGoals.value.filter(goal => goal.statut?.toLowerCase() !== 'termine' && goal.statut?.toLowerCase() !== 'terminé')
    })

    const totalCaloriesConsumed = computed(() => {
      return Math.round(userConsumptions.value.reduce((sum, c) => sum + (c.calories_calculees || 0), 0))
    })

    const lastConsumptionDate = computed(() => {
      if (!userConsumptions.value.length) return '-'
      return formatDate(userConsumptions.value[0].date_consommation)
    })

    async function fetchJson(endpoint: string, token: string) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      })

      if (!response.ok) {
        if (response.status === 401) {
          auth.logout()
          router.push('/connexion')
          throw new Error('Session expirée. Veuillez vous reconnecter.')
        }
        throw new Error(`Erreur ${response.status} sur ${endpoint}`)
      }

      return response.json()
    }

    async function loadUserData() {
      if (isAdmin.value) return

      const token = auth.getToken()
      const connectedUser = auth.getCurrentUser()
      const userId = Number(connectedUser?.id)

      if (!token || !Number.isFinite(userId)) {
        userError.value = 'Utilisateur non authentifié.'
        return
      }

      try {
        userLoading.value = true
        userError.value = ''

        const [profile, metrics, activities, consumptions, goals] = await Promise.all([
          fetchJson(`/utilisateurs/${userId}`, token),
          fetchJson('/metriques-sante/', token),
          fetchJson('/activites/', token),
          fetchJson('/consommations/', token),
          fetchJson('/objectifs/', token)
        ])

        userProfile.value = profile as UserProfile
        userMetrics.value = (metrics as Metrique[])
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_mesure).getTime() - new Date(a.date_mesure).getTime())

        userActivities.value = (activities as Activite[])
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_activite).getTime() - new Date(a.date_activite).getTime())

        userConsumptions.value = (consumptions as Consommation[])
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_consommation).getTime() - new Date(a.date_consommation).getTime())

        userGoals.value = (goals as Objectif[])
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_debut).getTime() - new Date(a.date_debut).getTime())
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors du chargement des données utilisateur.'
      } finally {
        userLoading.value = false
      }
    }

    onMounted(() => {
      loadUserData()
    })

    return {
      isAdmin,
      userProfile,
      userMetrics,
      userActivities,
      userConsumptions,
      userGoals,
      userLoading,
      userError,
      activeTab,
      tabs,
      displayedMetrics,
      recentActivities,
      activeGoals,
      totalCaloriesConsumed,
      lastConsumptionDate,
      formatDate
    }
  }
})
</script>

<style scoped>
.user-view {
  max-width: 980px;
  margin: 0 auto;
}

.user-panel {
  background: #fff;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.user-section {
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid #eee;
}

.user-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.user-tab {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px 6px 0 0;
  background: #e8edf3;
  color: #555;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.user-tab:hover {
  background: #d0d8e4;
  color: #333;
}

.user-tab.active {
  background: #fff;
  color: #1e3a5f;
  font-weight: 700;
  box-shadow: 0 -2px 0 #2563eb inset;
}

.tab-count {
  background: #2563eb;
  color: #fff;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 10px;
  min-width: 18px;
  text-align: center;
}

.user-tab.active .tab-count {
  background: #2563eb;
}

.goal-status {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 0.78rem;
  font-weight: 600;
  background: #e8edf3;
  color: #555;
}

.user-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-top: 12px;
}

.user-grid-2 {
  grid-template-columns: 1fr 1fr;
}

.user-card,
.user-subpanel {
  padding: 12px;
  background: #f6f6f6;
  border-radius: 6px;
}

.user-label {
  font-size: 12px;
  color: #666;
}

.user-value {
  font-weight: 600;
  margin-top: 4px;
}

.user-loading,
.user-error,
.user-empty {
  padding: 12px;
  border-radius: 6px;
}

.user-loading {
  background: #f5f7fa;
  color: #2f4b66;
}

.user-error {
  background: #ffebee;
  color: #c62828;
}

.user-empty {
  background: #f5f7fa;
  color: #666;
}

.table-wrap {
  overflow-x: auto;
}

.simple-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.simple-table th,
.simple-table td {
  border-bottom: 1px solid #e8edf3;
  padding: 8px 10px;
  text-align: left;
}

.simple-table th {
  background: #f7f9fc;
}

.user-list {
  margin: 8px 0 0;
  padding-left: 18px;
}

.user-list li {
  margin-bottom: 6px;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 32px;
  max-width: 900px;
}
.nav-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 32px;
  background: #fff;
  border-radius: 8px;
  text-decoration: none;
  color: #333;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s, box-shadow 0.2s;
  font-size: 18px;
  font-weight: 500;
}
.nav-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.15);
}
.nav-icon {
  font-size: 48px;
}

@media (max-width: 900px) {
  .user-grid,
  .user-grid-2 {
    grid-template-columns: 1fr;
  }
  .nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 500px) {
  .nav-grid {
    grid-template-columns: 1fr;
  }
}
</style>
