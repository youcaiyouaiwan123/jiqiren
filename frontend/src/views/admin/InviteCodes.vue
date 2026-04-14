<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

interface InviteCodeRow {
  id: number
  code: string
  status: 'active' | 'used' | 'disabled' | 'expired'
  remark: string | null
  used_by: number | null
  used_at: string | null
  expire_at: string | null
  created_at: string | null
}

const loading = ref(false)
const list = ref<InviteCodeRow[]>([])
const total = ref(0)
const page = ref(1)

const genDialog = ref(false)
const genForm = ref({ count: 10, expire_at: '', remark: '' })
const generatedCodes = ref<string[]>([])

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/invite-codes', { params: { page: page.value, page_size: 20 } })
    list.value = res.data.list
    total.value = res.data.total
  } catch {
    /* handled */
  } finally {
    loading.value = false
  }
}

async function generate() {
  try {
    const data: Record<string, unknown> = { count: genForm.value.count }
    if (genForm.value.expire_at) data.expire_at = genForm.value.expire_at
    if (genForm.value.remark) data.remark = genForm.value.remark
    const res = await api.post('/admin/invite-codes/generate', data)
    generatedCodes.value = res.data.codes
    ElMessage.success(`已生成 ${res.data.count} 个邀请码`)
    await fetchList()
  } catch {
    /* handled */
  }
}

function copyAll() {
  navigator.clipboard.writeText(generatedCodes.value.join('\n'))
  ElMessage.success('已复制到剪贴板')
}

async function toggleStatus(row: InviteCodeRow) {
  const nextStatus = row.status === 'active' ? 'disabled' : 'active'
  try {
    await api.put(`/admin/invite-codes/${row.id}/status`, { status: nextStatus })
    ElMessage.success(nextStatus === 'disabled' ? '已禁用' : '已启用')
    await fetchList()
  } catch {
    /* handled */
  }
}

async function handleDelete(id: number) {
  try {
    await api.delete(`/admin/invite-codes/${id}`)
    ElMessage.success('删除成功')
    await fetchList()
  } catch {
    /* handled */
  }
}

function exportCsv() {
  const token = localStorage.getItem('admin_token')
  const url = `${api.defaults.baseURL || ''}/admin/invite-codes/export`
  fetch(url, { headers: { Authorization: `Bearer ${token}` } })
    .then(res => res.blob())
    .then(blob => {
      const link = document.createElement('a')
      link.href = URL.createObjectURL(blob)
      link.download = 'invite_codes.csv'
      link.click()
      URL.revokeObjectURL(link.href)
      ElMessage.success('导出成功')
    })
    .catch(() => ElMessage.error('导出失败'))
}

onMounted(fetchList)
</script>

<template>
  <div>
    <div class="mb-4 flex items-center justify-between">
      <span class="text-sm text-gray-500">共 {{ total }} 条</span>
      <div class="flex gap-2">
        <el-button @click="exportCsv">导出 CSV</el-button>
        <el-button type="primary" @click="genDialog = true; generatedCodes = []">生成邀请码</el-button>
      </div>
    </div>

    <el-table :data="list" v-loading="loading" border stripe class="rounded-lg">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="code" label="邀请码" width="200" />
      <el-table-column prop="remark" label="备注" min-width="120" show-overflow-tooltip />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : row.status === 'used' ? 'info' : row.status === 'disabled' ? 'warning' : 'danger'" size="small">
            {{ row.status === 'active' ? '可使用' : row.status === 'used' ? '已使用' : row.status === 'disabled' ? '已禁用' : '已过期' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="used_by" label="使用用户" width="100" />
      <el-table-column prop="used_at" label="使用时间" width="180" />
      <el-table-column prop="expire_at" label="过期时间" width="180" />
      <el-table-column prop="created_at" label="创建时间" width="180" />
      <el-table-column label="操作" width="150" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'active' || row.status === 'disabled'" size="small" text :type="row.status === 'active' ? 'warning' : 'success'" @click="toggleStatus(row)">
            {{ row.status === 'active' ? '禁用' : '启用' }}
          </el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > 20">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchList" />
    </div>

    <el-dialog v-model="genDialog" title="生成邀请码" width="520px">
      <el-form label-width="90px">
        <el-form-item label="数量">
          <el-input-number v-model="genForm.count" :min="1" :max="100" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="genForm.remark" placeholder="如：渠道来源、活动名称" maxlength="200" show-word-limit />
        </el-form-item>
        <el-form-item label="过期时间">
          <el-date-picker
            v-model="genForm.expire_at"
            type="datetime"
            value-format="YYYY-MM-DD HH:mm:ss"
            placeholder="留空则不过期"
            class="!w-full"
          />
        </el-form-item>
      </el-form>
      <div v-if="generatedCodes.length" class="mt-4 rounded-lg bg-gray-50 p-3">
        <div class="mb-2 flex items-center justify-between">
          <span class="text-sm font-semibold text-gray-600">已生成：</span>
          <el-button size="small" text type="primary" @click="copyAll">复制全部</el-button>
        </div>
        <div class="max-h-48 space-y-1 overflow-y-auto font-mono text-xs text-gray-700">
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
