<script setup>
import { ref, computed, nextTick, onMounted } from 'vue'
import axios from 'axios'
import { useChatStore } from './stores/chatStore'
import { marked } from 'marked'

const store = useChatStore()
const word = ref('')
const loading = ref(false)
const error = ref('')
const sidebarOpen = ref(window.innerWidth > 1024)
const isDark = ref(true)

const activeMenuId = ref(null)
const showAboutModal = ref(false)

const toggleMenu = (id, event) => {
  activeMenuId.value = activeMenuId.value === id ? null : id
}

const activeConversation = computed(() => {
  return store.conversations.find(c => c.id === store.activeConversationId)
})

const messages = computed(() => activeConversation.value?.messages || [])
const showWelcome = computed(() => messages.value.length === 0)

const parseMarkdown = (text) => {
  if (!text) return ''
  return marked.parse(text)
}

const learnWord = async () => {
  if (!word.value.trim() || loading.value) return
  
  const currentText = word.value.trim()
  loading.value = true
  error.value = ''
  
  store.addMessageToActive({
    type: 'user',
    text: currentText,
    timestamp: new Date().toISOString()
  })
  
  word.value = ''
  await nextTick()
  scrollToBottom()
  
  // Logic to determine if it's a general question or a dictionary lookup
  const wordsCount = currentText.split(/\s+/).length;
  
  try {
    if (wordsCount > 3 || currentText.includes('?')) {
      // General Chat Mode
      const response = await axios.post('http://localhost:8001/chat', {
        prompt: currentText
      })
      
      const aiResponseText = response.data.choices?.[0]?.message?.content || "Je n'ai pas pu générer de réponse."
      
      store.addMessageToActive({
        type: 'ai',
        mode: 'chat',
        text: aiResponseText,
        timestamp: new Date().toISOString()
      })
    } else {
      // Dictionary Mode
      const response = await axios.post('http://localhost:8001/learn-word', {
        word: currentText
      })
      
      store.addMessageToActive({
        type: 'ai',
        mode: 'dictionary',
        ...response.data,
        timestamp: new Date().toISOString()
      })
    }
    
    await nextTick()
    scrollToBottom()
  } catch (err) {
    console.error(err)
    error.value = "Oups ! Une erreur s'est produite lors de la communication avec l'IA."
  } finally {
    loading.value = false
  }
}

const scrollToBottom = () => {
  const container = document.querySelector('.messages-list-wrapper')
  if (container) {
    container.scrollTo({ top: container.scrollHeight, behavior: 'smooth' })
  }
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
  window.addEventListener('resize', () => {
    if (window.innerWidth > 1024) sidebarOpen.value = true
  })
  window.addEventListener('click', () => {
    activeMenuId.value = null
  })
})
</script>

<template>
  <div class="chatgpt-app" :class="{ 'sidebar-closed': !sidebarOpen }">
    <!-- Sidebar -->
    <aside class="sidebar">
      <div class="sidebar-top">
        <div class="sidebar-header">
          <i class='bx bx-sidebar sidebar-toggle-btn' @click.stop="toggleSidebar" ></i>
        </div>
        <button @click="startNewChat" class="sidebar-btn new-chat">
          <div class="icon-wrap"><i class='bx bx-edit-alt'></i></div>
          <span>Nouveau chat</span>
        </button>

        <!-- Real Chat History -->
        <div class="sidebar-section history">
          <label>Récents</label>
          <div 
            v-for="convo in store.conversations.slice(0, 10)" 
            :key="convo.id"
            class="nav-item chat-history-item"
            :class="{ active: convo.id === store.activeConversationId }"
            @click="selectChat(convo.id)"
          >
            <span>{{ convo.title }}</span>
            <div class="item-action-wrapper">
              <button @click.stop="toggleMenu(convo.id)" class="item-action">
                <i class='bx bx-dots-horizontal-rounded'></i>
              </button>
              <div v-if="activeMenuId === convo.id" class="action-dropdown" @click.stop>
                <button @click="store.deleteConversation(convo.id); activeMenuId = null" class="dropdown-item delete">
                  <i class='bx bx-trash'></i> Supprimer
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="sidebar-footer">
        <button class="about-author-btn" @click="showAboutModal = true">
          <div class="author-avatar-modern">
            <span class="initials">AM</span>
            <div class="glow-ring"></div>
          </div>
          <div class="author-info-modern">
            <span class="author-name">Abdou Mandara</span>
            <span class="author-role">Découvrir le créateur ✨</span>
          </div>
          <i class='bx bx-chevron-right icon-arrow'></i>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="chat-header">
        <button v-if="!sidebarOpen" @click="toggleSidebar" class="mobile-sidebar-toggle">
          <i class='bx bx-sidebar'></i>
        </button>
        
        <div class="model-dropdown">
          <span>DinaGPT-A</span>
          <i class='bx bx-chevron-down'></i>
        </div>

       
      </header>

      <!-- Chat Body -->
      <div class="messages-list-wrapper">
        <div class="messages-container">
          <!-- Welcome Screen -->
          <div v-if="showWelcome" class="welcome-screen">
            <div class="welcome-logo">
              <i class='bx bxs-bot'></i>
            </div>
          </div>

          <!-- Messages -->
          <div v-for="(msg, idx) in messages" :key="idx" class="message-row" :class="msg.type">
            <div class="message-content">
              <!-- User Message -->
              <div v-if="msg.type === 'user'" class="user-bubble">
                {{ msg.text }}
              </div>

              <!-- AI Message -->
              <div v-else class="ai-msg">
                <div class="ai-avatar">
                  <i class='bx bxs-bot'></i>
                </div>
                <div class="ai-text">
                  <!-- General Chat Message (Markdown) -->
                  <div v-if="msg.mode === 'chat'" class="markdown-body" v-html="parseMarkdown(msg.text)"></div>

                  <!-- Word Card integration (ChatGPT style) -->
                  <div v-else class="result-card">
                    <h2 class="result-title">{{ msg.word }} <small v-if="msg.phonetic">{{ msg.phonetic }}</small></h2>
                    <p class="result-meta">{{ msg.part_of_speech }} • {{ msg.translation }}</p>
                    
                    <div class="result-section">
                      <h3 class="section-label">1. Signification</h3>
                      <p>{{ msg.definition }}</p>
                    </div>

                    <div v-if="msg.synonyms?.length" class="result-section">
                      <h3 class="section-label">2. Synonymes</h3>
                      <div class="tag-list">
                        <span v-for="s in msg.synonyms" :key="s" class="tag">{{ s }}</span>
                      </div>
                    </div>

                    <div v-if="msg.examples?.length" class="result-section">
                      <h3 class="section-label">3. Exemples</h3>
                      <div class="example-item" v-for="(ex, i) in msg.examples" :key="i">
                        <p class="en">"{{ ex.en }}"</p>
                        <p class="fr">{{ ex.fr }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="loading" class="message-row ai loading">
             <div class="ai-avatar"><i class='bx bxs-bot'></i></div>
             <div class="typing-indicator"><span></span><span></span><span></span></div>
          </div>
          
          <div v-if="error" class="error-msg">{{ error }}</div>
        </div>
      </div>

      <!-- Input Area -->
      <footer class="input-area">
        <div class="input-wrapper">
          <div class="input-card">
            <input 
              v-model="word" 
              @keyup.enter="learnWord"
              placeholder="Poser une question"
              :disabled="loading"
            />
            <div class="input-actions">
              <button @click="learnWord" class="send-btn" :disabled="!word.trim() || loading">
                <i class='bx bx-up-arrow-alt'></i>
              </button>
            </div>
          </div>
          <!-- <p class="footer-note">ChatGPT peut faire des erreurs. Envisagez de vérifier les informations importantes.</p> -->
        </div>
      </footer>
    </main>

    <!-- About Modal -->
    <div class="modal-overlay" v-if="showAboutModal" @click="showAboutModal = false">
      <div class="modal-card" @click.stop>
        <button class="close-btn" @click="showAboutModal = false"><i class='bx bx-x'></i></button>
        
        <div class="modal-header">
          <div class="avatar large">AM</div>
          <div class="author-details">
            <h3>Abdou Mandara</h3>
            <p>Développeur Fullstack</p>
          </div>
        </div>

        <div class="modal-body">
          <div class="info-section">
            <h4>Mes technos</h4>
            <div class="tech-tags">
              <span class="tech-tag laravel"><i class='bx bxl-joomla'></i> Laravel</span>
              <span class="tech-tag vue"><i class='bx bxl-vuejs'></i> Vue.js</span>
              <span class="tech-tag fastapi"><i class='bx bxl-python'></i> FastAPI</span>
            </div>
          </div>

          <div class="info-section">
            <h4>Mes réseaux sociaux</h4>
            <div class="social-grid">
              <a href="#" class="social-btn"><i class='bx bxl-linkedin-square'></i> LinkedIn</a>
              <a href="#" class="social-btn"><i class='bx bxl-instagram-alt'></i> Instagram</a>
              <a href="#" class="social-btn"><i class='bx bxl-tiktok'></i> TikTok</a>
              <a href="#" class="social-btn"><i class='bx bxl-twitter'></i> X</a>
            </div>
          </div>

          <div class="info-section">
            <h4>Me contacter</h4>
            <div class="contact-links">
              <a href="https://wa.me/237693472977" target="_blank" class="contact-link whatsapp"><i class='bx bxl-whatsapp'></i> +237 693472977</a>
              <a href="mailto:cabdoumandara@gmail.com" class="contact-link email"><i class='bx bx-envelope'></i> Envoyer un email</a>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');


:root {
  --bg-main: #212121;
  --bg-sidebar: #171717;
  --bg-card: #2f2f2f;
  --text-main: #ececec;
  --text-dim: #b4b4b4;
  --border: rgba(255,255,255,0.1);
  --accent-green: #10a37f;
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  font-family: var(--font-sans);
  background-color: var(--bg-main);
  color: var(--text-main);
  overflow: hidden;
  -webkit-font-smoothing: antialiased;
}

.chatgpt-app {
  display: flex;
  height: 100vh;
  width: 100%;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: var(--bg-sidebar);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease, transform 0.3s ease;
  flex-shrink: 0;
  z-index: 100;
}

.sidebar-closed .sidebar {
  width: 0;
  transform: translateX(-100%);
  overflow: hidden;
}

.sidebar-top {
  flex: 1;
  padding: 0.75rem;
  overflow-y: auto;
}

.sidebar-header {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 0.5rem;
}

.sidebar-toggle-btn {
  font-size: 1.5rem;
  color: var(--text-dim);
  cursor: pointer;
  transition: color 0.2s;
  opacity: 0.7;
}

.sidebar-toggle-btn:hover {
  color: var(--text-main);
  opacity: 1;
}

.sidebar-btn.new-chat {
  width: 100%;
  display: flex;
  align-items: center;
  padding: 0.75rem;
  background: transparent;
  border: none;
  color: var(--text-main);
  border-radius: 8px;
  cursor: pointer;
  margin-bottom: 1rem;
  transition: background 0.2s;
}

.sidebar-btn.new-chat:hover { background: var(--bg-card); }

.icon-wrap {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
}

.sidebar-btn span { font-weight: 500; flex: 1; text-align: left; }

.toggle-icon { opacity: 0.5; cursor: pointer; }
.toggle-icon:hover { opacity: 1; }

.sidebar-nav, .sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 2px;
  margin-bottom: 1.5rem;
}

.sidebar-section label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-dim);
  padding: 0.5rem 0.75rem;
  text-transform: uppercase;
}

.nav-item {
  display: flex;
  align-items: center;
  padding: 0.6rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  color: var(--text-main);
  font-size: 0.9rem;
  transition: background 0.2s;
  gap: 0.75rem;
}

.nav-item:hover { background: var(--bg-card); }
.nav-item i { font-size: 1.2rem; }

.chat-history-item { justify-content: space-between; overflow: visible; }
.chat-history-item.active { background: var(--bg-card); font-weight: 500; }

.item-action-wrapper { position: relative; display: flex; align-items: center; }
.item-action { background: none; border: none; color: var(--text-dim); cursor: pointer; opacity: 0; padding: 2px; border-radius: 4px; transition: all 0.2s; }
.chat-history-item:hover .item-action { opacity: 1; }
.item-action:hover {  color: var(--text-main); }

.action-dropdown {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 4px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.3rem;
  box-shadow: 0 4px 12px rgba(0,0,0,0.5);
  z-index: 200;
  min-width: 120px;
}
.dropdown-item {
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  color: var(--text-main);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  transition: background 0.2s;
}
.dropdown-item.delete { color: #f87171; }
.dropdown-item:hover { background: rgba(255,255,255,0.1); }

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  background: linear-gradient(to top, rgba(0,0,0,0.2) 0%, transparent 100%);
}

.about-author-btn {
  width: 100%;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 0.6rem;
  display: flex;
  align-items: center;
  gap: 0.8rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  color: var(--text-main);
  position: relative;
  overflow: hidden;
}

.about-author-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, rgba(16, 163, 127, 0.15), transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.about-author-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  border-color: rgba(16, 163, 127, 0.4);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4), 0 0 12px rgba(16, 163, 127, 0.15);
}

.about-author-btn:hover::before {
  opacity: 1;
}

.author-avatar-modern {
  position: relative;
  width: 38px;
  height: 38px;
  border-radius: 50%;
  background: linear-gradient(135deg, #10a37f 0%, #066049 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  z-index: 2;
  box-shadow: 0 4px 10px rgba(0,0,0,0.3);
}

.author-avatar-modern .initials {
  font-weight: 700;
  font-size: 0.85rem;
  color: #fff;
  letter-spacing: 0.5px;
}

.glow-ring {
  position: absolute;
  top: -2px; left: -2px; right: -2px; bottom: -2px;
  border-radius: 50%;
  border: 1px solid rgba(16, 163, 127, 0.6);
  opacity: 0;
  transform: scale(0.9);
  transition: all 0.3s ease;
}

.about-author-btn:hover .glow-ring {
  opacity: 1;
  transform: scale(1);
  animation: spinGlow 4s linear infinite;
}

@keyframes spinGlow {
  100% { transform: scale(1) rotate(360deg); }
}

.author-info-modern {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  z-index: 2;
}

.author-info-modern .author-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
}

.author-info-modern .author-role {
  font-size: 0.7rem;
  color: var(--text-dim);
  margin-top: 2px;
  transition: color 0.3s;
}

.about-author-btn:hover .author-role {
  color: rgba(255, 255, 255, 0.8);
}

.icon-arrow {
  font-size: 1.3rem;
  color: rgba(255,255,255,0.4);
  z-index: 2;
  transition: transform 0.3s ease, color 0.3s ease;
}

.about-author-btn:hover .icon-arrow {
  color: #10a37f;
  transform: translateX(4px);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

/* Header */
.chat-header {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  z-index: 10;
}

.model-dropdown {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1.1rem;
}
.model-dropdown:hover { background: var(--bg-card); }

.header-actions { display: flex; align-items: center; gap: 0.75rem; }

.plus-badge {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  background: #3c3c44;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
}
.plus-badge i { color: #8e8ea0; }
.plus-badge .close-badge { font-size: 1rem; cursor: pointer; }

.action-icon {
  background: none;
  border: 1px solid var(--border);
  color: var(--text-main);
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  cursor: pointer;
}
.action-icon:hover { background: var(--bg-card); }

/* Chat Space */
.messages-list-wrapper {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 0;
}

.messages-container {
  max-width: 950px;
  margin: 0 auto;
  padding: 0 1rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.welcome-screen {
  height: 40vh;
  display: flex;
  align-items: center;
  justify-content: center;
}

.welcome-logo {
  width: 60px;
  height: 60px;
  border: 1px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  opacity: 0.8;
}

.message-row { display: flex; width: 100%; transition: opacity 0.3s; margin-bottom: 1.5rem; }

.message-row.user { justify-content: flex-end; }
.user-bubble {
    background: #2f2f2f;
    padding: 0.75rem 1rem;
    border-radius: 20px;
    max-width: max-content;
    font-size: 1rem;
    line-height: 1.5;
    color: var(--text-main);
    align-self: flex-end;

}

.ai-msg {
  display: flex;
  gap: 1.25rem;
  width: 100%;
}

.ai-avatar {
  width: 32px;
  height: 32px;
  background: var(--accent-green);
  border: 1px solid var(--border);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.2rem;
  color: white;
}

.ai-text { flex: 1; font-size: 1rem; line-height: 1.6; }

/* Markdown Styles */
.markdown-body {
  color: var(--text-main);
  line-height: 1.6;
}
.markdown-body p { margin-bottom: 1rem; }
.markdown-body p:last-child { margin-bottom: 0; }
.markdown-body strong { font-weight: 600; color: #fff; }
.markdown-body h1, .markdown-body h2, .markdown-body h3 {
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-weight: 600;
  color: #fff;
}
.markdown-body ul, .markdown-body ol { margin-bottom: 1rem; padding-left: 1.5rem; }
.markdown-body li { margin-bottom: 0.25rem; }

/* Result Card */
.result-card {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.result-title { font-size: 1.4rem; font-weight: 700; }
.result-title small { font-weight: 400; opacity: 0.5; font-size: 1rem; margin-left: 0.5rem; font-style: italic; }

.result-meta { color: var(--text-dim); font-size: 0.9rem; margin-top: -0.5rem; }

.section-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim); margin-bottom: 0.5rem; }

.tag-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.tag { background: var(--bg-card); padding: 0.2rem 0.6rem; border-radius: 4px; font-size: 0.85rem; }

.example-item { margin-bottom: 1rem; }
.example-item .en { font-style: italic; color: var(--text-main); margin-bottom: 0.25rem; }
.example-item .fr { font-size: 0.9rem; color: var(--text-dim); }

/* Input Bar */
.input-area {
  padding: 1.5rem 1rem 1rem;
  background: linear-gradient(to top, var(--bg-main) 70%, transparent);
}

.input-wrapper {
  max-width: 800px;
  margin: 0 auto;
  position: relative;
}

.input-card {
  background: var(--bg-card);
  border-radius: 26px;
  padding: 0.6rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.input-card input {
  flex: 1;
  background: none;
  border: none;
  color: var(--text-main);
  outline: none;
  padding: 0.5rem 0;
  font-size: 1rem;
}

.input-card input::placeholder { color: var(--text-dim); opacity: 0.5; }

.attach-btn, .action-btn {
  background: none;
  border: none;
  color: var(--text-main);
  font-size: 1.4rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  opacity: 0.7;
}

.attach-btn:hover, .action-btn:hover { opacity: 1; color: var(--accent-green); }

.send-btn {
  width: 32px;
  height: 32px;
  background: var(--text-main);
  color: var(--bg-main);
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 8px rgba(0,0,0,0.2);
}

.send-btn:disabled { background: #3c3c44; color: #171717; cursor: default; box-shadow: none; }
.send-btn:not(:disabled):hover { background: #fff; transform: scale(1.05); }

.footer-note {
  text-align: center;
  font-size: 0.72rem;
  color: var(--text-dim);
  margin-top: 1rem;
  opacity: 0.8;
}

/* Modal Styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

.modal-card {
  background: var(--bg-main);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 2rem;
  width: 90%;
  max-width: 450px;
  position: relative;
  box-shadow: 0 10px 40px rgba(0,0,0,0.5);
}

.close-btn {
  position: absolute;
  top: 1rem; right: 1rem;
  background: none; border: none;
  color: var(--text-dim);
  font-size: 1.5rem; cursor: pointer;
  transition: color 0.2s;
}
.close-btn:hover { color: var(--text-main); }

.modal-header {
  display: flex; align-items: center; gap: 1rem; margin-bottom: 2rem;
}
.avatar.large { width: 64px; height: 64px; font-size: 1.5rem; }
.author-details h3 { font-size: 1.5rem; font-weight: 700; color: var(--text-main); }
.author-details p { color: var(--accent-green); font-weight: 500; font-size: 0.95rem; }

.info-section { margin-bottom: 1.5rem; }
.info-section h4 { font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; color: var(--text-dim); margin-bottom: 0.75rem; }

.tech-tags { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.tech-tag { padding: 0.4rem 0.8rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500; display: flex; align-items: center; gap: 0.3rem; border: 1px solid var(--border); }
.tech-tag.laravel { color: #f05340; background: rgba(240, 83, 64, 0.1); border-color: rgba(240, 83, 64, 0.3); }
.tech-tag.vue { color: #4fc08d; background: rgba(79, 192, 141, 0.1); border-color: rgba(79, 192, 141, 0.3); }
.tech-tag.fastapi { color: #009688; background: rgba(0, 150, 136, 0.1); border-color: rgba(0, 150, 136, 0.3); }

.social-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.75rem; }
.social-btn { display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem; border-radius: 12px; background: var(--bg-card); color: var(--text-main); text-decoration: none; font-size: 0.9rem; transition: background 0.2s; border: 1px solid transparent; }
.social-btn:hover { background: #3a3a3a; border-color: var(--border); }
.social-btn i { font-size: 1.2rem; color: var(--text-dim); }

.contact-links { display: flex; flex-direction: column; gap: 0.5rem; }
.contact-link { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 12px; text-decoration: none; font-weight: 500; font-size: 0.95rem; transition: transform 0.2s, background 0.2s; }
.contact-link.whatsapp { background: #25D366; color: white; }
.contact-link.whatsapp:hover { background: #20ba56; transform: translateY(-2px); }
.contact-link.email { background: var(--bg-card); color: var(--text-main); border: 1px solid var(--border); }
.contact-link.email:hover { background: #3a3a3a; }

.mobile-sidebar-toggle {
  background: none;
  border: none;
  color: var(--text-main);
  font-size: 1.5rem;
  cursor: pointer;
  margin-right: 1rem;
}

/* Typing Indicator */
.typing-indicator { display: flex; gap: 4px; padding: 10px 0; }
.typing-indicator span { width: 6px; height: 6px; background: var(--text-dim); border-radius: 50%; animation: blink 1s infinite both; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes blink { 0%, 100% { opacity: 0.3; } 50% { opacity: 1; } }

/* Scrollbar */
::-webkit-scrollbar { width: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(255,255,255,0.2); }

/* Mobile Adaptations */
@media (max-width: 1024px) {
  .sidebar { position: fixed; height: 100%; transform: translateX(-100%); width: 280px; }
  .sidebar-closed .sidebar { transform: translateX(-100%); }
  .chatgpt-app:not(.sidebar-closed) .sidebar { transform: translateX(0); box-shadow: 10px 0 30px rgba(0,0,0,0.5); }
  .chatgpt-app { overflow: hidden; }
}
</style>
