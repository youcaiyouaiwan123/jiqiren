<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import type { OverviewData } from '@/types'

const overview = ref<OverviewData | null>(null)

/* ── 时间筛选 ── */
const dateRange = ref<string[]>([])

function dateParams(): Record<string, string> {
  const p: Record<string, string> = {}
  if (dateRange.value?.length === 2) {
    p.start_date = dateRange.value[0]!
    p.end_date = dateRange.value[1]!
  }
  return p
}

const rangeLabel = computed(() => {
  if (dateRange.value?.length === 2) return `${dateRange.value[0]} ~ ${dateRange.value[1]}`
  return '全部时间'
})

interface TrendItem {
  date: string; new_users: number; active_users: number
  conversations: number; messages: number
  input_tokens: number; output_tokens: number; cost_usd: number
}
const trends = ref<TrendItem[]>([])

interface TopUser {
  rank: number; user_id: number; nickname: string; phone: string
  msg_count: number; conv_count: number
}
const topUsers = ref<TopUser[]>([])

interface ModelStat {
  model: string; count: number; user_count: number
  input_tokens: number; output_tokens: number; cost_usd: number
}
const modelStats = ref<ModelStat[]>([])

interface HotQuestion { rank: number; question: string; count: number; user_count: number }
const hotQuestions = ref<HotQuestion[]>([])

const statCards = [
  { key: 'user_total', label: '用户', todayKey: 'user_today', todayLabel: '今日新增', isMoney: false, surfaceClass: 'from-blue-500/10 via-white to-white', badgeClass: 'bg-blue-50 text-blue-700 ring-blue-100', todayTextClass: 'text-blue-600', barClass: 'bg-blue-500' },
  { key: 'active_users', label: '活跃用户', todayKey: 'active_users_today', todayLabel: '今日', isMoney: false, surfaceClass: 'from-emerald-500/10 via-white to-white', badgeClass: 'bg-emerald-50 text-emerald-700 ring-emerald-100', todayTextClass: 'text-emerald-600', barClass: 'bg-emerald-500' },
  { key: 'conversation_total', label: '对话', todayKey: 'conversation_today', todayLabel: '今日', isMoney: false, surfaceClass: 'from-violet-500/10 via-white to-white', badgeClass: 'bg-violet-50 text-violet-700 ring-violet-100', todayTextClass: 'text-violet-600', barClass: 'bg-violet-500' },
  { key: 'message_total', label: '消息', todayKey: 'message_today', todayLabel: '今日', isMoney: false, surfaceClass: 'from-amber-500/10 via-white to-white', badgeClass: 'bg-amber-50 text-amber-700 ring-amber-100', todayTextClass: 'text-amber-600', barClass: 'bg-amber-500' },
  { key: 'cost_usd_total', label: '费用 (USD)', todayKey: 'cost_usd_today', todayLabel: '今日', isMoney: true, surfaceClass: 'from-teal-500/10 via-white to-white', badgeClass: 'bg-teal-50 text-teal-700 ring-teal-100', todayTextClass: 'text-teal-600', barClass: 'bg-teal-500' },
  { key: 'token_input_total', label: 'Input Tokens', todayKey: '', todayLabel: '', isMoney: false, surfaceClass: 'from-indigo-500/10 via-white to-white', badgeClass: 'bg-indigo-50 text-indigo-700 ring-indigo-100', todayTextClass: 'text-indigo-600', barClass: 'bg-indigo-500' },
]

function fmt(v: number, isMoney = false): string {
  if (isMoney) return '$' + Number(v).toFixed(4)
  return v >= 10000 ? (v / 10000).toFixed(1) + '万' : String(v)
}

function getVal(key: string, isMoney = false): string {
  if (!overview.value) return '-'
  const v = (overview.value as Record<string, number>)[key]
  if (v === undefined) return '-'
  return fmt(v, isMoney)
}

async function fetchAll() {
  try {
    const dp = dateParams()
    const [ovRes, trRes, tuRes, msRes, hqRes] = await Promise.all([
      api.get('/admin/analytics/overview', { params: dp }),
      api.get('/admin/analytics/trends', { params: { days: 14, ...dp } }),
      api.get('/admin/analytics/top-users', { params: { top_n: 10, days: 7, ...dp } }),
      api.get('/admin/analytics/model-stats', { params: { days: 30, ...dp } }),
      api.get('/admin/analytics/hot-questions', { params: { top_n: 15, days: 7, ...dp } }),
    ])
    overview.value = ovRes.data
    trends.value = trRes.data.items
    topUsers.value = tuRes.data.items
    modelStats.value = msRes.data.items
    hotQuestions.value = hqRes.data.items
  } catch { /* handled */ }
}

function onSearch() { fetchAll() }
function onReset() { dateRange.value = []; fetchAll() }

onMounted(fetchAll)
</script>

<template>
  <div class="space-y-6">
    <!-- 时间筛选 -->
    <div class="dashboard-hero rounded-3xl border border-slate-200 p-5 sm:p-6">
      <div class="flex flex-col gap-5 2xl:flex-row 2xl:items-center 2xl:justify-between">
        <div class="min-w-0">
          <div class="inline-flex rounded-full bg-slate-900 px-3 py-1 text-xs font-semibold text-white">运营总览</div>
          <h2 class="mt-4 text-2xl font-semibold tracking-tight text-slate-900">数据分析总览</h2>
          <p class="mt-2 max-w-2xl text-sm leading-6 text-slate-500">按时间范围查看用户、对话、模型费用与高频问题，快速感知近期运营和使用趋势。</p>
          <div class="mt-4 flex flex-wrap gap-2 text-xs font-medium">
            <span class="rounded-full bg-slate-100 px-3 py-1 text-slate-600">统计范围：{{ rangeLabel }}</span>
            <span class="rounded-full bg-sky-50 px-3 py-1 text-sm font-semibold text-sky-700">趋势 {{ trends.length || 0 }} 天</span>
            <span class="rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">模型 {{ modelStats.length }} 个</span>
            <span class="rounded-full bg-violet-50 px-3 py-1 text-sm font-semibold text-violet-700">热门问题 {{ hotQuestions.length }} 条</span>
          </div>
        </div>
        <div class="rounded-3xl border border-slate-200 bg-slate-50/80 p-3 sm:p-4 2xl:w-[460px]">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div class="w-full lg:w-[380px]">
              <el-date-picker
                v-model="dateRange"
                type="datetimerange"
                range-separator="至"
                start-placeholder="开始时间"
                end-placeholder="结束时间"
                value-format="YYYY-MM-DD HH:mm:ss"
                :default-time="[new Date(2000, 0, 1, 0, 0, 0), new Date(2000, 0, 1, 23, 59, 59)]"
                style="width: 100%"
              />
            </div>
            <div class="flex items-center gap-2">
              <el-button round type="primary" @click="onSearch">查询</el-button>
              <el-button round @click="onReset">重置</el-button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 概览卡片 -->
    <div class="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-6">
      <div v-for="s in statCards" :key="s.key" class="relative overflow-hidden rounded-3xl border border-slate-200 bg-gradient-to-br p-5 shadow-sm transition duration-200 hover:-translate-y-0.5 hover:shadow-lg" :class="s.surfaceClass">
        <div class="absolute inset-x-5 top-0 h-1.5 rounded-b-full" :class="s.barClass"></div>
        <div class="flex items-start justify-between gap-3">
          <div class="rounded-full px-3 py-1 text-xs font-semibold ring-1 ring-inset" :class="s.badgeClass">{{ s.label }}</div>
          <div class="text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">{{ s.todayKey ? s.todayLabel : '累计' }}</div>
        </div>
        <div class="mt-5 text-3xl font-semibold tracking-tight text-slate-900">{{ getVal(s.key, s.isMoney) }}</div>
        <div class="mt-4 flex items-center justify-between text-xs">
          <span class="text-slate-500">{{ s.todayKey ? '当前周期' : '累计统计' }}</span>
          <span class="font-semibold" :class="s.todayTextClass">{{ s.todayKey ? getVal(s.todayKey, s.isMoney) : '—' }}</span>
        </div>
      </div>
    </div>

    <!-- 第二行：趋势 + 模型统计 -->
    <div class="grid grid-cols-1 gap-5 2xl:grid-cols-[minmax(0,1.7fr)_minmax(340px,1fr)]">
      <!-- 趋势 -->
      <div class="dashboard-panel">
        <div class="dashboard-panel-header">
          <div>
            <h3 class="text-base font-semibold text-slate-800">每日趋势</h3>
            <p class="dashboard-panel-subtitle">展示最近 14 天的活跃、消息、对话与成本变化。</p>
          </div>
          <span class="dashboard-chip bg-sky-50 text-sky-700">14 天趋势</span>
        </div>
        <div class="overflow-hidden rounded-2xl border border-slate-100">
          <el-table :data="trends" class="dashboard-table" stripe size="large" style="width: 100%">
            <el-table-column prop="date" label="日期" min-width="100">
              <template #default="{ row }">{{ row.date.slice(5) }}</template>
            </el-table-column>
            <el-table-column prop="active_users" label="活跃" min-width="60" align="right" />
            <el-table-column prop="new_users" label="新增" min-width="60" align="right" />
            <el-table-column prop="messages" label="消息" min-width="60" align="right" />
            <el-table-column prop="conversations" label="对话" min-width="60" align="right" />
            <el-table-column label="费用" min-width="80" align="right">
              <template #default="{ row }">
                <span class="text-green-600">${{ Number(row.cost_usd).toFixed(4) }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </div>

      <!-- 模型使用统计 -->
      <div class="dashboard-panel">
        <div class="dashboard-panel-header">
          <div>
            <h3 class="text-base font-semibold text-slate-800">模型使用统计</h3>
            <p class="dashboard-panel-subtitle">查看不同模型的调用次数、覆盖用户和累计成本。</p>
          </div>
          <span class="dashboard-chip bg-emerald-50 text-emerald-700">{{ modelStats.length }} 个模型</span>
        </div>
        <div class="space-y-3" v-if="modelStats.length">
          <div v-for="ms in modelStats" :key="ms.model" class="rounded-2xl border border-slate-200 bg-slate-50/80 p-4 transition duration-200 hover:border-slate-300 hover:bg-white hover:shadow-sm">
            <div class="flex items-start justify-between gap-3">
              <div class="min-w-0">
                <div class="truncate text-sm font-semibold text-slate-800">{{ ms.model }}</div>
                <div class="mt-1 text-xs text-slate-500">{{ ms.user_count }} 位用户 · {{ ms.count }} 次调用</div>
              </div>
              <span class="rounded-full bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">${{ Number(ms.cost_usd).toFixed(4) }}</span>
            </div>
            <div class="mt-4 grid grid-cols-2 gap-2 text-xs sm:grid-cols-4">
              <div class="rounded-2xl bg-white px-3 py-2">
                <div class="text-[11px] text-slate-400">调用次数</div>
                <div class="mt-1 text-sm font-semibold text-slate-700">{{ ms.count }}</div>
              </div>
              <div class="rounded-2xl bg-white px-3 py-2">
                <div class="text-[11px] text-slate-400">覆盖用户</div>
                <div class="mt-1 text-sm font-semibold text-slate-700">{{ ms.user_count }}</div>
              </div>
              <div class="rounded-2xl bg-white px-3 py-2">
                <div class="text-[11px] text-slate-400">Input</div>
                <div class="mt-1 text-sm font-semibold text-slate-700">{{ ms.input_tokens.toLocaleString() }}</div>
              </div>
              <div class="rounded-2xl bg-white px-3 py-2">
                <div class="text-[11px] text-slate-400">Output</div>
                <div class="mt-1 text-sm font-semibold text-slate-700">{{ ms.output_tokens.toLocaleString() }}</div>
              </div>
            </div>
          </div>
        </div>
        <div v-else class="rounded-2xl border border-dashed border-slate-200 bg-slate-50 py-10 text-center text-sm text-slate-400">暂无数据</div>
      </div>
    </div>

    <!-- 第三行：活跃用户 + 高频问题 -->
    <div class="grid grid-cols-1 gap-5 2xl:grid-cols-2">
      <!-- 活跃用户 TOP -->
      <div class="dashboard-panel">
        <div class="dashboard-panel-header">
          <div>
            <h3 class="text-base font-semibold text-slate-800">活跃用户排行</h3>
            <p class="dashboard-panel-subtitle">筛选近期高活跃用户，便于运营跟进和重点观察。</p>
          </div>
          <span class="dashboard-chip bg-violet-50 text-violet-700">TOP 10</span>
        </div>
        <div class="dashboard-table-card dashboard-table-card-sm overflow-hidden rounded-2xl border border-slate-100">
          <el-table :data="topUsers" class="dashboard-table" stripe size="large" height="320" style="width: 100%">
          <el-table-column label="序号" width="68" align="center">
            <template #default="{ row }">
              <span class="rank-pill" :class="row.rank <= 3 ? 'rank-pill-top' : ''">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column label="用户" min-width="120">
            <template #default="{ row }">
              <div>{{ row.nickname }}</div>
              <div class="text-xs text-gray-400" v-if="row.phone">{{ row.phone }}</div>
            </template>
          </el-table-column>
          <el-table-column prop="msg_count" label="消息数" min-width="80" align="right" />
          <el-table-column prop="conv_count" label="对话数" min-width="80" align="right" />
          </el-table>
        </div>
      </div>

      <!-- 高频问题 -->
      <div class="dashboard-panel">
        <div class="dashboard-panel-header">
          <div>
            <h3 class="text-base font-semibold text-slate-800">高频问题排行</h3>
            <p class="dashboard-panel-subtitle">聚焦重复提问内容，帮助你发现文档空白和运营机会。</p>
          </div>
          <span class="dashboard-chip bg-amber-50 text-amber-700">TOP 15</span>
        </div>
        <div class="dashboard-table-card dashboard-table-card-sm overflow-hidden rounded-2xl border border-slate-100">
          <el-table :data="hotQuestions" class="dashboard-table" stripe size="large" height="320" style="width: 100%">
          <el-table-column label="序号" width="68" align="center">
            <template #default="{ row }">
              <span class="rank-pill" :class="row.rank <= 3 ? 'rank-pill-top' : ''">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="question" label="问题内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="count" label="次数" width="70" align="right" />
          <el-table-column prop="user_count" label="用户数" width="75" align="right" />
          </el-table>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 32%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98) 0%, rgba(248, 250, 252, 0.98) 100%);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
}

.dashboard-panel {
  border: 1px solid #e2e8f0;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.92);
  padding: 20px;
  box-shadow: 0 14px 32px rgba(15, 23, 42, 0.05);
}

.dashboard-panel-header {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 16px;
}

.dashboard-panel-subtitle {
  margin-top: 4px;
  font-size: 13px;
  line-height: 20px;
  color: #64748b;
}

.dashboard-chip {
  display: inline-flex;
  align-items: center;
  border-radius: 9999px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
}

.dashboard-table-card-sm {
  max-height: 322px;
}

.rank-pill {
  display: inline-flex;
  min-width: 28px;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  background: #e2e8f0;
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 700;
  line-height: 1;
  color: #475569;
}

.rank-pill-top {
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 100%);
  color: #ffffff;
}

:deep(.dashboard-table.el-table) {
  --el-table-header-bg-color: #f8fafc;
  --el-table-header-text-color: #475569;
  --el-table-text-color: #334155;
  --el-table-row-hover-bg-color: #f8fafc;
  --el-table-current-row-bg-color: #eff6ff;
  --el-table-border-color: #e2e8f0;
}

:deep(.dashboard-table.el-table),
:deep(.dashboard-table.el-table .el-table__inner-wrapper),
:deep(.dashboard-table.el-table .el-table__header-wrapper),
:deep(.dashboard-table.el-table .el-table__body-wrapper) {
  box-shadow: none;
}

:deep(.dashboard-table.el-table .el-table__inner-wrapper::before) {
  display: none;
}

:deep(.dashboard-table.el-table th.el-table__cell) {
  background: #f8fafc;
  font-weight: 600;
}

:deep(.dashboard-table.el-table .el-table__cell) {
  padding-top: 12px;
  padding-bottom: 12px;
}

:deep(.dashboard-table.el-table .cell) {
  line-height: 1.45;
}
</style>
