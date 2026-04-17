<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { User, Lock, ArrowLeft } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'

const router = useRouter()
const auth = useAuthStore()

// ── profile ──────────────────────────────────────────────────────────────────
const profileLoading = ref(false)
const nicknameEditing = ref(false)
const nicknameValue = ref('')
const nicknameSaving = ref(false)

onMounted(async () => {
  profileLoading.value = true
  try {
    await auth.fetchProfile()
    nicknameValue.value = auth.user?.nickname ?? ''
  } finally {
    profileLoading.value = false
  }
})

function startEditNickname() {
  nicknameValue.value = auth.user?.nickname ?? ''
  nicknameEditing.value = true
}

async function saveNickname() {
  const trimmed = nicknameValue.value.trim()
  if (!trimmed) { ElMessage.warning('昵称不能为空'); return }
  nicknameSaving.value = true
  try {
    const res = await api.put('/auth/profile', { nickname: trimmed })
    auth.user = res.data
    nicknameEditing.value = false
    ElMessage.success('昵称已更新')
  } catch {
    // handled by interceptor
  } finally {
    nicknameSaving.value = false
  }
}

// ── change password ───────────────────────────────────────────────────────────
const pwdForm = reactive({ old_password: '', new_password: '', confirm: '' })
const pwdLoading = ref(false)

function validatePwd(pwd: string): string | null {
  if (pwd.length < 8) return '密码不能少于 8 位'
  if (!/[a-z]/.test(pwd)) return '密码必须包含小写字母'
  if (!/[A-Z]/.test(pwd)) return '密码必须包含大写字母'
  if (!/\d/.test(pwd)) return '密码必须包含数字'
  return null
}

async function submitChangePwd() {
  if (!pwdForm.old_password) { ElMessage.warning('请输入原密码'); return }
  const err = validatePwd(pwdForm.new_password)
  if (err) { ElMessage.warning(err); return }
  if (pwdForm.new_password !== pwdForm.confirm) { ElMessage.warning('两次输入的新密码不一致'); return }
  pwdLoading.value = true
  try {
    await api.post('/auth/change-password', {
      old_password: pwdForm.old_password,
      new_password: pwdForm.new_password,
    })
    ElMessage.success('密码已修改，请重新登录')
    pwdForm.old_password = ''
    pwdForm.new_password = ''
    pwdForm.confirm = ''
    auth.logout()
    setTimeout(() => router.push('/login'), 1200)
  } catch {
    // handled by interceptor
  } finally {
    pwdLoading.value = false
  }
}

function planLabel(plan: string) {
  if (plan === 'free') return '免费版'
  if (plan === 'monthly') return '月度会员'
  if (plan === 'yearly') return '年度会员'
  return plan
}
</script>

<template>
  <div class="profile-wrap">
    <div class="profile-header">
      <button class="back-btn" @click="router.push('/chat')">
        <el-icon><ArrowLeft /></el-icon>
        返回
      </button>
      <h2 class="page-title">个人中心</h2>
    </div>

    <div class="profile-body">
      <!-- Info Card -->
      <div class="card">
        <div class="card-title">
          <el-icon><User /></el-icon>
          基本信息
        </div>
        <div v-if="profileLoading" class="loading-placeholder">加载中…</div>
        <template v-else>
          <div class="avatar-row">
            <div class="avatar-circle">
              <el-icon :size="32"><User /></el-icon>
            </div>
          </div>
          <div class="info-rows">
            <div class="info-row">
              <span class="label">昵称</span>
              <div class="value-area">
                <template v-if="nicknameEditing">
                  <el-input v-model="nicknameValue" size="small" style="width:160px" maxlength="50" />
                  <el-button size="small" type="primary" :loading="nicknameSaving" @click="saveNickname">保存</el-button>
                  <el-button size="small" @click="nicknameEditing = false">取消</el-button>
                </template>
                <template v-else>
                  <span class="value">{{ auth.user?.nickname }}</span>
                  <el-button size="small" text type="primary" @click="startEditNickname">修改</el-button>
                </template>
              </div>
            </div>
            <div class="info-row">
              <span class="label">手机号</span>
              <span class="value muted">{{ auth.user?.phone || '未绑定' }}</span>
            </div>
            <div class="info-row">
              <span class="label">邮箱</span>
              <span class="value muted">{{ auth.user?.email || '未绑定' }}</span>
            </div>
            <div class="info-row">
              <span class="label">套餐</span>
              <span class="value">
                <span class="plan-tag" :class="auth.user?.subscribe_plan">{{ planLabel(auth.user?.subscribe_plan ?? 'free') }}</span>
              </span>
            </div>
            <div v-if="auth.user?.subscribe_plan !== 'free'" class="info-row">
              <span class="label">到期时间</span>
              <span class="value muted">{{ auth.user?.subscribe_expire || '永久' }}</span>
            </div>
            <div v-if="auth.user?.subscribe_plan === 'free'" class="info-row">
              <span class="label">剩余次数</span>
              <span class="value">{{ auth.user?.free_chats_left }} 次</span>
            </div>
            <div class="info-row">
              <span class="label">注册时间</span>
              <span class="value muted">{{ auth.user?.created_at ? new Date(auth.user.created_at).toLocaleDateString() : '—' }}</span>
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
        <div class="pwd-hint">密码要求：至少 8 位，包含大写字母、小写字母和数字</div>
        <div class="form-rows">
          <div class="form-row">
            <span class="label">原密码</span>
            <el-input v-model="pwdForm.old_password" type="password" show-password placeholder="请输入原密码" style="width:260px" />
          </div>
          <div class="form-row">
            <span class="label">新密码</span>
            <el-input v-model="pwdForm.new_password" type="password" show-password placeholder="至少8位，含大小写字母和数字" style="width:260px" />
          </div>
          <div class="form-row">
            <span class="label">确认新密码</span>
            <el-input v-model="pwdForm.confirm" type="password" show-password placeholder="再次输入新密码" style="width:260px" />
          </div>
          <div class="form-row">
            <span class="label" />
            <el-button type="primary" :loading="pwdLoading" @click="submitChangePwd">修改密码</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-wrap {
  min-height: 100vh;
  background: #f8fafc;
  padding: 0;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  background: #fff;
  border-bottom: 1px solid #e2e8f0;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  padding: 6px 10px;
  border-radius: 8px;
  transition: all 0.15s;
}
.back-btn:hover { background: #f1f5f9; color: #334155; }

.page-title {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
  margin: 0;
}

.profile-body {
  max-width: 560px;
  margin: 32px auto;
  padding: 0 16px;
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
.value-area { display: flex; align-items: center; gap: 8px; flex: 1; }
.value { font-size: 14px; color: #1e293b; }
.value.muted { color: #64748b; }

.plan-tag {
  font-size: 12px;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 20px;
  background: #f1f5f9;
  color: #475569;
}
.plan-tag.monthly, .plan-tag.yearly {
  background: #eff6ff;
  color: #2563eb;
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

@media (max-width: 639px) {
  .profile-body { margin: 16px auto; }
  .card { padding: 18px; }
  .form-row { flex-direction: column; align-items: flex-start; gap: 6px; }
  .form-row .label { width: auto; }
  .form-row :deep(.el-input) { width: 100% !important; }
  .info-row { flex-wrap: wrap; }
  .value-area { flex-wrap: wrap; }
}
</style>
