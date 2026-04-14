<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Column {
  prop: string
  label: string
  width?: number
  type?: 'tag' | 'switch' | 'datetime' | 'text'
  tagMap?: Record<string, { label: string; type: string }>
}

const props = defineProps<{
  apiBase: string
  columns: Column[]
  formFields: { key: string; label: string; type?: string; options?: { label: string; value: string | number }[]; required?: boolean }[]
  title?: string
  createBtnLabel?: string
  searchable?: boolean
  searchPlaceholder?: string
}>()

const loading = ref(false)
const list = ref<Record<string, unknown>[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const keyword = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref<Record<string, unknown>>({})

function initForm() {
  const f: Record<string, unknown> = {}
  for (const field of props.formFields) {
    f[field.key] = field.type === 'switch' ? 1 : ''
  }
  return f
}

async function fetchList() {
  loading.value = true
  try {
    const params: Record<string, unknown> = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    const res = await api.get(props.apiBase, { params })
    list.value = res.data.list ?? res.data ?? []
    total.value = res.data.total ?? list.value.length
  } catch { /* handled */ } finally { loading.value = false }
}

function openCreate() {
  isEdit.value = false
  editId.value = null
  form.value = initForm()
  dialogVisible.value = true
}

function openEdit(row: Record<string, unknown>) {
  isEdit.value = true
  editId.value = row.id as number
  const f: Record<string, unknown> = {}
  for (const field of props.formFields) {
    f[field.key] = row[field.key] ?? ''
  }
  form.value = f
  dialogVisible.value = true
}

async function handleSubmit() {
  const data: Record<string, unknown> = {}
  for (const field of props.formFields) {
    if (form.value[field.key] !== '' && form.value[field.key] !== undefined) {
      data[field.key] = form.value[field.key]
    }
  }
  try {
    if (isEdit.value && editId.value) {
      await api.put(`${props.apiBase}/${editId.value}`, data)
      ElMessage.success('更新成功')
    } else {
      await api.post(props.apiBase, data)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    await fetchList()
  } catch { /* handled */ }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除？', '提示', { type: 'warning' })
    await api.delete(`${props.apiBase}/${id}`)
    ElMessage.success('删除成功')
    await fetchList()
  } catch { /* cancel or error */ }
}

watch(page, fetchList)

onMounted(fetchList)

defineExpose({ fetchList })
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-4">
      <div class="flex items-center gap-3">
        <el-input v-if="searchable" v-model="keyword" :placeholder="searchPlaceholder || '搜索...'" clearable style="width: 240px" @keyup.enter="fetchList" @clear="fetchList" />
      </div>
      <el-button type="primary" @click="openCreate">{{ createBtnLabel || '新增' }}</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe style="width: 100%" class="rounded-lg">
      <el-table-column v-for="col in columns" :key="col.prop" :prop="col.prop" :label="col.label" :width="col.width" :show-overflow-tooltip="true">
        <template #default="{ row }">
          <template v-if="col.type === 'tag' && col.tagMap">
            <el-tag :type="(col.tagMap[String(row[col.prop])]?.type as any) || 'info'" size="small">
              {{ col.tagMap[String(row[col.prop])]?.label || row[col.prop] }}
            </el-tag>
          </template>
          <template v-else-if="col.type === 'switch'">
            <el-tag :type="row[col.prop] ? 'success' : 'info'" size="small">{{ row[col.prop] ? '启用' : '禁用' }}</el-tag>
          </template>
          <template v-else>{{ row[col.prop] }}</template>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" text type="primary" @click="openEdit(row)">编辑</el-button>
          <el-button size="small" text type="danger" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" background />
    </div>

    <!-- Dialog -->
    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑' : '新增'" width="520px" destroy-on-close>
      <el-form label-width="100px">
        <el-form-item v-for="field in formFields" :key="field.key" :label="field.label" :required="field.required">
          <el-select v-if="field.type === 'select'" v-model="form[field.key]" class="w-full">
            <el-option v-for="opt in field.options" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-switch v-else-if="field.type === 'switch'" v-model="form[field.key]" :active-value="1" :inactive-value="0" />
          <el-input v-else-if="field.type === 'textarea'" v-model="form[field.key]" type="textarea" :rows="3" />
          <el-input v-else v-model="form[field.key]" :type="field.type === 'password' ? 'password' : 'text'" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
