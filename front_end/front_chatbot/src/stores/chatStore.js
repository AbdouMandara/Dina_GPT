import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useChatStore = defineStore('chat', () => {
  const conversations = ref(JSON.parse(localStorage.getItem('dinagpt_conversations')) || [])
  const activeConversationId = ref(localStorage.getItem('dinagpt_active_id') || null)

  const createNewConversation = () => {
    const id = Date.now().toString()
    conversations.value.unshift({
      id,
      title: 'Nouvelle discussion',
      messages: [],
      createdAt: new Date().toISOString()
    })
    activeConversationId.value = id
    return id
  }

  const addMessageToActive = (message) => {
    const convo = conversations.value.find(c => c.id === activeConversationId.value)
    if (convo) {
      convo.messages.push(message)
      
      // Auto-generate title after first user message
      if (convo.messages.length === 1 && message.type === 'user') {
        convo.title = message.text.charAt(0).toUpperCase() + message.text.slice(1, 20) + (message.text.length > 20 ? '...' : '')
      }
    }
  }

  const switchConversation = (id) => {
    activeConversationId.value = id
  }

  const deleteConversation = (id) => {
    conversations.value = conversations.value.filter(c => c.id !== id)
    if (activeConversationId.value === id) {
      activeConversationId.value = conversations.value.length > 0 ? conversations.value[0].id : null
    }
  }

  const clearHistory = () => {
    conversations.value = []
    activeConversationId.value = null
  }

  // Persistence
  watch(conversations, (newVal) => {
    localStorage.setItem('dinagpt_conversations', JSON.stringify(newVal))
  }, { deep: true })

  watch(activeConversationId, (newVal) => {
    if (newVal) localStorage.setItem('dinagpt_active_id', newVal)
  })

  // Initialize with a new conversation if empty
  if (conversations.value.length === 0) {
    createNewConversation()
  }

  return {
    conversations,
    activeConversationId,
    createNewConversation,
    addMessageToActive,
    switchConversation,
    deleteConversation,
    clearHistory
  }
})
