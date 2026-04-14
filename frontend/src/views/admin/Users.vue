<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const loading = ref(false)
const list = ref<Record<string, unknown>[]>([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: 20 }
    if (keyword.value) params.keyword = keyword.value
    const res = await api.get('/admin/users', { params })
    list.value = res.data.list
    total.value = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

async function toggleBan(row: Record<string, unknown>) {
  const newStatus = row.status === 'banned' ? 'active' : 'banned'
  const label = newStatus === 'banned' ? '封禁' : '解封'
  try {
    await ElMessageBox.confirm(`确定${label}该用户？`, '提示', { type: 'warning' })
    await api.put(`/admin/users/${row.id}/status`, { status: newStatus })
    ElMessage.success(`${label}成功`)
    await fetchList()
  } catch { /* cancel */ }
}

// 修改订阅弹窗
const dialogVisible = ref(false)
const editUser = ref<Record<string, unknown>>({})
const subForm = ref({ subscribe_plan: 'free', subscribe_expire: '', free_chats_left: 0 })

function openSubscribe(row: Record<string, unknown>) {
  editUser.value = row
  subForm.value = {
    subscribe_plan: String(row.subscribe_plan || 'free'),
    subscribe_expire: String(row.subscribe_expire || ''),
    free_chats_left: Number(row.free_chats_left || 0),
  }
  dialogVisible.value = true
}

async function saveSubscribe() {
  try {
    await api.put(`/admin/users/${editUser.value.id}/subscribe`, subForm.value)
    ElMessage.success('更新成功')
    dialogVisible.value = false
    await fetchList()
  } catch { /* handled */ }
}

onMounted(fetchList)
</script>

<template>
  <div>
    <div class="flex items-center gap-3 mb-4">
      <el-input v-model="keyword" placeholder="搜索昵称/手机号/邮箱" clearable style="width: 280px" @keyup.enter="fetchList" @clear="fetchList" />
      <el-button type="primary" @click="fetchList">搜索</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe class="rounded-lg">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column prop="nickname" label="昵称" width="120" />
      <el-table-column prop="phone" label="手机号" width="130" />
      <el-table-column prop="email" label="邮箱" min-width="160" />
      <el-table-column prop="subscribe_plan" label="订阅" width="100">
        <template #default="{ row }">
          <el-tag :type="row.subscribe_plan === 'free' ? 'info' : 'success'" size="small">{{ row.subscribe_plan }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="free_chats_left" label="免费次数" width="90" />
      <el-table-column prop="status" label="状态" width="80">
        <template #default="{ row }">
          <el-tag :type="row.status === 'active' ? 'success' : 'danger'" size="small">{{ row.status === 'active' ? '正常' : '封禁' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="conversation_count" label="对话数" width="80" />
      <el-table-column prop="created_at" label="注册时间" width="170" />
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="openSubscribe(row)">订阅</el-button>
          <el-button size="small" text :type="row.status === 'banned' ? 'success' : 'danger'" @click="toggleBan(row)">
            {{ row.status === 'banned' ? '解封' : '封禁' }}
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > 20">
      <el-pagination v-model:current-page="page" :page-size="20" :total="total" layout="prev, pager, next" background @current-change="fetchList" />
    </div>

    <el-dialog v-model="dialogVisible" title="修改订阅" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="订阅计划">
          <el-select v-model="subForm.subscribe_plan" class="w-full">
            <el-option label="免费" value="free" />
            <el-option label="月度" value="monthly" />
            <el-option label="年度" value="yearly" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期时间">
          <el-input v-model="subForm.subscribe_expire" placeholder="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="免费次数">
          <el-input-number v-model="subForm.free_chats_left" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSubscribe">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
