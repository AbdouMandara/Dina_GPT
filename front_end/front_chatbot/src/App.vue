<script setup>
import { ref, onMounted, nextTick } from 'vue'
import axios from 'axios'

const word = ref('')
const loading = ref(false)
const result = ref(null)
const error = ref('')
const resultsContainer = ref(null)

const learnWord = async () => {
  if (!word.value.trim() || loading.value) return
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await axios.post('http://localhost:8001/learn-word', {
      word: word.value
    })
    result.value = response.data
    word.value = '' // Reset input after success like a chat
    
    // Scroll to bottom after result appears
    await nextTick()
    window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })
  } catch (err) {
    console.error(err)
    error.value = "Oups ! Impossible de récupérer les informations pour ce mot."
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="app-wrapper">
    <!-- Background Elements -->
    <div class="mesh-gradient"></div>
    
    <div class="container">
      <header class="main-header" :class="{ 'minimized': result }">
        <div class="logo-area">
          <h1 class="logo-text">Vocab<span>AI</span></h1>
        </div>
        <p class="hero-subtitle">Votre compagnon linguistique intelligent, inspiré par la recherche et l'innovation.</p>
      </header>

      <main class="content-area" ref="resultsContainer">
        <transition name="slide-up">
          <div v-if="result" class="result-display">
            <div class="word-card">
              <div class="card-header">
                <div class="badge-row">
                  <span class="badge secondary" v-if="result.part_of_speech">{{ result.part_of_speech }}</span>
                  <span class="badge primary">Apprentissage</span>
                </div>
                
                <div class="title-section">
                  <h2 class="main-word">{{ result.word }}</h2>
                  <div class="phonetic" v-if="result.phonetic">{{ result.phonetic }}</div>
                </div>
                
                <div class="translation-highlight">
                  {{ result.translation }}
                </div>
              </div>

              <div class="card-body">
                <section class="info-group">
                  <div class="section-title">
                    <svg viewBox="0 0 24 24" class="icon"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 15h-2v-6h2v6zm0-8h-2V7h2v2z" fill="currentColor"/></svg>
                    <span>Signification</span>
                  </div>
                  <p class="definition-text">{{ result.definition }}</p>
                </section>

                <section class="info-group" v-if="result.synonyms && result.synonyms.length">
                  <div class="section-title">
                    <span>Synonymes</span>
                  </div>
                  <div class="synonyms-list">
                    <span v-for="syn in result.synonyms" :key="syn" class="syn-tag">{{ syn }}</span>
                  </div>
                </section>

                <div class="divider"></div>

                <section class="info-group">
                  <div class="section-title">
                    <svg viewBox="0 0 24 24" class="icon"><path d="M21 15.46l-5.27-.61-2.52-4.74-2.52 4.74-5.27.61 3.81 3.71-.9 5.25L13 21.88l4.67 2.45-.9-5.25 3.81-3.71-.63-4.46z" fill="currentColor"/></svg>
                    <span>Exemples immersifs</span>
                  </div>
                  <div class="examples-stack">
                    <div 
                      v-for="(item, index) in result.examples" 
                      :key="index"
                      class="example-item"
                    >
                      <div class="example-content">
                        <p class="en-text">{{ item.en }}</p>
                        <p class="fr-text">{{ item.fr }}</p>
                      </div>
                    </div>
                  </div>
                </section>
              </div>
            </div>
          </div>
        </transition>

        <div v-if="error" class="error-toast">
          {{ error }}
        </div>
      </main>

      <!-- Fixed Bottom Search Bar -->
      <footer class="footer-controls">
        <div class="search-container">
          <div class="input-wrapper">
            <input 
              v-model="word" 
              @keyup.enter="learnWord"
              type="text" 
              placeholder="Quel mot souhaitez-vous explorer aujourd'hui ?" 
              class="chat-input"
              :disabled="loading"
            />
            <button @click="learnWord" :disabled="loading || !word.trim()" class="send-button">
              <svg v-if="!loading" viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M22 2L11 13M22 2L15 22L11 13M11 13L2 9L22 2" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              <div v-else class="chat-loader"></div>
            </button>
          </div>
          <p class="input-hint">Propulsé par Gemma 4 & Novita AI</p>
        </div>
      </footer>
    </div>
  </div>
</template>

<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');

:root {
  --primary: #3b82f6;
  --primary-glow: rgba(59, 130, 246, 0.5);
  --bg-dark: #0a0a0c;
  --card-bg: rgba(23, 23, 26, 0.7);
  --glass-border: rgba(255, 255, 255, 0.08);
  --text-main: #f4f4f5;
  --text-muted: #a1a1aa;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background-color: var(--bg-dark);
  color: var(--text-main);
  overflow-x: hidden;
  -webkit-font-smoothing: antialiased;
}

.app-wrapper {
  position: relative;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Mesh Gradient Background */
.mesh-gradient {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: -1;
  background: 
    radial-gradient(at 0% 0%, rgba(59, 130, 246, 0.15) 0px, transparent 50%),
    radial-gradient(at 100% 0%, rgba(147, 51, 234, 0.1) 0px, transparent 50%),
    radial-gradient(at 50% 100%, rgba(59, 130, 246, 0.05) 0px, transparent 50%);
  filter: blur(80px);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  width: 100%;
  padding: 0 1.5rem;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

/* Header Styles */
.main-header {
  padding-top: 15vh;
  text-align: center;
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}

.main-header.minimized {
  padding-top: 3rem;
  transform: scale(0.9);
  opacity: 0.8;
}

.logo-area {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-bottom: 1rem;
}

.logo-icon {
  width: 42px;
  height: 42px;
  background: linear-gradient(135deg, #3b82f6, #8b5cf6);
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  color: white;
  font-size: 1.5rem;
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
}

.logo-text {
  font-size: 2.2rem;
  font-weight: 700;
  letter-spacing: -1px;
}

.logo-text span {
  background: linear-gradient(to right, #3b82f6, #8b5cf6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.hero-subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
  max-width: 500px;
  margin: 0 auto;
  line-height: 1.6;
}

/* Content Area */
.content-area {
  flex: 1;
  padding: 4rem 0 10rem;
}

.result-display {
  width: 100%;
  animation: fadeIn 1s ease-out;
}

.word-card {
  background: rgba(23, 23, 26, 0.4);
  backdrop-filter: blur(40px) saturate(180%);
  -webkit-backdrop-filter: blur(40px) saturate(180%);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 2.5rem;
  padding: 0;
  overflow: hidden;
  box-shadow: 
    0 40px 100px -20px rgba(0, 0, 0, 0.6),
    inset 0 1px 1px rgba(255, 255, 255, 0.05);
  transition: transform 0.4s cubic-bezier(0.2, 0.8, 0.2, 1);
}

.card-header {
  padding: 3rem 3rem 2rem;
  background: linear-gradient(180deg, rgba(59, 130, 246, 0.05) 0%, transparent 100%);
  border-bottom: 1px solid rgba(255, 255, 255, 0.03);
}

.badge-row {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.badge {
  padding: 0.5rem 1.25rem;
  border-radius: 2rem;
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
}

.badge.primary {
  background: var(--primary);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.badge.secondary {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.title-section {
  display: flex;
  align-items: baseline;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

.main-word {
  font-size: 5rem;
  font-weight: 800;
  letter-spacing: -4px;
  line-height: 0.9;
  background: linear-gradient(to bottom, #fff 40%, rgba(255,255,255,0.7));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  filter: drop-shadow(0 0 20px rgba(59, 130, 246, 0.2));
}

.phonetic {
  font-family: 'Inter', sans-serif;
  font-size: 1.5rem;
  color: var(--primary);
  opacity: 0.8;
  font-weight: 300;
}

.translation-highlight {
  font-size: 1.8rem;
  font-weight: 600;
  color: var(--text-main);
  opacity: 0.9;
}

.card-body {
  padding: 3rem;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: var(--text-muted);
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.15em;
}

.section-title .icon {
  width: 18px;
  height: 18px;
  opacity: 0.5;
}

.definition-text {
  font-size: 1.4rem;
  line-height: 1.6;
  color: #e4e4e7;
  font-weight: 400;
}

.synonyms-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.syn-tag {
  background: rgba(59, 130, 246, 0.08);
  color: #60a5fa;
  padding: 0.4rem 1rem;
  border-radius: 0.75rem;
  font-size: 0.9rem;
  font-weight: 500;
  border: 1px solid rgba(59, 130, 246, 0.1);
}

.divider {
  height: 1px;
  background: linear-gradient(90deg, rgba(255,255,255,0.05), transparent);
  margin: 3rem 0;
}

.examples-stack {
  display: grid;
  gap: 1.5rem;
}

.example-item {
  position: relative;
  padding-left: 2rem;
  border-left: 2px solid rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.example-item:hover {
  border-left-color: var(--primary);
  transform: translateX(8px);
}

.en-text {
  font-size: 1.25rem;
  color: white;
  margin-bottom: 0.5rem;
  line-height: 1.5;
}

.fr-text {
  font-size: 1rem;
  color: var(--text-muted);
  font-weight: 400;
}

/* Footer / Search controls */
.footer-controls {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 2rem 1.5rem 3rem;
  background: linear-gradient(to top, var(--bg-dark) 50%, transparent);
  pointer-events: none;
  z-index: 100;
}

.search-container {
  max-width: 800px;
  margin: 0 auto;
  pointer-events: auto;
}

.input-wrapper {
  background: rgba(30,30,35,0.6);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 2rem;
  padding: 0.75rem 0.75rem 0.75rem 1.5rem;
  display: flex;
  align-items: center;
  box-shadow: 0 30px 60px rgba(0,0,0,0.5);
  transition: all 0.3s;
}

.input-wrapper:focus-within {
  border-color: rgba(59, 130, 246, 0.4);
  background: rgba(35,35,40,0.8);
  box-shadow: 0 0 0 1px rgba(59, 130, 246, 0.2), 0 30px 60px rgba(0,0,0,0.5);
}

.chat-input {
  flex: 1;
  background: transparent;
  border: none;
  color: white;
  font-size: 1.1rem;
  padding: 0.8rem 0;
  outline: none;
  font-family: inherit;
}

.send-button {
  background: var(--primary);
  color: white;
  border: none;
  width: 48px;
  height: 48px;
  border-radius: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
}

.send-button:hover:not(:disabled) {
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 12px 20px rgba(59, 130, 246, 0.4);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  filter: grayscale(1);
}

.input-hint {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.7rem;
  color: #4a4a4e;
  font-weight: 500;
  letter-spacing: 0.05em;
}

/* Utils */
.error-toast {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  padding: 1rem 1.5rem;
  border-radius: 1rem;
  border: 1px solid rgba(239, 68, 68, 0.2);
  text-align: center;
  margin-top: 2rem;
}

.chat-loader {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Transitions */
.slide-up-enter-active {
  transition: all 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.slide-up-enter-from {
  opacity: 0;
  transform: translateY(60px) scale(0.95);
}

@media (max-width: 640px) {
  .main-word { font-size: 3rem; letter-spacing: -2px; }
  .card-header, .card-body { padding: 2rem 1.5rem; }
  .word-card { border-radius: 1.5rem; }
  .phonetic { font-size: 1.1rem; }
}
</style>
