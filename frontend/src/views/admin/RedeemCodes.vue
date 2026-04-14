<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const list = ref<Record<string, unknown>[]>([])
const total = ref(0)
const page = ref(1)

const genDialog = ref(false)
const genForm = ref({ type: 'days', value: 30, count: 10, expire_at: '' })
const generatedCodes = ref<string[]>([])

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/redeem-codes', { params: { page: page.value, page_size: 20 } })
    list.value = res.data.list
    total.value = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

async function generate() {
  try {
    const data: Record<string, unknown> = { type: genForm.value.type, value: genForm.value.value, count: genForm.value.count }
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

async function handleDelete(id: number) {
  try {
    await api.delete(`/admin/redeem-codes/${id}`)
    ElMessage.success('删除成功')
    await fetchList()
  } catch { /* handled */ }
}

onMounted(fetchList)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <span class="text-sm text-gray-500">共 {{ total }} 条</span>
      <el-button type="primary" @click="genDialog = true; generatedCodes = []">生成兑换码</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe class="rounded-lg">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="code" label="兑换码" width="200" />
      <el-table-column prop="type" label="类型" width="80">
        <template #default="{ row }">
          <el-tag :type="row.type === 'days' ? '' : 'success'" size="small">{{ row.type === 'days' ? '天数' : '次数' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="value" label="值" width="70" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'unused' ? 'success' : row.status === 'used' ? 'info' : 'danger'" size="small">
            {{ row.status === 'unused' ? '未使用' : row.status === 'used' ? '已使用' : '已过期' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="used_by" label="使用者" width="80" />
      <el-table-column prop="used_at" label="使用时间" width="170" />
      <el-table-column prop="expire_at" label="过期时间" width="170" />
      <el-table-column prop="created_at" label="创建时间" width="170" />
      <el-table-column label="操作" width="80" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > 20">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchList" />
    </div>

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
      <div v-if="generatedCodes.length" class="mt-4 p-3 bg-gray-50 rounded-lg">
        <div class="flex items-center justify-between mb-2">
          <span class="text-sm font-semibold text-gray-600">已生成：</span>
          <el-button size="small" text type="primary" @click="copyAll">复制全部</el-button>
        </div>
        <div class="text-xs text-gray-700 font-mono space-y-1 max-h-40 overflow-y-auto">
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
