<template>
  <div class="canvas" role="main" aria-label="Recherche et liste des utilisateurs">
    <Navbar title="Utilisateurs" />
    <div id="main-content" class="utilisateurs-container">
      <section class="card" aria-labelledby="search-title">
        <h2 id="search-title">Rechercher des utilisateurs</h2>
        <div class="search-bar">
          <label for="search-input" class="sr-only">Recherche par nom d'utilisateur</label>
          <input
            id="search-input"
            v-model="searchQuery"
            type="search"
            placeholder="Nom d'utilisateur..."
            aria-label="Recherche par nom d'utilisateur"
            class="search-input"
            @input="debouncedSearch"
          />
          <button
            type="button"
            class="btn"
            aria-label="Lancer la recherche"
            @click="doSearch"
          >
            Rechercher
          </button>
        </div>
      </section>

      <section class="card" aria-labelledby="create-title">
        <div class="section-header">
          <h2 id="create-title">Créer un utilisateur</h2>
          <button
            type="button"
            class="btn btn-secondary"
            @click="showCreateForm = !showCreateForm"
          >
            {{ showCreateForm ? 'Masquer le formulaire' : 'Nouvel utilisateur' }}
          </button>
        </div>

        <form v-if="showCreateForm" class="user-form" @submit.prevent="submitCreate">
          <div class="form-grid">
            <label>
              <span>Nom d'utilisateur</span>
              <input v-model="createForm.username" type="text" required />
            </label>
            <label>
              <span>Adresse mail</span>
              <input v-model="createForm.email" type="email" required />
            </label>
            <label>
              <span>Mot de passe</span>
              <input v-model="createForm.password" type="password" required minlength="4" />
            </label>
            <label>
              <span>Âge</span>
              <input v-model.number="createForm.age" type="number" min="1" required />
            </label>
            <label>
              <span>Sexe</span>
              <select v-model="createForm.sexe" required>
                <option value="H">H</option>
                <option value="F">F</option>
                <option value="Autre">Autre</option>
              </select>
            </label>
            <label>
              <span>Taille (cm)</span>
              <input v-model.number="createForm.taille_cm" type="number" min="1" required />
            </label>
            <label>
              <span>Poids (kg)</span>
              <input v-model.number="createForm.poids_kg" type="number" min="1" required />
            </label>
            <label>
              <span>Niveau d'activité</span>
              <select v-model.number="createForm.niveau_activite" required>
                <option :value="1">Tres faible</option>
                <option :value="2">Faible</option>
                <option :value="3">Moderee</option>
                <option :value="4">Elevee</option>
                <option :value="5">Tres elevee</option>
              </select>
            </label>
            <label>
              <span>Type d'abonnement</span>
              <input v-model.number="createForm.type_abonnement" type="number" min="1" required />
            </label>
            <label>
              <span>Date d'inscription</span>
              <input v-model="createForm.date_inscription" type="date" required />
            </label>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn" :disabled="submittingCreate">
              {{ submittingCreate ? 'Création...' : 'Créer l’utilisateur' }}
            </button>
          </div>
        </form>
      </section>

      <div v-if="loading" class="loading" role="status" aria-live="polite">
        Chargement...
      </div>
      <div v-if="error" class="error" role="alert">
        {{ error }}
      </div>
      <div v-if="successMessage" class="success" role="status" aria-live="polite">
        {{ successMessage }}
      </div>

      <section v-if="utilisateurs.length && !loading" class="card" aria-labelledby="list-title">
        <h2 id="list-title">{{ utilisateurs.length }} utilisateur(s) trouvé(s)</h2>
        <div class="table-wrapper">
          <table class="table" role="table" aria-describedby="list-title">
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Nom d'utilisateur</th>
                <th scope="col">Adresse mail</th>
                <th scope="col">Âge</th>
                <th scope="col">Sexe</th>
                <th scope="col">Inscription</th>
                <th scope="col">Consommations</th>
                <th scope="col">Activités</th>
                <th scope="col">Métriques</th>
                <th scope="col">Objectifs</th>
                <th scope="col">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="u in utilisateurs" :key="u.id_utilisateur">
                <td data-label="ID">{{ u.id_utilisateur }}</td>
                <td data-label="Utilisateur">{{ u.username }}</td>
                <td data-label="Email">{{ u.email }}</td>
                <td data-label="Age">{{ u.age }}</td>
                <td data-label="Sexe">{{ u.sexe }}</td>
                <td data-label="Inscription">{{ u.date_inscription }}</td>
                <td data-label="Consommations">{{ u.stats.nb_consommations }}</td>
                <td data-label="Activites">{{ u.stats.nb_activites }}</td>
                <td data-label="Metriques">{{ u.stats.nb_metriques }}</td>
                <td data-label="Objectifs">{{ u.stats.nb_objectifs }}</td>
                <td data-label="Actions">
                  <router-link
                    :to="`/utilisateurs/${u.id_utilisateur}`"
                    class="btn btn-small"
                    :aria-label="`Voir les données de ${u.username}`"
                  >
                    Voir données
                  </router-link>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>

      <div v-else-if="!loading && searchDone" class="empty" role="status">
        Aucun utilisateur trouvé.
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted } from 'vue'
import Navbar from '../components/Navbar.vue'
import {
  createUtilisateur,
  searchUtilisateurs,
  type UtilisateurAdmin,
  type UtilisateurCreatePayload
} from '../services/adminApi'

let debounceTimer: ReturnType<typeof setTimeout> | null = null

function createInitialForm(): UtilisateurCreatePayload {
  return {
    username: '',
    email: '',
    password: '',
    age: 30,
    sexe: 'H',
    taille_cm: 170,
    poids_kg: 70,
    niveau_activite: 1,
    type_abonnement: 1,
    date_inscription: new Date().toISOString().slice(0, 10)
  }
}

export default defineComponent({
  components: { Navbar },
  setup() {
    const utilisateurs = ref<UtilisateurAdmin[]>([])
    const searchQuery = ref('')
    const loading = ref(false)
    const error = ref('')
    const searchDone = ref(false)
    const successMessage = ref('')
    const showCreateForm = ref(false)
    const submittingCreate = ref(false)
    const createForm = ref<UtilisateurCreatePayload>(createInitialForm())

    const doSearch = async () => {
      try {
        loading.value = true
        error.value = ''
        const res = await searchUtilisateurs(searchQuery.value.trim() || undefined)
        utilisateurs.value = res.utilisateurs
        searchDone.value = true
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de la recherche.'
        utilisateurs.value = []
      } finally {
        loading.value = false
      }
    }

    const submitCreate = async () => {
      try {
        submittingCreate.value = true
        error.value = ''
        successMessage.value = ''
        await createUtilisateur(createForm.value)
        createForm.value = createInitialForm()
        showCreateForm.value = false
        successMessage.value = 'Utilisateur créé avec succès.'
        await doSearch()
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Erreur lors de la création.'
      } finally {
        submittingCreate.value = false
      }
    }

    const debouncedSearch = () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => doSearch(), 300)
    }

    onMounted(() => {
      doSearch()
    })

    return {
      utilisateurs,
      searchQuery,
      loading,
      error,
      searchDone,
      successMessage,
      showCreateForm,
      submittingCreate,
      createForm,
      doSearch,
      debouncedSearch,
      submitCreate
    }
  }
})
</script>

<style scoped>
.utilisateurs-container {
  padding: 24px;
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.card {
  background: #fff;
  padding: 16px;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.20);
  box-shadow: var(--shadow);
  margin-bottom: 16px;
}

.card h2 {
  font-size: 1rem;
  margin: 0 0 12px 0;
  color: #2f4b66;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.search-bar {
  display: flex;
  gap: 12px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 400px;
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 1rem;
}

.btn {
  padding: 10px 16px;
  border-radius: 6px;
  border: none;
  background: #5294E2;
  color: #fff;
  cursor: pointer;
  font-size: 0.95rem;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
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

.btn-small {
  padding: 6px 12px;
  font-size: 0.85rem;
}

.user-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  color: #2f4b66;
  font-size: 0.9rem;
}

.form-grid input,
.form-grid select {
  padding: 10px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
  font-size: 0.95rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.table-wrapper {
  overflow-x: auto;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 8px;
  background: #fff;
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

.loading, .error, .empty, .success {
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

@media (max-width: 700px) {
  .utilisateurs-container {
    padding: 16px 12px;
  }

  .card {
    padding: 14px;
  }

  .section-header,
  .search-bar,
  .form-actions {
    align-items: stretch;
    flex-direction: column;
  }

  .search-input {
    max-width: none;
  }

  .btn,
  .form-actions button {
    width: 100%;
    text-align: center;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .table-wrapper {
    overflow: visible;
    border: 0;
    background: transparent;
  }

  .table,
  .table tbody,
  .table tr,
  .table td {
    display: block;
    width: 100%;
  }

  .table thead {
    display: none;
  }

  .table tr {
    padding: 10px 12px;
    margin-bottom: 10px;
    background: #fff;
    border: 1px solid rgba(148, 163, 184, 0.22);
    border-radius: 8px;
    box-shadow: var(--shadow-sm);
  }

  .table td {
    display: flex;
    justify-content: space-between;
    gap: 14px;
    padding: 8px 0;
    text-align: right;
    border-bottom: 1px solid var(--gray-100);
    overflow-wrap: anywhere;
  }

  .table td:last-child {
    display: block;
    border-bottom: 0;
  }

  .table td::before {
    content: attr(data-label);
    flex: 0 0 42%;
    color: var(--gray-500);
    font-size: 0.74rem;
    font-weight: 800;
    letter-spacing: 0.04em;
    text-align: left;
    text-transform: uppercase;
  }

  .table td:last-child::before {
    display: none;
  }
}
</style>
