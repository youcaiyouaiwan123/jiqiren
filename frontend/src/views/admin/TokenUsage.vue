<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '@/utils/api'
import AdminPage from '@/components/AdminPage.vue'

function formatDateTime(value: string | null | undefined): string {
  if (!value) return '-'
  return String(value).replace('T', ' ').replace(/\.\d+/, '').replace(/Z$/, '').replace(/[+-]\d{2}:\d{2}$/, '').slice(0, 19)
}

/* ── 汇总 ── */
const summary = ref({ total_input_tokens: 0, total_output_tokens: 0, total_cost_usd: 0, request_count: 0 })

/* ── 按模型费用统计 ── */
interface ModelCost { model: string; count: number; input_tokens: number; output_tokens: number; cost_usd: number }
const modelCosts = ref<ModelCost[]>([])

/* ── 筛选 ── */
const filters = reactive({
  dateRange: [] as string[],
  keyword: '',
  model: '',
})
const modelOptions = ref<string[]>([])

/* ── 明细列表 ── */
interface UsageRow {
  id: number; user_id: number; nickname: string; phone: string
  model: string; input_tokens: number; output_tokens: number
  cost_usd: number; created_at: string
}
const listData = ref<UsageRow[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

function buildFilterParams(): Record<string, string> {
  const params: Record<string, string> = {}
  const [startDate, endDate] = filters.dateRange
  if (startDate && endDate) {
    params.start_date = startDate
    params.end_date = endDate
  }
  if (filters.keyword) params.keyword = filters.keyword
  if (filters.model) params.model = filters.model
  return params
}

const filterLabel = computed(() => {
  if (filters.dateRange?.length === 2) return `${filters.dateRange[0]} ~ ${filters.dateRange[1]}`
  return '全部时间'
})

async function fetchSummary() {
  try {
    const res = await api.get('/admin/token-usage/summary', { params: buildFilterParams() })
    summary.value = res.data
  } catch { /* handled */ }
}

async function fetchModelCosts() {
  try {
    const params: Record<string, string> = {}
    const [startDate, endDate] = filters.dateRange
    if (startDate && endDate) {
      params.start_date = startDate
      params.end_date = endDate
    }
    const res = await api.get('/admin/token-usage/cost-by-model', { params })
    modelCosts.value = res.data.items
  } catch { /* handled */ }
}

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, string | number> = { ...buildFilterParams(), page: page.value, page_size: pageSize.value }
    const res = await api.get('/admin/token-usage/list', { params })
    listData.value = res.data.items
    total.value = res.data.total
  } catch { /* handled */ }
  loading.value = false
}

async function fetchModels() {
  try {
    const res = await api.get('/admin/token-usage/models')
    modelOptions.value = res.data.models
  } catch { /* handled */ }
}

function onSearch() {
  page.value = 1
  fetchSummary()
  fetchModelCosts()
  fetchList()
}

function onReset() {
  filters.dateRange = []
  filters.keyword = ''
  filters.model = ''
  onSearch()
}

watch(page, fetchList)

onMounted(() => {
  fetchSummary()
  fetchModelCosts()
  fetchList()
  fetchModels()
})
</script>

<template>
  <AdminPage title="Token 计费" :subtitle="filterLabel" no-card>
    <template #tools>
      <el-date-picker
        v-model="filters.dateRange"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        value-format="YYYY-MM-DD HH:mm:ss"
        :default-time="[new Date(2000, 0, 1, 0, 0, 0), new Date(2000, 0, 1, 23, 59, 59)]"
        size="default"
        style="width: 320px"
      />
      <el-input
        v-model="filters.keyword"
        placeholder="用户名 / 手机号"
        clearable
        size="default"
        style="width: 160px"
        @keyup.enter="onSearch"
      />
      <el-select v-model="filters.model" placeholder="模型" clearable size="default" style="width: 160px">
        <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
      </el-select>
      <el-button type="primary" size="default" @click="onSearch">查询</el-button>
      <el-button size="default" @click="onReset">重置</el-button>
    </template>

    <!-- 4 个统计卡片：统一样式 -->
    <div class="grid grid-cols-2 xl:grid-cols-4 gap-3">
      <div class="tu-stat-card">
        <div class="tu-stat-label">总费用 (USD)</div>
        <div class="tu-stat-value text-emerald-600">${{ Number(summary.total_cost_usd).toFixed(4) }}</div>
        <div class="tu-stat-hint">{{ filterLabel }}</div>
      </div>
      <div class="tu-stat-card">
        <div class="tu-stat-label">请求次数</div>
        <div class="tu-stat-value text-sky-600">{{ summary.request_count.toLocaleString() }}</div>
        <div class="tu-stat-hint">
          平均 ${{ summary.request_count ? (Number(summary.total_cost_usd) / summary.request_count).toFixed(4) : '0.0000' }}/次
        </div>
      </div>
      <div class="tu-stat-card">
        <div class="tu-stat-label">Input Tokens</div>
        <div class="tu-stat-value text-indigo-600">{{ summary.total_input_tokens.toLocaleString() }}</div>
        <div class="tu-stat-hint">累计</div>
      </div>
      <div class="tu-stat-card">
        <div class="tu-stat-label">Output Tokens</div>
        <div class="tu-stat-value text-pink-600">{{ summary.total_output_tokens.toLocaleString() }}</div>
        <div class="tu-stat-hint">累计</div>
      </div>
    </div>

    <!-- 按模型费用统计 -->
    <div class="tu-panel" v-if="modelCosts.length">
      <div class="tu-panel-header">
        <span class="tu-panel-title">按模型费用统计</span>
        <span class="tu-panel-tag">{{ modelCosts.length }} 个模型</span>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3 p-3">
        <div v-for="mc in modelCosts" :key="mc.model" class="tu-model-card">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-sm text-slate-700 truncate">{{ mc.model }}</span>
            <span class="text-emerald-600 font-semibold text-sm">${{ Number(mc.cost_usd).toFixed(4) }}</span>
          </div>
          <div class="flex gap-3 text-xs text-slate-500">
            <span>{{ mc.count.toLocaleString() }} 次</span>
            <span>In {{ mc.input_tokens.toLocaleString() }}</span>
            <span>Out {{ mc.output_tokens.toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 明细表 -->
    <div class="tu-panel">
      <div class="tu-panel-header">
        <span class="tu-panel-title">使用明细</span>
        <span class="tu-panel-tag">{{ total.toLocaleString() }} 条</span>
      </div>
      <el-table :data="listData" v-loading="loading" stripe border size="small" style="width: 100%">
        <el-table-column label="时间" min-width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="nickname" label="用户" min-width="110">
          <template #default="{ row }">
            <div>{{ row.nickname }}</div>
            <div class="text-xs text-gray-400" v-if="row.phone">{{ row.phone }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" min-width="140" />
        <el-table-column prop="input_tokens" label="Input" min-width="90" align="right">
          <template #default="{ row }">{{ row.input_tokens.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="output_tokens" label="Output" min-width="90" align="right">
          <template #default="{ row }">{{ row.output_tokens.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column label="缓存读取" min-width="95" align="right">
          <template #default="{ row }">
            <span :class="(row.cache_read_tokens || 0) > 0 ? 'text-emerald-600 font-medium' : 'text-gray-400'">
              {{ (row.cache_read_tokens || 0).toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column label="缓存写入" min-width="95" align="right">
          <template #default="{ row }">
            <span :class="(row.cache_creation_tokens || 0) > 0 ? 'text-amber-600 font-medium' : 'text-gray-400'">
              {{ (row.cache_creation_tokens || 0).toLocaleString() }}
            </span>
          </template>
        </el-table-column>
        <el-table-column prop="cost_usd" label="费用 (USD)" min-width="110" align="right">
          <template #default="{ row }">
            <span :class="row.cost_usd > 0 ? 'text-emerald-600 font-medium' : 'text-gray-400'">
              ${{ Number(row.cost_usd).toFixed(6) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div class="flex justify-end mt-3 px-3 pb-3" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
        />
      </div>
    </div>
  </AdminPage>
</template>

<style scoped>
.tu-stat-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 14px 16px;
  min-height: 92px;
  display: flex; flex-direction: column; justify-content: space-between;
}
.tu-stat-label { font-size: 12px; color: #94a3b8; font-weight: 500; }
.tu-stat-value { font-size: 22px; font-weight: 600; letter-spacing: -0.01em; }
.tu-stat-hint { font-size: 11px; color: #94a3b8; }

.tu-panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.tu-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
  background: #fafbfc;
}
.tu-panel-title { font-size: 13px; font-weight: 600; color: #1f2937; }
.tu-panel-tag { font-size: 11px; padding: 2px 8px; border-radius: 4px; background: #f1f5f9; color: #475569; }

.tu-model-card {
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 10px 12px;
  background: #fff;
  transition: border-color 0.15s;
}
.tu-model-card:hover {
  border-color: #cbd5e1;
}
</style>
