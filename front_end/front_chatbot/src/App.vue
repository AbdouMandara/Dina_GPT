<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import axios from 'axios'
import { useChatStore } from './stores/chatStore'

const store = useChatStore()
const word = ref('')
const loading = ref(false)
const error = ref('')
const sidebarOpen = ref(false)

const activeConversation = computed(() => {
  return store.conversations.find(c => c.id === store.activeConversationId)
})

const messages = computed(() => activeConversation.value?.messages || [])
const showHeader = computed(() => messages.value.length === 0)

const learnWord = async () => {
  if (!word.value.trim() || loading.value) return
  
  const currentWord = word.value.trim()
  loading.value = true
  error.value = ''
  
  // 1. Add user message
  store.addMessageToActive({
    type: 'user',
    text: currentWord,
    timestamp: new Date().toISOString()
  })
  
  word.value = ''
  await nextTick()
  scrollToBottom()
  
  try {
    const response = await axios.post('http://localhost:8001/learn-word', {
      word: currentWord
    })
    
    // 2. Add AI message
    store.addMessageToActive({
      type: 'ai',
      ...response.data,
      timestamp: new Date().toISOString()
    })
    
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error(err)
    error.value = "Oups ! Impossible de récupérer les informations pour ce mot."
  } finally {
    loading.value = false
  }
}

const scrollToBottom = () => {
  window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
}

const toggleSidebar = () => {
  sidebarOpen.value = !sidebarOpen.value
}

const startNewChat = () => {
  store.createNewConversation()
  if (window.innerWidth < 1024) sidebarOpen.value = false
}

const selectChat = (id) => {
  store.switchConversation(id)
  if (window.innerWidth < 1024) sidebarOpen.value = false
}

onMounted(() => {
  scrollToBottom()
})
</script>

<template>
  <div class="dina-app" :class="{ 'sidebar-open': sidebarOpen }">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-header">
        <button @click="startNewChat" class="new-chat-btn">
          <svg viewBox="0 0 24 24" class="icon"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z" fill="currentColor"/></svg>
          <span>Nouvelle discussion</span>
        </button>
      </div>
      
      <div class="history-list">
        <div 
          v-for="convo in store.conversations" 
          :key="convo.id"
          class="history-item"
          :class="{ active: convo.id === store.activeConversationId }"
          @click="selectChat(convo.id)"
        >
          <svg viewBox="0 0 24 24" class="convo-icon"><path d="M21 15.46l-5.27-.61-2.52-4.74-2.52 4.74-5.27.61 3.81 3.71-.9 5.25L13 21.88l4.67 2.45-.9-5.25 3.81-3.71-.63-4.46z" fill="currentColor"/></svg>
          <span class="convo-title">{{ convo.title }}</span>
          <button @click.stop="store.deleteConversation(convo.id)" class="delete-btn">
            <svg viewBox="0 0 24 24" class="icon"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12 19 6.41z" fill="currentColor"/></svg>
          </button>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <div class="user-profile">
          <div class="avatar">D</div>
          <span>Utilisateur Dina</span>
        </div>
      </div>
    </aside>

    <!-- Overlay for mobile sidebar -->
    <div v-if="sidebarOpen" class="sidebar-overlay" @click="toggleSidebar"></div>

    <!-- Main Content -->
    <div class="main-content">
      <!-- Top Navigation -->
      <nav class="top-nav">
        <button @click="toggleSidebar" class="burger-btn">
          <svg viewBox="0 0 24 24" class="icon" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 6h16M4 12h16M4 18h16" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </button>
        <span class="app-name">DinaGPT</span>
        <div class="nav-spacer"></div>
      </nav>

      <div class="chat-container">
        <!-- Initial Header -->
        <header v-if="showHeader" class="hero-header">
          <div class="logo-circle">D</div>
          <h1 class="hero-title">Comment puis-je vous aider aujourd'hui ?</h1>
          <p class="hero-subtitle">Explorez le langage avec DinaGPT, votre assistant linguistique intelligent.</p>
        </header>

        <!-- Message List -->
        <div class="messages-list">
          <div 
            v-for="(msg, idx) in messages" 
            :key="idx"
            class="message-wrapper"
            :class="msg.type"
          >
            <div class="message-bubble">
              <!-- User Message -->
              <div v-if="msg.type === 'user'" class="user-text">
                {{ msg.text }}
              </div>

              <!-- AI Message / Result Card -->
              <div v-else class="ai-response">
                <div class="word-card-simple">
                  <div class="word-header">
                    <span class="word-nature" v-if="msg.part_of_speech">{{ msg.part_of_speech }}</span>
                    <h2 class="word-title">{{ msg.word }}</h2>
                    <span class="word-phonetic" v-if="msg.phonetic">{{ msg.phonetic }}</span>
                  </div>
                  
                  <div class="word-translation">{{ msg.translation }}</div>
                  
                  <div class="word-section">
                    <label>Signification</label>
                    <p>{{ msg.definition }}</p>
                  </div>

                  <div v-if="msg.synonyms?.length" class="word-section">
                    <label>Synonymes</label>
                    <div class="syn-tags">
                      <span v-for="s in msg.synonyms" :key="s" class="tag">{{ s }}</span>
                    </div>
                  </div>

                  <div class="word-section">
                    <label>Exemples</label>
                    <div class="example-list">
                      <div v-for="(ex, i) in msg.examples" :key="i" class="example-box">
                        <p class="en">{{ ex.en }}</p>
                        <p class="fr">{{ ex.fr }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="loading" class="message-wrapper ai">
            <div class="message-bubble loading-bubble">
              <div class="dot-pulse"></div>
            </div>
          </div>

          <div v-if="error" class="error-msg">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- Search Area -->
      <footer class="input-area">
        <div class="input-container">
          <div class="input-box">
            <input 
              v-model="word" 
              @keyup.enter="learnWord"
              type="text" 
              placeholder="Testez un mot ou une expression..." 
              :disabled="loading"
            />
            <button @click="learnWord" :disabled="loading || !word.trim()" class="send-btn">
              <svg viewBox="0 0 24 24" class="icon"><path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
            </button>
          </div>
          <p class="disclaimer">DinaGPT peut faire des erreurs. Vérifiez les informations importantes.</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bg-sidebar: #171717;
  --bg-main: #212121;
  --bg-bubble-user: #2f2f2f;
  --text-main: #ececec;
  --text-muted: #b4b4b4;
  --accent: #3b82f6;
  --border: rgba(255, 255, 255, 0.1);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: 'Inter', sans-serif;
  background-color: var(--bg-main);
  color: var(--text-main);
  height: 100vh;
  width: 100%;
  /* overflow: hidden; */
}

.dina-app {
  display: flex;
  height: 100vh;
  width: 100%;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 260px;
  flex-shrink: 0;
  background-color: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--border);
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1000;
}

.sidebar-header { padding: 1rem; }

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: transparent;
  border: 1px solid var(--border);
  border-radius: 0.5rem;
  color: var(--text-main);
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
}

.new-chat-btn:hover { background: rgba(255,255,255,0.05); }

.history-list {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.history-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  cursor: pointer;
  margin-bottom: 0.25rem;
  position: relative;
  transition: background 0.2s;
}

.history-item:hover { background: rgba(255,255,255,0.05); }
.history-item.active { background: rgba(255,255,255,0.1); }

.convo-icon { width: 16px; height: 16px; color: var(--text-muted); }
.convo-title { flex: 1; font-size: 0.9rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.delete-btn {
  opacity: 0;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
}

.history-item:hover .delete-btn { opacity: 1; }
.delete-btn:hover { color: #f87171; }

.sidebar-footer { padding: 1rem; border-top: 1px solid var(--border); }
.user-profile { display: flex; align-items: center; gap: 0.75rem; font-size: 0.9rem; }
.avatar { width: 32px; height: 32px; background: var(--accent); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; }

/* Main Content */
.main-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  height: 100%;
  background: var(--bg-main);
  overflow-y: auto;
}

.top-nav {
  height: 56px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  padding: 0 1rem;
  border-bottom: 1px solid var(--border);
  background: var(--bg-main);
}

.burger-btn { background: transparent; border: none; color: var(--text-main); cursor: pointer; display: none; margin-right: 1rem; }
.app-name { font-weight: 600; font-size: 1.1rem; }

/* Chat Container */
.chat-container {
  flex: 1;
  padding: 2rem 1rem;
  display: flex;
  flex-direction: column;
}

.hero-header {
  margin: 10vh auto;
  text-align: center;
  max-width: 600px;
  width: 100%;
}

.logo-circle { width: 80px; height: 80px; border: 2px solid var(--border); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 2rem; font-size: 2.5rem; font-weight: 800; }
.hero-title { font-size: 2.5rem; font-weight: 600; margin-bottom: 1rem; letter-spacing: -1px; }
.hero-subtitle { color: var(--text-muted); font-size: 1.1rem; }

.messages-list {
  width: 100%;
  max-width: 800px;
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin: 0 auto;
}

.message-wrapper { display: flex; width: 100%; }
.message-wrapper.user { justify-content: flex-start; }
.message-wrapper.ai { justify-content: flex-end; }

.message-bubble { max-width: 85%; }

.user-text {
  background-color: var(--bg-bubble-user);
  padding: 0.75rem 1.25rem;
  border-radius: 1.5rem;
  font-size: 1rem;
  line-height: 1.5;
}

/* Simplified AI Result Card */
.word-card-simple {
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border);
  border-radius: 1.5rem;
  padding: 2rem;
}

.word-header { display: flex; align-items: baseline; gap: 1rem; margin-bottom: 0.5rem; }
.word-nature { font-size: 0.7rem; color: var(--accent); text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; }
.word-title { font-size: 2.5rem; font-weight: 700; }
.word-phonetic { font-size: 1.1rem; color: var(--text-muted); }

.word-translation { font-size: 1.4rem; font-weight: 500; margin-bottom: 2rem; opacity: 0.9; }

.word-section { margin-bottom: 1.5rem; }
.word-section label { display: block; font-size: 0.7rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem; font-weight: 600; }
.word-section p { font-size: 1.1rem; line-height: 1.5; }

.syn-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.tag { background: rgba(59, 130, 246, 0.1); color: var(--accent); padding: 0.3rem 0.8rem; border-radius: 0.5rem; font-size: 0.85rem; }

.example-box { margin-bottom: 1rem; padding-left: 1rem; border-left: 2px solid var(--border); }
.example-box:last-child { margin-bottom: 0; }
.example-box .en { font-size: 1.1rem; margin-bottom: 0.25rem; }
.example-box .fr { font-size: 0.9rem; color: var(--text-muted); }

/* Input Area */
.input-area {
  padding: 1rem 1rem 2.5rem;
  background: linear-gradient(to top, var(--bg-main) 70%, transparent);
}

.input-container { max-width: 800px; margin: 0 auto; width: 100%; }

.input-box {
  background: var(--bg-bubble-user);
  border: 1px solid var(--border);
  border-radius: 1.5rem;
  padding: 0.5rem 0.5rem 0.5rem 1.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 10px 20px rgba(0,0,0,0.2);
}

.input-box input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 1rem;
  padding: 0.75rem 0;
  outline: none;
}

.send-btn {
  width: 40px;
  height: 40px;
  background: var(--accent);
  border: none;
  border-radius: 50%;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: transform 0.2s;
}

.send-btn:hover:not(:disabled) { transform: scale(1.1); }
.send-btn:disabled { opacity: 0.3; cursor: not-allowed; }

.disclaimer { text-align: center; margin-top: 0.75rem; font-size: 0.7rem; color: var(--text-muted); }

/* Loading */
.loading-bubble { background: rgba(255,255,255,0.05); padding: 1.5rem 2rem; border-radius: 1.5rem; }
.dot-pulse { width: 10px; height: 10px; background: var(--text-muted); border-radius: 50%; animation: pulse 1s infinite alternate; }
@keyframes pulse { from { opacity: 0.3; transform: scale(0.8); } to { opacity: 1; transform: scale(1.2); } }

/* Mobile Adaptations */
@media (max-width: 1024px) {
  .sidebar { position: fixed; left: 0; top: 0; bottom: 0; transform: translateX(-100%); width: 280px; }
  .sidebar-open .sidebar { transform: translateX(0); }
  .burger-btn { display: block; }
  .sidebar-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); z-index: 999; }
}

@media (max-width: 640px) {
  .hero-title { font-size: 1.8rem; }
  .word-title { font-size: 1.8rem; }
}

.icon { width: 20px; height: 20px; }
</style>
