<template>
  <div class="canvas" role="main" aria-label="Détail des données utilisateur">
    <Navbar :title="`Utilisateur : ${data?.utilisateur?.username ?? '...'}`" />
    <div id="main-content" class="detail-container">
      <div v-if="loading" class="loading" role="status" aria-live="polite">
        Chargement des données...
      </div>
      <div v-if="error" class="error" role="alert">
        {{ error }}
      </div>

      <template v-if="data && !loading">
        <section class="card" aria-labelledby="profil-title">
          <div class="header-row">
            <h2 id="profil-title">Profil : {{ data.utilisateur.username }}</h2>
            <div class="header-actions">
              <button type="button" class="btn btn-secondary" @click="toggleEdit">
                {{ isEditing ? 'Annuler' : 'Modifier' }}
              </button>
              <button type="button" class="btn btn-danger" :disabled="deleting" @click="removeUser">
                {{ deleting ? 'Suppression...' : 'Supprimer' }}
              </button>
              <router-link to="/utilisateurs" class="btn btn-back" aria-label="Retour à la liste des utilisateurs">
                ← Retour
              </router-link>
            </div>
          </div>
          <div v-if="successMessage" class="success" role="status" aria-live="polite">
            {{ successMessage }}
          </div>

          <form v-if="isEditing" class="edit-form" @submit.prevent="saveUser">
            <div class="profil-grid">
              <label class="profil-item">
                <span class="label">Âge</span>
                <input v-model.number="editForm.age" type="number" min="1" required />
              </label>
              <label class="profil-item">
                <span class="label">Sexe</span>
                <select v-model="editForm.sexe" required>
                  <option value="H">H</option>
                  <option value="F">F</option>
                  <option value="Autre">Autre</option>
                </select>
              </label>
              <label class="profil-item">
                <span class="label">Taille</span>
                <input v-model.number="editForm.taille_cm" type="number" min="1" required />
              </label>
              <label class="profil-item">
                <span class="label">Poids</span>
                <input v-model.number="editForm.poids_kg" type="number" min="1" required />
              </label>
              <label class="profil-item">
                <span class="label">Niveau d'activité</span>
                <input v-model.number="editForm.niveau_activite" type="number" min="1" max="5" required />
              </label>
              <label class="profil-item">
                <span class="label">Type d'abonnement</span>
                <input v-model.number="editForm.type_abonnement" type="number" min="1" required />
              </label>
              <label class="profil-item">
                <span class="label">Inscription</span>
                <input v-model="editForm.date_inscription" type="date" required />
              </label>
            </div>
            <div class="form-actions">
              <button type="submit" class="btn" :disabled="saving">
                {{ saving ? 'Enregistrement...' : 'Enregistrer' }}
              </button>
            </div>
          </form>

          <div v-else class="profil-grid">
            <div class="profil-item"><span class="label">ID</span><span class="value">{{ data.utilisateur.id_utilisateur }}</span></div>
            <div class="profil-item"><span class="label">Âge</span><span class="value">{{ data.utilisateur.age }} ans</span></div>
            <div class="profil-item"><span class="label">Sexe</span><span class="value">{{ data.utilisateur.sexe }}</span></div>
            <div class="profil-item"><span class="label">Taille</span><span class="value">{{ data.utilisateur.taille_cm }} cm</span></div>
            <div class="profil-item"><span class="label">Poids</span><span class="value">{{ data.utilisateur.poids_kg }} kg</span></div>
            <div class="profil-item"><span class="label">Inscription</span><span class="value">{{ data.utilisateur.date_inscription }}</span></div>
          </div>
        </section>

        <section class="card" aria-labelledby="cons-title">
          <h2 id="cons-title">Consommations ({{ data.consommations.length }})</h2>
          <div v-if="data.consommations.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Quantité (g)</th>
                  <th scope="col">Calories</th>
                  <th scope="col">ID aliment</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="c in data.consommations" :key="c.id_consommation">
                  <td>{{ c.date_consommation }}</td>
                  <td>{{ c.quantite_g }}</td>
                  <td>{{ c.calories_calculees }}</td>
                  <td>{{ c.id_aliment }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucune consommation</p>
        </section>

        <section class="card" aria-labelledby="act-title">
          <h2 id="act-title">Activités ({{ data.activites.length }})</h2>
          <div v-if="data.activites.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Durée (min)</th>
                  <th scope="col">Calories dépensées</th>
                  <th scope="col">ID exercice</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in data.activites" :key="a.id_activite">
                  <td>{{ a.date_activite }}</td>
                  <td>{{ a.duree_minutes }}</td>
                  <td>{{ a.calories_depensees }}</td>
                  <td>{{ a.id_exercice }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucune activité</p>
        </section>

        <section class="card" aria-labelledby="met-title">
          <h2 id="met-title">Métriques santé ({{ data.metriques.length }})</h2>
          <div v-if="data.metriques.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Date</th>
                  <th scope="col">Poids (kg)</th>
                  <th scope="col">FC</th>
                  <th scope="col">Sommeil (h)</th>
                  <th scope="col">Pas</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in data.metriques" :key="m.id_metrique">
                  <td>{{ m.date_mesure }}</td>
                  <td>{{ m.poids_kg ?? '-' }}</td>
                  <td>{{ m.frequence_cardiaque ?? '-' }}</td>
                  <td>{{ m.duree_sommeil_h ?? '-' }}</td>
                  <td>{{ m.pas ?? '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucune métrique</p>
        </section>

        <section class="card" aria-labelledby="obj-title">
          <h2 id="obj-title">Objectifs ({{ data.objectifs.length }})</h2>
          <div v-if="data.objectifs.length" class="table-wrapper">
            <table class="table" role="table">
              <thead>
                <tr>
                  <th scope="col">Type</th>
                  <th scope="col">Description</th>
                  <th scope="col">Début</th>
                  <th scope="col">Fin</th>
                  <th scope="col">Statut</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="o in data.objectifs" :key="o.id_objectif">
                  <td>{{ o.type_objectif }}</td>
                  <td>{{ o.description }}</td>
                  <td>{{ o.date_debut }}</td>
                  <td>{{ o.date_fin }}</td>
                  <td>{{ o.statut }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <p v-else class="empty-msg">Aucun objectif</p>
        </section>
      </template>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, watch, computed } from 'vue'
import Navbar from '../components/Navbar.vue'
import { useRoute, useRouter } from 'vue-router'
import {
  deleteUtilisateur,
  getUtilisateurDonnees,
  updateUtilisateur,
  type UtilisateurDonnees,
  type UtilisateurUpdatePayload
} from '../services/adminApi'

function toEditForm(data: UtilisateurDonnees): UtilisateurUpdatePayload {
  return {
    age: data.utilisateur.age,
    sexe: data.utilisateur.sexe,
    taille_cm: data.utilisateur.taille_cm,
    poids_kg: data.utilisateur.poids_kg,
    niveau_activite: data.utilisateur.niveau_activite,
    type_abonnement: data.utilisateur.type_abonnement,
    date_inscription: data.utilisateur.date_inscription
  }
}

async function loadUser(id: number, data: { value: UtilisateurDonnees | null }, loading: { value: boolean }, error: { value: string }) {
  if (!Number.isFinite(id)) {
    error.value = 'ID utilisateur invalide'
    loading.value = false
    return
  }
  try {
    loading.value = true
    error.value = ''
    data.value = await getUtilisateurDonnees(id)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Erreur lors du chargement.'
    data.value = null
  } finally {
    loading.value = false
  }
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const route = useRoute()
    const router = useRouter()
    const id = computed(() => {
      const p = route.params.id
      return Number(Array.isArray(p) ? p[0] : p)
    })
    const data = ref<UtilisateurDonnees | null>(null)
    const loading = ref(true)
    const error = ref('')
    const successMessage = ref('')
    const isEditing = ref(false)
    const saving = ref(false)
    const deleting = ref(false)
    const editForm = ref<UtilisateurUpdatePayload>({})

    const fetchData = async () => {
      await loadUser(id.value, data, loading, error)
      if (data.value) {
        editForm.value = toEditForm(data.value)
      }
    }

    const toggleEdit = () => {
      isEditing.value = !isEditing.value
      successMessage.value = ''
      if (data.value) {
        editForm.value = toEditForm(data.value)
      }
    }

    const saveUser = async () => {
      try {
        saving.value = true
        error.value = ''
        successMessage.value = ''
        await updateUtilisateur(id.value, editForm.value)
        await fetchData()
        isEditing.value = false
        successMessage.value = 'Utilisateur mis à jour avec succès.'
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de la modification.'
      } finally {
        saving.value = false
      }
    }

    const removeUser = async () => {
      if (!window.confirm('Supprimer cet utilisateur ? Cette action est irréversible.')) {
        return
      }

      try {
        deleting.value = true
        error.value = ''
        await deleteUtilisateur(id.value)
        router.push('/utilisateurs')
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de la suppression.'
      } finally {
        deleting.value = false
      }
    }

    onMounted(fetchData)
    watch(id, fetchData)

    return {
      data,
      loading,
      error,
      successMessage,
      isEditing,
      saving,
      deleting,
      editForm,
      toggleEdit,
      saveUser,
      removeUser
    }
  }
})
</script>

<style scoped>
.detail-container {
  padding: 24px;
  max-width: 1000px;
  width: 100%;
  margin: 0 auto;
}

.card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
}

.header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.header-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.card h2 {
  font-size: 1rem;
  margin: 0;
  color: #2f4b66;
}

.profil-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.profil-item {
  padding: 8px 12px;
  background: #f7f9fc;
  border-radius: 6px;
}

.profil-item input,
.profil-item select {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #2f4b66;
  background: #fff;
}

.profil-item .label {
  display: block;
  font-size: 0.8rem;
  color: #5a6c7d;
}

.profil-item .value {
  font-weight: 600;
  color: #2f4b66;
}

.btn-back {
  padding: 8px 16px;
  border-radius: 6px;
  background: #5a6c7d;
  color: #fff;
  text-decoration: none;
  font-size: 0.9rem;
}

.btn {
  padding: 8px 16px;
  border-radius: 6px;
  border: none;
  background: #5294E2;
  color: #fff;
  cursor: pointer;
  font-size: 0.9rem;
}

.btn:hover {
  background: #3d7bc7;
}

.btn-secondary {
  background: #5a6c7d;
}

.btn-secondary:hover {
  background: #4a5c6d;
}

.btn-danger {
  background: #d32f2f;
}

.btn-danger:hover {
  background: #b71c1c;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-back:hover {
  background: #4a5c6d;
}

.table-wrapper {
  overflow-x: auto;
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

.empty-msg {
  margin: 0;
  color: #666;
  font-style: italic;
}

.loading, .error, .success {
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
</style>
