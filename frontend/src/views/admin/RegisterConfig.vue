<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

type SyncResult = {
  affectedUsers: number
  defaultFreeChats: number
  syncedAt: string
}

const form = ref({
  register_enabled: 'true',
  register_methods: 'phone,email',
  invite_code_required: 'false',
  default_free_chats: '3',
  terms_url: '',
  privacy_url: '',
  sms_enabled: 'false',
  sms_provider: '',
  sms_access_key: '',
  sms_access_secret: '',
  sms_sign_name: '',
  sms_sdk_app_id: '',
  sms_template_code: '',
  email_enabled: 'false',
  smtp_host: '',
  smtp_port: '465',
  smtp_user: '',
  smtp_password: '',
  smtp_from: '',
})
const lastSyncResult = ref<SyncResult | null>(null)

const smsConfigEnabled = computed(() => form.value.sms_enabled === 'true')
const defaultFreeChatsValue = computed({
  get: () => Number(form.value.default_free_chats || 0),
  set: (value: number | null | undefined) => {
    form.value.default_free_chats = String(value ?? 0)
  },
})
const registerEnabled = computed(() => form.value.register_enabled === 'true')
const inviteCodeEnabled = computed(() => form.value.invite_code_required === 'true')
const isAliyunSms = computed(() => form.value.sms_provider === 'aliyun')
const isTencentSms = computed(() => form.value.sms_provider === 'tencent')
const enabledChannelCount = computed(() => (form.value.sms_enabled === 'true' ? 1 : 0) + (form.value.email_enabled === 'true' ? 1 : 0))
const smsProviderLabel = computed(() => {
  if (isTencentSms.value) return '腾讯云'
  if (isAliyunSms.value) return '阿里云'
  return '未配置'
})
const showSmsSdkAppId = computed(() => form.value.sms_provider === 'tencent')
const emailConfigEnabled = computed(() => form.value.email_enabled === 'true')

async function fetchConfig() {
  try {
    const res = await api.get('/admin/register/config')
    for (const item of res.data.list) {
      if (item.config_key in form.value) {
        (form.value as Record<string, string>)[item.config_key] = item.config_value
      }
    }
  } catch { /* handled */ }
}

async function save() {
  try {
    const res = await api.put('/admin/register/config', form.value)
    const affected = Number(res.data?.affected_users ?? 0)
    const defaultFreeChats = Number(res.data?.default_free_chats ?? defaultFreeChatsValue.value)
    if (res.data?.default_free_chats != null) {
      lastSyncResult.value = {
        affectedUsers: affected,
        defaultFreeChats,
        syncedAt: new Date().toLocaleString('zh-CN', { hour12: false }),
      }
      ElMessage.success(`保存成功，已同步 ${affected} 个免费用户`)
      return
    }
    ElMessage.success('保存成功')
  } catch { /* handled */ }
}

async function syncExistingFreeUsers() {
  try {
    await ElMessageBox.confirm(
      `将所有免费套餐用户的剩余免费次数统一改为 ${defaultFreeChatsValue.value} 次，是否继续？`,
      '同步现有用户',
      { type: 'warning' },
    )
    const res = await api.post('/admin/register/config/sync-free-chats')
    const affected = res.data?.affected_users ?? 0
    const defaultFreeChats = Number(res.data?.default_free_chats ?? defaultFreeChatsValue.value)
    lastSyncResult.value = {
      affectedUsers: affected,
      defaultFreeChats,
      syncedAt: new Date().toLocaleString('zh-CN', { hour12: false }),
    }
    ElMessage.success(`同步成功，已更新 ${affected} 个免费用户`)
  } catch { /* handled */ }
}

onMounted(fetchConfig)
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-8 pb-6">
    <div class="rounded-[28px] border border-slate-200 bg-white px-5 py-4 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)] sm:px-6">
      <div class="flex flex-col gap-3 xl:flex-row xl:items-center xl:justify-between">
        <div class="min-w-0">
          <h2 class="text-xl font-semibold tracking-tight text-slate-900 sm:text-2xl">注册设置中心</h2>
        </div>
        <div class="grid grid-cols-2 gap-2.5 sm:grid-cols-3 xl:min-w-[390px] xl:max-w-[430px]">
          <div class="rounded-2xl border border-sky-100 bg-sky-50/70 px-3.5 py-3">
            <div class="text-[11px] font-medium text-sky-700">注册状态</div>
            <div class="mt-1 text-sm font-semibold text-slate-900">{{ registerEnabled ? '已开启' : '已关闭' }}</div>
          </div>
          <div class="rounded-2xl border border-emerald-100 bg-emerald-50/70 px-3.5 py-3">
            <div class="text-[11px] font-medium text-emerald-700">验证码通道</div>
            <div class="mt-1 text-sm font-semibold text-slate-900">{{ enabledChannelCount }} 个</div>
          </div>
          <div class="rounded-2xl border border-violet-100 bg-violet-50/70 px-3.5 py-3">
            <div class="text-[11px] font-medium text-violet-700">默认赠送</div>
            <div class="mt-1 text-sm font-semibold text-slate-900">{{ defaultFreeChatsValue }} 次</div>
          </div>
        </div>
      </div>
    </div>
    <!-- 基本注册设置 -->
    <div class="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)]">
      <div class="border-b border-slate-200 px-6 py-4 sm:px-7">
        <div class="flex flex-col gap-2.5 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h3 class="text-lg font-semibold text-slate-900">基本设置</h3>
            <p class="mt-1 text-sm text-slate-500">统一控制注册入口、邀请码和默认赠送次数。</p>
          </div>
          <div class="flex flex-wrap gap-2">
            <span class="rounded-full px-3 py-1 text-xs font-medium" :class="registerEnabled ? 'bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200' : 'bg-slate-100 text-slate-600'">
              {{ registerEnabled ? '注册已开启' : '注册已关闭' }}
            </span>
            <span class="rounded-full px-3 py-1 text-xs font-medium" :class="inviteCodeEnabled ? 'bg-amber-50 text-amber-700 ring-1 ring-amber-200' : 'bg-slate-100 text-slate-600'">
              {{ inviteCodeEnabled ? '邀请码开启' : '邀请码关闭' }}
            </span>
          </div>
        </div>
      </div>
      <div class="p-5 sm:p-6">
        <el-form label-position="top">
          <div class="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-4">
            <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 xl:col-span-1">
              <div class="mb-2.5 text-sm font-medium text-slate-700">开放注册</div>
              <el-switch v-model="form.register_enabled" active-value="true" inactive-value="false" inline-prompt active-text="开" inactive-text="关" />
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 xl:col-span-1">
              <div class="mb-2.5 text-sm font-medium text-slate-700">需要邀请码</div>
              <el-switch v-model="form.invite_code_required" active-value="true" inactive-value="false" inline-prompt active-text="开" inactive-text="关" />
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 xl:col-span-2">
              <div class="mb-2.5 text-sm font-medium text-slate-700">默认免费次数</div>
              <el-input-number v-model="defaultFreeChatsValue" :min="0" :step="1" controls-position="right" class="!w-full" />
            </div>
          </div>
        </el-form>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-5 xl:grid-cols-2">
      <!-- 短信服务配置 -->
      <div :class="['overflow-hidden rounded-[28px] border bg-white shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)] transition', smsConfigEnabled ? 'border-sky-200' : 'border-slate-200']">
        <div :class="['px-5 py-3 sm:px-6 border-b', smsConfigEnabled ? 'border-sky-100 bg-sky-50/80 text-slate-900' : 'border-slate-200 bg-slate-50/80 text-slate-700']">
          <div class="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h3 class="text-base font-semibold">短信服务配置</h3>
              <p class="mt-1 text-xs text-slate-500">用于手机号注册发送验证码，支持阿里云和腾讯云。</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="smsConfigEnabled ? 'bg-sky-100 text-sky-700' : 'bg-white text-slate-500 ring-1 ring-slate-200'">
                {{ smsConfigEnabled ? '短信已启用' : '短信未启用' }}
              </span>
              <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="smsConfigEnabled ? 'bg-white text-sky-700 ring-1 ring-sky-200' : 'bg-white text-slate-500 ring-1 ring-slate-200'">
                {{ smsProviderLabel }}
              </span>
            </div>
          </div>
        </div>

        <div class="p-4 sm:p-5" :class="smsConfigEnabled ? 'bg-white' : 'bg-slate-50/60'">
          <div v-if="smsConfigEnabled && !form.sms_provider" class="mb-2.5 rounded-2xl border border-amber-200 bg-amber-50 px-3.5 py-2 text-xs text-amber-700">
            启用短信前，请先选择供应商并填写对应密钥与模板信息。
          </div>
          <div v-else-if="smsConfigEnabled && isAliyunSms" class="mb-2.5 rounded-2xl border border-sky-100 bg-sky-50 px-3.5 py-2 text-xs text-sky-700">
            阿里云模板变量请使用 `code`。
          </div>
          <div v-else-if="smsConfigEnabled && isTencentSms" class="mb-2.5 rounded-2xl border border-sky-100 bg-sky-50 px-3.5 py-2 text-xs text-sky-700">
            腾讯云模板参数将按顺序传入，当前第一个参数为验证码。
          </div>

          <el-form label-position="top">
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-3.5 py-2.5">
                <div class="mb-2 text-sm font-medium text-slate-700">是否启用</div>
                <el-switch v-model="form.sms_enabled" active-value="true" inactive-value="false" inline-prompt active-text="开" inactive-text="关" />
              </div>
              <el-form-item class="!mb-0" label="服务商">
                <el-select v-model="form.sms_provider" clearable placeholder="未配置" :disabled="!smsConfigEnabled" class="!w-full">
                  <el-option label="阿里云" value="aliyun" />
                  <el-option label="腾讯云" value="tencent" />
                </el-select>
              </el-form-item>
              <el-form-item class="!mb-0" :label="isTencentSms ? 'SecretId' : 'AccessKey ID'">
                <el-input v-model="form.sms_access_key" :disabled="!smsConfigEnabled" :placeholder="isTencentSms ? '腾讯云 SecretId' : '阿里云 AccessKey ID'" />
              </el-form-item>
              <el-form-item class="!mb-0" :label="isTencentSms ? 'SecretKey' : 'AccessKey Secret'">
                <el-input v-model="form.sms_access_secret" :disabled="!smsConfigEnabled" type="password" show-password :placeholder="isTencentSms ? '腾讯云 SecretKey' : '阿里云 AccessKey Secret'" />
              </el-form-item>
              <el-form-item class="!mb-0" label="短信签名">
                <el-input v-model="form.sms_sign_name" :disabled="!smsConfigEnabled" placeholder="例如：AI智能客服" />
              </el-form-item>
              <el-form-item v-if="showSmsSdkAppId" class="!mb-0" label="SDK AppId">
                <el-input v-model="form.sms_sdk_app_id" :disabled="!smsConfigEnabled" placeholder="腾讯云必填" />
              </el-form-item>
              <el-form-item class="md:col-span-2 !mb-0" :label="isTencentSms ? '模板 ID' : '模板编号'">
                <el-input v-model="form.sms_template_code" :disabled="!smsConfigEnabled" :placeholder="isTencentSms ? '腾讯云模板 ID' : '例如：SMS_123456'" />
              </el-form-item>
            </div>
          </el-form>
        </div>
      </div>

      <!-- 邮件服务配置 -->
      <div :class="['overflow-hidden rounded-[28px] border bg-white shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)] transition', emailConfigEnabled ? 'border-indigo-200' : 'border-slate-200']">
        <div :class="['px-5 py-3 sm:px-6 border-b', emailConfigEnabled ? 'border-indigo-100 bg-indigo-50/80 text-slate-900' : 'border-slate-200 bg-slate-50/80 text-slate-700']">
          <div class="flex flex-col gap-2 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h3 class="text-base font-semibold">邮件服务配置</h3>
              <p class="mt-1 text-xs text-slate-500">用于邮箱注册发送验证码，建议填写专用发件账号。</p>
            </div>
            <span class="rounded-full px-2.5 py-1 text-xs font-medium" :class="emailConfigEnabled ? 'bg-indigo-100 text-indigo-700' : 'bg-white text-slate-500 ring-1 ring-slate-200'">
              {{ emailConfigEnabled ? '邮件已启用' : '邮件未启用' }}
            </span>
          </div>
        </div>

        <div class="p-4 sm:p-5" :class="emailConfigEnabled ? 'bg-white' : 'bg-slate-50/60'">
          <div v-if="emailConfigEnabled" class="mb-2.5 rounded-2xl border border-indigo-100 bg-indigo-50 px-3.5 py-2 text-xs text-indigo-700">
            建议发件人地址与 SMTP 账号保持一致，避免被服务商拦截。
          </div>

          <el-form label-position="top">
            <div class="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-3.5 py-2.5">
                <div class="mb-2 text-sm font-medium text-slate-700">是否启用</div>
                <el-switch v-model="form.email_enabled" active-value="true" inactive-value="false" inline-prompt active-text="开" inactive-text="关" />
              </div>
              <el-form-item class="!mb-0" label="SMTP 服务器">
                <el-input v-model="form.smtp_host" :disabled="!emailConfigEnabled" placeholder="例如：smtp.qq.com" />
              </el-form-item>
              <el-form-item class="!mb-0" label="SMTP 端口">
                <el-input v-model="form.smtp_port" :disabled="!emailConfigEnabled" placeholder="465" />
              </el-form-item>
              <el-form-item class="!mb-0" label="账号">
                <el-input v-model="form.smtp_user" :disabled="!emailConfigEnabled" placeholder="发件邮箱账号" />
              </el-form-item>
              <el-form-item class="!mb-0" label="密码 / 授权码">
                <el-input v-model="form.smtp_password" :disabled="!emailConfigEnabled" type="password" show-password placeholder="SMTP 密码或授权码" />
              </el-form-item>
              <el-form-item class="!mb-0" label="发件人地址">
                <el-input v-model="form.smtp_from" :disabled="!emailConfigEnabled" placeholder="noreply@example.com" />
              </el-form-item>
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <div class="flex flex-col gap-4 rounded-[28px] border border-slate-200 bg-white px-6 py-5 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)] sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="text-sm font-medium text-slate-800">保存后会同步新老免费用户</div>
        <div class="mt-1 text-xs text-slate-500">默认免费次数会同时用于后续新注册用户，并覆盖当前所有免费套餐用户的剩余免费次数。建议至少启用一种可用的短信或邮件验证码通道，再开放对应注册方式。</div>
      </div>
      <div class="flex flex-col gap-3 sm:flex-row">
        <el-button size="large" class="sm:min-w-[180px]" @click="syncExistingFreeUsers">重新同步免费用户</el-button>
        <el-button type="primary" size="large" class="sm:min-w-[180px]" @click="save">保存所有配置</el-button>
      </div>
    </div>

    <div v-if="lastSyncResult" class="rounded-[24px] border border-slate-200 bg-white px-6 py-5 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)]">
      <div class="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <div class="text-sm font-semibold text-slate-900">最近一次同步已完成</div>
          <div class="mt-1 text-xs text-slate-500">已将所有免费套餐用户的剩余免费次数统一为 {{ lastSyncResult.defaultFreeChats }} 次。</div>
        </div>
        <div class="grid grid-cols-1 gap-3 text-sm sm:grid-cols-2">
          <div class="rounded-2xl border border-emerald-100 bg-emerald-50/70 px-4 py-3">
            <div class="text-xs text-emerald-600">影响用户数</div>
            <div class="mt-1 text-lg font-semibold">{{ lastSyncResult.affectedUsers }}</div>
          </div>
          <div class="rounded-2xl border border-sky-100 bg-sky-50/70 px-4 py-3">
            <div class="text-xs text-sky-600">同步时间</div>
            <div class="mt-1 text-sm font-semibold">{{ lastSyncResult.syncedAt }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
