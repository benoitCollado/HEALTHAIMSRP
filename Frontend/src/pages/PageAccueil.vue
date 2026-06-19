<template>
  <div class="canvas nav-page">
    <Navbar
      title="Accueil"
      :page-actions="isAdmin ? [] : userHeaderActions"
      :active-action="activeTab"
      @select-action="activeTab = $event"
    />
    <div id="main-content" class="page-content">
      <!-- Admin view: Navigation -->
      <div v-if="isAdmin" class="admin-home">
        <div class="admin-hero">
          <div>
            <span class="eyebrow">Administration</span>
            <h2>Page d'accueil</h2>
            <p>Bienvenue dans le systeme de gestion des flux HealthAI.</p>
          </div>
        </div>
        <div class="nav-grid">
          <router-link to="/dashboard" class="nav-card">
            <div class="nav-icon">DB</div>
            <div>
              <strong>Dashboard</strong>
              <span>Indicateurs et tendances</span>
            </div>
          </router-link>
          <router-link to="/gestion-des-flux" class="nav-card">
            <div class="nav-icon">FL</div>
            <div>
              <strong>Gestion des flux</strong>
              <span>Imports et pipelines</span>
            </div>
          </router-link>
          <router-link to="/nettoyage" class="nav-card">
            <div class="nav-icon">QA</div>
            <div>
              <strong>Nettoyage</strong>
              <span>Qualite des donnees</span>
            </div>
          </router-link>
          <router-link to="/utilisateurs" class="nav-card">
            <div class="nav-icon">US</div>
            <div>
              <strong>Utilisateurs</strong>
              <span>Comptes et roles</span>
            </div>
          </router-link>
          <router-link to="/test-backend" class="nav-card">
            <div class="nav-icon">API</div>
            <div>
              <strong>Test API</strong>
              <span>Controle backend</span>
            </div>
          </router-link>
        </div>
      </div>

      <!-- User view: Profile -->
      <div v-else class="user-view">
        <div class="user-panel">
          <div v-if="userLoading" class="user-loading">Chargement des données utilisateur...</div>
          <div v-else-if="userError" class="user-error">{{ userError }}</div>
          <template v-else>
          <div v-if="userSuccess" class="user-success">{{ userSuccess }}</div>

          <!-- Tab: Profil -->
          <div v-if="activeTab === 'profil'" class="user-section">
            <div class="section-header">
              <h3>Informations personnelles</h3>
              <button class="action-btn" @click="toggleProfileEdit">
                {{ isEditingProfile ? 'Annuler' : 'Modifier mon profil' }}
              </button>
            </div>
            <div v-if="estimatedDailyCalories" class="calorie-highlight">
              <div>
                <span class="calorie-label">Recommandation calories du jour</span>
                <strong>{{ estimatedDailyCalories.calories }} kcal</strong>
              </div>
              <p>{{ estimatedDailyCalories.detail }}</p>
            </div>
            <div v-if="estimatedDailyCalories" class="calorie-balance-panel">
              <div class="calorie-balance-header">
                <div>
                  <span class="calorie-label">Bilan consommation / depense</span>
                  <strong>{{ dailyNetCalories }} kcal net</strong>
                </div>
                <span class="balance-status" :class="calorieBalanceStatus.className">
                  {{ calorieBalanceStatus.label }}
                </span>
              </div>
              <div class="calorie-balance-grid">
                <div>
                  <span>Jour analyse</span>
                  <strong>{{ latestCalorieDate ? formatDate(latestCalorieDate) : 'Aucune donnee' }}</strong>
                </div>
                <div>
                  <span>Consommees</span>
                  <strong>{{ dailyCaloriesConsumed }} kcal</strong>
                </div>
                <div>
                  <span>Depensees sport</span>
                  <strong>{{ dailyCaloriesSpent }} kcal</strong>
                </div>
                <div>
                  <span>Reste recommande</span>
                  <strong>{{ dailyCaloriesRemaining }} kcal</strong>
                </div>
              </div>
              <p>{{ calorieBalanceStatus.detail }}</p>
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
                  <select v-model.number="profileForm.niveau_activite" required>
                    <option :value="1">Tres faible</option>
                    <option :value="2">Faible</option>
                    <option :value="3">Moderee</option>
                    <option :value="4">Elevee</option>
                    <option :value="5">Tres elevee</option>
                  </select>
                </label>
                <label class="field-block">
                  <span class="user-label">Type abonnement</span>
                  <input v-model.number="profileForm.type_abonnement" type="number" min="1" required />
                </label>
                <label class="field-block">
                  <span class="user-label">Date d'inscription</span>
                  <input v-model="profileForm.date_inscription" type="date" required />
                </label>
                <label v-for="option in goalOptions" :key="option.key" class="field-block checkbox-block">
                  <input v-model="profileForm[option.key]" type="checkbox" />
                  <span class="user-label">{{ option.label }}</span>
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
                <div class="user-value">{{ formatActivityLevel(userProfile?.niveau_activite) }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Type abonnement</div>
                <div class="user-value">{{ userProfile?.type_abonnement ?? '-' }}</div>
              </div>
              <div class="user-card">
                <div class="user-label">Date d'inscription</div>
                <div class="user-value">{{ formatDate(userProfile?.date_inscription) }}</div>
              </div>
              <div v-for="option in goalOptions" :key="option.key" class="user-card">
                <div class="user-label">{{ option.label }}</div>
                <div class="user-value">{{ userProfile?.[option.key] ? 'Oui' : 'Non' }}</div>
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
                    <td data-label="Date">{{ formatDate(metric.date_mesure) }}</td>
                    <td data-label="Poids">{{ metric.poids_kg ?? '-' }}</td>
                    <td data-label="FC">{{ metric.frequence_cardiaque ?? '-' }}</td>
                    <td data-label="Sommeil">{{ metric.duree_sommeil_h ?? '-' }}</td>
                    <td data-label="Calories">{{ metric.calories_brulees ?? '-' }}</td>
                    <td data-label="Pas">{{ metric.pas ?? '-' }}</td>
                    <td data-label="Actions"><button class="table-action" @click="toggleMetricForm(metric)">Modifier</button></td>
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
                    <td data-label="Date">{{ formatDate(activity.date_activite) }}</td>
                    <td data-label="Exercice">{{ getExerciseName(activity.id_exercice) }}</td>
                    <td data-label="Duree">{{ activity.duree_minutes }}</td>
                    <td data-label="Calories">{{ activity.calories_depensees }} kcal</td>
                    <td data-label="Actions"><button class="table-action" @click="toggleActivityForm(activity)">Modifier</button></td>
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
                    <td data-label="Date">{{ formatDate(c.date_consommation) }}</td>
                    <td data-label="Aliment">{{ getAlimentName(c.id_aliment) }}</td>
                    <td data-label="Quantite">{{ c.quantite_g }} g</td>
                    <td data-label="Calories">{{ c.calories_calculees }} kcal</td>
                    <td data-label="Actions"><button class="table-action" @click="toggleConsumptionForm(c)">Modifier</button></td>
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
                    <td data-label="Type">{{ goal.type_objectif }}</td>
                    <td data-label="Description">{{ goal.description }}</td>
                    <td data-label="Statut">
                      <span class="goal-status" :class="goal.statut?.toLowerCase().replace(/\s+/g, '-')">
                        {{ goal.statut }}
                      </span>
                    </td>
                    <td data-label="Debut">{{ formatDate(goal.date_debut) }}</td>
                    <td data-label="Fin">{{ formatDate(goal.date_fin) }}</td>
                    <td data-label="Actions"><button class="table-action" @click="toggleGoalForm(goal)">Modifier</button></td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Tab: Securite A2A / 2FA -->
          <div v-if="activeTab === 'securite'">
            <div class="twofa-panel">
              <div class="section-header">
                <h3>Securite du compte (A2A / 2FA TOTP)</h3>
              </div>

              <div class="twofa-status-row">
                <span class="user-label">Statut 2FA</span>
                <span class="goal-status" :class="twoFactorEnabled ? 'termine' : 'en_pause'">
                  {{ twoFactorEnabled ? 'Activee' : 'Desactivee' }}
                </span>
              </div>

              <p class="helper-text">Comptes existants et nouveaux comptes: 2FA desactivee par defaut.</p>

              <div class="twofa-actions">
                <button
                  v-if="!twoFactorEnabled"
                  class="action-btn"
                  @click="startTwoFactorSetup"
                  :disabled="savingKey === 'twofa'"
                >
                  {{ savingKey === 'twofa' ? 'Preparation...' : 'Configurer la 2FA' }}
                </button>
              </div>

              <div v-if="twoFactorSetupSecret" class="twofa-setup-box">
                <p class="helper-text">
                  1) Scanne l'URL dans Google Authenticator / Authy ou copie la cle secrete.
                </p>
                <div class="user-grid user-grid-2 twofa-grid">
                  <div class="user-card twofa-qr-card">
                    <div class="user-label">QR code</div>
                    <img v-if="twoFactorQrDataUrl" :src="twoFactorQrDataUrl" alt="QR code 2FA" class="twofa-qr" />
                    <div v-else class="user-value">Generation du QR en cours...</div>
                  </div>
                  <div class="user-card">
                    <div class="user-label">Cle secrete</div>
                    <div class="user-value twofa-mono">{{ twoFactorSetupSecret }}</div>
                    <button class="table-action" @click="copyText(twoFactorSetupSecret, 'Cle secrete')">Copier la cle</button>
                  </div>
                  <div class="user-card">
                    <div class="user-label">URL OTPAUTH</div>
                    <div class="user-value twofa-mono">{{ twoFactorProvisioningUri }}</div>
                    <button class="table-action" @click="copyText(twoFactorProvisioningUri, 'URL OTPAUTH')">Copier l'URL</button>
                  </div>
                </div>
                <p class="helper-text">2) Entre le code a 6 chiffres pour activer.</p>
              </div>

              <div v-if="twoFactorSetupSecret || twoFactorEnabled" class="twofa-code-row">
                <input
                  v-model="twoFactorCode"
                  type="text"
                  inputmode="numeric"
                  maxlength="6"
                  placeholder="Code 2FA (6 chiffres)"
                />
                <button
                  v-if="!twoFactorEnabled"
                  class="action-btn"
                  @click="enableTwoFactor"
                  :disabled="savingKey === 'twofa'"
                >
                  Activer
                </button>
                <button
                  v-else
                  class="action-btn danger"
                  @click="disableTwoFactor"
                  :disabled="savingKey === 'twofa'"
                >
                  Desactiver
                </button>
              </div>
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
import QRCode from 'qrcode'
import { estimateDailyCalories, type CalorieProfile } from '../services/calorieCalculator'

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
  destresse: boolean
  sante: boolean
  perte_de_poids: boolean
  performance: boolean
  endurance: boolean
  force: boolean
}

interface TwoFactorStatus {
  enabled: boolean
}

interface TwoFactorSetup {
  enabled: boolean
  secret: string
  provisioning_uri: string
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
  destresse: boolean
  sante: boolean
  perte_de_poids: boolean
  performance: boolean
  endurance: boolean
  force: boolean
}

type GoalFlagKey = 'destresse' | 'sante' | 'perte_de_poids' | 'performance' | 'endurance' | 'force'

const goalOptions: Array<{ key: GoalFlagKey; label: string }> = [
  { key: 'destresse', label: 'Reduire mon stress' },
  { key: 'sante', label: 'Ameliorer ma sante generale' },
  { key: 'perte_de_poids', label: 'Perdre du poids' },
  { key: 'performance', label: 'Ameliorer mes performances sportives' },
  { key: 'endurance', label: 'Gagner en endurance' },
  { key: 'force', label: 'Developper ma force musculaire' }
]

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
    date_inscription: profile?.date_inscription ?? today(),
    destresse: profile?.destresse ?? false,
    sante: profile?.sante ?? false,
    perte_de_poids: profile?.perte_de_poids ?? false,
    performance: profile?.performance ?? false,
    endurance: profile?.endurance ?? false,
    force: profile?.force ?? false
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
    const twoFactorEnabled = ref(false)
    const twoFactorSetupSecret = ref('')
    const twoFactorProvisioningUri = ref('')
    const twoFactorQrDataUrl = ref('')
    const twoFactorCode = ref('')
    const profileForm = ref<ProfileForm>(createProfileForm(null))
    const metricForm = ref<MetricForm>(createMetricForm())
    const activityForm = ref<ActivityForm>(createActivityForm())
    const consumptionForm = ref<ConsumptionForm>(createConsumptionForm())
    const goalForm = ref<GoalForm>(createGoalForm())

    const userHeaderActions = computed(() => [
      { id: 'profil', label: 'Profil' },
      { id: 'sante', label: 'Sante', count: userMetrics.value.length },
      { id: 'activites', label: 'Activites', count: userActivities.value.length },
      { id: 'alimentation', label: 'Alimentation', count: userConsumptions.value.length },
      { id: 'objectifs', label: 'Objectifs', count: userGoals.value.length },
      { id: 'securite', label: 'Securite A2A' }
    ])

    const formatDate = (dateValue?: string) => {
      if (!dateValue) return '-'
      const date = new Date(dateValue)
      if (Number.isNaN(date.getTime())) return '-'
      return date.toLocaleDateString('fr-FR')
    }

    const formatActivityLevel = (level?: number) => {
      const labels: Record<number, string> = {
        1: 'Tres faible',
        2: 'Faible',
        3: 'Moderee',
        4: 'Elevee',
        5: 'Tres elevee'
      }
      return level ? labels[level] ?? '-' : '-'
    }

    const totalCaloriesConsumed = computed(() => {
      return Math.round(userConsumptions.value.reduce((sum, c) => sum + (c.calories_calculees || 0), 0))
    })

    const totalCaloriesSpent = computed(() => {
      return Math.round(userActivities.value.reduce((sum, activity) => sum + (activity.calories_depensees || 0), 0))
    })

    const calorieProfile = computed<CalorieProfile | null>(() => {
      if (isEditingProfile.value) {
        return profileForm.value
      }
      return userProfile.value
    })

    const estimatedDailyCalories = computed(() => estimateDailyCalories(calorieProfile.value))

    const latestCalorieDate = computed(() => {
      const dates = [
        ...userConsumptions.value.map(item => item.date_consommation),
        ...userActivities.value.map(item => item.date_activite)
      ].filter(Boolean)

      if (!dates.length) return ''
      return dates.sort((a, b) => new Date(b).getTime() - new Date(a).getTime())[0]
    })

    const dailyCaloriesConsumed = computed(() => {
      if (!latestCalorieDate.value) return 0
      return Math.round(
        userConsumptions.value
          .filter(item => item.date_consommation === latestCalorieDate.value)
          .reduce((sum, item) => sum + (item.calories_calculees || 0), 0)
      )
    })

    const dailyCaloriesSpent = computed(() => {
      if (!latestCalorieDate.value) return 0
      return Math.round(
        userActivities.value
          .filter(item => item.date_activite === latestCalorieDate.value)
          .reduce((sum, item) => sum + (item.calories_depensees || 0), 0)
      )
    })

    const dailyNetCalories = computed(() => dailyCaloriesConsumed.value - dailyCaloriesSpent.value)

    const dailyCaloriesRemaining = computed(() => {
      if (!estimatedDailyCalories.value) return 0
      return estimatedDailyCalories.value.calories + dailyNetCalories.value
    })

    const calorieBalanceStatus = computed(() => {
      if (!latestCalorieDate.value) {
        return {
          label: 'Aucune donnee',
          className: 'neutral',
          detail: 'Ajoutez une consommation ou une activite pour comparer le bilan au besoin journalier.'
        }
      }

      if (!estimatedDailyCalories.value) {
        return {
          label: 'Profil incomplet',
          className: 'neutral',
          detail: 'Completez le profil pour obtenir une recommandation calories par jour.'
        }
      }

      const remaining = dailyCaloriesRemaining.value
      if (remaining > 150) {
        return {
          label: 'Sous la recommandation',
          className: 'low',
          detail: `Il reste environ ${remaining} kcal avant la recommandation du jour.`
        }
      }

      if (remaining < -150) {
        return {
          label: 'Au-dessus',
          className: 'high',
          detail: `Le bilan depasse la recommandation d'environ ${Math.abs(remaining)} kcal.`
        }
      }

      return {
        label: 'Equilibre',
        className: 'balanced',
        detail: 'Le bilan est proche de la recommandation du jour.'
      }
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

    async function renderTwoFactorQr(uri: string) {
      try {
        twoFactorQrDataUrl.value = await QRCode.toDataURL(uri, {
          width: 220,
          margin: 1
        })
      } catch {
        twoFactorQrDataUrl.value = ''
      }
    }

    async function copyText(value: string, label: string) {
      try {
        await navigator.clipboard.writeText(value)
        userSuccess.value = `${label} copie dans le presse-papiers.`
      } catch {
        userError.value = `Impossible de copier ${label.toLowerCase()}.`
      }
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

    async function startTwoFactorSetup() {
      try {
        savingKey.value = 'twofa'
        clearFeedback()
        const token = getTokenOrThrow()
        const setup = await apiRequest<TwoFactorSetup>('/auth/2fa/setup', token, { method: 'POST' })
        twoFactorSetupSecret.value = setup.secret
        twoFactorProvisioningUri.value = setup.provisioning_uri
        await renderTwoFactorQr(setup.provisioning_uri)
        twoFactorEnabled.value = false
        twoFactorCode.value = ''
        userSuccess.value = 'Configuration creee. Validez avec un code de votre application d\'authentification.'
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de la configuration 2FA.'
      } finally {
        savingKey.value = null
      }
    }

    async function enableTwoFactor() {
      try {
        savingKey.value = 'twofa'
        clearFeedback()
        const token = getTokenOrThrow()
        await apiRequest('/auth/2fa/enable', token, {
          method: 'POST',
          body: JSON.stringify({ code: twoFactorCode.value })
        })
        twoFactorEnabled.value = true
        twoFactorSetupSecret.value = ''
        twoFactorProvisioningUri.value = ''
        twoFactorQrDataUrl.value = ''
        twoFactorCode.value = ''
        userSuccess.value = '2FA activee avec succes.'
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de l\'activation 2FA.'
      } finally {
        savingKey.value = null
      }
    }

    async function disableTwoFactor() {
      try {
        savingKey.value = 'twofa'
        clearFeedback()
        const token = getTokenOrThrow()
        await apiRequest('/auth/2fa/disable', token, {
          method: 'POST',
          body: JSON.stringify({ code: twoFactorCode.value })
        })
        twoFactorEnabled.value = false
        twoFactorSetupSecret.value = ''
        twoFactorProvisioningUri.value = ''
        twoFactorQrDataUrl.value = ''
        twoFactorCode.value = ''
        userSuccess.value = '2FA desactivee.'
      } catch (err) {
        userError.value = err instanceof Error ? err.message : 'Erreur lors de la desactivation 2FA.'
      } finally {
        savingKey.value = null
      }
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

        const [profile, metrics, activities, consumptions, goals, alimentsResponse, exercicesResponse, twoFactorStatus] = await Promise.all([
          apiRequest<UserProfile>(`/utilisateurs/${userId}`, token),
          apiRequest<Metrique[]>('/metriques-sante/', token),
          apiRequest<Activite[]>('/activites/', token),
          apiRequest<Consommation[]>('/consommations/', token),
          apiRequest<Objectif[]>('/objectifs/', token),
          apiRequest<Aliment[]>('/aliments/', token),
          apiRequest<Exercice[]>('/exercices/', token),
          apiRequest<TwoFactorStatus>('/auth/2fa/status', token)
        ])

        userProfile.value = profile
        profileForm.value = createProfileForm(profile)
        twoFactorEnabled.value = Boolean(twoFactorStatus.enabled)
        if (twoFactorEnabled.value) {
          twoFactorSetupSecret.value = ''
          twoFactorProvisioningUri.value = ''
          twoFactorQrDataUrl.value = ''
        }
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
      userHeaderActions,
      goalOptions,
      savingKey,
      isEditingProfile,
      showMetricForm,
      showActivityForm,
      showConsumptionForm,
      showGoalForm,
      twoFactorEnabled,
      twoFactorSetupSecret,
      twoFactorProvisioningUri,
      twoFactorQrDataUrl,
      twoFactorCode,
      profileForm,
      metricForm,
      activityForm,
      consumptionForm,
      goalForm,
      totalCaloriesConsumed,
      totalCaloriesSpent,
      latestCalorieDate,
      dailyCaloriesConsumed,
      dailyCaloriesSpent,
      dailyNetCalories,
      dailyCaloriesRemaining,
      calorieBalanceStatus,
      lastConsumptionDate,
      selectedAliment,
      suggestedConsumptionCalories,
      estimatedDailyCalories,
      formatDate,
      formatActivityLevel,
      getExerciseName,
      getAlimentName,
      toggleProfileEdit,
      toggleMetricForm,
      toggleActivityForm,
      toggleConsumptionForm,
      toggleGoalForm,
      startTwoFactorSetup,
      enableTwoFactor,
      disableTwoFactor,
      copyText,
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
  border: 1px solid rgba(148, 163, 184, 0.20);
  box-shadow: var(--shadow);
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

.calorie-highlight {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin: 12px 0 16px;
  padding: 16px;
  border: 1px solid rgba(22, 163, 74, 0.28);
  border-radius: 8px;
  background: linear-gradient(135deg, #ecfdf5, #eff6ff);
}

.calorie-highlight > div {
  display: grid;
  gap: 4px;
}

.calorie-label {
  color: #166534;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.calorie-highlight strong {
  color: #0f172a;
  font-size: 1.7rem;
  line-height: 1;
}

.calorie-highlight p {
  max-width: 360px;
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
  text-align: right;
}

.calorie-balance-panel {
  display: grid;
  gap: 12px;
  margin: 0 0 18px;
  padding: 16px;
  border: 1px solid rgba(37, 99, 235, 0.22);
  border-radius: 8px;
  background: #f8fbff;
}

.calorie-balance-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.calorie-balance-header > div {
  display: grid;
  gap: 4px;
}

.calorie-balance-header strong {
  color: #0f172a;
  font-size: 1.45rem;
  line-height: 1.1;
}

.calorie-balance-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 10px;
}

.calorie-balance-grid > div {
  display: grid;
  gap: 4px;
  padding: 10px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
  background: #fff;
}

.calorie-balance-grid span {
  color: #64748b;
  font-size: 0.78rem;
  font-weight: 700;
}

.calorie-balance-grid strong {
  color: #0f172a;
  font-size: 1rem;
}

.calorie-balance-panel p {
  margin: 0;
  color: #475569;
  font-size: 0.9rem;
}

.balance-status {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.78rem;
  font-weight: 800;
  white-space: nowrap;
}

.balance-status.low {
  background: #eff6ff;
  color: #1d4ed8;
}

.balance-status.high {
  background: #fef2f2;
  color: #b91c1c;
}

.balance-status.balanced {
  background: #ecfdf5;
  color: #15803d;
}

.balance-status.neutral {
  background: #f1f5f9;
  color: #475569;
}

.user-card,
.user-subpanel {
  padding: 12px;
  background: #f8fbff;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
}

.field-block {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.checkbox-block {
  flex-direction: row;
  align-items: center;
  padding: 10px 12px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  border-radius: 8px;
  background: #fff;
}

.checkbox-block input {
  width: auto;
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

.action-btn.danger {
  background: #b91c1c;
}

.action-btn.danger:hover {
  background: #991b1b;
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

.twofa-panel {
  margin-top: 18px;
  padding: 14px;
  border: 1px solid #e8edf3;
  border-radius: 8px;
  background: #f9fbff;
}

.twofa-status-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.twofa-actions {
  margin-bottom: 12px;
}

.twofa-setup-box {
  margin-bottom: 12px;
}

.twofa-grid {
  align-items: stretch;
}

.twofa-qr-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.twofa-qr {
  width: 220px;
  height: 220px;
  max-width: 100%;
  border: 1px solid #d7e0eb;
  border-radius: 8px;
  background: #fff;
  padding: 6px;
}

.twofa-mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  overflow-wrap: anywhere;
}

.twofa-code-row {
  display: flex;
  gap: 10px;
  align-items: center;
}

.twofa-code-row input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #cfd8e3;
  border-radius: 6px;
  font-size: 14px;
  background: #fff;
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
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  background: #fff;
}

.simple-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.simple-table th,
.simple-table td {
  border-bottom: 1px solid #e8edf3;
  padding: 10px 12px;
  text-align: left;
}

.simple-table th {
  background: #f7f9fc;
  color: var(--gray-500);
  font-size: 0.76rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.user-list {
  margin: 8px 0 0;
  padding-left: 18px;
}

.user-list li {
  margin-bottom: 6px;
}

.admin-home {
  max-width: 980px;
  margin: 0 auto;
}

.admin-hero {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  padding: 26px;
  margin-bottom: 20px;
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  box-shadow: var(--shadow);
}

.admin-hero h2 {
  margin-bottom: 6px;
}

.admin-hero p {
  margin-bottom: 0;
}

.eyebrow {
  display: inline-flex;
  margin-bottom: 8px;
  color: var(--primary-dark);
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
}

.nav-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}
.nav-card {
  display: flex;
  align-items: center;
  gap: 14px;
  min-height: 112px;
  padding: 18px;
  background: rgba(255, 255, 255, 0.94);
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  text-decoration: none;
  color: var(--gray-900);
  box-shadow: var(--shadow-sm);
  transition: transform 0.2s, box-shadow 0.2s, border-color 0.2s;
}
.nav-card:hover {
  transform: translateY(-2px);
  border-color: rgba(37, 99, 235, 0.30);
  box-shadow: var(--shadow);
  text-decoration: none;
}
.nav-icon {
  display: flex;
  flex: 0 0 48px;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  color: var(--primary-dark);
  font-size: 0.78rem;
  font-weight: 900;
  background: linear-gradient(135deg, var(--primary-light), var(--accent-light));
  border: 1px solid rgba(37, 99, 235, 0.14);
  border-radius: 8px;
}

.nav-card strong {
  display: block;
  margin-bottom: 2px;
}

.nav-card span {
  color: var(--gray-500);
  font-size: 0.86rem;
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

  .calorie-highlight {
    align-items: flex-start;
    flex-direction: column;
  }

  .calorie-highlight p {
    max-width: none;
    text-align: left;
  }

  .calorie-balance-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .calorie-balance-grid {
    grid-template-columns: 1fr 1fr;
  }

  .form-actions,
  .twofa-actions,
  .twofa-code-row {
    align-items: stretch;
    flex-direction: column;
  }

  .form-actions button,
  .twofa-actions button,
  .twofa-code-row button {
    width: 100%;
    justify-content: center;
  }
}
@media (max-width: 500px) {
  .user-view {
    max-width: none;
  }

  .calorie-balance-grid {
    grid-template-columns: 1fr;
  }

  .user-panel,
  .admin-hero {
    padding: 16px;
  }

  .entry-form {
    padding: 12px;
  }

  .table-wrap {
    overflow: visible;
    border: 0;
    background: transparent;
    box-shadow: none;
  }

  .simple-table,
  .simple-table tbody,
  .simple-table tr,
  .simple-table td {
    display: block;
    width: 100%;
  }

  .simple-table thead {
    display: none;
  }

  .simple-table {
    border-collapse: separate;
    border-spacing: 0 10px;
  }

  .simple-table tr {
    padding: 10px 12px;
    background: #fff;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
  }

  .simple-table td {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 16px;
    min-height: 34px;
    padding: 8px 0;
    color: var(--gray-900);
    text-align: right;
    border-bottom: 1px solid var(--gray-100);
    overflow-wrap: anywhere;
  }

  .simple-table td:last-child {
    border-bottom: 0;
  }

  .simple-table td::before {
    content: attr(data-label);
    flex: 0 0 38%;
    color: var(--gray-500);
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-align: left;
    text-transform: uppercase;
  }

  .simple-table td[data-label="Actions"] {
    display: block;
    padding-top: 10px;
    text-align: left;
  }

  .simple-table td[data-label="Actions"]::before {
    display: none;
  }

  .table-action {
    width: 100%;
    min-height: 40px;
    justify-content: center;
  }

  .nav-grid {
    grid-template-columns: 1fr;
  }

  .nav-card {
    min-height: auto;
  }
}
</style>
