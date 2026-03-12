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

      <div v-if="loading" class="loading" role="status" aria-live="polite">
        Chargement...
      </div>
      <div v-if="error" class="error" role="alert">
        {{ error }}
      </div>

      <section v-if="utilisateurs.length && !loading" class="card" aria-labelledby="list-title">
        <h2 id="list-title">{{ utilisateurs.length }} utilisateur(s) trouvé(s)</h2>
        <div class="table-wrapper">
          <table class="table" role="table" aria-describedby="list-title">
            <thead>
              <tr>
                <th scope="col">ID</th>
                <th scope="col">Nom d'utilisateur</th>
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
                <td>{{ u.id_utilisateur }}</td>
                <td>{{ u.username }}</td>
                <td>{{ u.age }}</td>
                <td>{{ u.sexe }}</td>
                <td>{{ u.date_inscription }}</td>
                <td>{{ u.stats.nb_consommations }}</td>
                <td>{{ u.stats.nb_activites }}</td>
                <td>{{ u.stats.nb_metriques }}</td>
                <td>{{ u.stats.nb_objectifs }}</td>
                <td>
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
import { searchUtilisateurs, type UtilisateurAdmin } from '../services/adminApi'

let debounceTimer: ReturnType<typeof setTimeout> | null = null

export default defineComponent({
  components: { Navbar },
  setup() {
    const utilisateurs = ref<UtilisateurAdmin[]>([])
    const searchQuery = ref('')
    const loading = ref(false)
    const error = ref('')
    const searchDone = ref(false)

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

    const debouncedSearch = () => {
      if (debounceTimer) clearTimeout(debounceTimer)
      debounceTimer = setTimeout(() => doSearch(), 300)
    }

    onMounted(() => {
      doSearch()
    })

    return { utilisateurs, searchQuery, loading, error, searchDone, doSearch, debouncedSearch }
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
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 16px;
}

.card h2 {
  font-size: 1rem;
  margin: 0 0 12px 0;
  color: #2f4b66;
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
  display: inline-block;
}

.btn:hover {
  background: #3d7bc7;
}

.btn-small {
  padding: 6px 12px;
  font-size: 0.85rem;
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

.loading, .error, .empty {
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
</style>
