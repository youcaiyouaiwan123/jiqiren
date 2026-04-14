<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import api from '@/utils/api'
import type { PaymentChannelOption, SubscribeCatalogData, SubscribeOrder, SubscribePlan } from '@/types'

const props = defineProps<{
  modelValue: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'refreshed'): void
}>()

const auth = useAuthStore()

const visible = computed({
  get: () => props.modelValue,
  set: (value: boolean) => emit('update:modelValue', value),
})

const catalogLoading = ref(false)
const orderLoading = ref(false)
const checkoutLoading = ref(false)
const redeeming = ref(false)

const catalog = ref<SubscribeCatalogData | null>(null)
const orders = ref<SubscribeOrder[]>([])
const billingCycle = ref<'monthly' | 'yearly'>('monthly')
const selectedPlanId = ref<number | null>(null)
const selectedChannelId = ref<number | null>(null)
const activeOrderId = ref<number | null>(null)
const checkoutUrlMap = ref<Record<number, string>>({})
const redeemCode = ref('')
const previousOrderStatusMap = ref<Record<number, SubscribeOrder['status']>>({})

let orderPollTimer: ReturnType<typeof setInterval> | null = null

function formatMoney(value: number | string | null | undefined) {
  const num = Number(value || 0)
  return Number.isInteger(num) ? String(num) : num.toFixed(2)
}

function formatDateTime(value: string | null | undefined) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
}

function planTypeLabel(type: SubscribePlan['type'] | SubscribeOrder['plan']) {
  if (type === 'yearly') return '年付'
  if (type === 'monthly') return '月付'
  return '订阅'
}

function statusLabel(status: SubscribeOrder['status']) {
  if (status === 'success') return '已开通'
  if (status === 'failed') return '已驳回'
  return '待审核'
}

function statusTagType(status: SubscribeOrder['status']) {
  if (status === 'success') return 'success'
  if (status === 'failed') return 'danger'
  return 'warning'
}

const availableCycles = computed(() => {
  const cycles = new Set(
    (catalog.value?.plans || [])
      .map(item => item.type)
      .filter((item): item is 'monthly' | 'yearly' => item === 'monthly' || item === 'yearly'),
  )
  return [
    { label: '月付', value: 'monthly' as const, visible: cycles.has('monthly') },
    { label: '年付', value: 'yearly' as const, visible: cycles.has('yearly') },
  ].filter(item => item.visible)
})

const visiblePlans = computed(() => {
  const plans = catalog.value?.plans || []
  const filtered = plans.filter(item => item.type === billingCycle.value)
  return filtered.length ? filtered : plans
})

const selectedPlan = computed<SubscribePlan | null>(() => {
  return visiblePlans.value.find(item => item.id === selectedPlanId.value) || visiblePlans.value[0] || null
})

const selectedChannel = computed<PaymentChannelOption | null>(() => {
  return (catalog.value?.channels || []).find(item => item.id === selectedChannelId.value) || null
})

const hasPendingOrders = computed(() => orders.value.some(item => item.status === 'pending'))

const activeOrder = computed<SubscribeOrder | null>(() => {
  return orders.value.find(item => item.id === activeOrderId.value) || orders.value[0] || null
})

const activeCheckoutUrl = computed(() => {
  if (!activeOrder.value) return ''
  return checkoutUrlMap.value[activeOrder.value.id] || ''
})

const planNameMap = computed(() => {
  return new Map((catalog.value?.plans || []).map(item => [item.id, item.name]))
})

const currentPlanLabel = computed(() => {
  const current = catalog.value?.current
  const freeLeft = current?.free_chats_left ?? auth.user?.free_chats_left ?? 0
  if (!current || current.subscribe_plan === 'free') {
    return `免费版 · 剩余 ${freeLeft} 次对话`
  }
  const label = current.subscribe_plan === 'yearly' ? '年付会员' : '月付会员'
  const expire = current.subscribe_expire ? formatDateTime(current.subscribe_expire).slice(0, 10) : '未设置'
  return `${label} · 到期 ${expire}`
})

const currentStateLabel = computed(() => {
  const current = catalog.value?.current
  const freeLeft = current?.free_chats_left ?? auth.user?.free_chats_left ?? 0
  if (current?.subscribe_plan && current.subscribe_plan !== 'free' && current.subscribe_expire) {
    const isActive = new Date(current.subscribe_expire).getTime() > Date.now()
    if (isActive) return '订阅生效中'
  }
  return freeLeft > 0 ? '免费额度剩余' : '需要开通订阅'
})

const selectedPlanFeatures = computed(() => {
  const points = selectedPlan.value?.display_config?.feature_points || []
  if (points.length) return points
  return ['继续使用对话能力', '适合高频咨询场景', '支持已有支付链路接入']
})

function resolveOrderPlanName(order: SubscribeOrder) {
  if (order.plan_name) return order.plan_name
  if (order.plan_id && planNameMap.value.has(order.plan_id)) {
    return planNameMap.value.get(order.plan_id) || '订阅套餐'
  }
  return planTypeLabel(order.plan)
}

function ensureDefaults() {
  const plans = visiblePlans.value
  if (!plans.length) {
    selectedPlanId.value = null
  } else if (!plans.some(item => item.id === selectedPlanId.value)) {
    selectedPlanId.value = plans.find(item => item.display_config?.is_recommended)?.id ?? plans[0].id
  }

  const channels = catalog.value?.channels || []
  if (!channels.length) {
    selectedChannelId.value = null
  } else if (!channels.some(item => item.id === selectedChannelId.value)) {
    selectedChannelId.value = channels[0].id
  }
}

function upsertOrder(order: SubscribeOrder) {
  const next = [order, ...orders.value.filter(item => item.id !== order.id)]
  orders.value = next
  previousOrderStatusMap.value = next.reduce<Record<number, SubscribeOrder['status']>>((acc, item) => {
    acc[item.id] = item.status
    return acc
  }, {})
}

function stopOrderPolling() {
  if (orderPollTimer) {
    clearInterval(orderPollTimer)
    orderPollTimer = null
  }
}

function syncOrderPolling() {
  stopOrderPolling()
  if (props.modelValue && hasPendingOrders.value) {
    orderPollTimer = setInterval(() => {
      void loadOrders(true)
    }, 12000)
  }
}

async function loadCatalog() {
  catalogLoading.value = true
  try {
    const res = await api.get('/subscribe/catalog')
    catalog.value = res.data as SubscribeCatalogData
    const supportedCycles = new Set((catalog.value.plans || []).map(item => item.type))
    if (!supportedCycles.has(billingCycle.value)) {
      billingCycle.value = supportedCycles.has('monthly') ? 'monthly' : 'yearly'
    }
    ensureDefaults()
  } catch {
    catalog.value = null
  } finally {
    catalogLoading.value = false
  }
}

async function loadOrders(silent = false) {
  if (!silent) orderLoading.value = true
  try {
    const res = await api.get('/subscribe/orders')
    const nextOrders = (res.data.list || []) as SubscribeOrder[]
    const approvedOrder = nextOrders.find(item => item.status === 'success' && previousOrderStatusMap.value[item.id] === 'pending')
    orders.value = nextOrders
    if (activeOrderId.value && !nextOrders.some(item => item.id === activeOrderId.value)) {
      activeOrderId.value = nextOrders[0]?.id ?? null
    } else if (!activeOrderId.value && nextOrders.length) {
      activeOrderId.value = nextOrders[0].id
    }
    previousOrderStatusMap.value = nextOrders.reduce<Record<number, SubscribeOrder['status']>>((acc, item) => {
      acc[item.id] = item.status
      return acc
    }, {})
    if (approvedOrder) {
      activeOrderId.value = approvedOrder.id
      await auth.fetchProfile()
      await loadCatalog()
      emit('refreshed')
      ElMessage.success('订阅已开通')
    }
  } catch {
    if (!silent) {
      orders.value = []
    }
  } finally {
    if (!silent) orderLoading.value = false
    syncOrderPolling()
  }
}

async function initializeDialog() {
  await Promise.all([loadCatalog(), loadOrders()])
}

async function checkout() {
  if (!selectedPlan.value) {
    ElMessage.warning('请先选择套餐')
    return
  }
  if (!selectedChannelId.value) {
    ElMessage.warning('请先选择支付方式')
    return
  }

  let paymentWindow: Window | null = null
  const mayHaveCheckoutPage = Boolean((selectedPlan.value.display_config?.cta_url || selectedChannel.value?.checkout_url || '').trim())
  if (mayHaveCheckoutPage) {
    paymentWindow = window.open('', '_blank', 'noopener,noreferrer')
  }

  checkoutLoading.value = true
  try {
    const res = await api.post('/subscribe/checkout', {
      plan_id: selectedPlan.value.id,
      channel_id: selectedChannelId.value,
    })
    const payment = res.data.payment as SubscribeOrder
    const checkoutUrl = String(res.data.checkout_url || '').trim()

    activeOrderId.value = payment.id
    upsertOrder(payment)
    if (checkoutUrl) {
      checkoutUrlMap.value = { ...checkoutUrlMap.value, [payment.id]: checkoutUrl }
      if (paymentWindow) {
        paymentWindow.location.href = checkoutUrl
      } else {
        window.open(checkoutUrl, '_blank', 'noopener,noreferrer')
      }
      ElMessage.success('订单已创建，支付页面已打开')
    } else {
      paymentWindow?.close()
      if (selectedChannel.value?.qrcode_url) {
        ElMessage.success('订单已创建，请扫码支付并等待审核')
      } else {
        ElMessage.success('订单已创建，请按当前渠道提示完成支付')
      }
    }
    await loadOrders(true)
  } catch {
    paymentWindow?.close()
  } finally {
    checkoutLoading.value = false
  }
}

function openCheckoutPage() {
  if (!activeCheckoutUrl.value) {
    ElMessage.warning('当前订单没有可打开的支付链接')
    return
  }
  window.open(activeCheckoutUrl.value, '_blank', 'noopener,noreferrer')
}

async function refreshStatus() {
  await Promise.all([loadCatalog(), loadOrders()])
}

async function redeem() {
  const code = redeemCode.value.trim()
  if (!code) {
    ElMessage.warning('请输入兑换码')
    return
  }
  redeeming.value = true
  try {
    await api.post('/subscribe/redeem', { code })
    redeemCode.value = ''
    await auth.fetchProfile()
    await Promise.all([loadCatalog(), loadOrders(true)])
    emit('refreshed')
    ElMessage.success('兑换成功')
  } catch {
    // handled globally
  } finally {
    redeeming.value = false
  }
}

watch(
  () => props.modelValue,
  (open) => {
    if (open) {
      void initializeDialog()
    } else {
      stopOrderPolling()
    }
  },
  { immediate: true },
)

watch(billingCycle, () => {
  ensureDefaults()
})

onBeforeUnmount(() => {
  stopOrderPolling()
})
</script>

<template>
  <el-dialog v-model="visible" width="1120px" destroy-on-close align-center>
    <template #header>
      <div>
        <div class="text-xs font-semibold uppercase tracking-[0.32em] text-sky-500">Subscription</div>
        <div class="mt-2 text-2xl font-semibold text-slate-900">升级订阅，继续使用智能客服</div>
        <div class="mt-2 text-sm text-slate-500">{{ currentPlanLabel }}</div>
      </div>
    </template>

    <div class="max-h-[76vh] space-y-6 overflow-y-auto pr-1">
      <section class="relative overflow-hidden rounded-[32px] bg-slate-950 px-7 py-7 text-white">
        <div class="absolute inset-x-0 top-0 h-40 bg-gradient-to-r from-sky-500/25 via-cyan-300/12 to-amber-300/12" />
        <div class="absolute right-0 top-0 h-40 w-40 rounded-full bg-white/10 blur-3xl" />
        <div class="relative grid gap-6 lg:grid-cols-[minmax(0,1fr)_240px]">
          <div>
            <div class="inline-flex items-center rounded-full border border-white/15 bg-white/8 px-3 py-1 text-xs text-slate-200">
              {{ currentStateLabel }}
            </div>
            <h2 class="mt-4 text-3xl font-semibold leading-tight">免费次数用完后，用户可以无缝转入订阅支付流程。</h2>
            <p class="mt-4 max-w-3xl text-sm leading-7 text-slate-300">
              套餐、支付渠道、按钮文案、收款码和外部跳转链接都来自管理端配置。用户端下单后，管理端可直接审核订单并开通订阅。
            </p>
            <div class="mt-5 flex flex-wrap gap-3 text-sm text-slate-200">
              <span class="rounded-full border border-white/15 px-3 py-1">先下单，再支付</span>
              <span class="rounded-full border border-white/15 px-3 py-1">支持二维码或外部支付页</span>
              <span class="rounded-full border border-white/15 px-3 py-1">管理员审核后即时生效</span>
            </div>
          </div>

          <div class="rounded-[28px] border border-white/12 bg-white/8 p-5">
            <div class="text-sm text-slate-300">当前状态</div>
            <div class="mt-3 text-3xl font-semibold">
              {{ catalog?.current?.subscribe_plan === 'free' ? (catalog?.current?.free_chats_left ?? auth.user?.free_chats_left ?? 0) : 'Active' }}
            </div>
            <div class="mt-2 text-sm text-slate-300">
              {{ catalog?.current?.subscribe_plan === 'free' ? '剩余免费对话次数' : '订阅权益已开启' }}
            </div>
            <div class="mt-6 text-xs uppercase tracking-[0.28em] text-slate-400">Billing</div>
            <div v-if="availableCycles.length > 1" class="mt-3 inline-flex rounded-full bg-white/10 p-1">
              <button
                v-for="cycle in availableCycles"
                :key="cycle.value"
                type="button"
                class="rounded-full px-4 py-2 text-sm transition"
                :class="billingCycle === cycle.value ? 'bg-white text-slate-950' : 'text-slate-300'"
                @click="billingCycle = cycle.value"
              >
                {{ cycle.label }}
              </button>
            </div>
            <div v-else class="mt-3 text-sm text-slate-300">
              {{ availableCycles[0]?.label || '按已配置套餐展示' }}
            </div>
          </div>
        </div>
      </section>

      <section class="grid gap-5 lg:grid-cols-[minmax(0,1.2fr)_360px]">
        <div class="space-y-5">
          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <div class="flex items-center justify-between gap-4">
              <div>
                <div class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Plans</div>
                <h3 class="mt-2 text-xl font-semibold text-slate-900">选择一个订阅套餐</h3>
              </div>
              <el-button text type="primary" @click="refreshStatus">刷新状态</el-button>
            </div>

            <div v-if="catalogLoading" class="mt-5 rounded-[24px] border border-slate-200 bg-slate-50 px-6 py-14 text-center text-sm text-slate-500">
              正在加载订阅配置...
            </div>

            <div v-else-if="!visiblePlans.length" class="mt-5 rounded-[24px] border border-dashed border-slate-300 bg-slate-50 px-6 py-14 text-center text-sm text-slate-500">
              管理端还没有上架可订阅套餐。
            </div>

            <div v-else class="mt-5 grid gap-4 xl:grid-cols-2">
              <button
                v-for="plan in visiblePlans"
                :key="plan.id"
                type="button"
                class="relative overflow-hidden rounded-[28px] border p-6 text-left transition"
                :class="selectedPlanId === plan.id ? 'border-sky-400 bg-sky-50 shadow-[0_24px_70px_-42px_rgba(2,132,199,0.5)]' : 'border-slate-200 bg-white hover:border-slate-300'"
                @click="selectedPlanId = plan.id"
              >
                <div
                  v-if="plan.display_config?.is_recommended || plan.display_config?.badge_text"
                  class="absolute right-4 top-4 rounded-full px-3 py-1 text-xs font-semibold"
                  :class="plan.display_config?.is_recommended ? 'bg-slate-950 text-white' : 'bg-amber-100 text-amber-900'"
                >
                  {{ plan.display_config?.badge_text || '推荐' }}
                </div>

                <div class="text-xs font-semibold uppercase tracking-[0.24em]" :class="selectedPlanId === plan.id ? 'text-sky-600' : 'text-slate-400'">
                  {{ planTypeLabel(plan.type) }}
                </div>
                <h4 class="mt-3 text-2xl font-semibold text-slate-900">{{ plan.name }}</h4>
                <p class="mt-3 text-sm leading-6 text-slate-600">
                  {{ plan.display_config?.summary || plan.description || '适合需要持续使用智能客服与高频咨询的用户。' }}
                </p>

                <div class="mt-5 flex items-end gap-2">
                  <span class="text-4xl font-semibold text-slate-900">¥{{ formatMoney(plan.price) }}</span>
                  <span class="pb-1 text-sm text-slate-500">/ {{ planTypeLabel(plan.type) }}</span>
                </div>
                <div v-if="plan.display_config?.original_price" class="mt-2 text-sm text-slate-400 line-through">
                  原价 ¥{{ plan.display_config?.original_price }}
                </div>

                <div class="mt-5 space-y-3">
                  <div
                    v-for="point in plan.display_config?.feature_points?.length ? plan.display_config?.feature_points : ['继续使用对话能力', '适合高频咨询场景']"
                    :key="point"
                    class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-700"
                  >
                    {{ point }}
                  </div>
                </div>
              </button>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <div class="flex items-center justify-between gap-4">
              <div>
                <div class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Orders</div>
                <h3 class="mt-2 text-xl font-semibold text-slate-900">订阅订单进度</h3>
              </div>
              <div class="text-sm text-slate-500">支付完成后请等待管理员审核</div>
            </div>

            <div v-if="orderLoading" class="mt-5 rounded-[24px] border border-slate-200 bg-slate-50 px-6 py-12 text-center text-sm text-slate-500">
              正在加载订单...
            </div>

            <div v-else-if="!orders.length" class="mt-5 rounded-[24px] border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center text-sm text-slate-500">
              还没有创建过订阅订单。
            </div>

            <div v-else class="mt-5 space-y-3">
              <button
                v-for="order in orders"
                :key="order.id"
                type="button"
                class="flex w-full items-start justify-between gap-4 rounded-[22px] border px-5 py-4 text-left transition"
                :class="activeOrder?.id === order.id ? 'border-sky-300 bg-sky-50' : 'border-slate-200 bg-white hover:border-slate-300'"
                @click="activeOrderId = order.id"
              >
                <div class="min-w-0">
                  <div class="flex flex-wrap items-center gap-2">
                    <div class="font-medium text-slate-900">{{ resolveOrderPlanName(order) }}</div>
                    <el-tag :type="statusTagType(order.status)" size="small">{{ statusLabel(order.status) }}</el-tag>
                  </div>
                  <div class="mt-2 text-sm text-slate-500">订单号 {{ order.order_no || order.id }}</div>
                  <div class="mt-1 text-xs text-slate-400">
                    {{ planTypeLabel(order.plan) }} · {{ order.channel || 'channel' }} · {{ formatDateTime(order.created_at) }}
                  </div>
                  <div v-if="order.remark" class="mt-2 text-xs text-slate-500">{{ order.remark }}</div>
                </div>
                <div class="shrink-0 text-right">
                  <div class="text-lg font-semibold text-slate-900">¥{{ formatMoney(order.amount) }}</div>
                  <div class="mt-1 text-xs text-slate-400">{{ order.paid_at ? formatDateTime(order.paid_at) : '待支付完成' }}</div>
                </div>
              </button>
            </div>
          </section>
        </div>

        <aside class="space-y-5">
          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <div class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Checkout</div>
            <h3 class="mt-2 text-2xl font-semibold text-slate-900">{{ selectedPlan?.name || '选择套餐后继续' }}</h3>
            <div v-if="selectedPlan" class="mt-4 flex items-end gap-2">
              <span class="text-4xl font-semibold text-slate-900">¥{{ formatMoney(selectedPlan.price) }}</span>
              <span class="pb-1 text-sm text-slate-500">/ {{ planTypeLabel(selectedPlan.type) }}</span>
            </div>
            <p class="mt-4 text-sm leading-6 text-slate-600">
              {{ selectedPlan?.display_config?.summary || selectedPlan?.description || '选择支付方式后即可创建订单。' }}
            </p>

            <div class="mt-6 space-y-3">
              <div class="text-sm font-semibold text-slate-900">支付方式</div>
              <button
                v-for="channel in catalog?.channels || []"
                :key="channel.id"
                type="button"
                class="w-full rounded-[22px] border px-4 py-4 text-left transition"
                :class="selectedChannelId === channel.id ? 'border-sky-300 bg-sky-50' : 'border-slate-200 bg-slate-50 hover:border-slate-300'"
                @click="selectedChannelId = channel.id"
              >
                <div class="flex items-start justify-between gap-3">
                  <div>
                    <div class="font-medium text-slate-900">{{ channel.display_name }}</div>
                    <div class="mt-1 text-xs leading-5 text-slate-500">{{ channel.description || '使用当前渠道完成支付。' }}</div>
                  </div>
                  <el-tag :type="selectedChannelId === channel.id ? 'success' : 'info'" size="small">
                    {{ channel.channel }}
                  </el-tag>
                </div>
              </button>

              <div v-if="catalog && !catalog.channels.length" class="rounded-[22px] border border-dashed border-slate-300 bg-slate-50 px-4 py-8 text-center text-sm text-slate-500">
                管理端还没有启用支付渠道。
              </div>
            </div>

            <div class="mt-6 rounded-[24px] border border-slate-200 bg-slate-50 p-4">
              <div class="text-sm font-semibold text-slate-900">支付说明</div>
              <div class="mt-2 text-xs leading-6 text-slate-500">
                {{ selectedChannel?.pay_tips || '创建订单后可跳转支付页，或按二维码完成支付。支付完成后由管理员审核开通订阅。' }}
              </div>
              <img
                v-if="selectedChannel?.qrcode_url"
                :src="selectedChannel.qrcode_url"
                alt="payment-qrcode"
                class="mx-auto mt-4 h-44 w-44 rounded-2xl border border-slate-200 object-cover"
              />
            </div>

            <div v-if="selectedPlanFeatures.length" class="mt-6 space-y-2">
              <div class="text-sm font-semibold text-slate-900">本次开通包含</div>
              <div
                v-for="point in selectedPlanFeatures"
                :key="point"
                class="rounded-2xl border border-slate-200 px-4 py-3 text-sm text-slate-700"
              >
                {{ point }}
              </div>
            </div>

            <el-button
              type="primary"
              class="mt-6 !h-12 w-full"
              :loading="checkoutLoading"
              :disabled="!selectedPlan || !selectedChannel"
              @click="checkout"
            >
              {{ selectedPlan?.display_config?.button_text || selectedChannel?.button_label || '创建订单并去支付' }}
            </el-button>

            <el-button v-if="activeCheckoutUrl" plain class="mt-3 !h-11 w-full" @click="openCheckoutPage">
              再次打开支付页
            </el-button>

            <div v-if="activeOrder" class="mt-5 rounded-[24px] bg-slate-950 px-5 py-4 text-white">
              <div class="flex items-center justify-between gap-3">
                <div class="text-sm font-medium">当前订单</div>
                <el-tag :type="statusTagType(activeOrder.status)" size="small">{{ statusLabel(activeOrder.status) }}</el-tag>
              </div>
              <div class="mt-3 text-lg font-semibold">{{ activeOrder.order_no || activeOrder.id }}</div>
              <div class="mt-2 text-sm text-slate-300">
                {{ resolveOrderPlanName(activeOrder) }} · ¥{{ formatMoney(activeOrder.amount) }}
              </div>
              <div class="mt-2 text-xs text-slate-400">{{ formatDateTime(activeOrder.created_at) }}</div>
            </div>
          </section>

          <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <div class="text-xs font-semibold uppercase tracking-[0.28em] text-slate-400">Redeem</div>
            <h3 class="mt-2 text-xl font-semibold text-slate-900">兑换码</h3>
            <p class="mt-2 text-sm leading-6 text-slate-500">如果你已有兑换码，也可以直接在这里兑换，不走支付流程。</p>
            <div class="mt-4 space-y-3">
              <el-input v-model="redeemCode" placeholder="输入兑换码" @keyup.enter="redeem" />
              <el-button type="primary" plain class="w-full" :loading="redeeming" @click="redeem">立即兑换</el-button>
            </div>
          </section>
        </aside>
      </section>
    </div>
  </el-dialog>
</template>
