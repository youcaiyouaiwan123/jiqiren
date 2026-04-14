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
  { key: 'user_total', label: '用户', todayKey: 'user_today', todayLabel: '今日新增', color: '#3b82f6' },
  { key: 'active_users', label: '活跃用户', todayKey: 'active_users_today', todayLabel: '今日', color: '#10b981' },
  { key: 'conversation_total', label: '对话', todayKey: 'conversation_today', todayLabel: '今日', color: '#8b5cf6' },
  { key: 'message_total', label: '消息', todayKey: 'message_today', todayLabel: '今日', color: '#f59e0b' },
  { key: 'cost_usd_total', label: '费用 (USD)', todayKey: 'cost_usd_today', todayLabel: '今日', color: '#059669', isMoney: true },
  { key: 'token_input_total', label: 'Input Tokens', todayKey: '', todayLabel: '', color: '#6366f1' },
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
  <div class="space-y-4">
    <!-- 时间筛选 -->
    <div class="bg-white rounded-xl p-4 shadow-sm border flex flex-wrap items-center gap-3">
      <el-date-picker
        v-model="dateRange"
        type="datetimerange"
        range-separator="至"
        start-placeholder="开始时间"
        end-placeholder="结束时间"
        value-format="YYYY-MM-DD HH:mm:ss"
        :default-time="[new Date(2000, 0, 1, 0, 0, 0), new Date(2000, 0, 1, 23, 59, 59)]"
        style="width: 380px"
      />
      <el-button type="primary" @click="onSearch">查询</el-button>
      <el-button @click="onReset">重置</el-button>
      <span class="text-xs text-gray-400 ml-2">{{ rangeLabel }}</span>
    </div>

    <!-- 概览卡片 -->
    <div class="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-4">
      <div v-for="s in statCards" :key="s.key" class="bg-white rounded-xl p-5 shadow-sm border">
        <div class="text-xs text-gray-400 mb-1">{{ s.label }}</div>
        <div class="text-2xl font-bold" :style="{ color: s.color }">{{ getVal(s.key, s.isMoney) }}</div>
        <div class="text-xs text-gray-400 mt-1" v-if="s.todayKey">
          {{ s.todayLabel }} {{ getVal(s.todayKey, s.isMoney) }}
        </div>
      </div>
    </div>

    <!-- 第二行：趋势 + 模型统计 -->
    <div class="grid grid-cols-1 xl:grid-cols-3 gap-4">
      <!-- 趋势 -->
      <div class="xl:col-span-2 bg-white rounded-xl p-4 shadow-sm border">
        <h3 class="text-sm font-semibold text-gray-600 mb-3">每日趋势</h3>
        <div class="overflow-x-auto">
          <el-table :data="trends" stripe border size="small" style="width: 100%">
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
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <h3 class="text-sm font-semibold text-gray-600 mb-3">模型使用统计</h3>
        <div class="space-y-3" v-if="modelStats.length">
          <div v-for="ms in modelStats" :key="ms.model" class="border rounded-lg p-3 bg-gray-50">
            <div class="flex justify-between items-center mb-1">
              <span class="font-medium text-sm">{{ ms.model }}</span>
              <span class="text-green-600 font-bold text-sm">${{ Number(ms.cost_usd).toFixed(4) }}</span>
            </div>
            <div class="flex flex-wrap gap-x-4 gap-y-1 text-xs text-gray-500">
              <span>{{ ms.count }} 次调用</span>
              <span>{{ ms.user_count }} 位用户</span>
              <span>In: {{ ms.input_tokens.toLocaleString() }}</span>
              <span>Out: {{ ms.output_tokens.toLocaleString() }}</span>
            </div>
          </div>
        </div>
        <div v-else class="text-sm text-gray-400 text-center py-8">暂无数据</div>
      </div>
    </div>

    <!-- 第三行：活跃用户 + 高频问题 -->
    <div class="grid grid-cols-1 xl:grid-cols-2 gap-4">
      <!-- 活跃用户 TOP -->
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <h3 class="text-sm font-semibold text-gray-600 mb-3">活跃用户 TOP 10</h3>
        <el-table :data="topUsers" stripe border size="small" style="width: 100%">
          <el-table-column prop="rank" label="#" width="45" align="center" />
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

      <!-- 高频问题 -->
      <div class="bg-white rounded-xl p-4 shadow-sm border">
        <h3 class="text-sm font-semibold text-gray-600 mb-3">用户常问问题 TOP 15</h3>
        <el-table :data="hotQuestions" stripe border size="small" style="width: 100%">
          <el-table-column prop="rank" label="#" width="45" align="center" />
          <el-table-column prop="question" label="问题内容" min-width="200" show-overflow-tooltip />
          <el-table-column prop="count" label="次数" width="70" align="right" />
          <el-table-column prop="user_count" label="用户数" width="75" align="right" />
        </el-table>
      </div>
    </div>
  </div>
</template>
