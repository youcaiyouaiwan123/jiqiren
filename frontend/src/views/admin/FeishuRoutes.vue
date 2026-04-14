<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface FeishuRoute {
  id: number
  name: string
  app_id: string
  app_token: string
  table_id: string
  is_active: number
  created_at?: string | null
  updated_at?: string | null
}

interface TestCandidate {
  name: string
  table_id: string
}

interface TestResult {
  ok: boolean
  message: string
  detail: string
  stage?: string
  app_token?: string
  table_id?: string
  table_name?: string
  table_count?: number
  raw_detail?: string
  candidates?: TestCandidate[]
  routeName?: string
}

interface ApiTestResponse {
  message?: string
  data?: Record<string, unknown>
}

const list = ref<FeishuRoute[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const testingId = ref<number | null>(null)
const pageTestResult = ref<TestResult | null>(null)

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const saving = ref(false)
const dialogTesting = ref(false)
const dialogTestResult = ref<TestResult | null>(null)
const form = ref(createEmptyForm())

function createEmptyForm() {
  return {
    name: '',
    app_id: '',
    app_secret: '',
    bitable_url: '',
    app_token: '',
    table_id: '',
    is_active: 1,
  }
}

function formatDateTime(value?: string | null) {
  return value ? value.replace('T', ' ').slice(0, 19) : '--'
}

function normalizeTestResult(ok: boolean, message: string, data: Record<string, unknown> | undefined, routeName?: string): TestResult {
  const candidates = Array.isArray(data?.candidates)
    ? data.candidates.map((item) => ({
        name: String((item as Record<string, unknown>).name || ''),
        table_id: String((item as Record<string, unknown>).table_id || ''),
      }))
    : []

  return {
    ok,
    message,
    detail: String(data?.detail || message),
    stage: data?.stage ? String(data.stage) : '',
    app_token: data?.app_token ? String(data.app_token) : '',
    table_id: data?.table_id ? String(data.table_id) : '',
    table_name: data?.table_name ? String(data.table_name) : '',
    table_count: typeof data?.table_count === 'number' ? Number(data.table_count) : undefined,
    raw_detail: data?.raw_detail ? String(data.raw_detail) : '',
    candidates,
    routeName,
  }
}

function extractApiError(err: unknown, routeName?: string): TestResult {
  if (err && typeof err === 'object') {
    const errorObj = err as { message?: unknown; data?: unknown }
    const data = errorObj.data && typeof errorObj.data === 'object'
      ? errorObj.data as Record<string, unknown>
      : undefined
    return normalizeTestResult(false, String(errorObj.message || '连接失败'), data, routeName)
  }
  return normalizeTestResult(false, '连接失败', undefined, routeName)
}

function buildPayload(includeRouteId = false) {
  const payload: Record<string, unknown> = {
    name: form.value.name.trim(),
    app_id: form.value.app_id.trim(),
    is_active: form.value.is_active,
  }
  if (form.value.app_secret.trim()) payload.app_secret = form.value.app_secret.trim()
  if (form.value.bitable_url.trim()) payload.bitable_url = form.value.bitable_url.trim()
  if (form.value.app_token.trim()) payload.app_token = form.value.app_token.trim()
  if (form.value.table_id.trim()) payload.table_id = form.value.table_id.trim()
  if (includeRouteId && editId.value) payload.route_id = editId.value
  return payload
}

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/feishu/routes', { params: { page: page.value, page_size: pageSize.value } })
    list.value = res.data.list ?? []
    total.value = res.data.total ?? list.value.length
  } catch { /* handled */ }
  loading.value = false
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = createEmptyForm()
  dialogTestResult.value = null
  dialogVisible.value = true
}

function openEdit(row: FeishuRoute) {
  isEdit.value = true
  editId.value = row.id
  form.value = {
    name: row.name,
    app_id: row.app_id,
    app_secret: '',
    bitable_url: '',
    app_token: row.app_token,
    table_id: row.table_id,
    is_active: row.is_active,
  }
  dialogTestResult.value = null
  dialogVisible.value = true
}

async function handleSubmit() {
  saving.value = true
  try {
    const payload = buildPayload(false)
    if (isEdit.value && editId.value) {
      await api.put(`/admin/feishu/routes/${editId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/feishu/routes', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    dialogTestResult.value = null
    await fetchList()
  } catch { /* handled */ }
  saving.value = false
}

async function testCurrentForm() {
  dialogTesting.value = true
  try {
    const res = await api.post('/admin/feishu/routes/test', buildPayload(true)) as ApiTestResponse
    dialogTestResult.value = normalizeTestResult(true, res.message || '连接成功', res.data)
    ElMessage.success('测试通过')
  } catch (err: unknown) {
    dialogTestResult.value = extractApiError(err)
  }
  dialogTesting.value = false
}

async function testSavedRoute(row: FeishuRoute) {
  testingId.value = row.id
  try {
    const res = await api.post(`/admin/feishu/routes/${row.id}/test`) as ApiTestResponse
    pageTestResult.value = normalizeTestResult(true, res.message || '连接成功', res.data, row.name)
    ElMessage.success(`「${row.name}」测试通过`)
  } catch (err: unknown) {
    pageTestResult.value = extractApiError(err, row.name)
  }
  testingId.value = null
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该飞书路由？', '提示', { type: 'warning' })
    await api.delete(`/admin/feishu/routes/${id}`)
    ElMessage.success('删除成功')
    await fetchList()
  } catch { /* cancel */ }
}

watch(page, fetchList)
onMounted(fetchList)
</script>

<template>
  <div class="space-y-6">
    <div class="rounded-[28px] border border-slate-200 bg-white/95 px-6 py-6 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.35)]">
      <div class="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div class="max-w-3xl">
          <div class="text-lg font-semibold text-slate-900">飞书多维表连接配置</div>
          <div class="mt-2 text-sm leading-6 text-slate-500">支持直接粘贴完整多维表链接，系统会自动解析 App Token 与 Table ID。测试连接采用只读校验，不会写入测试数据。</div>
        </div>
        <el-button type="primary" size="large" @click="openCreate">新增路由</el-button>
      </div>
      <div class="mt-5 grid gap-3 sm:grid-cols-3">
        <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-4">
          <div class="text-xs font-medium uppercase tracking-wide text-slate-500">应用凭证</div>
          <div class="mt-2 text-sm text-slate-700">仅需填写开放平台里的 `App ID` 与 `App Secret`。</div>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-4">
          <div class="text-xs font-medium uppercase tracking-wide text-slate-500">多维表链接</div>
          <div class="mt-2 text-sm text-slate-700">推荐直接粘贴完整多维表地址，系统会自动解析后两个参数。</div>
        </div>
        <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-4">
          <div class="text-xs font-medium uppercase tracking-wide text-slate-500">连接测试</div>
          <div class="mt-2 text-sm text-slate-700">一键判断是 `App Token`、`Table ID` 还是权限有问题。</div>
        </div>
      </div>
    </div>

    <div
      v-if="pageTestResult"
      class="rounded-[24px] px-6 py-5 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.28)]"
      :class="pageTestResult.ok ? 'border border-emerald-200 bg-emerald-50' : 'border border-rose-200 bg-rose-50'"
    >
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div class="text-sm font-semibold" :class="pageTestResult.ok ? 'text-emerald-800' : 'text-rose-800'">
            {{ pageTestResult.routeName ? `最近一次测试：${pageTestResult.routeName}` : '最近一次测试结果' }}
          </div>
          <div class="mt-1 text-sm" :class="pageTestResult.ok ? 'text-emerald-700' : 'text-rose-700'">{{ pageTestResult.detail }}</div>
        </div>
        <el-tag :type="pageTestResult.ok ? 'success' : 'danger'" size="large">{{ pageTestResult.ok ? '连接成功' : '连接失败' }}</el-tag>
      </div>
      <div class="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
          <div class="text-xs text-slate-500">App Token</div>
          <div class="mt-1 break-all text-sm font-medium text-slate-800">{{ pageTestResult.app_token || '--' }}</div>
        </div>
        <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
          <div class="text-xs text-slate-500">Table ID</div>
          <div class="mt-1 break-all text-sm font-medium text-slate-800">{{ pageTestResult.table_id || '--' }}</div>
        </div>
        <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
          <div class="text-xs text-slate-500">表名称</div>
          <div class="mt-1 break-all text-sm font-medium text-slate-800">{{ pageTestResult.table_name || '--' }}</div>
        </div>
        <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
          <div class="text-xs text-slate-500">可见表数量</div>
          <div class="mt-1 text-sm font-medium text-slate-800">{{ pageTestResult.table_count ?? '--' }}</div>
        </div>
      </div>
      <div v-if="pageTestResult.raw_detail" class="mt-4 rounded-2xl border border-white/60 bg-white/70 px-4 py-3 text-xs leading-6 text-slate-600">
        {{ pageTestResult.raw_detail }}
      </div>
      <div v-if="pageTestResult.candidates?.length" class="mt-4 rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
        <div class="text-xs font-medium text-slate-500">当前 Base 下已识别到的表</div>
        <div class="mt-2 grid gap-2 sm:grid-cols-2">
          <div v-for="item in pageTestResult.candidates" :key="item.table_id" class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
            <div class="text-sm font-medium text-slate-800">{{ item.name || '未命名表' }}</div>
            <div class="mt-1 break-all text-xs text-slate-500">{{ item.table_id }}</div>
          </div>
        </div>
      </div>
    </div>

    <div class="rounded-[28px] border border-slate-200 bg-white/95 px-6 py-5 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.35)]">
      <div class="mb-4 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <div class="text-sm text-slate-500">共 {{ total }} 条飞书路由，系统默认使用启用状态的首条对话记录路由。</div>
        <div class="text-xs text-slate-400">行内可直接测试，不需要先去发用户对话。</div>
      </div>

      <el-table :data="list" v-loading="loading" border stripe class="rounded-lg" style="width: 100%">
        <el-table-column prop="id" label="ID" width="70" />
        <el-table-column prop="name" label="名称" min-width="120" show-overflow-tooltip />
        <el-table-column prop="app_id" label="App ID" min-width="180" show-overflow-tooltip />
        <el-table-column prop="app_token" label="App Token" min-width="200" show-overflow-tooltip />
        <el-table-column prop="table_id" label="Table ID" min-width="180" show-overflow-tooltip />
        <el-table-column prop="is_active" label="启用" width="90">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="updated_at" label="更新时间" width="170">
          <template #default="{ row }">{{ formatDateTime(row.updated_at) }}</template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" text type="success" :loading="testingId === row.id" @click="testSavedRoute(row)">测试连接</el-button>
            <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <div v-if="total > pageSize" class="mt-4 flex justify-end">
        <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" background />
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑飞书路由' : '新增飞书路由'" width="760px" destroy-on-close>
      <el-form label-width="110px">
        <div class="grid grid-cols-1 gap-x-4 sm:grid-cols-2">
          <el-form-item label="名称" required class="sm:col-span-2">
            <el-input v-model="form.name" placeholder="例如：对话记录表" />
          </el-form-item>
          <el-form-item label="App ID" required>
            <el-input v-model="form.app_id" placeholder="开放平台中的 App ID" />
          </el-form-item>
          <el-form-item :label="isEdit ? 'App Secret（留空沿用）' : 'App Secret'" :required="!isEdit">
            <el-input v-model="form.app_secret" type="password" show-password placeholder="编辑时留空则沿用已保存密钥" />
          </el-form-item>
          <el-form-item label="多维表链接" class="sm:col-span-2">
            <div class="w-full space-y-2">
              <el-input v-model="form.bitable_url" type="textarea" :rows="3" placeholder="直接粘贴完整多维表链接，系统会自动解析 App Token 与 Table ID" />
              <div class="text-xs leading-6 text-slate-500">推荐直接填写完整链接；如果手头已经有分开的参数，也可以继续手填下面两个字段。</div>
            </div>
          </el-form-item>
          <el-form-item label="App Token">
            <el-input v-model="form.app_token" placeholder="可手填，也可由链接自动解析" />
          </el-form-item>
          <el-form-item label="Table ID">
            <el-input v-model="form.table_id" placeholder="可手填，也可由链接自动解析" />
          </el-form-item>
          <el-form-item label="启用状态" class="sm:col-span-2">
            <el-switch v-model="form.is_active" :active-value="1" :inactive-value="0" />
          </el-form-item>
        </div>
      </el-form>

      <div
        v-if="dialogTestResult"
        class="mt-2 rounded-[24px] px-5 py-4"
        :class="dialogTestResult.ok ? 'border border-emerald-200 bg-emerald-50' : 'border border-rose-200 bg-rose-50'"
      >
        <div class="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div class="text-sm font-semibold" :class="dialogTestResult.ok ? 'text-emerald-800' : 'text-rose-800'">{{ dialogTestResult.ok ? '当前填写可用' : '当前填写仍有问题' }}</div>
            <div class="mt-1 text-sm" :class="dialogTestResult.ok ? 'text-emerald-700' : 'text-rose-700'">{{ dialogTestResult.detail }}</div>
          </div>
          <el-tag :type="dialogTestResult.ok ? 'success' : 'danger'">{{ dialogTestResult.ok ? '已通过' : '待修正' }}</el-tag>
        </div>
        <div class="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
          <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
            <div class="text-xs text-slate-500">App Token</div>
            <div class="mt-1 break-all text-sm font-medium text-slate-800">{{ dialogTestResult.app_token || '--' }}</div>
          </div>
          <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
            <div class="text-xs text-slate-500">Table ID</div>
            <div class="mt-1 break-all text-sm font-medium text-slate-800">{{ dialogTestResult.table_id || '--' }}</div>
          </div>
          <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
            <div class="text-xs text-slate-500">表名称</div>
            <div class="mt-1 break-all text-sm font-medium text-slate-800">{{ dialogTestResult.table_name || '--' }}</div>
          </div>
          <div class="rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
            <div class="text-xs text-slate-500">可见表数量</div>
            <div class="mt-1 text-sm font-medium text-slate-800">{{ dialogTestResult.table_count ?? '--' }}</div>
          </div>
        </div>
        <div v-if="dialogTestResult.raw_detail" class="mt-4 rounded-2xl border border-white/60 bg-white/70 px-4 py-3 text-xs leading-6 text-slate-600">
          {{ dialogTestResult.raw_detail }}
        </div>
        <div v-if="dialogTestResult.candidates?.length" class="mt-4 rounded-2xl border border-white/60 bg-white/70 px-4 py-3">
          <div class="text-xs font-medium text-slate-500">当前 Base 下已识别到的表</div>
          <div class="mt-2 grid gap-2 sm:grid-cols-2">
            <div v-for="item in dialogTestResult.candidates" :key="item.table_id" class="rounded-xl border border-slate-200 bg-slate-50 px-3 py-2">
              <div class="text-sm font-medium text-slate-800">{{ item.name || '未命名表' }}</div>
              <div class="mt-1 break-all text-xs text-slate-500">{{ item.table_id }}</div>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button :loading="dialogTesting" @click="testCurrentForm">测试连接</el-button>
        <el-button type="primary" :loading="saving" @click="handleSubmit">{{ isEdit ? '保存修改' : '创建路由' }}</el-button>
      </template>
    </el-dialog>
  </div>
</template>
