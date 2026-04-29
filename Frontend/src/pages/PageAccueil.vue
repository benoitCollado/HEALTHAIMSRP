<template>
  <div class="canvas nav-page">
    <Navbar title="Accueil" />
    <div id="main-content" class="page-content">
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
          <router-link to="/utilisateurs" class="nav-card">
            <div class="nav-icon">👥</div>
            <div>Utilisateurs</div>
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
          <div v-else-if="userSuccess" class="user-success">{{ userSuccess }}</div>

          <template v-else>

          <!-- Tab: Profil -->
          <div v-if="activeTab === 'profil'" class="user-section">
            <div class="section-header">
              <h3>Informations personnelles</h3>
              <button class="action-btn" @click="toggleProfileEdit">
                {{ isEditingProfile ? 'Annuler' : 'Modifier mon profil' }}
              </button>
            </div>
            <form v-if="isEditingProfile" class="entry-form" @submit.prevent="saveProfile">
              <div class="user-grid">
                <label class="field-block">
                  <span class="user-label">Âge</span>
                  <input v-model.number="profileForm.age" type="number" min="1" required />
                </label>
                <label class="field-block">
                  <span class="user-label">Sexe</span>
                  <select v-model="profileForm.sexe" required>
                    <option value="H">H</option>
                    <option value="F">F</option>
                    <option value="Autre">Autre</option>
                  </select>
                </label>
                <label class="field-block">
                  <span class="user-label">Taille (cm)</span>
                  <input v-model.number="profileForm.taille_cm" type="number" min="1" required />
                </label>
                <label class="field-block">
                  <span class="user-label">Poids (kg)</span>
                  <input v-model.number="profileForm.poids_kg" type="number" min="1" required />
                </label>
                <label class="field-block">
                  <span class="user-label">Niveau activité</span>
                  <input v-model.number="profileForm.niveau_activite" type="number" min="1" max="5" required />
                </label>
                <label class="field-block">
                  <span class="user-label">Type abonnement</span>
                  <input v-model.number="profileForm.type_abonnement" type="number" min="1" required />
                </label>
                <label class="field-block">
                  <span class="user-label">Date d'inscription</span>
                  <input v-model="profileForm.date_inscription" type="date" required />
                </label>
              </div>
              <div class="form-actions">
                <button class="action-btn" type="submit" :disabled="savingKey === 'profile'">
                  {{ savingKey === 'profile' ? 'Enregistrement...' : 'Enregistrer' }}
                </button>
              </div>
            </form>
            <div v-else class="user-grid">
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
            <div class="section-header">
              <h3>Mesures santé</h3>
              <button class="action-btn" @click="toggleMetricForm()">
                {{ metricForm.id_metrique ? 'Annuler' : 'Ajouter une mesure' }}
              </button>
            </div>
            <form v-if="showMetricForm" class="entry-form" @submit.prevent="saveMetric">
              <div class="user-grid">
                <label class="field-block"><span class="user-label">Date</span><input v-model="metricForm.date_mesure" type="date" required /></label>
                <label class="field-block"><span class="user-label">Poids (kg)</span><input v-model.number="metricForm.poids_kg" type="number" min="0" step="0.1" /></label>
                <label class="field-block"><span class="user-label">Fréquence cardiaque</span><input v-model.number="metricForm.frequence_cardiaque" type="number" min="0" /></label>
                <label class="field-block"><span class="user-label">Sommeil (h)</span><input v-model.number="metricForm.duree_sommeil_h" type="number" min="0" step="0.1" /></label>
                <label class="field-block"><span class="user-label">Calories brûlées</span><input v-model.number="metricForm.calories_brulees" type="number" min="0" /></label>
                <label class="field-block"><span class="user-label">Pas</span><input v-model.number="metricForm.pas" type="number" min="0" /></label>
              </div>
              <div class="form-actions">
                <button class="action-btn" type="submit" :disabled="savingKey === 'metric'">
                  {{ savingKey === 'metric' ? 'Enregistrement...' : (metricForm.id_metrique ? 'Modifier la mesure' : 'Ajouter la mesure') }}
                </button>
              </div>
            </form>
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
                    <th>Actions</th>
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
                    <td><button class="table-action" @click="toggleMetricForm(metric)">Modifier</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Activités -->
          <div v-if="activeTab === 'activites'">
            <div class="section-header">
              <h3>Activités physiques</h3>
              <button class="action-btn" @click="toggleActivityForm()">
                {{ activityForm.id_activite ? 'Annuler' : 'Ajouter une activité' }}
              </button>
            </div>
            <form v-if="showActivityForm" class="entry-form" @submit.prevent="saveActivity">
              <div class="user-grid">
                <label class="field-block"><span class="user-label">Date</span><input v-model="activityForm.date_activite" type="date" required /></label>
                <label class="field-block"><span class="user-label">Durée (min)</span><input v-model.number="activityForm.duree_minutes" type="number" min="1" required /></label>
                <label class="field-block"><span class="user-label">Calories dépensées</span><input v-model.number="activityForm.calories_depensees" type="number" min="0" step="0.1" required /></label>
                <label class="field-block"><span class="user-label">Intensité</span><input v-model="activityForm.intensite" type="text" placeholder="Modérée, intense..." /></label>
                <label class="field-block field-span-2"><span class="user-label">Exercice</span>
                  <select v-model.number="activityForm.id_exercice" required>
                    <option disabled :value="null">Choisir un exercice</option>
                    <option v-for="exercise in exercises" :key="exercise.id_exercice" :value="exercise.id_exercice">{{ exercise.nom_exercice }} · {{ exercise.type_exercice }}</option>
                  </select>
                </label>
              </div>
              <div class="form-actions">
                <button class="action-btn" type="submit" :disabled="savingKey === 'activity'">
                  {{ savingKey === 'activity' ? 'Enregistrement...' : (activityForm.id_activite ? 'Modifier l’activité' : 'Ajouter l’activité') }}
                </button>
              </div>
            </form>
            <div v-if="!userActivities.length" class="user-empty">Aucune activité enregistrée.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Exercice</th>
                    <th>Durée (min)</th>
                    <th>Calories dépensées</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="activity in userActivities" :key="activity.id_activite">
                    <td>{{ formatDate(activity.date_activite) }}</td>
                    <td>{{ getExerciseName(activity.id_exercice) }}</td>
                    <td>{{ activity.duree_minutes }}</td>
                    <td>{{ activity.calories_depensees }} kcal</td>
                    <td><button class="table-action" @click="toggleActivityForm(activity)">Modifier</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Alimentation -->
          <div v-if="activeTab === 'alimentation'">
            <div class="section-header">
              <h3>Alimentation</h3>
              <button class="action-btn" @click="toggleConsumptionForm()">
                {{ consumptionForm.id_consommation ? 'Annuler' : 'Ajouter une consommation' }}
              </button>
            </div>
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
            <form v-if="showConsumptionForm" class="entry-form" @submit.prevent="saveConsumption">
              <div class="user-grid">
                <label class="field-block"><span class="user-label">Date</span><input v-model="consumptionForm.date_consommation" type="date" required /></label>
                <label class="field-block field-span-2"><span class="user-label">Aliment</span>
                  <select v-model.number="consumptionForm.id_aliment" required>
                    <option disabled :value="null">Choisir un aliment</option>
                    <option v-for="aliment in aliments" :key="aliment.id_aliment" :value="aliment.id_aliment">{{ aliment.nom_aliment }} · {{ aliment.calories }} kcal / 100g</option>
                  </select>
                </label>
                <label class="field-block"><span class="user-label">Quantité (g)</span><input v-model.number="consumptionForm.quantite_g" type="number" min="1" step="0.1" required /></label>
                <label class="field-block"><span class="user-label">Calories calculées</span><input v-model.number="consumptionForm.calories_calculees" type="number" min="0" step="0.1" required /></label>
              </div>
              <div class="helper-text" v-if="selectedAliment">Calories suggérées: {{ suggestedConsumptionCalories }} kcal</div>
              <div class="form-actions">
                <button class="action-btn" type="submit" :disabled="savingKey === 'consumption'">
                  {{ savingKey === 'consumption' ? 'Enregistrement...' : (consumptionForm.id_consommation ? 'Modifier la consommation' : 'Ajouter la consommation') }}
                </button>
              </div>
            </form>
            <div v-if="!userConsumptions.length" class="user-empty">Aucune consommation enregistrée.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Aliment</th>
                    <th>Quantité</th>
                    <th>Calories</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="c in userConsumptions" :key="c.id_consommation">
                    <td>{{ formatDate(c.date_consommation) }}</td>
                    <td>{{ getAlimentName(c.id_aliment) }}</td>
                    <td>{{ c.quantite_g }} g</td>
                    <td>{{ c.calories_calculees }} kcal</td>
                    <td><button class="table-action" @click="toggleConsumptionForm(c)">Modifier</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Objectifs -->
          <div v-if="activeTab === 'objectifs'">
            <div class="section-header">
              <h3>Objectifs</h3>
              <button class="action-btn" @click="toggleGoalForm()">
                {{ goalForm.id_objectif ? 'Annuler' : 'Ajouter un objectif' }}
              </button>
            </div>
            <form v-if="showGoalForm" class="entry-form" @submit.prevent="saveGoal">
              <div class="user-grid">
                <label class="field-block"><span class="user-label">Type</span><input v-model="goalForm.type_objectif" type="text" required /></label>
                <label class="field-block"><span class="user-label">Statut</span>
                  <select v-model="goalForm.statut" required>
                    <option value="en_cours">en_cours</option>
                    <option value="termine">termine</option>
                    <option value="en_pause">en_pause</option>
                  </select>
                </label>
                <label class="field-block field-span-2"><span class="user-label">Description</span><textarea v-model="goalForm.description" rows="3" required></textarea></label>
                <label class="field-block"><span class="user-label">Date de début</span><input v-model="goalForm.date_debut" type="date" required /></label>
                <label class="field-block"><span class="user-label">Date de fin</span><input v-model="goalForm.date_fin" type="date" required /></label>
              </div>
              <div class="form-actions">
                <button class="action-btn" type="submit" :disabled="savingKey === 'goal'">
                  {{ savingKey === 'goal' ? 'Enregistrement...' : (goalForm.id_objectif ? 'Modifier l’objectif' : 'Ajouter l’objectif') }}
                </button>
              </div>
            </form>
            <div v-if="!userGoals.length" class="user-empty">Aucun objectif enregistré.</div>
            <div v-else class="table-wrap">
              <table class="simple-table">
                <thead>
                  <tr>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Statut</th>
                    <th>Début</th>
                    <th>Fin</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="goal in userGoals" :key="goal.id_objectif">
                    <td>{{ goal.type_objectif }}</td>
                    <td>{{ goal.description }}</td>
                    <td>
                      <span class="goal-status" :class="goal.statut?.toLowerCase().replace(/\s+/g, '-')">
                        {{ goal.statut }}
                      </span>
                    </td>
                    <td>{{ formatDate(goal.date_debut) }}</td>
                    <td>{{ formatDate(goal.date_fin) }}</td>
                    <td><button class="table-action" @click="toggleGoalForm(goal)">Modifier</button></td>
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
import { defineComponent, computed, ref, onMounted, watch } from 'vue'
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
  intensite?: string | null
  id_exercice: number
  id_utilisateur: number
}

interface Consommation {
  id_consommation: number
  date_consommation: string
  quantite_g: number
  calories_calculees: number
  id_aliment: number
  id_utilisateur: number
}

interface Objectif {
  id_objectif: number
  type_objectif: string
  description: string
  date_debut: string
  date_fin: string
  statut: string
  id_utilisateur: number
}

interface Aliment {
  id_aliment: number
  nom_aliment: string
  calories: number
}

interface Exercice {
  id_exercice: number
  nom_exercice: string
  type_exercice: string
}

interface ProfileForm {
  age: number
  sexe: string
  taille_cm: number
  poids_kg: number
  niveau_activite: number
  type_abonnement: number
  date_inscription: string
}

interface MetricForm {
  id_metrique: number | null
  date_mesure: string
  poids_kg: number | null
  frequence_cardiaque: number | null
  duree_sommeil_h: number | null
  calories_brulees: number | null
  pas: number | null
}

interface ActivityForm {
  id_activite: number | null
  date_activite: string
  duree_minutes: number
  calories_depensees: number
  intensite: string
  id_exercice: number | null
}

interface ConsumptionForm {
  id_consommation: number | null
  date_consommation: string
  quantite_g: number
  calories_calculees: number
  id_aliment: number | null
}

interface GoalForm {
  id_objectif: number | null
  type_objectif: string
  description: string
  date_debut: string
  date_fin: string
  statut: string
}

function today(): string {
  return new Date().toISOString().slice(0, 10)
}

function createProfileForm(profile: UserProfile | null): ProfileForm {
  return {
    age: profile?.age ?? 30,
    sexe: profile?.sexe ?? 'H',
    taille_cm: profile?.taille_cm ?? 170,
    poids_kg: profile?.poids_kg ?? 70,
    niveau_activite: profile?.niveau_activite ?? 1,
    type_abonnement: profile?.type_abonnement ?? 1,
    date_inscription: profile?.date_inscription ?? today()
  }
}

function createMetricForm(metric?: Metrique): MetricForm {
  return {
    id_metrique: metric?.id_metrique ?? null,
    date_mesure: metric?.date_mesure ?? today(),
    poids_kg: metric?.poids_kg ?? null,
    frequence_cardiaque: metric?.frequence_cardiaque ?? null,
    duree_sommeil_h: metric?.duree_sommeil_h ?? null,
    calories_brulees: metric?.calories_brulees ?? null,
    pas: metric?.pas ?? null
  }
}

function createActivityForm(activity?: Activite): ActivityForm {
  return {
    id_activite: activity?.id_activite ?? null,
    date_activite: activity?.date_activite ?? today(),
    duree_minutes: activity?.duree_minutes ?? 30,
    calories_depensees: activity?.calories_depensees ?? 200,
    intensite: activity?.intensite ?? '',
    id_exercice: activity?.id_exercice ?? null
  }
}

function createConsumptionForm(consumption?: Consommation): ConsumptionForm {
  return {
    id_consommation: consumption?.id_consommation ?? null,
    date_consommation: consumption?.date_consommation ?? today(),
    quantite_g: consumption?.quantite_g ?? 100,
    calories_calculees: consumption?.calories_calculees ?? 0,
    id_aliment: consumption?.id_aliment ?? null
  }
}

function createGoalForm(goal?: Objectif): GoalForm {
  return {
    id_objectif: goal?.id_objectif ?? null,
    type_objectif: goal?.type_objectif ?? '',
    description: goal?.description ?? '',
    date_debut: goal?.date_debut ?? today(),
    date_fin: goal?.date_fin ?? today(),
    statut: goal?.statut ?? 'en_cours'
  }
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
    const aliments = ref<Aliment[]>([])
    const exercises = ref<Exercice[]>([])
    const userLoading = ref(false)
    const userError = ref('')
    const userSuccess = ref('')
    const activeTab = ref('profil')
    const savingKey = ref<string | null>(null)
    const isEditingProfile = ref(false)
    const showMetricForm = ref(false)
    const showActivityForm = ref(false)
    const showConsumptionForm = ref(false)
    const showGoalForm = ref(false)
    const profileForm = ref<ProfileForm>(createProfileForm(null))
    const metricForm = ref<MetricForm>(createMetricForm())
    const activityForm = ref<ActivityForm>(createActivityForm())
    const consumptionForm = ref<ConsumptionForm>(createConsumptionForm())
    const goalForm = ref<GoalForm>(createGoalForm())

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

    const totalCaloriesConsumed = computed(() => {
      return Math.round(userConsumptions.value.reduce((sum, c) => sum + (c.calories_calculees || 0), 0))
    })

    const lastConsumptionDate = computed(() => {
      if (!userConsumptions.value.length) return '-'
      return formatDate(userConsumptions.value[0].date_consommation)
    })

    const selectedAliment = computed(() => {
      return aliments.value.find(item => item.id_aliment === consumptionForm.value.id_aliment) ?? null
    })

    const suggestedConsumptionCalories = computed(() => {
      if (!selectedAliment.value) return 0
      return Math.round((selectedAliment.value.calories * consumptionForm.value.quantite_g) / 100)
    })

    async function apiRequest<T>(endpoint: string, token: string, init?: RequestInit): Promise<T> {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: init?.method ?? 'GET',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
          ...(init?.headers ?? {})
        },
        body: init?.body
      })

      if (!response.ok) {
        if (response.status === 401) {
          auth.logout()
          router.push('/connexion')
          throw new Error('Session expirée. Veuillez vous reconnecter.')
        }
        throw new Error(`Erreur ${response.status} sur ${endpoint}`)
      }

      if (response.status === 204) {
        return undefined as T
      }

      return response.json()
    }

    function currentUserId(): number {
      const connectedUser = auth.getCurrentUser()
      return Number(connectedUser?.id)
    }

    function clearFeedback() {
      userError.value = ''
      userSuccess.value = ''
    }

    function getTokenOrThrow(): string {
      const token = auth.getToken()
      if (!token) {
        throw new Error('Session expirée. Veuillez vous reconnecter.')
      }
      return token
    }

    function getExerciseName(id: number): string {
      return exercises.value.find(item => item.id_exercice === id)?.nom_exercice ?? `Exercice #${id}`
    }

    function getAlimentName(id: number): string {
      return aliments.value.find(item => item.id_aliment === id)?.nom_aliment ?? `Aliment #${id}`
    }

    function toggleProfileEdit() {
      isEditingProfile.value = !isEditingProfile.value
      profileForm.value = createProfileForm(userProfile.value)
      clearFeedback()
    }

    function toggleMetricForm(metric?: Metrique) {
      showMetricForm.value = !showMetricForm.value || Boolean(metric)
      metricForm.value = createMetricForm(metric)
      clearFeedback()
    }

    function toggleActivityForm(activity?: Activite) {
      showActivityForm.value = !showActivityForm.value || Boolean(activity)
      activityForm.value = createActivityForm(activity)
      clearFeedback()
    }

    function toggleConsumptionForm(consumption?: Consommation) {
      showConsumptionForm.value = !showConsumptionForm.value || Boolean(consumption)
      consumptionForm.value = createConsumptionForm(consumption)
      clearFeedback()
    }

    function toggleGoalForm(goal?: Objectif) {
      showGoalForm.value = !showGoalForm.value || Boolean(goal)
      goalForm.value = createGoalForm(goal)
      clearFeedback()
    }

    async function saveProfile() {
      try {
        savingKey.value = 'profile'
        clearFeedback()
        const token = getTokenOrThrow()
        const userId = currentUserId()
        await apiRequest(`/utilisateurs/${userId}`, token, {
          method: 'PUT',
          body: JSON.stringify(profileForm.value)
        })
        userSuccess.value = 'Profil mis à jour.'
        isEditingProfile.value = false
        await loadUserData()
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de la mise à jour du profil.'
      } finally {
        savingKey.value = null
      }
    }

    async function saveMetric() {
      try {
        savingKey.value = 'metric'
        clearFeedback()
        const token = getTokenOrThrow()
        const payload = {
          date_mesure: metricForm.value.date_mesure,
          poids_kg: metricForm.value.poids_kg,
          frequence_cardiaque: metricForm.value.frequence_cardiaque,
          duree_sommeil_h: metricForm.value.duree_sommeil_h,
          calories_brulees: metricForm.value.calories_brulees,
          pas: metricForm.value.pas,
          id_utilisateur: currentUserId()
        }
        await apiRequest(metricForm.value.id_metrique ? `/metriques-sante/${metricForm.value.id_metrique}` : '/metriques-sante/', token, {
          method: metricForm.value.id_metrique ? 'PUT' : 'POST',
          body: JSON.stringify(payload)
        })
        userSuccess.value = metricForm.value.id_metrique ? 'Mesure santé modifiée.' : 'Mesure santé ajoutée.'
        showMetricForm.value = false
        metricForm.value = createMetricForm()
        await loadUserData()
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de l’enregistrement de la mesure.'
      } finally {
        savingKey.value = null
      }
    }

    async function saveActivity() {
      try {
        savingKey.value = 'activity'
        clearFeedback()
        const token = getTokenOrThrow()
        const payload = {
          date_activite: activityForm.value.date_activite,
          duree_minutes: activityForm.value.duree_minutes,
          calories_depensees: activityForm.value.calories_depensees,
          intensite: activityForm.value.intensite || null,
          id_exercice: activityForm.value.id_exercice,
          id_utilisateur: currentUserId()
        }
        await apiRequest(activityForm.value.id_activite ? `/activites/${activityForm.value.id_activite}` : '/activites/', token, {
          method: activityForm.value.id_activite ? 'PUT' : 'POST',
          body: JSON.stringify(payload)
        })
        userSuccess.value = activityForm.value.id_activite ? 'Activité modifiée.' : 'Activité ajoutée.'
        showActivityForm.value = false
        activityForm.value = createActivityForm()
        await loadUserData()
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de l’enregistrement de l’activité.'
      } finally {
        savingKey.value = null
      }
    }

    async function saveConsumption() {
      try {
        savingKey.value = 'consumption'
        clearFeedback()
        const token = getTokenOrThrow()
        const payload = {
          date_consommation: consumptionForm.value.date_consommation,
          quantite_g: consumptionForm.value.quantite_g,
          calories_calculees: consumptionForm.value.calories_calculees,
          id_aliment: consumptionForm.value.id_aliment,
          id_utilisateur: currentUserId()
        }
        await apiRequest(consumptionForm.value.id_consommation ? `/consommations/${consumptionForm.value.id_consommation}` : '/consommations/', token, {
          method: consumptionForm.value.id_consommation ? 'PUT' : 'POST',
          body: JSON.stringify(payload)
        })
        userSuccess.value = consumptionForm.value.id_consommation ? 'Consommation modifiée.' : 'Consommation ajoutée.'
        showConsumptionForm.value = false
        consumptionForm.value = createConsumptionForm()
        await loadUserData()
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de l’enregistrement de la consommation.'
      } finally {
        savingKey.value = null
      }
    }

    async function saveGoal() {
      try {
        savingKey.value = 'goal'
        clearFeedback()
        const token = getTokenOrThrow()
        const payload = {
          type_objectif: goalForm.value.type_objectif,
          description: goalForm.value.description,
          date_debut: goalForm.value.date_debut,
          date_fin: goalForm.value.date_fin,
          statut: goalForm.value.statut,
          id_utilisateur: currentUserId()
        }
        await apiRequest(goalForm.value.id_objectif ? `/objectifs/${goalForm.value.id_objectif}` : '/objectifs/', token, {
          method: goalForm.value.id_objectif ? 'PUT' : 'POST',
          body: JSON.stringify(payload)
        })
        userSuccess.value = goalForm.value.id_objectif ? 'Objectif modifié.' : 'Objectif ajouté.'
        showGoalForm.value = false
        goalForm.value = createGoalForm()
        await loadUserData()
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de l’enregistrement de l’objectif.'
      } finally {
        savingKey.value = null
      }
    }

    async function loadUserData() {
      if (isAdmin.value) return

      const token = auth.getToken()
      const userId = currentUserId()

      if (!token || !Number.isFinite(userId)) {
        userError.value = 'Utilisateur non authentifié.'
        return
      }

      try {
        userLoading.value = true
        userError.value = ''

        const [profile, metrics, activities, consumptions, goals, alimentsResponse, exercicesResponse] = await Promise.all([
          apiRequest<UserProfile>(`/utilisateurs/${userId}`, token),
          apiRequest<Metrique[]>('/metriques-sante/', token),
          apiRequest<Activite[]>('/activites/', token),
          apiRequest<Consommation[]>('/consommations/', token),
          apiRequest<Objectif[]>('/objectifs/', token),
          apiRequest<Aliment[]>('/aliments/', token),
          apiRequest<Exercice[]>('/exercices/', token)
        ])

        userProfile.value = profile
        profileForm.value = createProfileForm(profile)
        aliments.value = alimentsResponse
        exercises.value = exercicesResponse
        userMetrics.value = metrics
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_mesure).getTime() - new Date(a.date_mesure).getTime())

        userActivities.value = activities
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_activite).getTime() - new Date(a.date_activite).getTime())

        userConsumptions.value = consumptions
          .filter(item => item.id_utilisateur === userId)
          .sort((a, b) => new Date(b.date_consommation).getTime() - new Date(a.date_consommation).getTime())

        userGoals.value = goals
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

    watch(suggestedConsumptionCalories, (value) => {
      if (!consumptionForm.value.id_consommation && selectedAliment.value) {
        consumptionForm.value.calories_calculees = value
      }
    })

    return {
      isAdmin,
      userProfile,
      userMetrics,
      userActivities,
      userConsumptions,
      userGoals,
      aliments,
      exercises,
      userLoading,
      userError,
      userSuccess,
      activeTab,
      tabs,
      savingKey,
      isEditingProfile,
      showMetricForm,
      showActivityForm,
      showConsumptionForm,
      showGoalForm,
      profileForm,
      metricForm,
      activityForm,
      consumptionForm,
      goalForm,
      totalCaloriesConsumed,
      lastConsumptionDate,
      selectedAliment,
      suggestedConsumptionCalories,
      formatDate,
      getExerciseName,
      getAlimentName,
      toggleProfileEdit,
      toggleMetricForm,
      toggleActivityForm,
      toggleConsumptionForm,
      toggleGoalForm,
      saveProfile,
      saveMetric,
      saveActivity,
      saveConsumption,
      saveGoal
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

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
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

.field-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field-span-2 {
  grid-column: span 2;
}

.entry-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 16px;
  padding: 16px;
  background: #f7f9fc;
  border: 1px solid #e8edf3;
  border-radius: 8px;
}

.entry-form input,
.entry-form select,
.entry-form textarea {
  padding: 10px 12px;
  border: 1px solid #cfd8e3;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  background: #fff;
}

.entry-form textarea {
  resize: vertical;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.action-btn,
.table-action {
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
}

.action-btn {
  padding: 10px 14px;
  background: #2563eb;
  color: #fff;
}

.action-btn:hover {
  background: #1d4ed8;
}

.table-action {
  padding: 6px 10px;
  background: #e8edf3;
  color: #1e3a5f;
}

.table-action:hover {
  background: #d6dfeb;
}

.helper-text {
  margin-top: -8px;
  color: #5a6c7d;
  font-size: 13px;
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

.user-success {
  background: #e8f5e9;
  color: #2e7d32;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 12px;
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
  .field-span-2 {
    grid-column: span 1;
  }
  .nav-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .section-header {
    flex-direction: column;
    align-items: stretch;
  }
}
@media (max-width: 500px) {
  .nav-grid {
    grid-template-columns: 1fr;
  }
}
</style>
