<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/utils/api'
import type { PlanDisplayConfig, SubscribePlan } from '@/types'

interface PlanFormState {
  id: number | null
  name: string
  type: 'monthly' | 'yearly' | 'custom'
  price: number
  duration_days: number
  chat_limit: number
  description: string
  is_active: boolean
  sort_order: number
  badge_text: string
  summary: string
  original_price: string
  button_text: string
  cta_url: string
  is_recommended: boolean
  feature_points_text: string
}

const loading = ref(false)
const saving = ref(false)
const list = ref<SubscribePlan[]>([])
const dialogVisible = ref(false)

function defaultForm(): PlanFormState {
  return {
    id: null,
    name: '',
    type: 'monthly',
    price: 29,
    duration_days: 30,
    chat_limit: -1,
    description: '',
    is_active: true,
    sort_order: 0,
    badge_text: '',
    summary: '',
    original_price: '',
    button_text: '立即订阅',
    cta_url: '',
    is_recommended: false,
    feature_points_text: '优先响应\n持续可用\n适合高频咨询',
  }
}

const form = ref<PlanFormState>(defaultForm())

function toFeaturePoints(text: string) {
  return text
    .split(/\r?\n/)
    .map(item => item.trim())
    .filter(Boolean)
}

function openCreate() {
  form.value = defaultForm()
  dialogVisible.value = true
}

function openEdit(row: SubscribePlan) {
  const display = row.display_config || {}
  form.value = {
    id: row.id,
    name: row.name,
    type: row.type,
    price: Number(row.price || 0),
    duration_days: Number(row.duration_days || 0),
    chat_limit: Number(row.chat_limit ?? -1),
    description: row.description || '',
    is_active: !!row.is_active,
    sort_order: Number(row.sort_order || 0),
    badge_text: String(display.badge_text || ''),
    summary: String(display.summary || ''),
    original_price: display.original_price == null ? '' : String(display.original_price),
    button_text: String(display.button_text || '立即订阅'),
    cta_url: String(display.cta_url || ''),
    is_recommended: !!display.is_recommended,
    feature_points_text: Array.isArray(display.feature_points) ? display.feature_points.join('\n') : '',
  }
  dialogVisible.value = true
}

function buildDisplayConfig(): PlanDisplayConfig {
  const display: PlanDisplayConfig = {
    badge_text: form.value.badge_text.trim(),
    summary: form.value.summary.trim(),
    button_text: form.value.button_text.trim() || '立即订阅',
    cta_url: form.value.cta_url.trim(),
    is_recommended: form.value.is_recommended,
    feature_points: toFeaturePoints(form.value.feature_points_text),
  }
  const originalPrice = form.value.original_price.trim()
  if (originalPrice) {
    display.original_price = originalPrice
  }
  return display
}

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/plans', { params: { page: 1, page_size: 200 } })
    list.value = (res.data.list || []) as SubscribePlan[]
  } catch {
    list.value = []
  } finally {
    loading.value = false
  }
}

async function savePlan() {
  saving.value = true
  const payload = {
    name: form.value.name.trim(),
    type: form.value.type,
    price: form.value.price,
    duration_days: form.value.duration_days,
    chat_limit: form.value.chat_limit,
    description: form.value.description.trim(),
    is_active: form.value.is_active ? 1 : 0,
    sort_order: form.value.sort_order,
    display_config: buildDisplayConfig(),
  }
  try {
    if (form.value.id) {
      await api.put(`/admin/plans/${form.value.id}`, payload)
      ElMessage.success('套餐已更新')
    } else {
      await api.post('/admin/plans', payload)
      ElMessage.success('套餐已创建')
    }
    dialogVisible.value = false
    await fetchList()
  } catch {
    // handled globally
  } finally {
    saving.value = false
  }
}

async function removePlan(id: number) {
  try {
    await ElMessageBox.confirm('确认删除这个套餐吗？', '删除套餐', { type: 'warning' })
    await api.delete(`/admin/plans/${id}`)
    ElMessage.success('套餐已删除')
    await fetchList()
  } catch {
    // ignore cancel
  }
}

const recommendedCount = computed(() => list.value.filter(item => item.display_config?.is_recommended).length)
const activeCount = computed(() => list.value.filter(item => item.is_active).length)

const previewCard = computed(() => ({
  name: form.value.name || 'Pro',
  typeLabel: form.value.type === 'yearly' ? '年付' : form.value.type === 'custom' ? '自定义' : '月付',
  price: form.value.price || 0,
  summary: form.value.summary || form.value.description || '适合高频使用与长期会话的订阅方案。',
  badgeText: form.value.badge_text || '',
  buttonText: form.value.button_text || '立即订阅',
  originalPrice: form.value.original_price.trim(),
  points: toFeaturePoints(form.value.feature_points_text),
  recommended: form.value.is_recommended,
}))

onMounted(fetchList)
</script>

<template>
  <div class="space-y-6">
    <section class="grid gap-4 md:grid-cols-3">
      <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">套餐总数</div>
        <div class="mt-3 text-3xl font-semibold text-slate-900">{{ list.length }}</div>
      </div>
      <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">已上架</div>
        <div class="mt-3 text-3xl font-semibold text-emerald-600">{{ activeCount }}</div>
      </div>
      <div class="rounded-3xl border border-slate-200 bg-white p-5 shadow-sm">
        <div class="text-sm text-slate-500">推荐套餐</div>
        <div class="mt-3 text-3xl font-semibold text-sky-600">{{ recommendedCount }}</div>
      </div>
    </section>

    <section class="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
      <div class="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 class="text-lg font-semibold text-slate-900">订阅套餐配置</h2>
          <p class="mt-1 text-sm text-slate-500">配置用户端弹窗里的价格卡片、卖点文案、推荐标签和跳转链接。</p>
        </div>
        <el-button type="primary" @click="openCreate">新增套餐</el-button>
      </div>

      <el-table :data="list" v-loading="loading" stripe border class="mt-6" style="width: 100%">
        <el-table-column prop="name" label="套餐" min-width="160">
          <template #default="{ row }">
            <div class="font-medium text-slate-900">{{ row.name }}</div>
            <div class="text-xs text-slate-500">{{ row.display_config?.summary || row.description || '未设置摘要' }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="type" label="周期" width="90" />
        <el-table-column prop="price" label="价格" width="100" />
        <el-table-column label="展示" width="140">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag v-if="row.display_config?.badge_text" size="small" type="warning">{{ row.display_config?.badge_text }}</el-tag>
              <el-tag v-if="row.display_config?.is_recommended" size="small" type="success">推荐</el-tag>
            </div>
          </template>
        </el-table-column>
        <el-table-column prop="duration_days" label="时长" width="90" />
        <el-table-column prop="sort_order" label="排序" width="80" />
        <el-table-column label="状态" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '上架' : '下架' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="160" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="removePlan(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </section>

    <el-dialog v-model="dialogVisible" :title="form.id ? '编辑套餐' : '新增套餐'" width="1080px" destroy-on-close>
      <div class="grid gap-6 lg:grid-cols-[minmax(0,1.3fr)_360px]">
        <div class="space-y-6">
          <section class="rounded-3xl border border-slate-200 bg-slate-50/70 p-5">
            <div class="mb-4 text-sm font-semibold text-slate-700">基础信息</div>
            <el-form label-position="top" class="grid gap-4 md:grid-cols-2">
              <el-form-item label="套餐名称" required>
                <el-input v-model="form.name" placeholder="例如 Pro" />
              </el-form-item>
              <el-form-item label="计费周期" required>
                <el-select v-model="form.type">
                  <el-option label="月付" value="monthly" />
                  <el-option label="年付" value="yearly" />
                  <el-option label="自定义" value="custom" />
                </el-select>
              </el-form-item>
              <el-form-item label="售价" required>
                <el-input-number v-model="form.price" :min="0" :precision="2" class="w-full" />
              </el-form-item>
              <el-form-item label="时长（天）" required>
                <el-input-number v-model="form.duration_days" :min="1" class="w-full" />
              </el-form-item>
              <el-form-item label="聊天限额">
                <el-input-number v-model="form.chat_limit" class="w-full" />
              </el-form-item>
              <el-form-item label="排序">
                <el-input-number v-model="form.sort_order" class="w-full" />
              </el-form-item>
              <el-form-item label="上架状态">
                <el-switch v-model="form.is_active" />
              </el-form-item>
              <el-form-item label="推荐套餐">
                <el-switch v-model="form.is_recommended" />
              </el-form-item>
              <el-form-item label="后台描述" class="md:col-span-2">
                <el-input v-model="form.description" type="textarea" :rows="3" placeholder="后台备注或简述" />
              </el-form-item>
            </el-form>
          </section>

          <section class="rounded-3xl border border-slate-200 bg-white p-5">
            <div class="mb-4 text-sm font-semibold text-slate-700">用户端展示配置</div>
            <el-form label-position="top" class="grid gap-4 md:grid-cols-2">
              <el-form-item label="角标文案">
                <el-input v-model="form.badge_text" placeholder="例如 最受欢迎" />
              </el-form-item>
              <el-form-item label="划线原价">
                <el-input v-model="form.original_price" placeholder="例如 99" />
              </el-form-item>
              <el-form-item label="摘要文案" class="md:col-span-2">
                <el-input v-model="form.summary" placeholder="一句话描述套餐定位" />
              </el-form-item>
              <el-form-item label="按钮文案">
                <el-input v-model="form.button_text" placeholder="例如 立即订阅" />
              </el-form-item>
              <el-form-item label="支付跳转链接">
                <el-input v-model="form.cta_url" placeholder="可选，未配置时走支付渠道链接或收款码" />
              </el-form-item>
              <el-form-item label="权益列表" class="md:col-span-2">
                <el-input
                  v-model="form.feature_points_text"
                  type="textarea"
                  :rows="5"
                  placeholder="每行一个卖点，例如：&#10;更快响应&#10;适合高频使用"
                />
              </el-form-item>
            </el-form>
          </section>
        </div>

        <aside class="rounded-[28px] border border-slate-200 bg-slate-950 p-6 text-white shadow-[0_24px_60px_-36px_rgba(15,23,42,0.75)]">
          <div class="flex items-start justify-between gap-3">
            <div>
              <div class="text-sm uppercase tracking-[0.24em] text-slate-400">{{ previewCard.typeLabel }}</div>
              <h3 class="mt-3 text-2xl font-semibold">{{ previewCard.name }}</h3>
            </div>
            <span v-if="previewCard.badgeText" class="rounded-full bg-amber-400 px-3 py-1 text-xs font-semibold text-slate-950">
              {{ previewCard.badgeText }}
            </span>
          </div>

          <div class="mt-6 flex items-end gap-2">
            <span class="text-4xl font-semibold">¥{{ previewCard.price }}</span>
            <span class="pb-1 text-sm text-slate-400">/{{ previewCard.typeLabel }}</span>
          </div>
          <div v-if="previewCard.originalPrice" class="mt-2 text-sm text-slate-500 line-through">原价 ¥{{ previewCard.originalPrice }}</div>
          <p class="mt-4 text-sm leading-6 text-slate-300">{{ previewCard.summary }}</p>

          <div class="mt-6 space-y-3">
            <div
              v-for="point in previewCard.points.length ? previewCard.points : ['建议补充权益说明']"
              :key="point"
              class="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-slate-100"
            >
              {{ point }}
            </div>
          </div>

          <button
            type="button"
            class="mt-8 flex w-full items-center justify-center rounded-2xl border border-transparent px-4 py-3 text-sm font-semibold transition"
            :class="previewCard.recommended ? 'bg-sky-400 text-slate-950' : 'bg-white text-slate-950'"
          >
            {{ previewCard.buttonText }}
          </button>
        </aside>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="savePlan">保存套餐</el-button>
      </template>
    </el-dialog>
  </div>
</template>
