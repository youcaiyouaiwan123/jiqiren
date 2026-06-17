<script setup lang="ts">
import { reactive, ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { ElMessage } from 'element-plus'
import { Setting, Right } from '@element-plus/icons-vue'
import api from '@/utils/api'

const router = useRouter()
const adminStore = useAdminStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const lockMsg = ref('')

// ── 验证码状态 ───────────────────────
const captcha = reactive({
  id: '',
  bg: '',
  jigsaw: '',
  jigsawY: 0,
  bgWidth: 320,
  bgHeight: 160,
  pieceSize: 50,
  loaded: false,
})
const slideX = ref(0)
const verified = ref(false)
const dragging = ref(false)
const sliderText = ref('向右拖动滑块完成验证')
const sliderError = ref(false)

const maxX = computed(() => captcha.bgWidth - captcha.pieceSize)
const sliderWidth = ref(0) // 由模板 ref 测量
const sliderTrackRef = ref<HTMLElement | null>(null)

async function loadCaptcha() {
  captcha.loaded = false
  verified.value = false
  slideX.value = 0
  sliderError.value = false
  sliderText.value = '向右拖动滑块完成验证'
  try {
    const res = await api.get('/admin/captcha/slide')
    const d = res.data as any
    captcha.id = d.captcha_id
    captcha.bg = d.bg_image
    captcha.jigsaw = d.jigsaw_image
    captcha.jigsawY = d.jigsaw_y
    captcha.bgWidth = d.bg_width
    captcha.bgHeight = d.bg_height
    captcha.pieceSize = d.piece_size
    captcha.loaded = true
  } catch (err) {
    ElMessage.error('验证码加载失败，请刷新重试')
  }
}

let dragStartX = 0
let dragStartSlide = 0

function onMouseDown(e: MouseEvent | TouchEvent) {
  if (verified.value || !captcha.loaded) return
  dragging.value = true
  sliderError.value = false
  dragStartX = 'touches' in e ? e.touches[0].clientX : e.clientX
  dragStartSlide = slideX.value
  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.addEventListener('touchmove', onMouseMove, { passive: false })
  document.addEventListener('touchend', onMouseUp)
}

function onMouseMove(e: MouseEvent | TouchEvent) {
  if (!dragging.value) return
  if ('touches' in e) e.preventDefault()
  const cx = 'touches' in e ? e.touches[0].clientX : e.clientX
  // 把 slider track 的像素移动比例换算到 bg image 的像素位置
  const deltaPx = cx - dragStartX
  const trackW = sliderTrackRef.value?.offsetWidth || captcha.bgWidth
  const ratio = maxX.value / (trackW - 40) // 40 = slider button width
  const newX = dragStartSlide + deltaPx * ratio
  slideX.value = Math.max(0, Math.min(maxX.value, newX))
}

async function onMouseUp() {
  if (!dragging.value) return
  dragging.value = false
  document.removeEventListener('mousemove', onMouseMove)
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('touchmove', onMouseMove)
  document.removeEventListener('touchend', onMouseUp)
  // 标记为已选定，等登录时一起提交
  verified.value = true
  sliderText.value = '已选定位置，点击下方"登录"提交验证'
}

async function handleLogin() {
  if (!form.username || !form.password) { ElMessage.warning('请填写用户名和密码'); return }
  if (!verified.value) { ElMessage.warning('请先完成滑块验证'); return }
  loading.value = true
  lockMsg.value = ''
  try {
    await adminStore.login(form.username, form.password, captcha.id, Math.round(slideX.value))
    router.push('/admin/dashboard')
  } catch (err: any) {
    if (err?.code === 1030) {
      lockMsg.value = err.message || '账号已锁定，请稍后重试'
    } else if (err?.code === 1040 || err?.code === 1041) {
      sliderError.value = true
      sliderText.value = '验证未通过，请重试'
      // 重新生成新的验证码
      await loadCaptcha()
    }
  } finally {
    loading.value = false
  }
}

const buttonLeft = computed(() => {
  if (!sliderTrackRef.value) return 0
  const trackW = sliderTrackRef.value.offsetWidth
  return (slideX.value / maxX.value) * (trackW - 40)
})

const pieceLeftPct = computed(() => {
  return (slideX.value / captcha.bgWidth) * 100
})

onMounted(() => { loadCaptcha() })
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-brand">
        <div class="brand-content">
          <el-icon :size="48" color="rgba(255,255,255,0.85)"><Setting /></el-icon>
          <h1 class="brand-title">AI 课程答疑助手</h1>
          <p class="brand-desc">管理后台</p>
        </div>
      </div>
      <div class="login-form-area">
        <div class="form-inner">
          <h2 class="form-title">管理员登录</h2>
          <p class="form-subtitle">请输入管理员凭据</p>
          <el-form @submit.prevent="handleLogin" class="mt-8">
            <el-form-item>
              <el-input v-model="form.username" placeholder="管理员用户名" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="form.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </el-form-item>

            <!-- 滑块验证码 -->
            <div class="captcha-wrap">
              <div class="captcha-bg" :style="{ height: captcha.bgHeight + 'px' }">
                <img v-if="captcha.loaded" :src="captcha.bg" class="bg-img" />
                <img
                  v-if="captcha.loaded"
                  :src="captcha.jigsaw"
                  class="piece-img"
                  :style="{ top: captcha.jigsawY + 'px', left: pieceLeftPct + '%', width: captcha.pieceSize + 'px', height: captcha.pieceSize + 'px' }"
                />
                <div v-if="!captcha.loaded" class="captcha-loading">加载中...</div>
                <div class="captcha-refresh" @click="loadCaptcha" title="刷新验证码">⟳</div>
              </div>
              <div ref="sliderTrackRef" class="slider-track" :class="{ 'is-error': sliderError, 'is-verified': verified }">
                <div class="slider-track-fill" :style="{ width: (buttonLeft + 20) + 'px' }"></div>
                <div class="slider-tip">{{ sliderText }}</div>
                <div
                  class="slider-btn"
                  :style="{ left: buttonLeft + 'px' }"
                  @mousedown="onMouseDown"
                  @touchstart="onMouseDown"
                >
                  <el-icon :size="18"><Right /></el-icon>
                </div>
              </div>
            </div>

            <el-alert v-if="lockMsg" :title="lockMsg" type="error" show-icon :closable="false" class="mb-3" />
            <el-button type="primary" size="large" :loading="loading" :disabled="!!lockMsg" class="w-full !h-11 !text-base" @click="handleLogin">登 录</el-button>
          </el-form>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page { min-height: 100vh; display: flex; align-items: center; justify-content: center; background: #f0f2f5; padding: 24px; }
.login-card { display: flex; width: 100%; max-width: 760px; min-height: 480px; background: #fff; border-radius: 16px; box-shadow: 0 2px 20px rgba(0,0,0,0.06); overflow: hidden; }
.login-brand { width: 280px; min-width: 280px; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); display: flex; align-items: center; justify-content: center; padding: 40px 28px; }
.brand-content { text-align: center; color: #fff; }
.brand-title { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.brand-desc { font-size: 13px; opacity: 0.7; }
.login-form-area { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 36px; }
.form-inner { width: 100%; max-width: 340px; }
.form-title { font-size: 22px; font-weight: 700; color: #1a202c; margin-bottom: 4px; }
.form-subtitle { font-size: 14px; color: #a0aec0; }
.mb-3 { margin-bottom: 12px; }

.captcha-wrap { margin-bottom: 16px; }
.captcha-bg { position: relative; width: 100%; max-width: 320px; border-radius: 8px; overflow: hidden; background: #f5f5f5; user-select: none; }
.bg-img { width: 100%; height: 100%; display: block; }
.piece-img { position: absolute; pointer-events: none; }
.captcha-loading { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; color: #9ca3af; font-size: 13px; }
.captcha-refresh { position: absolute; top: 6px; right: 6px; width: 26px; height: 26px; line-height: 26px; text-align: center; background: rgba(0,0,0,0.4); color: #fff; border-radius: 50%; cursor: pointer; font-size: 16px; }
.captcha-refresh:hover { background: rgba(0,0,0,0.6); }

.slider-track {
  position: relative; margin-top: 12px; height: 40px; width: 100%; max-width: 320px;
  background: #f1f5f9; border-radius: 4px; border: 1px solid #e2e8f0;
  user-select: none;
}
.slider-track.is-error { border-color: #fca5a5; background: #fef2f2; }
.slider-track.is-verified { border-color: #86efac; background: #f0fdf4; }
.slider-track-fill { position: absolute; left: 0; top: 0; bottom: 0; background: #dbeafe; border-radius: 4px; transition: width 0.05s; }
.is-error .slider-track-fill { background: #fee2e2; }
.is-verified .slider-track-fill { background: #dcfce7; }
.slider-tip { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; font-size: 13px; color: #64748b; pointer-events: none; }
.is-error .slider-tip { color: #b91c1c; }
.is-verified .slider-tip { color: #166534; }

.slider-btn {
  position: absolute; top: -1px; left: 0; width: 40px; height: 40px;
  background: #fff; border: 1px solid #cbd5e1; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  cursor: grab; color: #475569; box-shadow: 0 1px 3px rgba(0,0,0,0.06);
  transition: background 0.15s;
}
.slider-btn:hover { background: #f8fafc; }
.slider-btn:active { cursor: grabbing; }
.is-verified .slider-btn { background: #22c55e; color: #fff; border-color: #16a34a; }
.is-error .slider-btn { background: #ef4444; color: #fff; border-color: #dc2626; }

@media (max-width: 640px) { .login-brand { display: none; } .login-card { max-width: 400px; } }
</style>
