<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const PAGE_SIZE = 20

interface RedeemRow {
  id: number
  code: string
  type: 'days' | 'chats'
  value: number
  status: 'unused' | 'used' | 'expired'
  used_by: number | null
  used_at: string | null
  expire_at: string | null
  created_at: string
}

// ── 列表 ──────────────────────────────────────────────────────
const loading = ref(false)
const list = ref<RedeemRow[]>([])
const total = ref(0)
const page = ref(1)
const statusFilter = ref('')

// ── 多选状态 ──────────────────────────────────────────────────
// 手动管理选中集合，支持跨页保留 + 全选所有页模式
const selectedIds = ref(new Set<number>())
const selectAllMode = ref(false)   // true = "选中了所有符合条件的数据"

const allCurrentPageSelected = computed(
  () => list.value.length > 0 && list.value.every(r => selectedIds.value.has(r.id)),
)
const someCurrentPageSelected = computed(
  () => !allCurrentPageSelected.value && list.value.some(r => selectedIds.value.has(r.id)),
)

const headerChecked = computed(() => selectAllMode.value || allCurrentPageSelected.value)
const headerIndeterminate = computed(() => !selectAllMode.value && someCurrentPageSelected.value)

const selectedCount = computed(() => selectAllMode.value ? total.value : selectedIds.value.size)
const hasSelection = computed(() => selectAllMode.value || selectedIds.value.size > 0)

function isRowSelected(row: RedeemRow) {
  return selectAllMode.value || selectedIds.value.has(row.id)
}

function onHeaderCheckboxChange() {
  if (selectAllMode.value || allCurrentPageSelected.value) {
    // 当前页已全选 → 再次点击，询问是否选中所有页
    if (total.value > PAGE_SIZE) {
      ElMessageBox.confirm(
        `是否选中所有 ${total.value} 条符合条件的数据？`,
        '全选确认',
        { confirmButtonText: '选中全部', cancelButtonText: '取消全选', type: 'info' },
      ).then(() => {
        selectAllMode.value = true
      }).catch(() => {
        selectAllMode.value = false
        selectedIds.value.clear()
      })
    } else {
      // 只有一页，直接切换为取消全选
      selectAllMode.value = false
      selectedIds.value.clear()
    }
  } else {
    // 第一次点击（未全选 → 全选当前页）
    list.value.forEach(r => selectedIds.value.add(r.id))
  }
}

function onRowCheckboxChange(row: RedeemRow, val: unknown) {
  const checked = Boolean(val)
  if (checked) {
    selectedIds.value.add(row.id)
  } else {
    if (selectAllMode.value) {
      // 退出全选模式，手动记录当前页除此行之外的所有行
      selectAllMode.value = false
      list.value.forEach(r => { if (r.id !== row.id) selectedIds.value.add(r.id) })
    } else {
      selectedIds.value.delete(row.id)
    }
  }
}

function clearSelection() {
  selectAllMode.value = false
  selectedIds.value.clear()
}

// ── 列表加载 ──────────────────────────────────────────────────
async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: PAGE_SIZE }
    if (statusFilter.value) params.status = statusFilter.value
    const res = await api.get('/admin/redeem-codes', { params })
    list.value = res.data.list
    total.value = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

function onFilterChange() {
  page.value = 1
  clearSelection()
  fetchList()
}

// ── 生成兑换码 ────────────────────────────────────────────────
const genDialog = ref(false)
const genForm = ref({ type: 'days', value: 30, count: 10, expire_at: '' })
const generatedCodes = ref<string[]>([])

async function generate() {
  try {
    const data: Record<string, unknown> = {
      type: genForm.value.type,
      value: genForm.value.value,
      count: genForm.value.count,
    }
    if (genForm.value.expire_at) data.expire_at = genForm.value.expire_at
    const res = await api.post('/admin/redeem-codes/generate', data)
    generatedCodes.value = res.data.codes
    ElMessage.success(`已生成 ${res.data.count} 个兑换码`)
    await fetchList()
  } catch { /* handled */ }
}

function copyAll() {
  navigator.clipboard.writeText(generatedCodes.value.join('\n'))
  ElMessage.success('已复制到剪贴板')
}

// ── 单条删除 ──────────────────────────────────────────────────
async function handleDelete(id: number) {
  try {
    await api.delete(`/admin/redeem-codes/${id}`)
    ElMessage.success('删除成功')
    await fetchList()
  } catch { /* handled */ }
}

// ── 批量作废 ──────────────────────────────────────────────────
const batchVoidLoading = ref(false)

async function batchVoid() {
  if (!hasSelection.value) return
  const label = selectAllMode.value ? `全部 ${total.value}` : `已选 ${selectedIds.value.size}`
  try {
    await ElMessageBox.confirm(
      `将对 ${label} 条兑换码中状态为「未使用」的码执行作废，已使用的码不受影响，是否继续？`,
      '批量作废确认',
      { type: 'warning', confirmButtonText: '确认作废', cancelButtonText: '取消' },
    )
  } catch { return }

  batchVoidLoading.value = true
  try {
    const payload: Record<string, unknown> = {}
    if (selectAllMode.value) {
      payload.select_all = true
      if (statusFilter.value) payload.status_filter = statusFilter.value
    } else {
      payload.ids = [...selectedIds.value]
    }
    const res = await api.put('/admin/redeem-codes/batch-void', payload)
    ElMessage.success(`已作废 ${res.data.voided} 条`)
    clearSelection()
    await fetchList()
  } catch { /* handled */ } finally { batchVoidLoading.value = false }
}

// ── 批量导出 ──────────────────────────────────────────────────
async function batchExport() {
  if (!hasSelection.value) return
  try {
    const params: Record<string, string> = {}
    if (selectAllMode.value) {
      params.select_all = 'true'
      if (statusFilter.value) params.status_filter = statusFilter.value
    } else {
      params.ids = [...selectedIds.value].join(',')
    }
    const qs = new URLSearchParams(params).toString()
    const res = await axios.get(`/api/admin/redeem-codes/export?${qs}`, {
      responseType: 'blob',
      headers: { Authorization: `Bearer ${localStorage.getItem('admin_token') ?? ''}` },
    })
    const url = URL.createObjectURL(res.data as Blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'redeem_codes.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('导出失败')
  }
}

onMounted(fetchList)
</script>

<template>
  <div>
    <!-- 工具栏 -->
    <div class="mb-3 flex items-center justify-between gap-3">
      <div class="flex items-center gap-3">
        <el-select
          v-model="statusFilter"
          placeholder="全部状态"
          clearable
          style="width: 130px"
          @change="onFilterChange"
        >
          <el-option label="未使用" value="unused" />
          <el-option label="已使用" value="used" />
          <el-option label="已过期" value="expired" />
        </el-select>
        <span class="text-sm text-gray-400">共 {{ total }} 条</span>
      </div>
      <el-button type="primary" @click="genDialog = true; generatedCodes = []">生成兑换码</el-button>
    </div>

    <!-- 批量操作栏（始终可见，无选中时置灰） -->
    <div
      class="mb-3 flex items-center gap-3 rounded-lg border px-4 py-2.5 transition-colors duration-150"
      :class="hasSelection ? 'border-blue-200 bg-blue-50' : 'border-gray-100 bg-gray-50'"
    >
      <span
        class="min-w-[110px] text-sm font-medium"
        :class="hasSelection ? 'text-blue-700' : 'text-gray-400'"
      >
        <template v-if="selectAllMode">已选全部 {{ total }} 条</template>
        <template v-else-if="selectedIds.size > 0">已选 {{ selectedCount }} 条</template>
        <template v-else>未选中任何数据</template>
      </span>
      <el-button
        size="small"
        type="warning"
        :disabled="!hasSelection"
        :loading="batchVoidLoading"
        @click="batchVoid"
      >
        批量作废
      </el-button>
      <el-button size="small" type="success" :disabled="!hasSelection" @click="batchExport">
        批量导出
      </el-button>
      <el-button v-if="hasSelection" size="small" text @click="clearSelection">清除选择</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe class="rounded-lg">
      <!-- 自定义选择列，实现两次点击全选逻辑 -->
      <el-table-column width="50" align="center">
        <template #header>
          <el-checkbox
            :model-value="headerChecked"
            :indeterminate="headerIndeterminate"
            @change="onHeaderCheckboxChange"
          />
        </template>
        <template #default="{ row }">
          <el-checkbox
            :model-value="isRowSelected(row)"
            @change="(val: unknown) => onRowCheckboxChange(row, val)"
          />
        </template>
      </el-table-column>

      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="code" label="兑换码" width="200" />
      <el-table-column prop="type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="row.type === 'days' ? '' : 'success'" size="small">
            {{ row.type === 'days' ? '天数' : '次数' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="value" label="值" width="70" />
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag
            :type="row.status === 'unused' ? 'success' : row.status === 'used' ? 'info' : 'danger'"
            size="small"
          >
            {{ row.status === 'unused' ? '未使用' : row.status === 'used' ? '已使用' : '已过期' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="使用者" width="80">
        <template #default="{ row }">{{ row.used_by || '-' }}</template>
      </el-table-column>
      <el-table-column label="使用时间" width="170">
        <template #default="{ row }">{{ row.used_at || '-' }}</template>
      </el-table-column>
      <el-table-column label="过期时间" width="170">
        <template #default="{ row }">{{ row.expire_at || '-' }}</template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > PAGE_SIZE">
      <el-pagination
        v-model:current-page="page"
        :page-size="PAGE_SIZE"
        :total="total"
        layout="prev, pager, next"
        background
        @current-change="fetchList"
      />
    </div>

    <!-- 生成兑换码 -->
    <el-dialog v-model="genDialog" title="生成兑换码" width="480px">
      <el-form label-width="80px">
        <el-form-item label="类型">
          <el-select v-model="genForm.type" class="w-full">
            <el-option label="天数" value="days" />
            <el-option label="次数" value="chats" />
          </el-select>
        </el-form-item>
        <el-form-item label="值">
          <el-input-number v-model="genForm.value" :min="1" />
        </el-form-item>
        <el-form-item label="数量">
          <el-input-number v-model="genForm.count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-input v-model="genForm.expire_at" placeholder="留空则不过期，格式 YYYY-MM-DD" />
        </el-form-item>
      </el-form>
      <div v-if="generatedCodes.length" class="mt-4 rounded-lg bg-gray-50 p-3">
        <div class="mb-2 flex items-center justify-between">
          <span class="text-sm font-semibold text-gray-600">已生成：</span>
          <el-button size="small" text type="primary" @click="copyAll">复制全部</el-button>
        </div>
        <div class="max-h-40 space-y-1 overflow-y-auto font-mono text-xs text-gray-700">
          <div v-for="c in generatedCodes" :key="c">{{ c }}</div>
        </div>
      </div>
      <template #footer>
        <el-button @click="genDialog = false">关闭</el-button>
        <el-button type="primary" @click="generate">生成</el-button>
      </template>
    </el-dialog>
  </div>
</template>
