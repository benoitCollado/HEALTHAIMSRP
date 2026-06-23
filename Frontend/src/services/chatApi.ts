import { API_BASE_URL } from '../config'
import { auth } from './auth'

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  images?: ChatImage[]
}

export interface ChatImage {
  object_key: string
  url: string
  content_type: string
  filename: string
}

export interface ChatRecommendation {
  answer: string
  recommendation: Record<string, unknown>
}

export interface ChatPhotoAnalysis {
  answer: string
  analysis: Record<string, unknown>
}

function getToken(): string {
  const token = auth.getToken()
  if (!token) {
    throw new Error('Utilisateur non authentifie.')
  }
  return token
}

export async function uploadChatImage(file: File): Promise<ChatImage> {
  const form = new FormData()
  form.append('file', file)

  const response = await fetch(`${API_BASE_URL}/chat/images`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`
    },
    body: form
  })

  if (!response.ok) {
    let messageErreur = "Impossible d'envoyer l'image."
    try {
      const body = await response.json()
      messageErreur = body?.detail || messageErreur
    } catch {
      // no-op
    }
    throw new Error(messageErreur)
  }

  return response.json()
}

export async function getChatRecommendations(): Promise<ChatRecommendation> {
  const response = await fetch(`${API_BASE_URL}/chat/recommendations`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`
    }
  })

  if (!response.ok) {
    let messageErreur = 'Recommandations IA indisponibles.'
    try {
      const body = await response.json()
      messageErreur = body?.detail || messageErreur
    } catch {
      // no-op
    }
    throw new Error(messageErreur)
  }

  return response.json()
}

export async function analyzeChatImage(image: ChatImage, question?: string): Promise<ChatPhotoAnalysis> {
  const response = await fetch(`${API_BASE_URL}/chat/images/analyze`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      image: {
        object_key: image.object_key,
        filename: image.filename
      },
      question
    })
  })

  if (!response.ok) {
    let messageErreur = 'Analyse photo indisponible.'
    try {
      const body = await response.json()
      messageErreur = body?.detail || messageErreur
    } catch {
      // no-op
    }
    throw new Error(messageErreur)
  }

  return response.json()
}

export interface ChatReply {
  answer: string
  recommendation?: Record<string, unknown> | null
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[],
  images: ChatImage[] = []
): Promise<ChatReply> {
  const response = await fetch(`${API_BASE_URL}/chat/`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${getToken()}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      message,
      history: history.slice(-10).map(({ role, content }) => ({ role, content })),
      images: images.map(({ object_key, filename }) => ({ object_key, filename }))
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
  return {
    answer: body.answer,
    recommendation: body.recommendation ?? null
  }
}
