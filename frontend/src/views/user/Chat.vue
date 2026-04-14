<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ChatDotRound, Plus, Fold, Expand, Promotion, User as UserIcon, SwitchButton, Search, Edit, Delete, Close, Check, Microphone, Picture } from '@element-plus/icons-vue'
import api from '@/utils/api'
import SubscriptionCheckoutDialog from '@/components/SubscriptionCheckoutDialog.vue'
import type { ChatDoneData, ChatImage, ChatMessage, Conversation, RetrievalInfo } from '@/types'

const router = useRouter()
const auth = useAuthStore()

const conversations = ref<Conversation[]>([])
const activeConvId = ref<number | null>(null)
const messages = ref<ChatMessage[]>([])
const inputText = ref('')
const sending = ref(false)
const streamText = ref('')
const thinking = ref(false)
const errorText = ref('')
const msgArea = ref<HTMLElement | null>(null)
const sideCollapsed = ref(false)
const subscribeDialogVisible = ref(false)

const searchQuery = ref('')
const contextMenuConvId = ref<number | null>(null)
const contextMenuPos = ref({ x: 0, y: 0 })
const renamingConvId = ref<number | null>(null)
const renameText = ref('')

interface AnnounceItem { id: number; title: string; content: string; type: string; is_pinned: number }
const announcements = ref<AnnounceItem[]>([])
const showAnnounceBanner = ref(true)
const announceIndex = ref(0)
let announceTimer: ReturnType<typeof setInterval> | null = null

async function loadAnnouncements() {
  try {
    const res = await api.get('/announcements')
    announcements.value = res.data.list ?? []
    if (announcements.value.length > 1) {
      announceTimer = setInterval(() => {
        announceIndex.value = (announceIndex.value + 1) % announcements.value.length
      }, 5000)
    }
  } catch { /* ignore */ }
}

function currentAnnounce() {
  if (!announcements.value.length) return null
  return announcements.value[announceIndex.value % announcements.value.length] ?? null
}

async function loadConversations() {
  try {
    const res = await api.get('/chat/conversations', { params: { page: 1, page_size: 100 } })
    conversations.value = res.data.list
  } catch { /* ignore */ }
}

const filteredConversations = computed(() => {
  const q = searchQuery.value.trim().toLowerCase()
  if (!q) return conversations.value
  return conversations.value.filter(c => (c.title || '').toLowerCase().includes(q))
})

interface ConvGroup { label: string; items: Conversation[] }

const groupedConversations = computed<ConvGroup[]>(() => {
  const now = new Date()
  const todayStart = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const yesterdayStart = new Date(todayStart.getTime() - 86400000)
  const weekStart = new Date(todayStart.getTime() - 6 * 86400000)

  const groups: { today: Conversation[]; yesterday: Conversation[]; week: Conversation[]; older: Conversation[] } = {
    today: [], yesterday: [], week: [], older: [],
  }

  for (const c of filteredConversations.value) {
    const d = new Date(c.updated_at || c.created_at || '')
    if (d >= todayStart) groups.today.push(c)
    else if (d >= yesterdayStart) groups.yesterday.push(c)
    else if (d >= weekStart) groups.week.push(c)
    else groups.older.push(c)
  }

  const result: ConvGroup[] = []
  if (groups.today.length) result.push({ label: '今天', items: groups.today })
  if (groups.yesterday.length) result.push({ label: '昨天', items: groups.yesterday })
  if (groups.week.length) result.push({ label: '近 7 天', items: groups.week })
  if (groups.older.length) result.push({ label: '更早', items: groups.older })
  return result
})

async function selectConv(conv: Conversation) {
  if (renamingConvId.value) return
  activeConvId.value = conv.id
  await loadMessages(conv.id)
}

async function loadMessages(convId: number) {
  try {
    const res = await api.get(`/chat/conversations/${convId}/messages`, { params: { page: 1, page_size: 200 } })
    messages.value = res.data.list
    scrollToBottom()
  } catch { /* ignore */ }
}

function newChat() {
  activeConvId.value = null
  messages.value = []
  streamText.value = ''
  errorText.value = ''
}

function showContextMenu(e: MouseEvent, convId: number) {
  e.preventDefault()
  contextMenuConvId.value = convId
  contextMenuPos.value = { x: e.clientX, y: e.clientY }
}

function closeContextMenu() {
  contextMenuConvId.value = null
}

function startRename(conv: Conversation) {
  closeContextMenu()
  renamingConvId.value = conv.id
  renameText.value = conv.title || ''
}

async function confirmRename() {
  if (!renamingConvId.value || !renameText.value.trim()) {
    renamingConvId.value = null
    return
  }
  try {
    await api.put(`/chat/conversations/${renamingConvId.value}`, { title: renameText.value.trim() })
    const conv = conversations.value.find(c => c.id === renamingConvId.value)
    if (conv) conv.title = renameText.value.trim()
  } catch { /* ignore */ }
  renamingConvId.value = null
}

function cancelRename() {
  renamingConvId.value = null
}

async function deleteConv(convId: number) {
  closeContextMenu()
  try {
    await api.delete(`/chat/conversations/${convId}`)
    conversations.value = conversations.value.filter(c => c.id !== convId)
    if (activeConvId.value === convId) {
      activeConvId.value = null
      messages.value = []
    }
  } catch { /* ignore */ }
}

function onDocumentClick() {
  closeContextMenu()
}

// ──────────────── 图片上传 ────────────────

const pendingImages = ref<ChatImage[]>([])
const imageInputRef = ref<HTMLInputElement | null>(null)
const uploadingImage = ref(false)

function triggerImagePicker() {
  imageInputRef.value?.click()
}

async function onImageSelected(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (!files?.length) return
  for (let i = 0; i < files.length; i++) {
    const file = files[i]
    if (!file) continue
    if (file.size > 10 * 1024 * 1024) {
      errorText.value = '图片过大，请控制在 10MB 以内'
      continue
    }
    uploadingImage.value = true
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/chat/upload-image', form)
      const data = res as unknown as { data?: { url?: string; filename?: string } }
      if (data.data?.url) {
        pendingImages.value.push({ url: data.data.url, filename: data.data.filename })
      }
    } catch {
      errorText.value = '图片上传失败，请重试'
    } finally {
      uploadingImage.value = false
    }
  }
  input.value = ''
}

function removePendingImage(index: number) {
  pendingImages.value.splice(index, 1)
}

const previewImageUrl = ref('')
function previewImage(url: string) {
  previewImageUrl.value = url
}
function closeImagePreview() {
  previewImageUrl.value = ''
}

async function onPasteImage(e: ClipboardEvent) {
  const items = e.clipboardData?.items
  if (!items) return
  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (!item || !item.type.startsWith('image/')) continue
    e.preventDefault()
    const file = item.getAsFile()
    if (!file) continue
    uploadingImage.value = true
    try {
      const form = new FormData()
      form.append('file', file)
      const res = await api.post('/chat/upload-image', form)
      const data = res as unknown as { data?: { url?: string; filename?: string } }
      if (data.data?.url) {
        pendingImages.value.push({ url: data.data.url, filename: data.data.filename })
      }
    } catch {
      errorText.value = '图片粘贴上传失败'
    } finally {
      uploadingImage.value = false
    }
  }
}

function hasActiveSubscription() {
  if (!auth.user || auth.user.subscribe_plan === 'free' || !auth.user.subscribe_expire) return false
  return new Date(auth.user.subscribe_expire).getTime() > Date.now()
}

function openSubscribeDialog(message = '') {
  if (message) errorText.value = message
  subscribeDialogVisible.value = true
}

async function handleSubscribeRefresh() {
  errorText.value = ''
  await auth.fetchProfile()
}

async function sendMessage() {
  const text = inputText.value.trim()
  const images = [...pendingImages.value]
  if ((!text && !images.length) || sending.value) return
  if (!hasActiveSubscription() && (auth.user?.free_chats_left ?? 0) <= 0) {
    openSubscribeDialog('免费次数已用完，请先订阅后继续使用')
    return
  }
  const optimisticMessageId = Date.now()
  inputText.value = ''
  pendingImages.value = []
  sending.value = true
  thinking.value = true
  streamText.value = ''
  errorText.value = ''

  messages.value.push({ id: optimisticMessageId, role: 'user', content: text || '(图片)', images, docs: [], created_at: new Date().toISOString() })
  scrollToBottom()

  try {
    const token = localStorage.getItem('token')
    const body = JSON.stringify({ conversation_id: activeConvId.value, message: text || '请看图片', images })
    const response = await fetch('/api/chat/send', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
      body,
    })

    const contentType = response.headers.get('content-type') || ''
    if (contentType.includes('application/json')) {
      const json = await response.json()
      thinking.value = false
      if (json.code === 2001) {
        errorText.value = '免费次数已用完，请订阅后继续使用'
      } else if (json.code === 1002) {
        errorText.value = '登录已过期，请重新登录'
        setTimeout(() => router.push('/login'), 1500)
      } else {
        errorText.value = json.message || '请求失败'
      }
      return
    }

    if (!response.body) { thinking.value = false; return }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    let currentEvent = ''

    while (true) {
      const { done, value } = await reader.read()
      if (done) break
      buffer += decoder.decode(value, { stream: true })
      const lines = buffer.split('\n')
      buffer = lines.pop() || ''
      for (const line of lines) {
        if (line.startsWith('event: ')) {
          currentEvent = line.slice(7).trim()
        } else if (line.startsWith('data: ')) {
          const jsonStr = line.slice(6)
          try {
            const obj = JSON.parse(jsonStr)
            if (currentEvent === 'error' || obj.code) {
              thinking.value = false
              errorText.value = obj.message || 'AI 响应异常，请稍后重试'
            } else if (currentEvent === 'chunk' || ('text' in obj && !('conversation_id' in obj))) {
              thinking.value = false
              streamText.value += obj.text
              scrollToBottom()
            } else if (currentEvent === 'done' || 'conversation_id' in obj) {
              const doneData = obj as ChatDoneData
              activeConvId.value = obj.conversation_id
              if (auth.user) {
                auth.user.free_chats_left = doneData.quota?.free_chats_left ?? auth.user.free_chats_left
              }
              messages.value.push({
                id: doneData.assistant_message_id,
                role: 'assistant',
                content: doneData.text,
                images: doneData.images || [],
                docs: doneData.docs || [],
                retrieval: doneData.retrieval || null,
                created_at: new Date().toISOString(),
              })
              streamText.value = ''
              loadConversations()
            }
          } catch { /* ignore partial JSON */ }
          currentEvent = ''
        }
      }
    }
  } catch {
    thinking.value = false
    streamText.value = ''
    errorText.value = '网络异常，请检查网络后重试'
  } finally {
    sending.value = false
    thinking.value = false
    scrollToBottom()
  }
}

function scrollToBottom() {
  nextTick(() => {
    if (msgArea.value) msgArea.value.scrollTop = msgArea.value.scrollHeight
  })
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

function formatTime(iso: string | null) {
  if (!iso) return ''
  const d = new Date(iso)
  const h = String(d.getHours()).padStart(2, '0')
  const m = String(d.getMinutes()).padStart(2, '0')
  return `${h}:${m}`
}

function retrievalTitle(retrieval?: RetrievalInfo | null) {
  if (retrieval?.status === 'success' && retrieval.mode === 'keyword_fallback') return '已切换关键词检索'
  if (retrieval?.status === 'failed') return '知识库检索失败'
  if (retrieval?.status === 'miss') return '未命中知识库'
  return ''
}

function retrievalDetail(retrieval?: RetrievalInfo | null) {
  if (!retrieval) return ''
  if (retrieval.status === 'success' && retrieval.mode === 'keyword_fallback') {
    return retrieval.message || '当前回答通过关键词检索补充了知识库内容。'
  }
  if (retrieval.status === 'failed') {
    return retrieval.error || retrieval.message || '当前回答未参考知识库。'
  }
  if (retrieval.status === 'miss') {
    return retrieval.message || '当前回答主要基于通用模型。'
  }
  return ''
}

function retrievalProviderLabel(retrieval?: RetrievalInfo | null) {
  if (!retrieval?.provider) return ''
  return `${retrieval.provider}${retrieval.model ? ` / ${retrieval.model}` : ''}`
}

// ──────────────── 语音识别 (后端 faster-whisper 优先, Web Speech API fallback) ────────────────

const SpeechRecognitionCtor = window.SpeechRecognition || window.webkitSpeechRecognition
const speechSupported = ref(!!navigator.mediaDevices?.getUserMedia || !!SpeechRecognitionCtor)
const isListening = ref(false)
const voiceError = ref('')
const voiceDuration = ref(0)
const transcribing = ref(false)
const voiceStatusText = ref('')
let mediaRecorder: MediaRecorder | null = null
let audioChunks: Blob[] = []
let voiceTimer: ReturnType<typeof setInterval> | null = null
let audioStream: MediaStream | null = null
const VOICE_MAX_SECONDS = 120
let useWebSpeechFallback = false

async function startListening() {
  voiceError.value = ''
  voiceStatusText.value = ''
  voiceDuration.value = 0
  audioChunks = []

  // 如果已标记用 Web Speech API fallback，或不支持 MediaRecorder
  if (useWebSpeechFallback || !navigator.mediaDevices?.getUserMedia) {
    startWebSpeech()
    return
  }

  try {
    audioStream = await navigator.mediaDevices.getUserMedia({ audio: true })
  } catch {
    voiceError.value = '麦克风权限被拒绝，请在浏览器设置中允许'
    return
  }

  const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
    ? 'audio/webm;codecs=opus'
    : MediaRecorder.isTypeSupported('audio/webm')
      ? 'audio/webm'
      : ''

  try {
    mediaRecorder = mimeType
      ? new MediaRecorder(audioStream, { mimeType })
      : new MediaRecorder(audioStream)
  } catch {
    voiceError.value = '无法启动录音'
    releaseAudioStream()
    return
  }

  mediaRecorder.ondataavailable = (e: BlobEvent) => {
    if (e.data.size > 0) audioChunks.push(e.data)
  }

  mediaRecorder.onstop = async () => {
    releaseAudioStream()
    if (audioChunks.length === 0) {
      voiceError.value = '未录到音频，请重试'
      return
    }
    const blob = new Blob(audioChunks, { type: mediaRecorder?.mimeType || 'audio/webm' })
    audioChunks = []
    await uploadAndTranscribe(blob)
  }

  mediaRecorder.start(500)
  isListening.value = true
  startVoiceTimer()
}

function startVoiceTimer() {
  voiceTimer = setInterval(() => {
    voiceDuration.value++
    if (voiceDuration.value >= VOICE_MAX_SECONDS) {
      stopListening()
    }
  }, 1000)
}

function stopListening() {
  isListening.value = false
  if (voiceTimer) { clearInterval(voiceTimer); voiceTimer = null }
  // 停 MediaRecorder
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    try { mediaRecorder.stop() } catch { /* ignore */ }
  } else {
    releaseAudioStream()
  }
  // 停 Web Speech API
  if (_webSpeechRecognition) {
    _webSpeechActive = false
    try { _webSpeechRecognition.stop() } catch { /* ignore */ }
  }
}

function releaseAudioStream() {
  if (audioStream) {
    audioStream.getTracks().forEach(t => t.stop())
    audioStream = null
  }
}

async function uploadAndTranscribe(blob: Blob) {
  transcribing.value = true
  voiceStatusText.value = '识别中...'
  voiceError.value = ''

  try {
    const form = new FormData()
    form.append('file', blob, 'recording.webm')
    const res = await api.post('/chat/transcribe', form, { timeout: 120000 })
    const data = res as unknown as { data?: { text?: string } }
    if (data.data?.text) {
      inputText.value += data.data.text
    } else {
      voiceError.value = '未识别到语音内容，请重试'
    }
  } catch {
    // 后端失败，尝试 Web Speech API fallback
    if (SpeechRecognitionCtor) {
      useWebSpeechFallback = true
      voiceError.value = '后端识别不可用，已切换到浏览器语音识别，请再试一次'
    } else {
      voiceError.value = '语音识别失败，请重试'
    }
  } finally {
    transcribing.value = false
    voiceStatusText.value = ''
  }
}

// ──── Web Speech API fallback ────

let _webSpeechRecognition: SpeechRecognition | null = null
let _webSpeechActive = false

function startWebSpeech() {
  if (!SpeechRecognitionCtor) {
    voiceError.value = '当前浏览器不支持语音识别'
    return
  }
  const recognition = new SpeechRecognitionCtor()
  _webSpeechRecognition = recognition
  _webSpeechActive = true
  recognition.lang = 'zh-CN'
  recognition.continuous = true
  recognition.interimResults = true
  recognition.maxAlternatives = 1

  recognition.onresult = (event: SpeechRecognitionEvent) => {
    let final = ''
    let interim = ''
    for (let i = 0; i < event.results.length; i++) {
      const result = event.results[i]
      if (!result) continue
      const text = result[0]?.transcript ?? ''
      if (result.isFinal) {
        final += text
      } else {
        interim += text
      }
    }
    if (final) inputText.value += final
    voiceStatusText.value = interim || ''
  }

  recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
    const code = event.error
    if (code === 'no-speech') {
      voiceError.value = '未检测到语音，请重试'
    } else if (code === 'not-allowed' || code === 'service-not-allowed') {
      voiceError.value = '麦克风权限被拒绝'
    } else if (code === 'network') {
      voiceError.value = '网络异常，浏览器语音识别不可用'
    } else if (code !== 'aborted') {
      voiceError.value = `语音识别错误: ${code}`
    }
    stopListening()
  }

  recognition.onend = () => {
    if (_webSpeechActive) {
      try { recognition.start() } catch { stopListening() }
    }
  }

  try {
    recognition.start()
  } catch {
    voiceError.value = '无法启动浏览器语音识别'
    return
  }

  isListening.value = true
  voiceStatusText.value = '浏览器识别中...'
  startVoiceTimer()
}

function toggleVoice() {
  if (isListening.value) {
    stopListening()
  } else {
    startListening()
  }
}

function formatVoiceDuration(s: number) {
  const m = String(Math.floor(s / 60)).padStart(2, '0')
  const sec = String(s % 60).padStart(2, '0')
  return `${m}:${sec}`
}

onMounted(async () => {
  document.addEventListener('click', onDocumentClick)
  loadAnnouncements()
  await loadConversations()
})

onUnmounted(() => {
  document.removeEventListener('click', onDocumentClick)
  if (announceTimer) clearInterval(announceTimer)
  stopListening()
})
</script>

<template>
  <div class="chat-layout">
    <!-- Sidebar -->
    <aside v-show="!sideCollapsed" class="chat-sidebar">
      <div class="sidebar-header">
        <button class="new-chat-btn" @click="newChat">
          <el-icon :size="16"><Plus /></el-icon>
          <span>新建对话</span>
        </button>
      </div>

      <div class="sidebar-search">
        <el-icon :size="14" class="search-icon"><Search /></el-icon>
        <input v-model="searchQuery" class="search-input" placeholder="搜索对话..." />
      </div>

      <div class="sidebar-list">
        <template v-for="group in groupedConversations" :key="group.label">
          <div class="conv-group-label">{{ group.label }}</div>
          <div
            v-for="c in group.items"
            :key="c.id"
            class="conv-item"
            :class="{ active: c.id === activeConvId }"
            @click="selectConv(c)"
            @contextmenu="showContextMenu($event, c.id)"
          >
            <el-icon :size="16" class="conv-icon"><ChatDotRound /></el-icon>
            <div v-if="renamingConvId === c.id" class="conv-rename" @click.stop>
              <input
                v-model="renameText"
                class="rename-input"
                autofocus
                @keyup.enter="confirmRename"
                @keyup.escape="cancelRename"
              />
              <button class="rename-action" @click="confirmRename"><el-icon :size="12"><Check /></el-icon></button>
              <button class="rename-action cancel" @click="cancelRename"><el-icon :size="12"><Close /></el-icon></button>
            </div>
            <div v-else class="conv-info">
              <div class="conv-title">{{ c.title || '新对话' }}</div>
              <div class="conv-meta">{{ c.message_count }} 条消息</div>
            </div>
            <div v-if="!renamingConvId" class="conv-actions" @click.stop>
              <button class="conv-action-btn" title="重命名" @click="startRename(c)"><el-icon :size="12"><Edit /></el-icon></button>
              <button class="conv-action-btn danger" title="删除" @click="deleteConv(c.id)"><el-icon :size="12"><Delete /></el-icon></button>
            </div>
          </div>
        </template>

        <div v-if="!filteredConversations.length" class="sidebar-empty">
          <el-icon :size="32" color="#475569"><ChatDotRound /></el-icon>
          <p v-if="searchQuery">未找到匹配的对话</p>
          <p v-else>暂无对话记录</p>
          <p class="text-xs">{{ searchQuery ? '尝试其他关键词' : '点击上方按钮开始新对话' }}</p>
        </div>
      </div>

      <div class="sidebar-footer">
        <div class="user-info">
          <div class="user-avatar">
            <el-icon :size="18"><UserIcon /></el-icon>
          </div>
          <div class="user-detail">
            <div class="user-name">{{ auth.user?.nickname }}</div>
            <div class="user-plan">
              <span v-if="auth.user?.subscribe_plan === 'free'">免费 {{ auth.user?.free_chats_left ?? 0 }} 次</span>
              <span v-else class="plan-badge">{{ auth.user?.subscribe_plan }}</span>
            </div>
          </div>
          <button class="logout-btn" @click="handleLogout" title="退出登录">
            <el-icon :size="16"><SwitchButton /></el-icon>
          </button>
        </div>
        <button class="subscribe-entry" @click="openSubscribeDialog()">
          {{ hasActiveSubscription() ? '管理订阅' : '升级订阅' }}
        </button>
      </div>
    </aside>

    <!-- Context Menu -->
    <Teleport to="body">
      <div
        v-if="contextMenuConvId !== null"
        class="ctx-menu"
        :style="{ left: contextMenuPos.x + 'px', top: contextMenuPos.y + 'px' }"
        @click.stop
      >
        <button class="ctx-item" @click="startRename(conversations.find(c => c.id === contextMenuConvId)!)">
          <el-icon :size="14"><Edit /></el-icon> 重命名
        </button>
        <button class="ctx-item danger" @click="deleteConv(contextMenuConvId!)">
          <el-icon :size="14"><Delete /></el-icon> 删除
        </button>
      </div>
    </Teleport>

    <!-- Main -->
    <div class="chat-main">
      <header class="chat-header">
        <button class="toggle-btn" @click="sideCollapsed = !sideCollapsed">
          <el-icon :size="18"><Expand v-if="sideCollapsed" /><Fold v-else /></el-icon>
        </button>
        <div class="header-title">
          <el-icon :size="18" color="#2563eb"><ChatDotRound /></el-icon>
          <span>AI 智能客服</span>
        </div>
      </header>

      <!-- 公告横幅 -->
      <div v-if="announcements.length > 0 && showAnnounceBanner && currentAnnounce()" class="announce-banner">
        <div class="announce-content">
          <span class="announce-tag" :class="currentAnnounce()!.type">{{ currentAnnounce()!.type === 'maintenance' ? '维护' : currentAnnounce()!.type === 'update' ? '更新' : '通知' }}</span>
          <span class="announce-title">{{ currentAnnounce()!.title }}</span>
          <span class="announce-text">{{ currentAnnounce()!.content }}</span>
          <span v-if="announcements.length > 1" class="announce-counter">{{ announceIndex + 1 }}/{{ announcements.length }}</span>
        </div>
        <button class="announce-close" @click="showAnnounceBanner = false">&times;</button>
      </div>

      <main ref="msgArea" class="chat-messages">
        <!-- Empty state -->
        <div v-if="!messages.length && !streamText" class="empty-state">
          <div class="empty-icon">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
              <rect width="64" height="64" rx="16" fill="#eff6ff"/>
              <rect x="14" y="16" width="24" height="16" rx="8" fill="#bfdbfe"/>
              <rect x="26" y="36" width="24" height="12" rx="6" fill="#93c5fd"/>
              <circle cx="22" cy="24" r="2" fill="#2563eb"/>
              <circle cx="30" cy="24" r="2" fill="#2563eb"/>
              <path d="M24 28q4 3 8 0" stroke="#2563eb" stroke-width="1.5" fill="none" stroke-linecap="round"/>
            </svg>
          </div>
          <h2 class="empty-title">有什么可以帮助你的?</h2>
          <p class="empty-desc">我是 AI 智能客服助手，基于飞书多维表格和大模型技术<br/>为你提供专业解答，请输入你的问题开始对话</p>
          <div class="empty-hints">
            <button class="hint-chip" @click="inputText = '账号登录不了怎么办？'">账号登录不了怎么办？</button>
            <button class="hint-chip" @click="inputText = '如何修改个人信息？'">如何修改个人信息？</button>
            <button class="hint-chip" @click="inputText = '会员套餐有哪些？'">会员套餐有哪些？</button>
          </div>
        </div>

        <!-- Messages -->
        <div v-for="msg in messages" :key="msg.id" class="msg-row" :class="msg.role">
          <div v-if="msg.role === 'assistant'" class="msg-avatar ai">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect width="20" height="20" rx="6" fill="#2563eb"/><circle cx="7.5" cy="8.5" r="1.5" fill="white"/><circle cx="12.5" cy="8.5" r="1.5" fill="white"/><path d="M7.5 13q2.5 2 5 0" stroke="white" stroke-width="1.2" fill="none" stroke-linecap="round"/></svg>
          </div>
          <div class="msg-body">
            <div v-if="msg.images?.length" class="msg-images">
              <img v-for="(img, imgIdx) in msg.images" :key="imgIdx" :src="img.url" class="msg-img" @click="previewImage(img.url)" />
            </div>
            <div class="msg-bubble" :class="msg.role">{{ msg.content }}</div>
            <div v-if="msg.role === 'assistant' && msg.docs?.length" class="doc-list">
              <div v-for="(doc, index) in msg.docs" :key="`${msg.id}-${index}-${doc.source}`" class="doc-card">
                <div class="doc-title">参考 {{ index + 1 }} · {{ doc.title }}</div>
                <div class="doc-source">{{ doc.source }}</div>
                <div v-if="doc.snippet" class="doc-snippet">{{ doc.snippet }}</div>
              </div>
            </div>
            <div v-if="msg.role === 'assistant' && (msg.retrieval?.status === 'miss' || (msg.retrieval?.status === 'success' && msg.retrieval?.mode === 'keyword_fallback'))" class="retrieval-card" :class="msg.retrieval?.status === 'miss' ? 'retrieval-miss' : 'retrieval-fallback'">
              <div class="retrieval-title">{{ retrievalTitle(msg.retrieval) }}</div>
              <div class="retrieval-text">{{ retrievalDetail(msg.retrieval) }}</div>
              <div v-if="retrievalProviderLabel(msg.retrieval)" class="retrieval-meta">{{ retrievalProviderLabel(msg.retrieval) }}</div>
            </div>
            <div class="msg-time">{{ formatTime(msg.created_at) }}</div>
          </div>
          <div v-if="msg.role === 'user'" class="msg-avatar user">
            <el-icon :size="14" color="white"><UserIcon /></el-icon>
          </div>
        </div>

        <!-- Thinking -->
        <div v-if="thinking && !streamText" class="msg-row assistant">
          <div class="msg-avatar ai">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect width="20" height="20" rx="6" fill="#2563eb"/><circle cx="7.5" cy="8.5" r="1.5" fill="white"/><circle cx="12.5" cy="8.5" r="1.5" fill="white"/><path d="M7.5 13q2.5 2 5 0" stroke="white" stroke-width="1.2" fill="none" stroke-linecap="round"/></svg>
          </div>
          <div class="msg-body">
            <div class="msg-bubble assistant thinking-bubble">
              <span class="dot-typing"><span></span><span></span><span></span></span>
            </div>
          </div>
        </div>

        <!-- Error -->
        <div v-if="errorText" class="msg-row assistant">
          <div class="msg-avatar ai">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect width="20" height="20" rx="6" fill="#ef4444"/><circle cx="7.5" cy="8.5" r="1.5" fill="white"/><circle cx="12.5" cy="8.5" r="1.5" fill="white"/><path d="M7.5 13q2.5-2 5 0" stroke="white" stroke-width="1.2" fill="none" stroke-linecap="round"/></svg>
          </div>
          <div class="msg-body">
            <div class="msg-bubble assistant error-bubble">{{ errorText }}</div>
          </div>
        </div>

        <!-- Streaming -->
        <div v-if="streamText" class="msg-row assistant">
          <div class="msg-avatar ai">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><rect width="20" height="20" rx="6" fill="#2563eb"/><circle cx="7.5" cy="8.5" r="1.5" fill="white"/><circle cx="12.5" cy="8.5" r="1.5" fill="white"/><path d="M7.5 13q2.5 2 5 0" stroke="white" stroke-width="1.2" fill="none" stroke-linecap="round"/></svg>
          </div>
          <div class="msg-body">
            <div class="msg-bubble assistant">{{ streamText }}<span class="cursor">|</span></div>
          </div>
        </div>
      </main>

      <footer class="chat-footer">
        <!-- 待发送图片预览 -->
        <div v-if="pendingImages.length" class="pending-images">
          <div v-for="(img, idx) in pendingImages" :key="img.url" class="pending-img-wrap">
            <img :src="img.url" class="pending-img" />
            <button class="pending-img-remove" @click="removePendingImage(idx)">&times;</button>
          </div>
          <div v-if="uploadingImage" class="pending-img-wrap uploading">
            <span class="voice-spinner"></span>
          </div>
        </div>

        <div class="input-bar" :class="{ recording: isListening, transcribing: transcribing }">
          <!-- 图片按钮 -->
          <button class="image-btn" title="发送图片" :disabled="sending || isListening" @click="triggerImagePicker">
            <el-icon :size="18"><Picture /></el-icon>
          </button>
          <input ref="imageInputRef" type="file" accept="image/*" multiple hidden @change="onImageSelected" />

          <!-- 麦克风按钮 -->
          <button
            v-if="speechSupported"
            class="voice-btn"
            :class="{ active: isListening, busy: transcribing }"
            :title="transcribing ? '正在识别...' : isListening ? '点击停止录音' : '点击开始语音输入'"
            :disabled="transcribing"
            @click="toggleVoice"
          >
            <template v-if="isListening">
              <span class="voice-pulse"></span>
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><rect x="6" y="6" width="12" height="12" rx="2" fill="currentColor"/></svg>
            </template>
            <template v-else-if="transcribing">
              <span class="voice-spinner"></span>
            </template>
            <el-icon v-else :size="18"><Microphone /></el-icon>
          </button>

          <!-- 录音中 / 转写中 / 正常输入 -->
          <template v-if="isListening">
            <div class="voice-indicator">
              <span class="voice-dot"></span>
              <span class="voice-label">{{ useWebSpeechFallback ? '浏览器识别' : '正在录音' }} {{ formatVoiceDuration(voiceDuration) }}</span>
            </div>
            <div class="voice-status-text">{{ voiceStatusText || (useWebSpeechFallback ? '请说话...' : '松开停止，自动识别') }}</div>
          </template>
          <template v-else-if="transcribing">
            <div class="voice-status-text transcribing-text">{{ voiceStatusText || '识别中...' }}</div>
          </template>
          <input
            v-else
            v-model="inputText"
            class="chat-input"
            :placeholder="voiceError || '输入你的问题，按 Enter 发送...'"
            :disabled="sending"
            @keyup.enter="sendMessage"
            @paste="onPasteImage"
          />

          <button class="send-btn" :class="{ active: (inputText.trim() || pendingImages.length) && !sending && !isListening && !transcribing }" :disabled="(!inputText.trim() && !pendingImages.length) || sending || isListening || transcribing" @click="sendMessage">
            <el-icon :size="18"><Promotion /></el-icon>
          </button>
        </div>
        <div class="input-hint">
          <template v-if="voiceError">
            <span class="voice-error-hint">{{ voiceError }}</span>
          </template>
          <template v-else>
            AI 回复仅供参考，请以实际情况为准
          </template>
        </div>
      </footer>
    </div>
  </div>

  <!-- 图片预览 -->
  <div v-if="previewImageUrl" class="image-preview-overlay" @click="closeImagePreview">
    <img :src="previewImageUrl" class="image-preview-img" @click.stop />
    <button class="image-preview-close" @click="closeImagePreview">&times;</button>
  </div>

  <SubscriptionCheckoutDialog v-model="subscribeDialogVisible" @refreshed="handleSubscribeRefresh" />
</template>

<style scoped>
.chat-layout { height: 100vh; display: flex; background: #f8fafc; overflow: hidden; }

/* ---- Sidebar ---- */
.chat-sidebar {
  width: 280px; min-width: 280px; background: #1e293b; display: flex; flex-direction: column; color: #e2e8f0;
}
.sidebar-header { padding: 16px 16px 8px; }
.new-chat-btn {
  width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;
  padding: 10px; border-radius: 10px; border: 1px dashed rgba(255,255,255,0.2);
  color: #e2e8f0; font-size: 14px; cursor: pointer; background: transparent;
  transition: all 0.2s;
}
.new-chat-btn:hover { background: rgba(255,255,255,0.08); border-color: rgba(255,255,255,0.35); }

/* Search */
.sidebar-search {
  position: relative; padding: 4px 16px 8px;
}
.search-icon { position: absolute; left: 28px; top: 50%; transform: translateY(-50%); color: #64748b; pointer-events: none; }
.search-input {
  width: 100%; padding: 8px 12px 8px 32px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);
  background: rgba(255,255,255,0.05); color: #e2e8f0; font-size: 13px; outline: none;
  transition: all 0.2s; box-sizing: border-box;
}
.search-input::placeholder { color: #64748b; }
.search-input:focus { border-color: rgba(59,130,246,0.5); background: rgba(255,255,255,0.08); }

/* Conv list */
.sidebar-list { flex: 1; overflow-y: auto; padding: 0 8px; }
.sidebar-list::-webkit-scrollbar { width: 4px; }
.sidebar-list::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.1); border-radius: 4px; }

/* Group labels */
.conv-group-label {
  font-size: 11px; font-weight: 600; color: #64748b; text-transform: uppercase;
  padding: 12px 12px 4px; letter-spacing: 0.5px;
}

.conv-item {
  display: flex; align-items: center; gap: 10px; padding: 8px 12px; border-radius: 10px;
  cursor: pointer; margin-bottom: 1px; transition: all 0.15s; position: relative;
}
.conv-item:hover { background: rgba(255,255,255,0.06); }
.conv-item.active { background: rgba(59,130,246,0.2); }
.conv-icon { color: #64748b; flex-shrink: 0; }
.conv-item.active .conv-icon { color: #93c5fd; }
.conv-info { min-width: 0; flex: 1; }
.conv-title { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.conv-meta { font-size: 11px; color: #64748b; margin-top: 2px; }

/* Hover actions */
.conv-actions {
  display: none; align-items: center; gap: 2px; flex-shrink: 0;
}
.conv-item:hover .conv-actions { display: flex; }
.conv-action-btn {
  width: 24px; height: 24px; border-radius: 6px; border: none; background: transparent;
  color: #94a3b8; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s;
}
.conv-action-btn:hover { background: rgba(255,255,255,0.1); color: #e2e8f0; }
.conv-action-btn.danger:hover { background: rgba(239,68,68,0.2); color: #f87171; }

/* Inline rename */
.conv-rename { display: flex; align-items: center; gap: 4px; flex: 1; min-width: 0; }
.rename-input {
  flex: 1; min-width: 0; padding: 4px 8px; border-radius: 6px; border: 1px solid rgba(59,130,246,0.5);
  background: rgba(255,255,255,0.1); color: #e2e8f0; font-size: 13px; outline: none;
}
.rename-action {
  width: 22px; height: 22px; border-radius: 5px; border: none; background: rgba(34,197,94,0.2);
  color: #4ade80; cursor: pointer; display: flex; align-items: center; justify-content: center;
  transition: all 0.15s; flex-shrink: 0;
}
.rename-action:hover { background: rgba(34,197,94,0.35); }
.rename-action.cancel { background: rgba(239,68,68,0.15); color: #f87171; }
.rename-action.cancel:hover { background: rgba(239,68,68,0.3); }

.sidebar-empty { padding: 40px 20px; text-align: center; color: #64748b; font-size: 13px; }
.sidebar-empty p { margin-top: 8px; }
.sidebar-footer { padding: 12px; border-top: 1px solid rgba(255,255,255,0.08); }
.user-info { display: flex; align-items: center; gap: 10px; }
.user-avatar {
  width: 34px; height: 34px; border-radius: 10px; background: rgba(59,130,246,0.2);
  display: flex; align-items: center; justify-content: center; color: #93c5fd; flex-shrink: 0;
}
.user-detail { flex: 1; min-width: 0; }
.user-name { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.user-plan { font-size: 11px; color: #64748b; margin-top: 1px; }
.plan-badge { color: #34d399; font-weight: 600; }
.logout-btn { background: none; border: none; color: #64748b; cursor: pointer; padding: 6px; border-radius: 8px; transition: all 0.15s; }
.logout-btn:hover { background: rgba(239,68,68,0.15); color: #f87171; }
.subscribe-entry {
  margin-top: 10px; width: 100%; border: 1px solid rgba(96,165,250,0.28); background: rgba(37,99,235,0.14);
  color: #dbeafe; border-radius: 12px; padding: 10px 12px; font-size: 13px; font-weight: 600; cursor: pointer;
  transition: all 0.15s;
}
.subscribe-entry:hover { background: rgba(37,99,235,0.22); border-color: rgba(147,197,253,0.42); }

/* ---- Context Menu ---- */
.ctx-menu {
  position: fixed; z-index: 9999; background: #1e293b; border: 1px solid rgba(255,255,255,0.12);
  border-radius: 10px; padding: 4px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); min-width: 140px;
}
.ctx-item {
  display: flex; align-items: center; gap: 8px; width: 100%; padding: 8px 12px; border: none;
  background: transparent; color: #e2e8f0; font-size: 13px; border-radius: 6px; cursor: pointer;
  transition: all 0.12s;
}
.ctx-item:hover { background: rgba(255,255,255,0.08); }
.ctx-item.danger { color: #f87171; }
.ctx-item.danger:hover { background: rgba(239,68,68,0.15); }

/* ---- Main ---- */
.chat-main { flex: 1; display: flex; flex-direction: column; min-width: 0; overflow: hidden; }
.chat-header {
  height: 56px; background: #fff; border-bottom: 1px solid #e2e8f0;
  display: flex; align-items: center; padding: 0 20px; gap: 12px; flex-shrink: 0;
}
.toggle-btn { background: none; border: none; cursor: pointer; padding: 6px; border-radius: 8px; color: #64748b; transition: all 0.15s; }
.toggle-btn:hover { background: #f1f5f9; color: #334155; }
.header-title { display: flex; align-items: center; gap: 8px; font-size: 15px; font-weight: 600; color: #1e293b; }

/* ---- Announce Banner ---- */
.announce-banner {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 20px; background: #eff6ff; border-bottom: 1px solid #bfdbfe;
  font-size: 13px; color: #1e40af; flex-shrink: 0;
}
.announce-content { display: flex; align-items: center; gap: 8px; min-width: 0; flex: 1; overflow: hidden; }
.announce-tag {
  padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; flex-shrink: 0;
  background: #dbeafe; color: #2563eb;
}
.announce-tag.maintenance { background: #fef3c7; color: #d97706; }
.announce-tag.update { background: #d1fae5; color: #059669; }
.announce-title { font-weight: 600; white-space: nowrap; flex-shrink: 0; }
.announce-text { color: #3b82f6; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.announce-counter { font-size: 11px; color: #93c5fd; flex-shrink: 0; margin-left: auto; }
.announce-close {
  background: none; border: none; font-size: 18px; color: #93c5fd; cursor: pointer;
  padding: 0 4px; line-height: 1; flex-shrink: 0;
}
.announce-close:hover { color: #2563eb; }

/* ---- Messages ---- */
.chat-messages { flex: 1; overflow-y: auto; padding: 24px 0; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; padding: 40px 24px; }
.empty-icon { margin-bottom: 20px; }
.empty-title { font-size: 20px; font-weight: 700; color: #1e293b; margin-bottom: 8px; }
.empty-desc { font-size: 14px; color: #94a3b8; text-align: center; line-height: 1.7; margin-bottom: 24px; }
.empty-hints { display: flex; flex-wrap: wrap; gap: 8px; justify-content: center; }
.hint-chip {
  padding: 8px 16px; border-radius: 20px; border: 1px solid #e2e8f0; background: #fff;
  font-size: 13px; color: #475569; cursor: pointer; transition: all 0.15s;
}
.hint-chip:hover { border-color: #93c5fd; color: #2563eb; background: #eff6ff; }

.msg-row {
  display: flex; align-items: flex-start; gap: 10px; padding: 6px 24px;
  max-width: 820px; margin: 0 auto; width: 100%; box-sizing: border-box;
}
.msg-row.user { flex-direction: row-reverse; }
.msg-avatar {
  width: 32px; height: 32px; border-radius: 10px; display: flex; align-items: center;
  justify-content: center; flex-shrink: 0; margin-top: 2px;
}
.msg-avatar.ai { background: #eff6ff; }
.msg-avatar.user { background: #2563eb; }
.msg-body { min-width: 0; max-width: calc(100% - 52px); }
.msg-bubble {
  padding: 10px 16px; border-radius: 16px; font-size: 14px; line-height: 1.7;
  white-space: pre-wrap; word-break: break-word; overflow-wrap: break-word;
}
.msg-bubble.user { background: #2563eb; color: #fff; border-bottom-right-radius: 4px; }
.msg-bubble.assistant { background: #fff; color: #1e293b; border: 1px solid #e2e8f0; border-bottom-left-radius: 4px; }
.doc-list { margin-top: 8px; display: flex; flex-direction: column; gap: 8px; }
.doc-card {
  background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px;
  padding: 10px 12px;
}
.doc-title { font-size: 12px; font-weight: 600; color: #1e293b; }
.doc-source { margin-top: 2px; font-size: 11px; color: #2563eb; word-break: break-all; }
.doc-snippet { margin-top: 6px; font-size: 12px; line-height: 1.6; color: #64748b; }
.retrieval-card {
  margin-top: 8px; border-radius: 12px; padding: 10px 12px; border: 1px solid;
}
.retrieval-failed { background: #fef2f2; border-color: #fecaca; }
.retrieval-miss { background: #fff7ed; border-color: #fed7aa; }
.retrieval-fallback { background: #ecfeff; border-color: #a5f3fc; }
.retrieval-title { font-size: 12px; font-weight: 600; color: #1e293b; }
.retrieval-text { margin-top: 4px; font-size: 12px; line-height: 1.6; color: #475569; }
.retrieval-meta { margin-top: 6px; font-size: 11px; color: #64748b; word-break: break-all; }
.msg-time { font-size: 11px; color: #94a3b8; margin-top: 4px; padding: 0 4px; }
.msg-row.user .msg-time { text-align: right; }
.cursor { animation: blink 0.8s infinite; font-weight: 300; color: #2563eb; }
@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }

/* Thinking dots */
.thinking-bubble { display: flex; align-items: center; min-height: 24px; }
.dot-typing { display: inline-flex; gap: 5px; align-items: center; }
.dot-typing span {
  width: 7px; height: 7px; border-radius: 50%; background: #94a3b8;
  animation: dotPulse 1.4s ease-in-out infinite;
}
.dot-typing span:nth-child(2) { animation-delay: 0.2s; }
.dot-typing span:nth-child(3) { animation-delay: 0.4s; }
@keyframes dotPulse {
  0%,80%,100% { opacity: 0.3; transform: scale(0.8); }
  40% { opacity: 1; transform: scale(1); }
}

/* Error bubble */
.error-bubble { background: #fef2f2 !important; color: #dc2626 !important; border-color: #fecaca !important; }

/* ---- Footer ---- */
.chat-footer { padding: 16px 24px 12px; background: #f8fafc; flex-shrink: 0; }
.input-bar {
  max-width: 780px; margin: 0 auto; display: flex; align-items: center;
  background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
  padding: 4px 4px 4px 8px; transition: all 0.2s;
  box-shadow: 0 1px 6px rgba(0,0,0,0.04); gap: 4px;
}
.input-bar:focus-within { border-color: #93c5fd; box-shadow: 0 0 0 3px rgba(59,130,246,0.1); }
.input-bar.recording { border-color: #f87171; box-shadow: 0 0 0 3px rgba(239,68,68,0.1); background: #fef2f2; }
.chat-input {
  flex: 1; border: none; outline: none; font-size: 14px; color: #1e293b;
  background: transparent; padding: 10px 0; min-width: 0;
}
.chat-input::placeholder { color: #94a3b8; }

/* Voice button */
.voice-btn {
  width: 36px; height: 36px; border-radius: 10px; border: none;
  background: transparent; color: #94a3b8; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; flex-shrink: 0; position: relative;
}
.voice-btn:hover { background: #f1f5f9; color: #64748b; }
.voice-btn.active { background: #fee2e2; color: #ef4444; }
.voice-btn.active:hover { background: #fecaca; }

/* Pulse ring */
.voice-pulse {
  position: absolute; inset: 2px; border-radius: 10px;
  border: 2px solid #ef4444; opacity: 0.4;
  animation: voicePulseRing 1.5s ease-out infinite;
}
@keyframes voicePulseRing {
  0% { transform: scale(1); opacity: 0.4; }
  100% { transform: scale(1.35); opacity: 0; }
}

/* Recording indicator */
.voice-indicator { display: flex; align-items: center; gap: 6px; flex-shrink: 0; }
.voice-dot {
  width: 8px; height: 8px; border-radius: 50%; background: #ef4444;
  animation: voiceDotBlink 1s ease-in-out infinite;
}
@keyframes voiceDotBlink { 0%,100%{opacity:1} 50%{opacity:0.3} }
.voice-label { font-size: 13px; color: #ef4444; font-weight: 500; white-space: nowrap; }

/* Voice status text */
.voice-status-text {
  flex: 1; min-width: 0; font-size: 13px; color: #94a3b8;
  padding: 10px 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
}
.transcribing-text { color: #2563eb; font-weight: 500; }

/* Voice spinner (transcribing) */
.voice-spinner {
  width: 18px; height: 18px; border: 2px solid #e2e8f0; border-top-color: #2563eb;
  border-radius: 50%; animation: voiceSpin 0.8s linear infinite;
}
@keyframes voiceSpin { to { transform: rotate(360deg); } }

/* Transcribing state */
.voice-btn.busy { background: #eff6ff; color: #2563eb; cursor: wait; }
.input-bar.transcribing { border-color: #93c5fd; background: #f0f9ff; }

/* Voice error */
.voice-error-hint { color: #ef4444; }

.send-btn {
  width: 40px; height: 40px; border-radius: 12px; border: none;
  background: #e2e8f0; color: #94a3b8; cursor: pointer; display: flex;
  align-items: center; justify-content: center; transition: all 0.2s; flex-shrink: 0;
}
.send-btn.active { background: #2563eb; color: #fff; }
.send-btn.active:hover { background: #1d4ed8; }
.input-hint { max-width: 780px; margin: 8px auto 0; font-size: 11px; color: #94a3b8; text-align: center; }

/* ---- Image button ---- */
.image-btn {
  width: 36px; height: 36px; border-radius: 10px; border: none;
  background: transparent; color: #94a3b8; cursor: pointer;
  display: flex; align-items: center; justify-content: center;
  transition: all 0.2s; flex-shrink: 0;
}
.image-btn:hover { background: #f1f5f9; color: #64748b; }
.image-btn:disabled { opacity: 0.4; cursor: not-allowed; }

/* ---- Pending images preview ---- */
.pending-images {
  display: flex; gap: 8px; padding: 8px 12px; flex-wrap: wrap;
  max-width: 780px; margin: 0 auto; width: 100%;
}
.pending-img-wrap {
  position: relative; width: 64px; height: 64px; border-radius: 8px;
  overflow: hidden; border: 1px solid #e2e8f0; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center; background: #f8fafc;
}
.pending-img { width: 100%; height: 100%; object-fit: cover; }
.pending-img-remove {
  position: absolute; top: 2px; right: 2px; width: 18px; height: 18px;
  border-radius: 50%; border: none; background: rgba(0,0,0,0.5); color: #fff;
  font-size: 14px; line-height: 1; cursor: pointer; display: flex;
  align-items: center; justify-content: center; padding: 0;
}
.pending-img-remove:hover { background: rgba(0,0,0,0.75); }
.pending-img-wrap.uploading { background: #f1f5f9; }

/* ---- Message images ---- */
.msg-images { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 6px; }
.msg-img {
  max-width: 240px; max-height: 180px; border-radius: 8px; cursor: pointer;
  object-fit: cover; border: 1px solid #e2e8f0; transition: opacity 0.2s;
}
.msg-img:hover { opacity: 0.85; }

/* ---- Image preview overlay ---- */
.image-preview-overlay {
  position: fixed; inset: 0; z-index: 9999; background: rgba(0,0,0,0.8);
  display: flex; align-items: center; justify-content: center; cursor: zoom-out;
}
.image-preview-img {
  max-width: 90vw; max-height: 90vh; border-radius: 8px; cursor: default;
  box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.image-preview-close {
  position: fixed; top: 16px; right: 16px; width: 40px; height: 40px;
  border-radius: 50%; border: none; background: rgba(255,255,255,0.15); color: #fff;
  font-size: 24px; cursor: pointer; display: flex; align-items: center;
  justify-content: center; backdrop-filter: blur(4px); transition: background 0.2s;
}
.image-preview-close:hover { background: rgba(255,255,255,0.3); }

@media (max-width: 768px) {
  .chat-sidebar { position: fixed; left: 0; top: 0; bottom: 0; z-index: 50; }
  .msg-row { padding: 6px 16px; }
  .chat-footer { padding: 12px 16px 8px; }
  .msg-img { max-width: 180px; max-height: 140px; }
}
</style>
