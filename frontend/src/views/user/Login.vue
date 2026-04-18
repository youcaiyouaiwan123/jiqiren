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
const regForm = reactive({ phone: '', email: '', password: '', confirmPassword: '', nickname: '', invite_code: '', verify_code: '', website: '' })
// 记录用户第一次与注册表单交互的时间，用于耗时校验
let _regFormStartTime = 0
function _touchRegForm() {
  if (!_regFormStartTime) _regFormStartTime = Date.now()
}
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
  if (resetCooldownTimer) {
    clearInterval(resetCooldownTimer)
    resetCooldownTimer = null
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

async function handleRegister() {  const account = normalizeTarget(regMethod.value === 'phone' ? regForm.phone : regForm.email, regMethod.value)
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
    const ft = _regFormStartTime ? Date.now() - _regFormStartTime : null
    const params: Record<string, unknown> = {
      password: regForm.password,
      nickname: regForm.nickname || undefined,
      verify_code: regForm.verify_code,
      website: regForm.website,   // 蜜罐（正常用户始终为空）
      ft,                          // 表单填写耗时
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

// ── 忘记密码 ──────────────────────────────────────────────────────────────────
const isForgot = ref(false)
const forgotForm = reactive({ account: '', verify_code: '', new_password: '', confirm_password: '' })
const forgotMethod = ref<'phone' | 'email'>('phone')
const resetCodeSending = ref(false)
const resetCodeCooldown = reactive<{ phone: number; email: number }>({ phone: 0, email: 0 })
const currentResetCooldown = computed(() => resetCodeCooldown[forgotMethod.value])
const resetSendBtnDisabled = computed(() => resetCodeSending.value || currentResetCooldown.value > 0)
const resetSendBtnText = computed(() => {
  if (resetCodeSending.value) return '发送中...'
  if (currentResetCooldown.value > 0) return `${currentResetCooldown.value}s 后重发`
  return '获取验证码'
})
let resetCooldownTimer: ReturnType<typeof setInterval> | null = null

function startResetCooldown(method: 'phone' | 'email') {
  resetCodeCooldown[method] = 60
  if (resetCooldownTimer) return
  resetCooldownTimer = setInterval(() => {
    let active = false
    ;(['phone', 'email'] as const).forEach((m) => {
      if (resetCodeCooldown[m] > 0) {
        resetCodeCooldown[m] -= 1
        if (resetCodeCooldown[m] > 0) active = true
      }
    })
    if (!active && resetCooldownTimer) {
      clearInterval(resetCooldownTimer)
      resetCooldownTimer = null
    }
  }, 1000)
}

function switchToForgot() {
  Object.assign(forgotForm, { account: '', verify_code: '', new_password: '', confirm_password: '' })
  forgotMethod.value = supportsPhone.value ? 'phone' : 'email'
  isForgot.value = true
}

async function handleSendResetCode() {
  const account = normalizeTarget(forgotForm.account, forgotMethod.value)
  if (!account) {
    ElMessage.warning(forgotMethod.value === 'phone' ? '请先填写手机号' : '请先填写邮箱')
    return
  }
  if (!isValidTarget(account, forgotMethod.value)) {
    ElMessage.warning(forgotMethod.value === 'phone' ? '请输入正确的手机号' : '请输入正确的邮箱')
    return
  }
  forgotForm.account = account
  resetCodeSending.value = true
  try {
    await api.post('/auth/send-reset-code', { target: account, type: forgotMethod.value })
    ElMessage.success(forgotMethod.value === 'phone' ? '验证码已发送到您的手机' : '验证码已发送到您的邮箱，请查收')
    startResetCooldown(forgotMethod.value)
  } catch {
    /* handled by interceptor */
  } finally {
    resetCodeSending.value = false
  }
}

async function handleResetPassword() {
  const account = normalizeTarget(forgotForm.account, forgotMethod.value)
  if (!account) {
    ElMessage.warning(forgotMethod.value === 'phone' ? '请填写手机号' : '请填写邮箱')
    return
  }
  if (!forgotForm.verify_code.trim()) {
    ElMessage.warning('请填写验证码')
    return
  }
  if (!forgotForm.new_password) {
    ElMessage.warning('请填写新密码')
    return
  }
  if (forgotForm.new_password !== forgotForm.confirm_password) {
    ElMessage.warning('两次密码不一致')
    return
  }
  loading.value = true
  try {
    const params: Record<string, unknown> = {
      verify_code: forgotForm.verify_code.trim(),
      new_password: forgotForm.new_password,
    }
    if (forgotMethod.value === 'phone') params.phone = account
    else params.email = account
    await api.post('/auth/reset-password', params)
    ElMessage.success('密码已重置，请重新登录')
    isForgot.value = false
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
      <!-- Left brand area -->
      <div class="login-brand">
        <div class="brand-logo">
          <div class="logo-wrapper">
            <img class="logo-img" src="/abj_new.png" alt="阿宝姐" />
          </div>
          <span>阿宝姐</span>
        </div>
        <div class="brand-title">AI课程答疑助手</div>
        <div class="brand-subtitle">AI赋能职场</div>
        <div class="brand-slogan">24小时在线的课程私教</div>
      </div>
      <!-- Right form -->
      <div class="login-form-area">
        <div class="form-inner">
          <h2 class="form-title">{{ isForgot ? '找回密码' : isLogin ? '欢迎回来' : '创建账号' }}</h2>
          <p class="form-subtitle">{{ isForgot ? '验证身份后重置密码' : isLogin ? '登录账号以继续使用' : '填写信息完成注册' }}</p>

          <el-form v-if="!isForgot && isLogin" @submit.prevent="handleLogin" class="mt-8">
            <el-form-item>
              <el-input v-model="loginForm.account" placeholder="手机号 / 邮箱" size="large" prefix-icon="User" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="loginForm.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleLogin" />
            </el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleLogin">登 录</el-button>
          </el-form>

          <el-form v-else-if="!isForgot" @submit.prevent="handleRegister" class="mt-8">
            <!-- 蜜罐字段：CSS 隐藏（不用 display:none 以防机器人识别），正常用户不可见也不会填写 -->
            <div class="hp-wrap" aria-hidden="true">
              <input v-model="regForm.website" type="text" name="website" autocomplete="off" tabindex="-1" />
            </div>
            <div v-if="supportsPhone && supportsEmail" class="reg-method-toggle">
              <el-radio-group v-model="regMethod" size="small">
                <el-radio-button value="phone">手机号注册</el-radio-button>
                <el-radio-button value="email">邮箱注册</el-radio-button>
              </el-radio-group>
            </div>
            <el-form-item v-if="regMethod === 'phone'">
              <el-input v-model="regForm.phone" placeholder="手机号" size="large" prefix-icon="Phone" @focus="_touchRegForm" />
            </el-form-item>
            <el-form-item v-if="regMethod === 'email'">
              <el-input v-model="regForm.email" placeholder="邮箱" size="large" prefix-icon="Message" @focus="_touchRegForm" />
            </el-form-item>
            <el-form-item>
              <div class="code-row">
                <el-input v-model="regForm.verify_code" placeholder="验证码" size="large" prefix-icon="Key" maxlength="6" @focus="_touchRegForm" />
                <el-button size="large" native-type="button" :disabled="sendBtnDisabled" :loading="codeSending" class="send-code-btn" @click="handleSendCode">
                  {{ sendBtnText }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.nickname" placeholder="昵称（选填）" size="large" prefix-icon="User" @focus="_touchRegForm" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.password" type="password" placeholder="密码" size="large" prefix-icon="Lock" show-password @focus="_touchRegForm" />
            </el-form-item>
            <el-form-item>
              <el-input v-model="regForm.confirmPassword" type="password" placeholder="确认密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleRegister" @focus="_touchRegForm" />
            </el-form-item>
            <el-form-item v-if="regConfig.invite_code_required">
              <el-input v-model="regForm.invite_code" placeholder="邀请码" size="large" prefix-icon="Ticket" @focus="_touchRegForm" />
            </el-form-item>
            <div v-if="regConfig.terms_url || regConfig.privacy_url" class="terms-text">
              注册即表示同意
              <a v-if="regConfig.terms_url" :href="regConfig.terms_url" target="_blank">服务条款</a>
              <span v-if="regConfig.terms_url && regConfig.privacy_url"> 和 </span>
              <a v-if="regConfig.privacy_url" :href="regConfig.privacy_url" target="_blank">隐私政策</a>
            </div>
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleRegister">注 册</el-button>
          </el-form>

          <!-- 忘记密码表单 -->
          <el-form v-else-if="isForgot" class="mt-8">
            <div v-if="supportsPhone && supportsEmail" class="reg-method-toggle">
              <el-radio-group v-model="forgotMethod" size="small">
                <el-radio-button value="phone">手机号</el-radio-button>
                <el-radio-button value="email">邮箱</el-radio-button>
              </el-radio-group>
            </div>
            <el-form-item v-if="forgotMethod === 'phone'">
              <el-input v-model="forgotForm.account" placeholder="注册手机号" size="large" prefix-icon="Phone" />
            </el-form-item>
            <el-form-item v-else>
              <el-input v-model="forgotForm.account" placeholder="注册邮箱" size="large" prefix-icon="Message" />
            </el-form-item>
            <el-form-item>
              <div class="code-row">
                <el-input v-model="forgotForm.verify_code" placeholder="验证码" size="large" prefix-icon="Key" maxlength="6" />
                <el-button size="large" native-type="button" :disabled="resetSendBtnDisabled" :loading="resetCodeSending" class="send-code-btn" @click="handleSendResetCode">
                  {{ resetSendBtnText }}
                </el-button>
              </div>
            </el-form-item>
            <el-form-item>
              <el-input v-model="forgotForm.new_password" type="password" placeholder="新密码（至少6位）" size="large" prefix-icon="Lock" show-password />
            </el-form-item>
            <el-form-item>
              <el-input v-model="forgotForm.confirm_password" type="password" placeholder="确认新密码" size="large" prefix-icon="Lock" show-password @keyup.enter="handleResetPassword" />
            </el-form-item>
            <el-button type="primary" size="large" :loading="loading" class="login-btn" @click="handleResetPassword">确认重置</el-button>
          </el-form>

          <div class="switch-text" v-if="!isForgot && isLogin && canRegister">
            <span>还没有账号？</span>
            <button @click="switchToRegister">立即注册</button>
          </div>
          <div class="switch-text" v-if="!isForgot && isLogin">
            <button class="forgot-link" @click="switchToForgot">忘记密码？</button>
          </div>
          <div class="switch-text" v-if="!isForgot && !isLogin">
            <span>已有账号？</span>
            <button @click="isLogin = true">返回登录</button>
          </div>
          <div class="switch-text" v-if="isForgot">
            <span>想起密码了？</span>
            <button @click="isForgot = false; isLogin = true">返回登录</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.hp-wrap {
  position: absolute;
  left: -9999px;
  top: -9999px;
  width: 1px;
  height: 1px;
  overflow: hidden;
  opacity: 0;
  pointer-events: none;
}

/* ── 页面背景 ── */
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #FFF3E8;
}

/* ── 卡片容器 ── */
.login-card {
  display: flex;
  width: 1000px;
  max-width: 95vw;
  min-height: 550px;
  background: #fff;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(255, 140, 0, 0.12);
  overflow: hidden;
}

/* ── 左侧品牌区 ── */
.login-brand {
  flex: 1;
  background: linear-gradient(135deg, #FF9933 0%, #FF6600 100%);
  color: #fff;
  padding: 60px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.brand-logo {
  font-size: 22px;
  font-weight: 700;
  margin-bottom: 32px;
  display: flex;
  align-items: center;
  gap: 14px;
}

.logo-wrapper {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: transparent;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.logo-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transform: scale(1.7);
}

.brand-title {
  font-size: 38px;
  font-weight: 800;
  margin-bottom: 10px;
  line-height: 1.2;
}

.brand-subtitle {
  font-size: 20px;
  font-weight: 500;
  margin-bottom: 28px;
  opacity: 0.9;
}

.brand-slogan {
  font-size: 15px;
  opacity: 0.82;
  border-left: 4px solid rgba(255, 255, 255, 0.55);
  padding-left: 14px;
  line-height: 1.6;
}

/* ── 右侧表单区 ── */
.login-form-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fff;
  padding: 60px 48px;
}

.form-inner {
  width: 100%;
  max-width: 360px;
}

.form-title {
  font-size: 26px;
  font-weight: 700;
  color: #333;
  margin-bottom: 6px;
}

.form-subtitle {
  font-size: 14px;
  color: #999;
  margin-bottom: 0;
}

/* ── 输入框 ── */
.form-inner :deep(.el-input__wrapper) {
  background-color: #fff !important;
  box-shadow: 0 0 0 1px #e0e0e0 inset !important;
}

.form-inner :deep(.el-input__wrapper.is-focus) {
  box-shadow: 0 0 0 1.5px #FF6600 inset !important;
}

.form-inner :deep(.el-input__inner) {
  color: #333 !important;
  caret-color: #FF6600;
}

.form-inner :deep(.el-input__inner::placeholder) {
  color: #bbb !important;
}

.form-inner :deep(.el-input__prefix),
.form-inner :deep(.el-input__suffix),
.form-inner :deep(.el-input__icon) {
  color: #ccc !important;
}

/* ── 登录/注册按钮 ── */
.login-btn {
  width: 100%;
  height: 46px !important;
  font-size: 16px !important;
  font-weight: 600;
  border-radius: 8px !important;
  background: #FF6600 !important;
  border: none !important;
  color: #fff !important;
  margin-top: 8px;
}

.login-btn:hover {
  background: #E65C00 !important;
}

/* ── 切换登录/注册 ── */
.switch-text {
  margin-top: 20px;
  text-align: center;
  font-size: 13px;
  color: #999;
}

.switch-text button {
  color: #FF6600;
  font-weight: 600;
  margin-left: 4px;
  background: none;
  border: none;
  cursor: pointer;
  font-size: 13px;
}

.switch-text button:hover {
  color: #E65C00;
}

.forgot-link {
  color: #aaa !important;
  font-weight: 400 !important;
  font-size: 12px !important;
}

.forgot-link:hover {
  color: #FF6600 !important;
}

/* ── 注册方式切换 ── */
.reg-method-toggle {
  text-align: center;
  margin-bottom: 16px;
}

.reg-method-toggle :deep(.el-radio-button__inner) {
  background: #fff !important;
  border-color: #e0e0e0 !important;
  color: #666 !important;
  box-shadow: none !important;
}

.reg-method-toggle :deep(.el-radio-button.is-active .el-radio-button__inner) {
  background: rgba(255, 102, 0, 0.08) !important;
  border-color: #FF6600 !important;
  color: #FF6600 !important;
  box-shadow: none !important;
}

/* ── 验证码行 ── */
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
  background: rgba(255, 102, 0, 0.06) !important;
  border: 1px solid rgba(255, 102, 0, 0.35) !important;
  color: #FF6600 !important;
}

.send-code-btn:hover {
  background: rgba(255, 102, 0, 0.14) !important;
  border-color: #FF6600 !important;
  color: #E65C00 !important;
}

.send-code-btn.is-disabled,
.send-code-btn.is-disabled:hover {
  background: #f5f5f5 !important;
  border-color: #e0e0e0 !important;
  color: #bbb !important;
}

/* ── 条款 ── */
.terms-text {
  font-size: 12px;
  color: #bbb;
  text-align: center;
  margin-bottom: 12px;
}

.terms-text a {
  color: #FF6600;
  text-decoration: none;
}

.terms-text a:hover {
  text-decoration: underline;
}

/* ── 响应式 ── */
@media (max-width: 768px) {
  .login-brand { display: none; }
  .login-card { max-width: 420px; min-height: unset; }
  .login-form-area { padding: 40px 24px; }
}
</style>
