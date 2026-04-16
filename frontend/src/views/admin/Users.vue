<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

const PAGE_SIZE = 20

interface UserRow {
  id: number
  nickname: string | null
  phone: string | null
  email: string | null
  remark: string | null
  free_chats_left: number
  subscribe_plan: 'free' | 'monthly' | 'yearly'
  subscribe_expire: string | null
  status: 'active' | 'banned'
  conversation_count: number
  message_count: number
  created_at: string | null
  deleted_at: string | null
}

const loading = ref(false)
const list = ref<UserRow[]>([])
const total = ref(0)
const page = ref(1)
const keyword = ref('')
const statusFilter = ref('')
const subscribePlanFilter = ref('')
const defaultFreeChats = ref(3)

const statusOptions = [
  { label: '正常', value: 'active' },
  { label: '封禁', value: 'banned' },
  { label: '已注销', value: 'deleted' },
]

const subscribePlanOptions = [
  { label: '免费', value: 'free' },
  { label: '月度', value: 'monthly' },
  { label: '年度', value: 'yearly' },
]

const trialModeOptions = [
  { label: '直接设置', value: 'set' },
  { label: '增加次数', value: 'increase' },
  { label: '扣减次数', value: 'decrease' },
  { label: '恢复默认值', value: 'reset_default' },
]

function normalizeDateTime(value: unknown) {
  const raw = String(value ?? '').trim()
  if (!raw) return ''
  return raw
    .replace('T', ' ')
    .replace(/\.\d+/, '')
    .replace(/Z$/, '')
    .replace(/[+-]\d{2}:\d{2}$/, '')
}

function normalizeText(value: unknown) {
  return String(value ?? '').trim()
}

function formatDateTime(value: unknown) {
  return normalizeDateTime(value) || '-'
}

function formatPlanLabel(plan: UserRow['subscribe_plan']) {
  if (plan === 'monthly') return '月度'
  if (plan === 'yearly') return '年度'
  return '免费'
}

function planTagType(plan: UserRow['subscribe_plan']) {
  return plan === 'free' ? 'info' : 'success'
}

function statusLabel(row: UserRow) {
  if (row.deleted_at) return '已注销'
  return row.status === 'active' ? '正常' : '封禁'
}

function statusTagType(row: UserRow) {
  if (row.deleted_at) return 'info'
  return row.status === 'active' ? 'success' : 'danger'
}

async function fetchDefaultFreeChats() {
  try {
    const res = await api.get('/admin/register/config')
    const row = res.data.list.find((item: Record<string, unknown>) => item.config_key === 'default_free_chats')
    const parsed = Number(row?.config_value ?? 3)
    defaultFreeChats.value = Number.isFinite(parsed) ? parsed : 3
  } catch { /* handled */ }
}

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: PAGE_SIZE }
    if (keyword.value) params.keyword = keyword.value
    if (statusFilter.value) params.status = statusFilter.value
    if (subscribePlanFilter.value) params.subscribe_plan = subscribePlanFilter.value
    const res = await api.get('/admin/users', { params })
    list.value = res.data.list
    total.value = res.data.total
  } catch { /* handled */ } finally { loading.value = false }
}

async function onSearch() {
  page.value = 1
  await fetchList()
}

async function onReset() {
  keyword.value = ''
  statusFilter.value = ''
  subscribePlanFilter.value = ''
  page.value = 1
  await fetchList()
}

async function toggleBan(row: UserRow) {
  if (row.deleted_at) return
  const newStatus = row.status === 'banned' ? 'active' : 'banned'
  const label = newStatus === 'banned' ? '封禁' : '解封'
  try {
    await ElMessageBox.confirm(`确定${label}该用户？`, '提示', { type: 'warning' })
    await api.put(`/admin/users/${row.id}/status`, { status: newStatus })
    ElMessage.success(`${label}成功`)
    await fetchList()
  } catch { /* cancel */ }
}

async function softDeleteUser(row: UserRow) {
  if (row.deleted_at) return
  try {
    await ElMessageBox.confirm('注销后会保留历史数据，但账号将无法登录，且手机号/邮箱将被释放，是否继续？', '提示', { type: 'warning' })
    await api.delete(`/admin/users/${row.id}`)
    ElMessage.success('用户已注销')
    await fetchList()
  } catch { /* cancel */ }
}

const createDialogVisible = ref(false)
const createForm = ref({
  nickname: '',
  phone: '',
  email: '',
  password: '',
  remark: '',
  subscribe_plan: 'free',
  subscribe_expire: '',
  free_chats_left: defaultFreeChats.value,
})

function resetCreateForm() {
  createForm.value = {
    nickname: '',
    phone: '',
    email: '',
    password: '',
    remark: '',
    subscribe_plan: 'free',
    subscribe_expire: '',
    free_chats_left: defaultFreeChats.value,
  }
}

function openCreateDialog() {
  resetCreateForm()
  createDialogVisible.value = true
}

async function saveCreateUser() {
  try {
    await api.post('/admin/users', {
      nickname: normalizeText(createForm.value.nickname),
      phone: normalizeText(createForm.value.phone),
      email: normalizeText(createForm.value.email),
      password: createForm.value.password,
      remark: normalizeText(createForm.value.remark),
      subscribe_plan: createForm.value.subscribe_plan,
      subscribe_expire: normalizeDateTime(createForm.value.subscribe_expire),
      free_chats_left: Number(createForm.value.free_chats_left || 0),
    })
    ElMessage.success('创建成功')
    createDialogVisible.value = false
    page.value = 1
    await fetchList()
  } catch { /* handled */ }
}

const editDialogVisible = ref(false)
const editForm = ref({ id: 0, nickname: '', phone: '', email: '', remark: '' })

function openEditDialog(row: UserRow) {
  editForm.value = {
    id: row.id,
    nickname: row.nickname || '',
    phone: row.phone || '',
    email: row.email || '',
    remark: row.remark || '',
  }
  editDialogVisible.value = true
}

async function saveEditUser() {
  try {
    await api.put(`/admin/users/${editForm.value.id}`, {
      nickname: normalizeText(editForm.value.nickname),
      phone: normalizeText(editForm.value.phone),
      email: normalizeText(editForm.value.email),
      remark: normalizeText(editForm.value.remark),
    })
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    await fetchList()
  } catch { /* handled */ }
}

// 修改订阅弹窗
const memberDialogVisible = ref(false)
const memberUserId = ref<number | null>(null)
const memberForm = ref({ subscribe_plan: 'free', subscribe_expire: '' })

function openSubscribe(row: UserRow) {
  memberUserId.value = row.id
  memberForm.value = {
    subscribe_plan: row.subscribe_plan,
    subscribe_expire: normalizeDateTime(row.subscribe_expire),
  }
  memberDialogVisible.value = true
}

async function saveSubscribe() {
  if (!memberUserId.value) return
  try {
    await api.put(`/admin/users/${memberUserId.value}/subscribe`, {
      subscribe_plan: memberForm.value.subscribe_plan,
      subscribe_expire: normalizeDateTime(memberForm.value.subscribe_expire),
    })
    ElMessage.success('会员信息已更新')
    memberDialogVisible.value = false
    await fetchList()
  } catch { /* handled */ }
}

const trialDialogVisible = ref(false)
const trialUser = ref<UserRow | null>(null)
const trialForm = ref({ mode: 'set', value: 0 })

function openTrialDialog(row: UserRow) {
  trialUser.value = row
  trialForm.value = { mode: 'set', value: Number(row.free_chats_left || 0) }
  trialDialogVisible.value = true
}

async function saveTrial() {
  if (!trialUser.value) return
  const payload: Record<string, unknown> = { mode: trialForm.value.mode }
  if (trialForm.value.mode !== 'reset_default') {
    payload.value = Number(trialForm.value.value || 0)
  }
  try {
    const res = await api.put(`/admin/users/${trialUser.value.id}/trial`, payload)
    if (res.data?.default_free_chats != null) {
      defaultFreeChats.value = Number(res.data.default_free_chats || defaultFreeChats.value)
    }
    ElMessage.success('试用次数已更新')
    trialDialogVisible.value = false
    await fetchList()
  } catch { /* handled */ }
}

onMounted(async () => {
  await fetchDefaultFreeChats()
  await fetchList()
})
</script>

<template>
  <div>
    <div class="mb-4 flex flex-wrap items-center gap-3">
      <el-input v-model="keyword" placeholder="搜索昵称/手机号/邮箱/备注" clearable style="width: 280px" @keyup.enter="onSearch" />
      <el-select v-model="statusFilter" placeholder="全部状态" clearable style="width: 130px">
        <el-option v-for="item in statusOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-select v-model="subscribePlanFilter" placeholder="全部订阅" clearable style="width: 130px">
        <el-option v-for="item in subscribePlanOptions" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <el-button type="primary" @click="onSearch">搜索</el-button>
      <el-button @click="onReset">重置</el-button>
      <el-button type="success" @click="openCreateDialog">新增用户</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe class="rounded-lg">
      <el-table-column prop="id" label="ID" width="72" />
      <el-table-column label="昵称" width="130">
        <template #default="{ row }">
          {{ row.nickname || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="手机号" width="138">
        <template #default="{ row }">
          {{ row.phone || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="邮箱" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.email || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="备注" min-width="180" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.remark || '-' }}
        </template>
      </el-table-column>
      <el-table-column label="会员" width="110">
        <template #default="{ row }">
          <el-tag :type="planTagType(row.subscribe_plan)" size="small">{{ formatPlanLabel(row.subscribe_plan) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="free_chats_left" label="试用次数" width="96" />
      <el-table-column label="状态" width="92">
        <template #default="{ row }">
          <el-tag :type="statusTagType(row)" size="small">{{ statusLabel(row) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="conversation_count" label="对话数" width="86" />
      <el-table-column prop="message_count" label="消息数" width="86" />
      <el-table-column label="注册时间" width="180">
        <template #default="{ row }">
          {{ formatDateTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="320" fixed="right">
        <template #default="{ row }">
          <div v-if="!row.deleted_at" class="flex flex-wrap gap-1">
            <el-button size="small" text type="primary" @click="openEditDialog(row)">编辑</el-button>
            <el-button size="small" text type="primary" @click="openSubscribe(row)">会员</el-button>
            <el-button size="small" text type="primary" @click="openTrialDialog(row)">试用</el-button>
            <el-button size="small" text :type="row.status === 'banned' ? 'success' : 'warning'" @click="toggleBan(row)">
              {{ row.status === 'banned' ? '解封' : '封禁' }}
            </el-button>
            <el-button size="small" text type="danger" @click="softDeleteUser(row)">注销</el-button>
          </div>
          <span v-else class="text-xs text-gray-400">已注销</span>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > PAGE_SIZE">
      <el-pagination v-model:current-page="page" :page-size="PAGE_SIZE" :total="total" layout="prev, pager, next" background @current-change="fetchList" />
    </div>

    <el-dialog v-model="createDialogVisible" title="新增用户" width="520px" destroy-on-close>
      <el-form label-width="92px">
        <el-form-item label="昵称">
          <el-input v-model="createForm.nickname" placeholder="可选，不填会自动生成" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="createForm.phone" placeholder="手机号与邮箱至少填写一个" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="createForm.email" placeholder="手机号与邮箱至少填写一个" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="createForm.password" type="password" show-password placeholder="至少 6 位" />
        </el-form-item>
        <el-form-item label="会员计划">
          <el-select v-model="createForm.subscribe_plan" class="w-full">
            <el-option v-for="item in subscribePlanOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期时间">
          <el-date-picker v-model="createForm.subscribe_expire" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" format="YYYY-MM-DD HH:mm:ss" placeholder="免费用户可留空" class="w-full" clearable />
        </el-form-item>
        <el-form-item label="试用次数">
          <el-input-number v-model="createForm.free_chats_left" :min="0" class="w-full" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="createForm.remark" type="textarea" :rows="3" maxlength="200" show-word-limit placeholder="可选备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCreateUser">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="editDialogVisible" title="编辑用户" width="520px" destroy-on-close>
      <el-form label-width="92px">
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickname" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="editForm.remark" type="textarea" :rows="3" maxlength="200" show-word-limit />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEditUser">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="memberDialogVisible" title="会员管理" width="450px" destroy-on-close>
      <el-form label-width="92px">
        <el-form-item label="会员计划">
          <el-select v-model="memberForm.subscribe_plan" class="w-full">
            <el-option v-for="item in subscribePlanOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="到期时间">
          <el-date-picker v-model="memberForm.subscribe_expire" type="datetime" value-format="YYYY-MM-DD HH:mm:ss" format="YYYY-MM-DD HH:mm:ss" placeholder="免费用户可留空" class="w-full" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="memberDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveSubscribe">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="trialDialogVisible" title="试用控制" width="450px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="当前剩余">
          <div>{{ trialUser?.free_chats_left ?? 0 }} 次</div>
        </el-form-item>
        <el-form-item label="默认值">
          <div>{{ defaultFreeChats }} 次</div>
        </el-form-item>
        <el-form-item label="操作方式">
          <el-select v-model="trialForm.mode" class="w-full">
            <el-option v-for="item in trialModeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="trialForm.mode !== 'reset_default'" label="次数">
          <el-input-number v-model="trialForm.value" :min="0" class="w-full" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="trialDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveTrial">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
