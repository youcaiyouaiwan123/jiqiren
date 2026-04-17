<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface LlmRow {
  id: number
  name: string
  provider: string
  model: string
  api_url: string
  priority: number
  input_price: number | null
  output_price: number | null
  is_default: number
  is_active: number
}

const loading = ref(false)
const list = ref<LlmRow[]>([])
const total = ref(0)
const page = ref(1)
const PAGE_SIZE = 20

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const submitLoading = ref(false)

const providerOptions = [
  { label: 'Claude (Anthropic)', value: 'claude' },
  { label: 'OpenAI / GPT', value: 'openai' },
  { label: 'Gemini (Google)', value: 'gemini' },
  { label: '智谱 GLM', value: 'zhipu' },
]

const defaultForm = () => ({
  name: '',
  provider: 'claude',
  api_url: '',
  api_key: '',
  model: '',
  priority: 100,
  input_price: null as number | null,
  output_price: null as number | null,
  is_default: 0,
  is_active: 1,
})
const form = ref(defaultForm())

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/llm-providers', {
      params: { page: page.value, page_size: PAGE_SIZE },
    })
    list.value = res.data.list ?? []
    total.value = res.data.total ?? 0
  } catch { /* handled */ } finally { loading.value = false }
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = defaultForm()
  dialogVisible.value = true
}

function openEdit(row: LlmRow) {
  isEdit.value = true
  editId.value = row.id
  form.value = {
    name: row.name,
    provider: row.provider,
    api_url: row.api_url,
    api_key: '',
    model: row.model,
    priority: row.priority ?? 100,
    input_price: row.input_price,
    output_price: row.output_price,
    is_default: row.is_default,
    is_active: row.is_active,
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  submitLoading.value = true
  try {
    const payload: Record<string, unknown> = {
      name: form.value.name,
      provider: form.value.provider,
      api_url: form.value.api_url,
      model: form.value.model,
      priority: Number(form.value.priority),
      input_price: form.value.input_price,
      output_price: form.value.output_price,
      is_default: form.value.is_default,
      is_active: form.value.is_active,
    }
    if (form.value.api_key) payload.api_key = form.value.api_key
    if (isEdit.value && editId.value) {
      await api.put(`/admin/llm-providers/${editId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      if (!form.value.api_key) {
        ElMessage.warning('新建时 API Key 不能为空')
        return
      }
      payload.api_key = form.value.api_key
      await api.post('/admin/llm-providers', payload)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchList()
  } catch { /* handled */ } finally { submitLoading.value = false }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该配置？', '提示', { type: 'warning' })
    await api.delete(`/admin/llm-providers/${id}`)
    ElMessage.success('删除成功')
    await fetchList()
  } catch { /* cancel */ }
}

async function setDefault(row: LlmRow) {
  try {
    await api.put(`/admin/llm-providers/${row.id}/default`)
    ElMessage.success('已设为默认')
    await fetchList()
  } catch { /* handled */ }
}

function providerLabel(value: string) {
  return providerOptions.find(o => o.value === value)?.label ?? value
}

onMounted(fetchList)
</script>

<template>
  <div>
    <!-- 说明卡片 -->
    <div class="mb-5 rounded-lg border border-blue-100 bg-blue-50 px-5 py-4 text-sm text-blue-700 leading-relaxed">
      <div class="font-medium mb-1">多 Key 高可用配置说明</div>
      <ul class="list-disc list-inside space-y-0.5 text-blue-600">
        <li>每行代表一个 API Key，相同厂商可添加多行（主 Key + 备用 Key）</li>
        <li><b>优先级</b>数字越小越先被调用；主 Key 建议设 1，备用 Key 设 2、3…</li>
        <li>主 Key 出现首包超时（默认 30s）或返回 4xx/5xx 错误时，自动切换到下一个 Key</li>
        <li>超时阈值可在「AI 配置」→ <code>stream_timeout</code> 中调整</li>
      </ul>
    </div>

    <!-- 工具栏 -->
    <div class="mb-4 flex justify-end">
      <el-button type="primary" @click="openCreate">添加模型</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="list" v-loading="loading" border stripe class="rounded-lg">
      <el-table-column prop="id" label="ID" width="64" />
      <el-table-column prop="name" label="名称" width="130" show-overflow-tooltip />
      <el-table-column label="厂商" width="130">
        <template #default="{ row }">{{ providerLabel(row.provider) }}</template>
      </el-table-column>
      <el-table-column prop="model" label="模型" width="200" show-overflow-tooltip />
      <el-table-column prop="api_url" label="API 地址" min-width="180" show-overflow-tooltip />
      <el-table-column prop="priority" label="优先级" width="90" align="center">
        <template #default="{ row }">
          <el-tag size="small" :type="row.priority <= 10 ? 'danger' : row.priority <= 50 ? 'warning' : 'info'">
            {{ row.priority }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="输入价格" width="100" align="right">
        <template #default="{ row }">{{ row.input_price ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="输出价格" width="100" align="right">
        <template #default="{ row }">{{ row.output_price ?? '-' }}</template>
      </el-table-column>
      <el-table-column label="默认" width="72" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_default ? 'success' : 'info'" size="small">{{ row.is_default ? '是' : '-' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="72" align="center">
        <template #default="{ row }">
          <el-tag :type="row.is_active ? 'success' : 'info'" size="small">{{ row.is_active ? '启用' : '禁用' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button v-if="!row.is_default && row.is_active" size="small" text type="success" @click="setDefault(row)">设默认</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > PAGE_SIZE">
      <el-pagination v-model:current-page="page" :page-size="PAGE_SIZE" :total="total" layout="prev, pager, next" background @current-change="fetchList" />
    </div>

    <!-- 新增 / 编辑 -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑模型配置' : '添加模型配置'" width="540px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="如：Claude 主 Key" />
        </el-form-item>
        <el-form-item label="厂商" required>
          <el-select v-model="form.provider" class="w-full">
            <el-option v-for="opt in providerOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </el-form-item>
        <el-form-item label="API 地址" required>
          <el-input v-model="form.api_url" placeholder="如：https://api.anthropic.com" />
        </el-form-item>
        <el-form-item :label="isEdit ? 'API Key' : 'API Key'" :required="!isEdit">
          <el-input v-model="form.api_key" type="password" show-password :placeholder="isEdit ? '留空则不修改' : '必填'" />
        </el-form-item>
        <el-form-item label="模型" required>
          <el-input v-model="form.model" placeholder="如：claude-sonnet-4-20250514" />
        </el-form-item>
        <el-form-item label="优先级">
          <el-input-number v-model="form.priority" :min="1" :max="999" class="w-full" />
          <div class="mt-1 text-xs text-gray-400">数字越小越先被调用（1=最高优先级，默认 100）</div>
        </el-form-item>
        <el-form-item label="输入价格">
          <el-input v-model.number="form.input_price" placeholder="USD / 百万 tokens，如 3.0" />
        </el-form-item>
        <el-form-item label="输出价格">
          <el-input v-model.number="form.output_price" placeholder="USD / 百万 tokens，如 15.0" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" :active-value="1" :inactive-value="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.is_active" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
