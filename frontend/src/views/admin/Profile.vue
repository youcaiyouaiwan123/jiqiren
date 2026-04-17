<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAdminStore } from '@/stores/admin'
import api from '@/utils/api'

const adminStore = useAdminStore()

// ── profile ──────────────────────────────────────────────────────────────────
const profile = ref<{ id: number; username: string; role: string; created_at: string | null } | null>(null)
const profileLoading = ref(false)

onMounted(async () => {
  profileLoading.value = true
  try {
    const res = await api.get('/admin/profile')
    profile.value = res.data
    // keep store in sync
    if (adminStore.admin && profile.value) {
      adminStore.admin = { id: profile.value.id, username: profile.value.username, role: profile.value.role }
    }
  } catch {
    // handled by interceptor
  } finally {
    profileLoading.value = false
  }
})

function roleLabel(role: string) {
  return role === 'super' ? '超级管理员' : '普通管理员'
}

// ── change password ───────────────────────────────────────────────────────────
const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })
const pwdLoading = ref(false)

const PWD_PATTERN = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()\-_=+\[\]{};:'",.<>?/\\|`~]).{12,}$/

function validatePwd(pwd: string): string | null {
  if (pwd.length < 12) return '密码不能少于 12 位'
  if (!/[a-z]/.test(pwd)) return '密码必须包含小写字母'
  if (!/[A-Z]/.test(pwd)) return '密码必须包含大写字母'
  if (!/\d/.test(pwd)) return '密码必须包含数字'
  if (!/[!@#$%^&*()\-_=+\[\]{};:'",./<>?\\|`~]/.test(pwd)) return '密码必须包含特殊字符（如 !@#$%^&*）'
  return null
}

async function submitChangePwd() {
  if (!pwdForm.old_password) { ElMessage.warning('请输入原密码'); return }
  const err = validatePwd(pwdForm.new_password)
  if (err) { ElMessage.warning(err); return }
  if (pwdForm.new_password !== pwdForm.confirm) { ElMessage.warning('两次输入的新密码不一致'); return }
  pwdLoading.value = true
  try {
    await api.post('/admin/change-password', {
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码已修改，请重新登录')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
    adminStore.logout()
    setTimeout(() => { window.location.href = '/admin/login' }, 1200)
  } catch {
    // handled by interceptor
  } finally {
    pwdLoading.value = false
  }
}
</script>

<template>
  <div class="profile-body">
    <!-- Info Card -->
    <div class="card">
      <div class="card-title">
        <el-icon><User /></el-icon>
        账号信息
      </div>
      <div v-if="profileLoading" class="loading-placeholder">加载中…</div>
      <template v-else-if="profile">
        <div class="avatar-row">
          <div class="avatar-circle">
            <el-icon :size="32"><User /></el-icon>
          </div>
        </div>
        <div class="info-rows">
          <div class="info-row">
            <span class="label">用户名</span>
            <span class="value">{{ profile.username }}</span>
          </div>
          <div class="info-row">
            <span class="label">角色</span>
            <span class="role-tag" :class="profile.role">{{ roleLabel(profile.role) }}</span>
          </div>
          <div class="info-row">
            <span class="label">注册时间</span>
            <span class="value muted">{{ profile.created_at ? new Date(profile.created_at).toLocaleDateString() : '—' }}</span>
          </div>
        </div>
      </template>
    </div>

    <!-- Change Password Card -->
    <div class="card">
      <div class="card-title">
        <el-icon><Lock /></el-icon>
        修改密码
      </div>
      <div class="pwd-hint">密码要求：至少 12 位，包含大小写字母、数字和特殊字符（如 !@#$%^&*）</div>
      <div class="form-rows">
        <div class="form-row">
          <span class="label">原密码</span>
          <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" style="width:280px" />
        </div>
        <div class="form-row">
          <span class="label">新密码</span>
          <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少12位，含大小写字母、数字及特殊字符" style="width:280px" />
        </div>
        <div class="form-row">
          <span class="label">确认新密码</span>
          <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" style="width:280px" />
        </div>
        <div class="form-row">
          <span class="label" />
          <el-button type="primary" :loading="pwdLoading" @click="submitChangePwd">修改密码</el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-body {
  max-width: 560px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.card {
  background: #fff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  padding: 24px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 15px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
}

.loading-placeholder { color: #94a3b8; font-size: 14px; }

.avatar-row {
  display: flex;
  justify-content: center;
  margin-bottom: 20px;
}

.avatar-circle {
  width: 72px;
  height: 72px;
  border-radius: 50%;
  background: #eff6ff;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #3b82f6;
  border: 2px solid #bfdbfe;
}

.info-rows { display: flex; flex-direction: column; gap: 14px; }
.info-row { display: flex; align-items: center; gap: 12px; }
.label { width: 90px; font-size: 13px; color: #64748b; flex-shrink: 0; }
.value { font-size: 14px; color: #1e293b; }
.value.muted { color: #64748b; }

.role-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
}
.role-tag.super {
  background: #fef3c7;
  color: #d97706;
}

.pwd-hint {
  font-size: 12px;
  color: #94a3b8;
  margin-bottom: 16px;
  background: #f8fafc;
  border-radius: 8px;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
}

.form-rows { display: flex; flex-direction: column; gap: 14px; }
.form-row { display: flex; align-items: center; gap: 12px; }
.form-row .label { width: 90px; font-size: 13px; color: #64748b; flex-shrink: 0; }
</style>
