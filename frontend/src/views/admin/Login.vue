<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { ElMessage } from 'element-plus'
import { Setting } from '@element-plus/icons-vue'

const router = useRouter()
const adminStore = useAdminStore()
const form = reactive({ username: '', password: '' })
const loading = ref(false)
const lockMsg = ref('')   // 锁定提示信息

async function handleLogin() {
  if (!form.username || !form.password) { ElMessage.warning('请填写用户名和密码'); return }
  loading.value = true
  lockMsg.value = ''
  try {
    await adminStore.login(form.username, form.password)
    router.push('/admin/dashboard')
  } catch (err: any) {
    // code 1030 = 账号锁定，展示在表单内而非全局 toast
    if (err?.code === 1030) {
      lockMsg.value = err.message || '账号已锁定，请稍后重试'
    }
  } finally {
    loading.value = false
  }
}
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
.login-card { display: flex; width: 100%; max-width: 760px; min-height: 420px; background: #fff; border-radius: 16px; box-shadow: 0 2px 20px rgba(0,0,0,0.06); overflow: hidden; }
.login-brand { width: 280px; min-width: 280px; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); display: flex; align-items: center; justify-content: center; padding: 40px 28px; }
.brand-content { text-align: center; color: #fff; }
.brand-title { font-size: 22px; font-weight: 700; margin-bottom: 8px; }
.brand-desc { font-size: 13px; opacity: 0.7; }
.login-form-area { flex: 1; display: flex; align-items: center; justify-content: center; padding: 40px 36px; }
.form-inner { width: 100%; max-width: 320px; }
.form-title { font-size: 22px; font-weight: 700; color: #1a202c; margin-bottom: 4px; }
.form-subtitle { font-size: 14px; color: #a0aec0; }
.mb-3 { margin-bottom: 12px; }
@media (max-width: 640px) { .login-brand { display: none; } .login-card { max-width: 400px; } }
</style>
