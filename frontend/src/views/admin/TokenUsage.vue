<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import api from '@/utils/api'

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
  <div class="space-y-4">
    <!-- 费用统计卡片 -->
    <div class="grid grid-cols-2 xl:grid-cols-4 gap-4">
      <div class="bg-white rounded-xl p-5 shadow-sm border">
        <div class="text-xs text-gray-400 mb-1">总费用 (USD)</div>
        <div class="text-2xl font-bold text-green-600">${{ Number(summary.total_cost_usd).toFixed(4) }}</div>
        <div class="text-xs text-gray-400 mt-1">{{ filterLabel }}</div>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border">
        <div class="text-xs text-gray-400 mb-1">请求次数</div>
        <div class="text-2xl font-bold text-blue-600">{{ summary.request_count }}</div>
        <div class="text-xs text-gray-400 mt-1">平均 ${{ summary.request_count ? (Number(summary.total_cost_usd) / summary.request_count).toFixed(4) : '0.0000' }}/次</div>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border">
        <div class="text-xs text-gray-400 mb-1">Input Tokens</div>
        <div class="text-2xl font-bold text-indigo-600">{{ summary.total_input_tokens.toLocaleString() }}</div>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm border">
        <div class="text-xs text-gray-400 mb-1">Output Tokens</div>
        <div class="text-2xl font-bold text-pink-600">{{ summary.total_output_tokens.toLocaleString() }}</div>
      </div>
    </div>

    <!-- 按模型费用统计 -->
    <div class="bg-white rounded-xl p-4 shadow-sm border" v-if="modelCosts.length">
      <h3 class="text-sm font-semibold text-gray-600 mb-3">按模型费用统计</h3>
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">
        <div v-for="mc in modelCosts" :key="mc.model" class="border rounded-lg p-4 bg-gray-50">
          <div class="flex justify-between items-center mb-2">
            <span class="font-medium text-sm text-gray-700">{{ mc.model }}</span>
            <span class="text-green-600 font-bold">${{ Number(mc.cost_usd).toFixed(4) }}</span>
          </div>
          <div class="flex gap-4 text-xs text-gray-500">
            <span>{{ mc.count }} 次</span>
            <span>In: {{ mc.input_tokens.toLocaleString() }}</span>
            <span>Out: {{ mc.output_tokens.toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 筛选栏 -->
    <div class="bg-white rounded-xl p-4 shadow-sm border flex flex-wrap items-center gap-3">
      <el-date-picker
        v-model="filters.dateRange"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        value-format="YYYY-MM-DD HH:mm:ss"
        :default-time="[new Date(2000, 0, 1, 0, 0, 0), new Date(2000, 0, 1, 23, 59, 59)]"
        style="width: 380px"
      />
      <el-input
        v-model="filters.keyword"
        placeholder="用户名 / 手机号"
        clearable
        style="width: 180px"
        @keyup.enter="onSearch"
      />
      <el-select v-model="filters.model" placeholder="模型" clearable style="width: 180px">
        <el-option v-for="m in modelOptions" :key="m" :label="m" :value="m" />
      </el-select>
      <el-button type="primary" @click="onSearch">搜索</el-button>
      <el-button @click="onReset">重置</el-button>
    </div>

    <!-- 明细表 -->
    <div class="bg-white rounded-xl p-4 shadow-sm border">
      <h3 class="text-sm font-semibold text-gray-600 mb-3">使用明细</h3>
      <el-table :data="listData" v-loading="loading" stripe border style="width: 100%">
        <el-table-column prop="created_at" label="时间" min-width="170">
          <template #default="{ row }">{{ row.created_at?.replace('T', ' ').slice(0, 19) }}</template>
        </el-table-column>
        <el-table-column prop="nickname" label="用户" min-width="110">
          <template #default="{ row }">
            <div>{{ row.nickname }}</div>
            <div class="text-xs text-gray-400" v-if="row.phone">{{ row.phone }}</div>
          </template>
        </el-table-column>
        <el-table-column prop="model" label="模型" min-width="140" />
        <el-table-column prop="input_tokens" label="Input" min-width="100" align="right">
          <template #default="{ row }">{{ row.input_tokens.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="output_tokens" label="Output" min-width="100" align="right">
          <template #default="{ row }">{{ row.output_tokens.toLocaleString() }}</template>
        </el-table-column>
        <el-table-column prop="cost_usd" label="费用 (USD)" min-width="110" align="right">
          <template #default="{ row }">
            <span :class="row.cost_usd > 0 ? 'text-green-600 font-medium' : 'text-gray-400'">
              ${{ Number(row.cost_usd).toFixed(6) }}
            </span>
          </template>
        </el-table-column>
      </el-table>
      <div class="flex justify-end mt-4" v-if="total > pageSize">
        <el-pagination
          v-model:current-page="page"
          :page-size="pageSize"
          :total="total"
          layout="prev, pager, next"
          background
        />
      </div>
    </div>
  </div>
</template>
