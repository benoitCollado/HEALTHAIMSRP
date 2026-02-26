<template>
  <div class="test-backend">
    <Navbar title="Test Backend API" />
    
    <!-- Page Title -->
    <h1>🧪 Test Backend API - Exploration Base de Données</h1>

    <!-- Control Buttons Section -->
    <div class="button-section">
      <button @click="testAuth" :disabled="loading" class="btn-test">
        <span>🔐</span> Auth
      </button>
      <button @click="seedTestData" :disabled="loading" class="btn-secondary">
        <span>🌱</span> {{ loading ? 'Remplissage...' : 'Seed' }}
      </button>
      <button @click="loadAllData" :disabled="loading" class="btn-primary">
        <span>📥</span> {{ loading ? 'Chargement...' : 'Load' }}
      </button>
      <button @click="clearAll" class="btn-danger">
        <span>🗑️</span> Clear
      </button>
    </div>

    <!-- Auth Status Bar -->
    <div class="auth-status">
      <span :style="{ color: tokenStatus.valid ? '#28a745' : '#dc3545' }">
        🔑 Token: {{ tokenStatus.valid ? '✓ Valide' : '✗ Absent ou invalide' }}
      </span>
      <span v-if="tokenStatus.user" style="margin-left: 1rem; color: #666;">
        Connecté: <strong>{{ tokenStatus.user }}</strong>
      </span>
    </div>

    <!-- Messages -->
    <div v-if="error" class="error-box">{{ error }}</div>
    <div v-if="success" class="success-box">{{ success }}</div>

    <!-- User Profile Card -->
    <div v-if="currentUser" class="user-profile">
      <div class="profile-header">
        <h2>👤 Mon Profil</h2>
        <span class="role-badge" :class="{ admin: currentUser.is_admin }">
          {{ currentUser.is_admin ? '👨‍💼 Admin' : '👤 Utilisateur' }}
        </span>
      </div>
      <div class="profile-grid">
        <div class="profile-item">
          <label>ID</label>
          <span>{{ currentUser.id_utilisateur }}</span>
        </div>
        <div class="profile-item">
          <label>Nom d'utilisateur</label>
          <span>{{ currentUser.username }}</span>
        </div>
        <div class="profile-item">
          <label>Âge</label>
          <span>{{ currentUser.age || '-' }} ans</span>
        </div>
        <div class="profile-item">
          <label>Sexe</label>
          <span>{{ currentUser.sexe || '-' }}</span>
        </div>
        <div class="profile-item">
          <label>Taille</label>
          <span>{{ currentUser.taille_cm ? currentUser.taille_cm + ' cm' : '-' }}</span>
        </div>
        <div class="profile-item">
          <label>Poids</label>
          <span>{{ currentUser.poids_kg ? currentUser.poids_kg + ' kg' : '-' }}</span>
        </div>
        <div class="profile-item">
          <label>Niveau activité</label>
          <span>{{ currentUser.niveau_activite ?? '-' }}</span>
        </div>
        <div class="profile-item">
          <label>Abonnement</label>
          <span>{{ currentUser.type_abonnement ?? '-' }}</span>
        </div>
        <div class="profile-item">
          <label>Inscrit depuis</label>
          <span>{{ formatDate(currentUser.date_inscription) }}</span>
        </div>
      </div>
    </div>

    <div v-if="currentUser" class="user-metrics-card">
      <div class="user-metrics-header">
        <h2>📊 Mesures santé (utilisateur connecté)</h2>
        <span class="count-small">{{ userMetrics.length }} mesure(s)</span>
      </div>

      <div v-if="userMetricsLoading" class="user-metrics-empty">Chargement des mesures...</div>
      <div v-else-if="!userMetrics.length" class="user-metrics-empty">
        Aucune mesure trouvée pour l'utilisateur ID {{ currentUser.id_utilisateur }}.
      </div>
      <div v-else class="metrics-table-wrapper">
        <table class="metrics-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Poids (kg)</th>
              <th>FC</th>
              <th>Sommeil (h)</th>
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

    <div v-if="currentUser" class="user-metrics-card">
      <div class="user-metrics-header">
        <h2>🏃 Activités (utilisateur connecté)</h2>
        <span class="count-small">{{ userActivities.length }} activité(s)</span>
      </div>

      <div v-if="userActivitiesLoading" class="user-metrics-empty">Chargement des activités...</div>
      <div v-else-if="!userActivities.length" class="user-metrics-empty">
        Aucune activité trouvée pour l'utilisateur ID {{ currentUser.id_utilisateur }}.
      </div>
      <div v-else class="metrics-table-wrapper">
        <table class="metrics-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Durée (min)</th>
              <th>Calories</th>
              <th>Intensité</th>
              <th>Exercice ID</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="activity in userActivities" :key="activity.id_activite">
              <td>{{ formatDate(activity.date_activite) }}</td>
              <td>{{ activity.duree_minutes ?? '-' }}</td>
              <td>{{ activity.calories_depensees ?? '-' }}</td>
              <td>{{ activity.intensite || '-' }}</td>
              <td>{{ activity.id_exercice }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="currentUser" class="user-metrics-card">
      <div class="user-metrics-header">
        <h2>🍽️ Consommations (utilisateur connecté)</h2>
        <span class="count-small">{{ userConsumptions.length }} consommation(s)</span>
      </div>

      <div v-if="userConsumptionsLoading" class="user-metrics-empty">Chargement des consommations...</div>
      <div v-else-if="!userConsumptions.length" class="user-metrics-empty">
        Aucune consommation trouvée pour l'utilisateur ID {{ currentUser.id_utilisateur }}.
      </div>
      <div v-else class="metrics-table-wrapper">
        <table class="metrics-table">
          <thead>
            <tr>
              <th>Date</th>
              <th>Quantité (g)</th>
              <th>Calories</th>
              <th>Aliment ID</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="consumption in userConsumptions" :key="consumption.id_consommation">
              <td>{{ formatDate(consumption.date_consommation) }}</td>
              <td>{{ consumption.quantite_g ?? '-' }}</td>
              <td>{{ consumption.calories_calculees ?? '-' }}</td>
              <td>{{ consumption.id_aliment }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="currentUser" class="user-metrics-card">
      <div class="user-metrics-header">
        <h2>🎯 Objectifs (utilisateur connecté)</h2>
        <span class="count-small">{{ userGoals.length }} objectif(s)</span>
      </div>

      <div v-if="userGoalsLoading" class="user-metrics-empty">Chargement des objectifs...</div>
      <div v-else-if="!userGoals.length" class="user-metrics-empty">
        Aucun objectif trouvé pour l'utilisateur ID {{ currentUser.id_utilisateur }}.
      </div>
      <div v-else class="metrics-table-wrapper">
        <table class="metrics-table">
          <thead>
            <tr>
              <th>Type</th>
              <th>Description</th>
              <th>Début</th>
              <th>Fin</th>
              <th>Statut</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="goal in userGoals" :key="goal.id_objectif">
              <td>{{ goal.type_objectif }}</td>
              <td>{{ goal.description }}</td>
              <td>{{ formatDate(goal.date_debut) }}</td>
              <td>{{ formatDate(goal.date_fin) }}</td>
              <td>{{ goal.statut }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- GROUP 1: Gestion des Utilisateurs -->
    <div class="group">
      <div class="group-header" @click="toggleGroup('users')">
        <span class="toggle">{{ openGroups.users ? '▼' : '▶' }}</span>
        <h2>👥 Gestion des Utilisateurs</h2>
        <span class="count-small">({{ responses.utilisateurs?.length || 0 }})</span>
      </div>
      <div v-if="openGroups.users" class="group-content">
        <div class="section-row">
          <div class="section-item">
            <h3>📋 Utilisateurs</h3>
            <p class="schema">id_utilisateur, username, age, sexe, taille_cm, poids_kg, is_admin, date_inscription</p>
            <button @click="loadEndpoint('utilisateurs', '/utilisateurs/')">📥 Charger</button>
            <pre v-if="responses.utilisateurs">{{ JSON.stringify(responses.utilisateurs, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- GROUP 2: Alimentation -->
    <div class="group">
      <div class="group-header" @click="toggleGroup('nutrition')">
        <span class="toggle">{{ openGroups.nutrition ? '▼' : '▶' }}</span>
        <h2>🍽️ Alimentation</h2>
        <span class="count-small">(A: {{ responses.aliments?.length || 0 }}, C: {{ responses.consommations?.length || 0 }})</span>
      </div>
      <div v-if="openGroups.nutrition" class="group-content">
        <div class="section-row">
          <div class="section-item">
            <h3>🍎 Aliments</h3>
            <p class="schema">id_aliment, nom_aliment, calories, proteines_g, glucides_g, lipides_g, categorie</p>
            <button @click="loadEndpoint('aliments', '/aliments/')">📥 Charger</button>
            <pre v-if="responses.aliments">{{ JSON.stringify(responses.aliments, null, 2) }}</pre>
          </div>
          <div class="section-item">
            <h3>🔄 Consommations</h3>
            <p class="schema">id_consommation, date_consommation, quantite_g, calories_calculees, id_aliment, id_utilisateur</p>
            <button @click="loadEndpoint('consommations', '/consommations/')">📥 Charger</button>
            <pre v-if="responses.consommations">{{ JSON.stringify(responses.consommations, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- GROUP 3: Activité & Exercices -->
    <div class="group">
      <div class="group-header" @click="toggleGroup('activity')">
        <span class="toggle">{{ openGroups.activity ? '▼' : '▶' }}</span>
        <h2>⚡ Activité & Exercices</h2>
        <span class="count-small">(E: {{ responses.exercices?.length || 0 }}, A: {{ responses.activites?.length || 0 }})</span>
      </div>
      <div v-if="openGroups.activity" class="group-content">
        <div class="section-row">
          <div class="section-item">
            <h3>💪 Exercices</h3>
            <p class="schema">id_exercice, nom_exercice, type_exercice, niveau_difficulte, equipement, muscle_principal</p>
            <button @click="loadEndpoint('exercices', '/exercices/')">📥 Charger</button>
            <pre v-if="responses.exercices">{{ JSON.stringify(responses.exercices, null, 2) }}</pre>
          </div>
          <div class="section-item">
            <h3>🏃 Activités</h3>
            <p class="schema">id_activite, date_activite, duree_minutes, calories_depensees, intensite, id_exercice, id_utilisateur</p>
            <button @click="loadEndpoint('activites', '/activites/')">📥 Charger</button>
            <pre v-if="responses.activites">{{ JSON.stringify(responses.activites, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>

    <!-- GROUP 4: Santé & Objectifs -->
    <div class="group">
      <div class="group-header" @click="toggleGroup('health')">
        <span class="toggle">{{ openGroups.health ? '▼' : '▶' }}</span>
        <h2>❤️ Santé & Objectifs</h2>
        <span class="count-small">(M: {{ responses.metriques?.length || 0 }}, O: {{ responses.objectifs?.length || 0 }})</span>
      </div>
      <div v-if="openGroups.health" class="group-content">
        <div class="section-row">
          <div class="section-item">
            <h3>❤️ Métriques Santé</h3>
            <p class="schema">id_metrique, date_mesure, poids_kg, frequence_cardiaque, duree_sommeil_h, calories_brulees, pas, id_utilisateur</p>
            <button @click="loadEndpoint('metriques', '/metriques-sante/')">📥 Charger</button>
            <pre v-if="responses.metriques">{{ JSON.stringify(responses.metriques, null, 2) }}</pre>
          </div>
          <div class="section-item">
            <h3>🎯 Objectifs</h3>
            <p class="schema">id_objectif, type_objectif, description, date_debut, date_fin, statut, id_utilisateur</p>
            <button @click="loadEndpoint('objectifs', '/objectifs/')">📥 Charger</button>
            <pre v-if="responses.objectifs">{{ JSON.stringify(responses.objectifs, null, 2) }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Navbar from '../components/Navbar.vue';
import { auth } from '../services/auth';
import { API_BASE_URL } from '../config';

interface Response {
  utilisateurs?: any[];
  aliments?: any[];
  exercices?: any[];
  activites?: any[];
  consommations?: any[];
  objectifs?: any[];
  metriques?: any[];
}

interface User {
  id_utilisateur: number;
  username: string;
  age?: number;
  sexe?: string;
  taille_cm?: number;
  poids_kg?: number;
  niveau_activite?: number;
  type_abonnement?: number;
  is_admin: boolean;
  date_inscription: string;
}

interface MetriqueSante {
  id_metrique: number;
  date_mesure: string;
  poids_kg?: number;
  frequence_cardiaque?: number;
  duree_sommeil_h?: number;
  calories_brulees?: number;
  pas?: number;
  id_utilisateur: number;
}

interface Activite {
  id_activite: number;
  date_activite: string;
  duree_minutes: number;
  calories_depensees: number;
  intensite?: string;
  id_exercice: number;
  id_utilisateur: number;
}

interface Consommation {
  id_consommation: number;
  date_consommation: string;
  quantite_g: number;
  calories_calculees: number;
  id_aliment: number;
  id_utilisateur: number;
}

interface Objectif {
  id_objectif: number;
  type_objectif: string;
  description: string;
  date_debut: string;
  date_fin: string;
  statut: string;
  id_utilisateur: number;
}

const loading = ref(false);
const error = ref('');
const success = ref('');
const responses = ref<Response>({});
const tokenStatus = ref({ valid: false, user: '' });
const currentUser = ref<User | null>(null);
const userMetrics = ref<MetriqueSante[]>([]);
const userMetricsLoading = ref(false);
const userActivities = ref<Activite[]>([]);
const userActivitiesLoading = ref(false);
const userConsumptions = ref<Consommation[]>([]);
const userConsumptionsLoading = ref(false);
const userGoals = ref<Objectif[]>([]);
const userGoalsLoading = ref(false);
const openGroups = ref({
  users: true,
  nutrition: false,
  activity: false,
  health: false
});

const toggleGroup = (group: keyof typeof openGroups.value) => {
  openGroups.value[group] = !openGroups.value[group];
};

const formatDate = (dateStr: string) => {
  const date = new Date(dateStr);
  return date.toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
};

const loadUserMetrics = async (userId: number, token: string) => {
  try {
    userMetricsLoading.value = true;

    const response = await fetch(`${API_BASE_URL}/metriques-sante/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return;
    }

    const metrics = await response.json() as MetriqueSante[];
    userMetrics.value = metrics
      .filter((metric) => metric.id_utilisateur === userId)
      .sort((a, b) => new Date(b.date_mesure).getTime() - new Date(a.date_mesure).getTime());
  } catch (err) {
    console.error('Erreur chargement mesures santé:', err);
  } finally {
    userMetricsLoading.value = false;
  }
};

const loadUserActivities = async (userId: number, token: string) => {
  try {
    userActivitiesLoading.value = true;

    const response = await fetch(`${API_BASE_URL}/activites/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return;
    }

    const activities = await response.json() as Activite[];
    userActivities.value = activities
      .filter((activity) => activity.id_utilisateur === userId)
      .sort((a, b) => new Date(b.date_activite).getTime() - new Date(a.date_activite).getTime());
  } catch (err) {
    console.error('Erreur chargement activités:', err);
  } finally {
    userActivitiesLoading.value = false;
  }
};

const loadUserConsumptions = async (userId: number, token: string) => {
  try {
    userConsumptionsLoading.value = true;

    const response = await fetch(`${API_BASE_URL}/consommations/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return;
    }

    const consumptions = await response.json() as Consommation[];
    userConsumptions.value = consumptions
      .filter((consumption) => consumption.id_utilisateur === userId)
      .sort((a, b) => new Date(b.date_consommation).getTime() - new Date(a.date_consommation).getTime());
  } catch (err) {
    console.error('Erreur chargement consommations:', err);
  } finally {
    userConsumptionsLoading.value = false;
  }
};

const loadUserGoals = async (userId: number, token: string) => {
  try {
    userGoalsLoading.value = true;

    const response = await fetch(`${API_BASE_URL}/objectifs/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      return;
    }

    const goals = await response.json() as Objectif[];
    userGoals.value = goals
      .filter((goal) => goal.id_utilisateur === userId)
      .sort((a, b) => new Date(b.date_debut).getTime() - new Date(a.date_debut).getTime());
  } catch (err) {
    console.error('Erreur chargement objectifs:', err);
  } finally {
    userGoalsLoading.value = false;
  }
};

const loadCurrentUser = async () => {
  try {
    const token = auth.getToken();
    if (!token) {
      error.value = 'Aucun token trouvé.';
      return;
    }

    // Get the user ID from token
    const parts = token.split('.');
    if (parts.length !== 3) return;
    const decoded = JSON.parse(atob(parts[1]));
    const userId = Number(decoded.sub);
    if (!Number.isFinite(userId)) return;

    // Fetch user details
    const response = await fetch(`${API_BASE_URL}/utilisateurs/${userId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      currentUser.value = await response.json();
      await loadUserMetrics(userId, token);
      await loadUserActivities(userId, token);
      await loadUserConsumptions(userId, token);
      await loadUserGoals(userId, token);
    }
  } catch (err) {
    console.error('Erreur chargement profil:', err);
  }
};

const testAuth = async () => {
  try {
    error.value = '';
    success.value = '';
    
    const token = auth.getToken();
    if (!token) {
      tokenStatus.value = { valid: false, user: '' };
      error.value = 'Aucun token trouvé. Veuillez vous connecter.';
      return;
    }

    const response = await fetch(`${API_BASE_URL}/utilisateurs/`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      const decoded = decodeToken(token);
      if (decoded) {
        tokenStatus.value = {
          valid: true,
          user: decoded.sub ? `ID: ${decoded.sub}${decoded.is_admin ? ' (Admin)' : ''}` : 'Unknown'
        };
        success.value = `✓ Auth OK! Payload: sub=${decoded.sub}, is_admin=${decoded.is_admin}. ${data.length} utilisateurs en base.`;
      } else {
        tokenStatus.value = { valid: false, user: '' };
        error.value = 'Token invalide ou non décodable';
      }
    } else {
      tokenStatus.value = { valid: false, user: '' };
      error.value = `Erreur ${response.status}: ${response.statusText}`;
    }
  } catch (err) {
    error.value = `Erreur: ${err instanceof Error ? err.message : String(err)}`;
  }
};

const loadEndpoint = async (key: keyof Response, endpoint: string) => {
  try {
    error.value = '';
    success.value = '';
    loading.value = true;

    const token = auth.getToken();
    if (!token) {
      error.value = 'Aucun token trouvé. Veuillez vous connecter.';
      return;
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      const data = await response.json();
      responses.value[key] = data;
      success.value = `✓ Chargé: ${endpoint} (${data.length || 0} éléments)`;
    } else {
      error.value = `Erreur ${response.status} sur ${endpoint}: ${response.statusText}`;
    }
  } catch (err) {
    error.value = `Erreur: ${err instanceof Error ? err.message : String(err)}`;
  } finally {
    loading.value = false;
  }
};

const loadAllData = async () => {
  try {
    error.value = '';
    success.value = '';
    loading.value = true;

    const endpoints = [
      ['utilisateurs', '/utilisateurs/'] as const,
      ['aliments', '/aliments/'] as const,
      ['exercices', '/exercices/'] as const,
      ['consommations', '/consommations/'] as const,
      ['activites', '/activites/'] as const,
      ['objectifs', '/objectifs/'] as const,
      ['metriques', '/metriques-sante/'] as const
    ];

    const token = auth.getToken();
    if (!token) {
      error.value = 'Aucun token trouvé. Veuillez vous connecter.';
      return;
    }

    for (const [key, endpoint] of endpoints) {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        responses.value[key] = data;
      }
    }

    success.value = '✓ Tous les endpoints chargés!';
  } catch (err) {
    error.value = `Erreur: ${err instanceof Error ? err.message : String(err)}`;
  } finally {
    loading.value = false;
  }
};

const seedTestData = async () => {
  if (!confirm('Êtes-vous sûr de vouloir ajouter les données de test?')) {
    return;
  }

  try {
    error.value = '';
    success.value = '';
    loading.value = true;

    const token = auth.getToken();
    if (!token) {
      error.value = 'Aucun token trouvé. Veuillez vous connecter.';
      return;
    }

    const response = await fetch(`${API_BASE_URL}/seed/populate`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });

    if (response.ok) {
      success.value = '✓ Données de test ajoutées! Cliquez sur "Charger TOUT" pour les voir.';
    } else {
      error.value = `Erreur ${response.status}: ${response.statusText}`;
    }
  } catch (err) {
    error.value = `Erreur: ${err instanceof Error ? err.message : String(err)}`;
  } finally {
    loading.value = false;
  }
};

const clearAll = () => {
  if (!confirm('Êtes-vous sûr de vouloir effacer les données affichées?')) {
    return;
  }
  responses.value = {};
  userMetrics.value = [];
  userActivities.value = [];
  userConsumptions.value = [];
  userGoals.value = [];
  error.value = '';
  success.value = '';
};

const decodeToken = (token: string) => {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) return null;
    const decoded = JSON.parse(atob(parts[1]));
    return decoded;
  } catch {
    return null;
  }
};

onMounted(() => {
  testAuth();
  loadCurrentUser();
});
</script>


<style scoped>
.test-backend {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: #ffffff;
}

h1 {
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 1rem;
  margin-bottom: 1.5rem;
  margin-top: 1rem;
}

/* Controls - FIXED, NOT STICKY */
.sticky-controls {
  background: white;
  padding: 1rem 0;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 2rem;
}

.auth-status {
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 8px;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 2rem;
  font-size: 0.95em;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.controls {
  margin: 1rem 0 2rem 0;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 0;
  background: transparent;
  border-radius: 0;
}

.button-section {
  margin: 1.5rem 0;
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

button {
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.3);
}

.btn-secondary {
  background: linear-gradient(135deg, #28a745 0%, #218838 100%);
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(40, 167, 69, 0.3);
}

.btn-test {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  color: white;
}

.btn-test:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(23, 162, 184, 0.3);
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(220, 53, 69, 0.3);
}

.error-box {
  padding: 1rem;
  background: linear-gradient(135deg, #f8d7da 0%, #f5c6cb 100%);
  color: #721c24;
  border-left: 4px solid #dc3545;
  border-radius: 6px;
  margin: 0.5rem 0;
  animation: slideDown 0.3s ease;
}

.success-box {
  padding: 1rem;
  background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%);
  color: #155724;
  border-left: 4px solid #28a745;
  border-radius: 6px;
  margin: 0.5rem 0;
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* User Profile Card */
.user-profile {
  margin: 2rem 0;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f0f4ff 0%, #e0e7ff 100%);
  border-radius: 12px;
  border-left: 4px solid #007bff;
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.15);
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  border-bottom: 2px solid rgba(0, 123, 255, 0.2);
  padding-bottom: 1rem;
}

.profile-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.3em;
}

.role-badge {
  padding: 0.5rem 1rem;
  background: #e7f3ff;
  color: #0056b3;
  border-radius: 20px;
  font-weight: 600;
  font-size: 0.9em;
}

.role-badge.admin {
  background: #fff3cd;
  color: #856404;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
}

.profile-item {
  background: white;
  padding: 1rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.profile-item label {
  display: block;
  color: #666;
  font-size: 0.85em;
  font-weight: 600;
  margin-bottom: 0.5rem;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.profile-item span {
  display: block;
  color: #333;
  font-size: 1.1em;
  font-weight: 500;
}

.user-metrics-card {
  margin: 1.5rem 0 2rem 0;
  padding: 1.5rem;
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.user-metrics-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.user-metrics-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.1em;
}

.user-metrics-empty {
  padding: 1rem;
  background: #f8f9fa;
  color: #666;
  border-radius: 8px;
}

.metrics-table-wrapper {
  overflow-x: auto;
}

.metrics-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.92em;
}

.metrics-table th,
.metrics-table td {
  text-align: left;
  padding: 0.75rem;
  border-bottom: 1px solid #e9ecef;
}

.metrics-table th {
  background: #f8f9fa;
  color: #333;
  font-weight: 700;
}

.metrics-table tbody tr:hover {
  background: #fafcff;
}

/* Group Styles */
.group {
  margin-bottom: 1.5rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.group-header {
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-bottom: 2px solid #dee2e6;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 1rem;
  user-select: none;
  transition: all 0.2s;
}

.group-header:hover {
  background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
}

.group-header h2 {
  margin: 0;
  flex: 1;
  color: #333;
  font-size: 1.2em;
}

.toggle {
  font-size: 1.2em;
  color: #007bff;
  transition: transform 0.2s;
  min-width: 20px;
}

.count-small {
  font-size: 0.85em;
  background: #007bff;
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  white-space: nowrap;
}

.group-content {
  padding: 1.5rem;
  animation: expandDown 0.3s ease;
}

@keyframes expandDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.section-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 2rem;
}

.section-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 4px solid #007bff;
}

.section-item h3 {
  margin-top: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.section-item button {
  background: #007bff;
  color: white;
  margin: 1rem 0;
  display: inline-flex;
}

.section-item button:hover:not(:disabled) {
  background: #0056b3;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 123, 255, 0.2);
}

.schema {
  font-size: 0.85em;
  color: #666;
  margin: 0.75rem 0;
  padding: 0.75rem;
  background: white;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  border: 1px solid #ddd;
  overflow-x: auto;
}

pre {
  background: #f8f9fa;
  padding: 1rem;
  border-radius: 6px;
  overflow-x: auto;
  border: 1px solid #dee2e6;
  max-height: 300px;
  overflow-y: auto;
  font-size: 0.8em;
  margin: 0;
  color: #333;
}

pre::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

pre::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

pre::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

pre::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Responsive */
@media (max-width: 768px) {
  .section-row {
    grid-template-columns: 1fr;
  }
  
  .controls {
    flex-direction: column;
  }
  
  button {
    width: 100%;
    justify-content: center;
  }

  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>
