import { API_BASE_URL } from '../config'
import { auth } from './auth'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export async function sendChatMessage(message: string, history: ChatMessage[]): Promise<string> {
  const token = auth.getToken()
  if (!token) {
    throw new Error('Utilisateur non authentifie.')
  }

  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      history: history.slice(-10)
    })
  })

  if (!response.ok) {
    let messageErreur = 'Assistant indisponible.'
    try {
      const body = await response.json()
      messageErreur = body?.detail || messageErreur
    } catch {
      // no-op
    }
    throw new Error(messageErreur)
  }

  const body = await response.json()
  return body.answer
}
