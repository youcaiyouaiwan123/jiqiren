<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '@/utils/api'
import type { OverviewData } from '@/types'
import AdminPage from '@/components/AdminPage.vue'

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
  <AdminPage title="数据分析" :subtitle="rangeLabel" no-card>
    <template #tools>
      <el-date-picker
        v-model="dateRange"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        value-format="YYYY-MM-DD HH:mm:ss"
        :default-time="[new Date(2000, 0, 1, 0, 0, 0), new Date(2000, 0, 1, 23, 59, 59)]"
        size="default"
        style="width: 320px"
      />
      <el-button size="default" type="primary" @click="onSearch">查询</el-button>
      <el-button size="default" @click="onReset">重置</el-button>
    </template>

    <!-- 概览卡片：6 个紧凑统计 -->
    <div class="dash-stats">
      <div v-for="s in statCards" :key="s.key" class="dash-stat-card">
        <span class="dash-stat-bar" :class="s.barClass"></span>
        <div class="dash-stat-row">
          <span class="dash-stat-label">{{ s.label }}</span>
          <span class="dash-stat-today">{{ s.todayKey ? s.todayLabel : '累计' }}</span>
        </div>
        <div class="dash-stat-value">{{ getVal(s.key, s.isMoney) }}</div>
        <div class="dash-stat-row">
          <span class="dash-stat-sub">{{ s.todayKey ? '当前周期' : '累计统计' }}</span>
          <span class="dash-stat-sub-val">{{ s.todayKey ? getVal(s.todayKey, s.isMoney) : '—' }}</span>
        </div>
      </div>
    </div>

    <!-- 第二行：趋势 + 模型统计 -->
    <div class="dash-grid-2">
      <!-- 趋势 -->
      <div class="dash-panel">
        <div class="dash-panel-header">
          <div class="dash-panel-title">每日趋势</div>
          <span class="dash-panel-tag dash-tag-sky">14 天</span>
        </div>
        <el-table :data="trends" stripe size="small" style="width: 100%">
          <el-table-column prop="date" label="日期" min-width="80">
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

      <!-- 模型使用统计 -->
      <div class="dash-panel">
        <div class="dash-panel-header">
          <div class="dash-panel-title">模型使用统计</div>
          <span class="dash-panel-tag dash-tag-emerald">{{ modelStats.length }} 个</span>
        </div>
        <div class="space-y-2" v-if="modelStats.length">
          <div v-for="ms in modelStats" :key="ms.model" class="dash-model-row">
            <div class="dash-model-head">
              <div class="dash-model-name">{{ ms.model }}</div>
              <span class="dash-model-cost">${{ Number(ms.cost_usd).toFixed(4) }}</span>
            </div>
            <div class="dash-model-meta">
              <span>{{ ms.user_count }} 用户</span>
              <span>{{ ms.count }} 次</span>
              <span>In {{ ms.input_tokens.toLocaleString() }}</span>
              <span>Out {{ ms.output_tokens.toLocaleString() }}</span>
            </div>
          </div>
        </div>
        <div v-else class="dash-empty">暂无数据</div>
      </div>
    </div>

    <!-- 第三行：活跃用户 + 高频问题 -->
    <div class="dash-grid-2">
      <!-- 活跃用户 TOP -->
      <div class="dash-panel">
        <div class="dash-panel-header">
          <div class="dash-panel-title">活跃用户排行</div>
          <span class="dash-panel-tag dash-tag-violet">TOP 10</span>
        </div>
        <el-table :data="topUsers" stripe size="small" height="320" style="width: 100%">
          <el-table-column label="#" width="50" align="center">
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
          <el-table-column prop="msg_count" label="消息" min-width="70" align="right" />
          <el-table-column prop="conv_count" label="对话" min-width="70" align="right" />
        </el-table>
      </div>

      <!-- 高频问题 -->
      <div class="dash-panel">
        <div class="dash-panel-header">
          <div class="dash-panel-title">高频问题排行</div>
          <span class="dash-panel-tag dash-tag-amber">TOP 15</span>
        </div>
        <el-table :data="hotQuestions" stripe size="small" height="320" style="width: 100%">
          <el-table-column label="#" width="50" align="center">
            <template #default="{ row }">
              <span class="rank-pill" :class="row.rank <= 3 ? 'rank-pill-top' : ''">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="question" label="问题内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="count" label="次数" width="70" align="right" />
          <el-table-column prop="user_count" label="用户" width="70" align="right" />
        </el-table>
      </div>
    </div>
  </AdminPage>
</template>

<style scoped>
/* ── 统计卡片 ─────────────── */
.dash-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
@media (min-width: 768px)  { .dash-stats { grid-template-columns: repeat(3, minmax(0, 1fr)); } }
@media (min-width: 1280px) { .dash-stats { grid-template-columns: repeat(6, minmax(0, 1fr)); } }

.dash-stat-card {
  position: relative;
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 12px 14px 10px;
  overflow: hidden;
}
.dash-stat-bar {
  position: absolute; top: 0; left: 0; right: 0; height: 2px;
  display: block;
}
.dash-stat-row { display: flex; align-items: center; justify-content: space-between; }
.dash-stat-label { font-size: 12px; font-weight: 600; color: #475569; }
.dash-stat-today { font-size: 10px; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.05em; }
.dash-stat-value { font-size: 22px; font-weight: 600; color: #0f172a; margin: 6px 0 8px; letter-spacing: -0.01em; }
.dash-stat-sub { font-size: 11px; color: #94a3b8; }
.dash-stat-sub-val { font-size: 12px; font-weight: 500; color: #1f2937; }

/* ── 两栏面板 ─────────────── */
.dash-grid-2 {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}
@media (min-width: 1280px) { .dash-grid-2 { grid-template-columns: 1fr 1fr; } }

.dash-panel {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.dash-panel-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
  background: #fafbfc;
}
.dash-panel-title { font-size: 13px; font-weight: 600; color: #1f2937; }
.dash-panel-tag {
  font-size: 11px; padding: 2px 8px; border-radius: 4px; font-weight: 500;
}
.dash-tag-sky { background: #e0f2fe; color: #0369a1; }
.dash-tag-emerald { background: #d1fae5; color: #047857; }
.dash-tag-violet { background: #ede9fe; color: #6d28d9; }
.dash-tag-amber { background: #fef3c7; color: #b45309; }

/* ── 模型行 ─────────────── */
.dash-model-row {
  padding: 10px 14px;
  border-bottom: 1px solid #f1f5f9;
}
.dash-model-row:last-child { border-bottom: none; }
.dash-model-head {
  display: flex; align-items: center; justify-content: space-between;
}
.dash-model-name { font-size: 13px; font-weight: 600; color: #1f2937; }
.dash-model-cost { font-size: 12px; font-weight: 600; color: #047857; }
.dash-model-meta {
  margin-top: 4px;
  display: flex; flex-wrap: wrap; gap: 12px;
  font-size: 11px; color: #94a3b8;
}
.dash-empty {
  padding: 40px 0;
  text-align: center; color: #94a3b8; font-size: 13px;
}

/* ── 排名小药丸 ─────────────── */
.rank-pill {
  display: inline-flex; align-items: center; justify-content: center;
  min-width: 22px; height: 20px; padding: 0 6px;
  border-radius: 4px; font-size: 11px; font-weight: 600;
  background: #f1f5f9; color: #475569;
}
.rank-pill-top { background: #fef3c7; color: #b45309; }
</style>