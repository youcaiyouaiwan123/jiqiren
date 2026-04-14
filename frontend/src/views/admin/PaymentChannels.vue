<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'

interface PaymentExtraConfig {
  display_name?: string
  description?: string
  button_label?: string
  qrcode_url?: string
  pay_tips?: string
  checkout_url?: string
}

interface PaymentConfigRow {
  id: number
  channel: 'wechat' | 'alipay' | string
  merchant_id: string | null
  notify_url: string | null
  is_active: number
  extra_config?: PaymentExtraConfig | null
}

interface PaymentFormState {
  id: number | null
  channel: 'wechat' | 'alipay'
  merchant_id: string
  api_key: string
  api_secret: string
  notify_url: string
  is_active: boolean
  display_name: string
  description: string
  button_label: string
  qrcode_url: string
  pay_tips: string
  checkout_url: string
}

const loading = ref(false)
const saving = ref(false)
const list = ref<PaymentConfigRow[]>([])
const dialogVisible = ref(false)

function defaultForm(): PaymentFormState {
  return {
    id: null,
    channel: 'wechat',
    merchant_id: '',
    api_key: '',
    api_secret: '',
    notify_url: '',
    is_active: true,
    display_name: '微信支付',
    description: '扫码完成支付后按你现有计费链路自动开通。',
    button_label: '前往支付',
    qrcode_url: '',
    pay_tips: '支付完成后返回页面查看状态。',
    checkout_url: '',
  }
}

const form = ref<PaymentFormState>(defaultForm())

function openCreate() {
  form.value = defaultForm()
  dialogVisible.value = true
}

function openEdit(row: PaymentConfigRow) {
  const extra = row.extra_config || {}
  form.value = {
    id: row.id,
    channel: row.channel === 'alipay' ? 'alipay' : 'wechat',
    merchant_id: row.merchant_id || '',
    api_key: '',
    api_secret: '',
    notify_url: row.notify_url || '',
    is_active: !!row.is_active,
    display_name: extra.display_name || (row.channel === 'alipay' ? '支付宝' : '微信支付'),
    description: extra.description || '',
    button_label: extra.button_label || '前往支付',
    qrcode_url: extra.qrcode_url || '',
    pay_tips: extra.pay_tips || '',
    checkout_url: extra.checkout_url || '',
  }
  dialogVisible.value = true
}

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/payment/config', { params: { page: 1, page_size: 50 } })
    list.value = (res.data.list || []) as PaymentConfigRow[]
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

async function saveChannel() {
  saving.value = true
  const payload = {
    channel: form.value.channel,
    merchant_id: form.value.merchant_id.trim(),
    api_key: form.value.api_key.trim() || undefined,
    api_secret: form.value.api_secret.trim() || undefined,
    notify_url: form.value.notify_url.trim(),
    is_active: form.value.is_active ? 1 : 0,
    extra_config: {
      display_name: form.value.display_name.trim(),
      description: form.value.description.trim(),
      button_label: form.value.button_label.trim() || '前往支付',
      qrcode_url: form.value.qrcode_url.trim(),
      pay_tips: form.value.pay_tips.trim(),
      checkout_url: form.value.checkout_url.trim(),
    },
  }
  try {
    if (form.value.id) {
      await api.put(`/admin/payment/config/${form.value.id}`, payload)
      ElMessage.success('支付渠道已更新')
    } else {
      await api.post('/admin/payment/config', payload)
      ElMessage.success('支付渠道已创建')
    }
    dialogVisible.value = false
    await fetchList()
  } catch {
    // handled globally
  } finally {
    saving.value = false
  }
}

async function removeChannel(id: number) {
  try {
    await ElMessageBox.confirm('确认删除这个支付渠道吗？', '删除支付渠道', { type: 'warning' })
    await api.delete(`/admin/payment/config/${id}`)
    ElMessage.success('支付渠道已删除')
    await fetchList()
  } catch {
    // ignore cancel
  }
}

const activeCount = computed(() => list.value.filter(item => item.is_active).length)
const previewTitle = computed(() => form.value.display_name || (form.value.channel === 'alipay' ? '支付宝' : '微信支付'))
const channelLabel = computed(() => (form.value.channel === 'alipay' ? '支付宝' : '微信'))

onMounted(fetchList)
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-3">
      <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">支付渠道</div>
        <div class="mt-3 text-3xl font-semibold text-slate-900">{{ list.length }}</div>
      </div>
      <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">已启用</div>
        <div class="mt-3 text-3xl font-semibold text-emerald-600">{{ activeCount }}</div>
      </div>
      <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">用户端展示</div>
        <div class="mt-3 text-sm leading-6 text-slate-600">支持配置展示名、按钮文案、收款码和外部支付链接。</div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">支付渠道配置</h2>
          <p class="mt-1 text-sm text-slate-500">保留现有商户配置，同时补充用户端可见的渠道说明和跳转配置。</p>
        </div>
        <el-button type="primary" @click="openCreate">新增渠道</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe border class="mt-6" style="width: 100%">
        <el-table-column prop="channel" label="渠道" width="100" />
        <el-table-column label="展示信息" min-width="200">
          <template #default="{ row }">
            <div class="font-medium text-slate-900">{{ row.extra_config?.display_name || row.channel }}</div>
            <div class="text-xs text-slate-500">{{ row.extra_config?.description || '未设置展示说明' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="merchant_id" label="商户号" min-width="180" />
        <el-table-column prop="notify_url" label="回调地址" min-width="220" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '停用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="removeChannel(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑支付渠道' : '新增支付渠道'" width="1040px" destroy-on-close>
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_360px]">
        <div class="space-y-6">
          <section class="rounded-3xl border border-slate-200 bg-slate-50/70 p-5">
            <div class="mb-4 text-sm font-semibold text-slate-700">商户配置</div>
            <el-form label-position="top" class="grid gap-4 md:grid-cols-2">
              <el-form-item label="支付渠道" required>
                <el-select v-model="form.channel">
                  <el-option label="微信支付" value="wechat" />
                  <el-option label="支付宝" value="alipay" />
                </el-select>
              </el-form-item>
              <el-form-item label="商户号">
                <el-input v-model="form.merchant_id" placeholder="商户号 / 渠道账号" />
              </el-form-item>
              <el-form-item label="API Key">
                <el-input v-model="form.api_key" type="password" show-password placeholder="留空则不覆盖已有值" />
              </el-form-item>
              <el-form-item label="API Secret">
                <el-input v-model="form.api_secret" type="password" show-password placeholder="留空则不覆盖已有值" />
              </el-form-item>
              <el-form-item label="回调地址" class="md:col-span-2">
                <el-input v-model="form.notify_url" placeholder="支付平台回调地址" />
              </el-form-item>
              <el-form-item label="启用状态">
                <el-switch v-model="form.is_active" />
              </el-form-item>
            </el-form>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-5">
            <div class="mb-4 text-sm font-semibold text-slate-700">用户端展示配置</div>
            <el-form label-position="top" class="grid gap-4 md:grid-cols-2">
              <el-form-item label="展示名称">
                <el-input v-model="form.display_name" placeholder="例如 微信支付 / 支付宝" />
              </el-form-item>
              <el-form-item label="按钮文案">
                <el-input v-model="form.button_label" placeholder="例如 前往支付" />
              </el-form-item>
              <el-form-item label="展示说明" class="md:col-span-2">
                <el-input v-model="form.description" placeholder="显示在订阅弹窗里的渠道说明" />
              </el-form-item>
              <el-form-item label="外部支付链接" class="md:col-span-2">
                <el-input v-model="form.checkout_url" placeholder="已有计费页面链接，可选" />
              </el-form-item>
              <el-form-item label="收款码图片链接" class="md:col-span-2">
                <el-input v-model="form.qrcode_url" placeholder="未配置外部链接时可展示收款码" />
              </el-form-item>
              <el-form-item label="支付提示" class="md:col-span-2">
                <el-input v-model="form.pay_tips" type="textarea" :rows="4" placeholder="例如：支付完成后返回当前页刷新状态" />
              </el-form-item>
            </el-form>
          </section>
        </div>

        <aside class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <div class="text-xs font-semibold uppercase tracking-[0.24em] text-slate-400">{{ channelLabel }}</div>
          <h3 class="mt-3 text-2xl font-semibold text-slate-900">{{ previewTitle }}</h3>
          <p class="mt-4 text-sm leading-6 text-slate-500">{{ form.description || '在订阅弹窗中引导用户完成支付。' }}</p>

          <div class="mt-6 rounded-3xl border border-dashed border-slate-300 bg-slate-50 p-4 text-center">
            <img v-if="form.qrcode_url" :src="form.qrcode_url" alt="支付二维码" class="mx-auto h-48 w-48 rounded-2xl object-cover" />
            <div v-else class="py-12 text-sm text-slate-400">未配置收款码预览</div>
          </div>

          <div class="mt-5 rounded-2xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white">
            {{ form.button_label || '前往支付' }}
          </div>
          <div class="mt-4 text-xs leading-6 text-slate-500">{{ form.pay_tips || '支付完成后，用户端会按当前计费链路继续处理订阅生效。' }}</div>
        </aside>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveChannel">保存渠道</el-button>
      </template>
    </el-dialog>
  </div>
</template>
