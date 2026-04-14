<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'
import api from '@/utils/api'

const router = useRouter()
const auth = useAuthStore()

const phonePattern = /^1\d{10}$/
const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/i

const isLogin = ref(true)
const loading = ref(false)

// 注册配置（从后端获取）
const regConfig = reactive({
  register_enabled: false,
  register_methods: ['phone', 'email'] as string[],
  invite_code_required: false,
  default_free_chats: 3,
  terms_url: '',
  privacy_url: '',
})
const configLoaded = ref(false)

async function fetchRegisterConfig() {
  try {
    const res = await api.get('/auth/register-config')
    Object.assign(regConfig, res.data)
    configLoaded.value = true
  } catch {
    configLoaded.value = true
  }
}

onMounted(fetchRegisterConfig)

const canRegister = computed(() => configLoaded.value && regConfig.register_enabled)
const supportsPhone = computed(() => regConfig.register_methods.includes('phone'))
const supportsEmail = computed(() => regConfig.register_methods.includes('email'))

function normalizeTarget(target: string, type: 'phone' | 'email') {
  const trimmed = target.trim()
  return type === 'email' ? trimmed.toLowerCase() : trimmed.replace(/\s+/g, '')
}

function isValidTarget(target: string, type: 'phone' | 'email') {
  return type === 'email' ? emailPattern.test(target) : phonePattern.test(target)
}

const loginForm = reactive({ account: '', password: '' })
const regForm = reactive({ phone: '', email: '', password: '', confirmPassword: '', nickname: '', invite_code: '', verify_code: '' })
const regMethod = ref<'phone' | 'email'>('phone')

// 验证码倒计时 & 发送状态
const codeSending = ref(false)
const codeCooldown = reactive<{ phone: number; email: number }>({ phone: 0, email: 0 })
const currentCodeCooldown = computed(() => codeCooldown[regMethod.value])
const sendBtnDisabled = computed(() => codeSending.value || currentCodeCooldown.value > 0)
const sendBtnText = computed(() => {
  if (codeSending.value) return '发送中...'
  if (currentCodeCooldown.value > 0) return `${currentCodeCooldown.value}s 后重发`
  return '获取验证码'
})
let cooldownTimer: ReturnType<typeof setInterval> | null = null

function startCodeCooldown(method: 'phone' | 'email') {
  codeCooldown[method] = 60
  if (cooldownTimer) return
  cooldownTimer = setInterval(() => {
    let hasActiveCooldown = false
    ;(['phone', 'email'] as const).forEach((item) => {
      if (codeCooldown[item] > 0) {
        codeCooldown[item] -= 1
        if (codeCooldown[item] > 0) hasActiveCooldown = true
      }
    })
    if (!hasActiveCooldown && cooldownTimer) {
      clearInterval(cooldownTimer)
      cooldownTimer = null
    }
  }, 1000)
}

onUnmounted(() => {
  if (cooldownTimer) {
    clearInterval(cooldownTimer)
    cooldownTimer = null
  }
})

async function handleSendCode() {
  const target = normalizeTarget(regMethod.value === 'phone' ? regForm.phone : regForm.email, regMethod.value)
  if (!target) {
    ElMessage.warning(regMethod.value === 'phone' ? '请先填写手机号' : '请先填写邮箱')
    return
  }
  if (!isValidTarget(target, regMethod.value)) {
    ElMessage.warning(regMethod.value === 'phone' ? '请输入正确的手机号' : '请输入正确的邮箱')
    return
  }
  if (regMethod.value === 'phone') regForm.phone = target
  else regForm.email = target
  codeSending.value = true
  try {
    await auth.sendCode(target, regMethod.value)
    ElMessage.success(regMethod.value === 'phone' ? '验证码已发送到您的手机' : '验证码已发送到您的邮箱，请查收')
    startCodeCooldown(regMethod.value)
  } catch {
    /* handled by interceptor */
  } finally {
    codeSending.value = false
  }
}

function switchToRegister() {
  if (supportsPhone.value) regMethod.value = 'phone'
  else if (supportsEmail.value) regMethod.value = 'email'
  isLogin.value = false
}

async function handleLogin() {
  if (!loginForm.account || !loginForm.password) {
    ElMessage.warning('请填写账号和密码')
    return
  }
  loading.value = true
  try {
    await auth.login(loginForm.account, loginForm.password)
    router.push('/chat')
  } catch {
    /* handled by interceptor */
  } finally {
    loading.value = false
  }
}

async function handleRegister() {
  const account = normalizeTarget(regMethod.value === 'phone' ? regForm.phone : regForm.email, regMethod.value)
  if (!account) {
    ElMessage.warning(regMethod.value === 'phone' ? '请填写手机号' : '请填写邮箱')
    return
  }
  if (!isValidTarget(account, regMethod.value)) {
    ElMessage.warning(regMethod.value === 'phone' ? '请输入正确的手机号' : '请输入正确的邮箱')
    return
  }
  if (regMethod.value === 'phone') regForm.phone = account
  else regForm.email = account
  if (!regForm.password) {
    ElMessage.warning('请填写密码')
    return
  }
  if (regForm.password !== regForm.confirmPassword) {
    ElMessage.warning('两次密码不一致')
    return
  }
  regForm.verify_code = regForm.verify_code.trim()
  if (!regForm.verify_code) {
    ElMessage.warning('请填写验证码')
    return
  }
  if (regConfig.invite_code_required && !regForm.invite_code) {
    ElMessage.warning('请填写邀请码')
    return
  }
  loading.value = true
  try {
    const params: { phone?: string; email?: string; password: string; nickname?: string; invite_code?: string; verify_code?: string } = {
      password: regForm.password,
      nickname: regForm.nickname || undefined,
      verify_code: regForm.verify_code,
    }
    if (regMethod.value === 'phone') params.phone = regForm.phone
    else params.email = regForm.email
    if (regConfig.invite_code_required) params.invite_code = regForm.invite_code
    await auth.register(params)
    ElMessage.success('注册成功，请登录')
    isLogin.value = true
    loginForm.account = account
  } catch {
    /* handled by interceptor */
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Left illustration area -->
      <div class="login-brand">
        <!-- AI Chat illustration -->
        <svg class="brand-illustration" viewBox="0 0 320 400" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Chat bubbles background -->
          <rect x="40" y="60" width="180" height="50" rx="12" fill="rgba(255,255,255,0.12)"/>
          <rect x="100" y="130" width="180" height="50" rx="12" fill="rgba(255,255,255,0.08)"/>
          <rect x="50" y="200" width="160" height="50" rx="12" fill="rgba(255,255,255,0.06)"/>
          <!-- Robot head -->
          <rect x="110" y="90" width="100" height="90" rx="20" fill="rgba(255,255,255,0.2)" stroke="rgba(255,255,255,0.35)" stroke-width="2"/>
          <!-- Eyes -->
          <circle cx="140" cy="125" r="8" fill="white"/>
          <circle cx="180" cy="125" r="8" fill="white"/>
          <circle cx="142" cy="126" r="4" fill="#2d3748"/>
          <circle cx="182" cy="126" r="4" fill="#2d3748"/>
          <!-- Mouth / smile -->
          <path d="M145 148 Q160 158 175 148" stroke="white" stroke-width="2.5" fill="none" stroke-linecap="round"/>
          <!-- Antenna -->
          <line x1="160" y1="90" x2="160" y2="70" stroke="rgba(255,255,255,0.5)" stroke-width="2"/>
          <circle cx="160" cy="66" r="5" fill="#63b3ed"/>
          <!-- Signal waves -->
          <path d="M148 60 Q160 50 172 60" stroke="rgba(255,255,255,0.3)" stroke-width="1.5" fill="none"/>
          <path d="M140 52 Q160 38 180 52" stroke="rgba(255,255,255,0.2)" stroke-width="1.5" fill="none"/>
          <!-- User chat bubble left -->
          <rect x="30" y="220" width="120" height="36" rx="18" fill="rgba(255,255,255,0.18)"/>
          <rect x="38" y="230" width="50" height="4" rx="2" fill="rgba(255,255,255,0.4)"/>
          <rect x="38" y="238" width="30" height="4" rx="2" fill="rgba(255,255,255,0.25)"/>
          <!-- AI response bubble right -->
          <rect x="170" y="270" width="120" height="50" rx="18" fill="rgba(255,255,255,0.15)"/>
          <rect x="182" y="282" width="60" height="4" rx="2" fill="rgba(255,255,255,0.4)"/>
          <rect x="182" y="290" width="90" height="4" rx="2" fill="rgba(255,255,255,0.3)"/>
          <rect x="182" y="298" width="40" height="4" rx="2" fill="rgba(255,255,255,0.2)"/>
          <!-- Feishu table icon -->
          <rect x="50" y="320" width="44" height="36" rx="6" fill="rgba(255,255,255,0.12)" stroke="rgba(255,255,255,0.25)" stroke-width="1.5"/>
          <line x1="50" y1="332" x2="94" y2="332" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
          <line x1="50" y1="344" x2="94" y2="344" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
          <line x1="72" y1="320" x2="72" y2="356" stroke="rgba(255,255,255,0.2)" stroke-width="1"/>
          <!-- Connection dots -->
          <circle cx="110" cy="338" r="3" fill="rgba(255,255,255,0.35)"/>
          <circle cx="125" cy="338" r="3" fill="rgba(255,255,255,0.25)"/>
          <circle cx="140" cy="338" r="3" fill="rgba(255,255,255,0.15)"/>
        </svg>
        <div class="brand-text">
          <h1>AI 智能客服</h1>
          <p>飞书多维表格 × AI 大模型<br/>专业、高效的智能服务平台</p>
        </div>
      </div>
      <!-- Right form -->
      <div class="login-form-area">
        <div class="form-inner">
          <h2 class="form-title">{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
          <p class="form-subtitle">{{ isLogin ? '登录账号以继续使用' : '填写信息完成注册' }}</p>

          <el-form v-if="isLogin" @submit.prevent="handleLogin" class="mt-8">
            <el-form-item>
              <el-input v-model="loginForm.account" placeholder="手机号 / 邮箱" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">登 录</el-button>
          </el-form>

          <el-form v-else @submit.prevent="handleRegister" class="mt-8">
            <div v-if="supportsPhone && supportsEmail" class="reg-method-toggle">
              <el-radio-group v-model="regMethod" size="small">
                <el-radio-button value="phone">手机号注册</el-radio-button>
                <el-radio-button value="email">邮箱注册</el-radio-button>
              </el-radio-group>
            </div>
            <el-form-item v-if="regMethod === 'phone'">
              <el-input v-model="regForm.phone" placeholder="手机号" size="large" prefix-icon="Phone" />
            </el-form-item>
            <el-form-item v-if="regMethod === 'email'">
              <el-input v-model="regForm.email" placeholder="邮箱" size="large" prefix-icon="Message" />
            </el-form-item>
            <el-form-item>
              <div class="code-row">
                <el-input v-model="regForm.verify_code" placeholder="验证码" size="large" prefix-icon="Key" maxlength="6" />
                <el-button size="large" native-type="button" :disabled="sendBtnDisabled" :loading="codeSending" class="send-code-btn" @click="handleSendCode">
                  {{ sendBtnText }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.nickname" placeholder="昵称（选填）" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.confirmPassword" type="password" placeholder="确认密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleRegister" />
            </el-form-item>
            <el-form-item v-if="regConfig.invite_code_required">
              <el-input v-model="regForm.invite_code" placeholder="邀请码" size="large" prefix-icon="Ticket" />
            </el-form-item>
            <div v-if="regConfig.terms_url || regConfig.privacy_url" class="terms-text">
              注册即表示同意
              <a v-if="regConfig.terms_url" :href="regConfig.terms_url" target="_blank">服务条款</a>
              <span v-if="regConfig.terms_url && regConfig.privacy_url"> 和 </span>
              <a v-if="regConfig.privacy_url" :href="regConfig.privacy_url" target="_blank">隐私政策</a>
            </div>
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleRegister">注 册</el-button>
          </el-form>

          <div class="switch-text" v-if="isLogin && canRegister">
            <span>还没有账号？</span>
            <button @click="switchToRegister">立即注册</button>
          </div>
          <div class="switch-text" v-if="!isLogin">
            <span>已有账号？</span>
            <button @click="isLogin = true">返回登录</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #e8ecf1;
  padding: 24px;
}
.login-card {
  display: flex;
  width: 100%;
  max-width: 900px;
  min-height: 540px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 4px 32px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}
.login-brand {
  width: 380px;
  min-width: 380px;
  background: linear-gradient(160deg, #1a365d 0%, #2c5282 50%, #2b6cb0 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 30px;
  position: relative;
  overflow: hidden;
}
.brand-illustration {
  width: 240px;
  height: 300px;
  margin-bottom: 16px;
}
.brand-text {
  text-align: center;
  color: #fff;
}
.brand-text h1 {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: 1px;
}
.brand-text p {
  font-size: 13px;
  opacity: 0.75;
  line-height: 1.8;
}
.login-form-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 44px;
}
.form-inner {
  width: 100%;
  max-width: 340px;
}
.form-title {
  font-size: 26px;
  font-weight: 700;
  color: #1a202c;
  margin-bottom: 6px;
}
.form-subtitle {
  font-size: 14px;
  color: #a0aec0;
  margin-bottom: 0;
}
.login-btn {
  width: 100%;
  height: 44px !important;
  font-size: 15px !important;
  font-weight: 600;
  border-radius: 8px !important;
  background: linear-gradient(135deg, #2b6cb0, #2c5282) !important;
  border: none !important;
}
.login-btn:hover {
  background: linear-gradient(135deg, #3182ce, #2b6cb0) !important;
}
.switch-text {
  margin-top: 24px;
  text-align: center;
  font-size: 13px;
  color: #a0aec0;
}
.switch-text button {
  color: #2b6cb0;
  font-weight: 600;
  margin-left: 4px;
  background: none;
  border: none;
  cursor: pointer;
}
.switch-text button:hover {
  color: #1a365d;
}
.reg-method-toggle {
  text-align: center;
  margin-bottom: 16px;
}
.code-row {
  display: flex;
  gap: 8px;
  width: 100%;
}
.code-row .el-input {
  flex: 1;
}
.send-code-btn {
  min-width: 110px;
  font-size: 13px !important;
  white-space: nowrap;
}
.terms-text {
  font-size: 12px;
  color: #a0aec0;
  text-align: center;
  margin-bottom: 16px;
}
.terms-text a {
  color: #2b6cb0;
  text-decoration: none;
}
.terms-text a:hover {
  text-decoration: underline;
}
@media (max-width: 768px) {
  .login-brand { display: none; }
  .login-card { max-width: 420px; }
  .login-form-area { padding: 32px 24px; }
}
</style>
