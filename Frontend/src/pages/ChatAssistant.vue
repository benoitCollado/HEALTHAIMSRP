<template>
  <div class="canvas nav-page">
    <Navbar title="Chat IA" />
    <main id="main-content" class="chat-page">
      <section class="chat-shell" aria-labelledby="chat-title">
        <header class="chat-header">
          <div>
            <h1 id="chat-title">Assistant HealthAI MSPR</h1>
            <p>Posez une question sur votre suivi sante ou l'utilisation de la plateforme.</p>
          </div>
          <button class="btn btn-outline" type="button" @click="resetChat" :disabled="messages.length === 0 || loading">
            Nouveau chat
          </button>
        </header>

        <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>

        <div class="chat-window" role="log" aria-live="polite" aria-label="Conversation">
          <div v-if="messages.length === 0" class="empty-state">
            <h2>Comment puis-je vous aider ?</h2>
            <div class="suggestions">
              <button type="button" @click="useSuggestion('Comment suivre mes objectifs sante dans HealthAI MSPR ?')">
                Objectifs sante
              </button>
              <button type="button" @click="useSuggestion('Que puis-je analyser avec mes metriques sante ?')">
                Metriques
              </button>
              <button type="button" @click="useSuggestion('Comment la plateforme gere les flux de donnees ?')">
                Flux de donnees
              </button>
            </div>
          </div>

          <div
            v-for="(message, index) in messages"
            :key="index"
            class="chat-message"
            :class="message.role"
          >
            <div class="message-author">{{ message.role === 'user' ? 'Vous' : 'HealthAI' }}</div>
            <p>{{ message.content }}</p>
          </div>

          <div v-if="loading" class="chat-message assistant">
            <div class="message-author">HealthAI</div>
            <p>Reponse en cours...</p>
          </div>
        </div>

        <form class="chat-form" @submit.prevent="submitMessage">
          <label class="sr-only" for="chat-input">Message</label>
          <textarea
            id="chat-input"
            v-model="draft"
            rows="3"
            maxlength="2000"
            placeholder="Exemple : aide-moi a comprendre mes metriques sante"
            :disabled="loading"
            @keydown.enter.exact.prevent="submitMessage"
          ></textarea>
          <button type="submit" :disabled="loading || !draft.trim()">Envoyer</button>
        </form>
      </section>
    </main>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue'
import Navbar from '../components/Navbar.vue'
import { sendChatMessage, type ChatMessage } from '../services/chatApi'

export default defineComponent({
  components: { Navbar },
  setup() {
    const draft = ref('')
    const error = ref('')
    const loading = ref(false)
    const messages = ref<ChatMessage[]>([])

    function resetChat() {
      messages.value = []
      error.value = ''
      draft.value = ''
    }

    function useSuggestion(text: string) {
      draft.value = text
    }

    async function submitMessage() {
      const content = draft.value.trim()
      if (!content || loading.value) return

      error.value = ''
      draft.value = ''
      const history = [...messages.value]
      messages.value.push({ role: 'user', content })
      loading.value = true

      try {
        const answer = await sendChatMessage(content, history)
        messages.value.push({ role: 'assistant', content: answer })
      } catch (err) {
        error.value = err instanceof Error ? err.message : 'Assistant indisponible.'
      } finally {
        loading.value = false
      }
    }

    return { draft, error, loading, messages, resetChat, submitMessage, useSuggestion }
  }
})
</script>

<style scoped>
.chat-page {
  width: 100%;
  max-width: 980px;
  margin: 0 auto;
  padding: 28px 20px;
}

.chat-shell {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 116px);
  background: var(--white);
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 22px 24px;
  border-bottom: 1px solid var(--gray-200);
}

.chat-header h1 {
  margin: 0 0 4px;
  font-size: 1.35rem;
}

.chat-header p {
  margin: 0;
  color: var(--gray-500);
}

.chat-window {
  flex: 1;
  min-height: 420px;
  max-height: calc(100vh - 290px);
  overflow-y: auto;
  padding: 24px;
  background: var(--gray-50);
}

.empty-state {
  display: grid;
  align-content: center;
  min-height: 330px;
  text-align: center;
}

.empty-state h2 {
  font-size: 1.2rem;
}

.suggestions {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-top: 12px;
}

.suggestions button {
  background: var(--white);
  color: var(--primary);
  border: 1px solid var(--gray-300);
  box-shadow: none;
}

.chat-message {
  max-width: 78%;
  margin-bottom: 14px;
  padding: 12px 14px;
  border: 1px solid var(--gray-200);
  border-radius: 8px;
  background: var(--white);
}

.chat-message.user {
  margin-left: auto;
  background: var(--primary);
  border-color: var(--primary);
}

.chat-message.user p,
.chat-message.user .message-author {
  color: var(--white);
}

.chat-message.assistant {
  margin-right: auto;
}

.message-author {
  margin-bottom: 4px;
  color: var(--gray-500);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}

.chat-message p {
  margin: 0;
  white-space: pre-wrap;
}

.chat-form {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  padding: 16px;
  border-top: 1px solid var(--gray-200);
  background: var(--white);
}

.chat-form textarea {
  resize: vertical;
  min-height: 72px;
  max-height: 180px;
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

@media (max-width: 720px) {
  .chat-page {
    padding: 12px;
  }

  .chat-shell {
    min-height: calc(100vh - 84px);
  }

  .chat-header,
  .chat-form {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .chat-message {
    max-width: 100%;
  }
}
</style>
