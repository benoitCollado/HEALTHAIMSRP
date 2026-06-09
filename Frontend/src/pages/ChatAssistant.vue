<template>
  <div class="canvas nav-page">
    <Navbar title="Chat IA" />
    <main id="main-content" class="chat-page">
      <section class="chat-shell" aria-labelledby="chat-title">
        <header class="chat-header">
          <div>
            <span class="chat-eyebrow">Assistant IA</span>
            <h1 id="chat-title">Assistant HealthAI MSPR</h1>
            <p>Posez une question sur vos donnees sante, vos objectifs ou le fonctionnement de la plateforme.</p>
          </div>
          <button class="btn btn-outline" type="button" @click="resetChat" :disabled="messages.length === 0 || loading">
            Nouveau chat
          </button>
        </header>

        <div v-if="error" class="alert alert-error" role="alert">{{ error }}</div>

        <div class="chat-window" role="log" aria-live="polite" aria-label="Conversation">
          <div v-if="messages.length === 0" class="empty-state">
            <div class="empty-mark">AI</div>
            <h2>Comment puis-je vous aider ?</h2>
            <p>Choisissez un exemple ou ecrivez directement votre question.</p>
            <div class="suggestions">
              <button type="button" @click="useSuggestion('Comment suivre mes objectifs sante dans HealthAI MSPR ?')">
                <span>Objectifs sante</span>
                <small>Suivi, progression, conseils</small>
              </button>
              <button type="button" @click="useSuggestion('Que puis-je analyser avec mes metriques sante ?')">
                <span>Metriques</span>
                <small>Poids, sommeil, cardio, pas</small>
              </button>
              <button type="button" @click="useSuggestion('Comment la plateforme gere les flux de donnees ?')">
                <span>Flux de donnees</span>
                <small>Import, controle, nettoyage</small>
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
  max-width: 900px;
  margin: 0 auto;
  padding: 16px 18px;
}

.chat-shell {
  display: flex;
  flex-direction: column;
  min-height: calc(100vh - 180px);
  background: rgba(255, 255, 255, 0.96);
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 8px;
  box-shadow: var(--shadow);
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  background: linear-gradient(180deg, #fff, #f8fbff);
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}

.chat-eyebrow {
  display: inline-flex;
  margin-bottom: 6px;
  color: var(--primary-dark);
  font-size: 0.74rem;
  font-weight: 800;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}

.chat-header h1 {
  margin: 0 0 4px;
  font-size: 1.12rem;
}

.chat-header p {
  font-size: 0.9rem;
  margin: 0;
  color: var(--gray-500);
}

.chat-window {
  flex: 1;
  min-height: 330px;
  max-height: calc(100vh - 330px);
  overflow-y: auto;
  padding: 20px;
  background:
    linear-gradient(180deg, rgba(248, 251, 255, 0.92), rgba(255, 255, 255, 0.92)),
    linear-gradient(90deg, rgba(226, 232, 240, 0.38) 1px, transparent 1px),
    linear-gradient(180deg, rgba(226, 232, 240, 0.38) 1px, transparent 1px);
  background-size: auto, 36px 36px, 36px 36px;
}

.empty-state {
  display: grid;
  justify-items: center;
  align-content: center;
  min-height: 300px;
  text-align: center;
}

.empty-mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  margin-bottom: 10px;
  color: #fff;
  font-size: 0.9rem;
  font-weight: 900;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  border-radius: 8px;
  box-shadow: var(--shadow-blue);
}

.empty-state h2 {
  margin-bottom: 6px;
  font-size: 1.15rem;
}

.empty-state p {
  max-width: 460px;
  margin-bottom: 16px;
  color: var(--gray-500);
}

.suggestions {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
  width: min(100%, 620px);
  margin-top: 2px;
}

.suggestions button {
  display: grid;
  gap: 4px;
  min-height: 70px;
  padding: 11px 12px;
  text-align: left;
  background: var(--white);
  color: var(--gray-900);
  border: 1px solid rgba(148, 163, 184, 0.28);
  border-radius: 8px;
  box-shadow: none;
}

.suggestions button:hover {
  border-color: rgba(37, 99, 235, 0.34);
  background: #f8fbff;
}

.suggestions span {
  color: var(--primary-dark);
  font-weight: 800;
}

.suggestions small {
  color: var(--gray-500);
  font-size: 0.8rem;
  font-weight: 600;
  white-space: normal;
}

.chat-message {
  max-width: min(78%, 620px);
  margin-bottom: 12px;
  padding: 11px 13px;
  border: 1px solid rgba(148, 163, 184, 0.24);
  border-radius: 8px;
  background: var(--white);
  box-shadow: var(--shadow-sm);
}

.chat-message.user {
  margin-left: auto;
  background: linear-gradient(135deg, var(--primary), #0f766e);
  border-color: transparent;
}

.chat-message.user p,
.chat-message.user .message-author {
  color: var(--white);
}

.chat-message.assistant {
  margin-right: auto;
  background: #fff;
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
  padding: 12px 14px;
  border-top: 1px solid rgba(148, 163, 184, 0.22);
  background: var(--white);
}

.chat-form textarea {
  resize: none;
  border-color: rgba(148, 163, 184, 0.34);
  box-shadow: inset 0 1px 0 rgba(15, 23, 42, 0.02);
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
    padding: 10px;
  }

  .chat-shell {
    min-height: calc(100vh - 88px);
  }

  .chat-header,
  .chat-form {
    grid-template-columns: 1fr;
    flex-direction: column;
  }

  .chat-window {
    min-height: 320px;
    max-height: none;
    padding: 14px 10px;
  }

  .suggestions {
    grid-template-columns: 1fr;
  }

  .chat-message {
    max-width: 100%;
  }

  .chat-form {
    padding: 12px;
  }

  .chat-form button {
    width: 100%;
    min-height: 46px;
  }
}
</style>
