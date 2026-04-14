<script setup lang="ts">
import { ref } from 'vue'
import CrudTable from '@/components/CrudTable.vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

interface ColumnItem {
  prop: string
  label: string
  width?: number
  type?: 'tag' | 'switch' | 'datetime' | 'text'
  tagMap?: Record<string, { label: string; type: string }>
}

const columns: ColumnItem[] = [
  { prop: 'id', label: 'ID', width: 60 },
  { prop: 'word', label: '词汇' },
  { prop: 'match_type', label: '匹配', width: 90, type: 'tag' as const, tagMap: { exact: { label: '精确', type: '' }, contains: { label: '包含', type: 'warning' }, regex: { label: '正则', type: 'danger' } } },
  { prop: 'action', label: '动作', width: 90, type: 'tag' as const, tagMap: { reject: { label: '拒绝', type: 'danger' }, replace: { label: '替换', type: 'warning' }, warn: { label: '警告', type: '' } } },
  { prop: 'is_active', label: '启用', width: 70, type: 'switch' as const },
  { prop: 'created_at', label: '创建时间', width: 170 },
]

const formFields = [
  { key: 'word', label: '词汇', required: true },
  { key: 'match_type', label: '匹配方式', type: 'select', options: [{ label: '精确', value: 'exact' }, { label: '包含', value: 'contains' }, { label: '正则', value: 'regex' }] },
  { key: 'action', label: '动作', type: 'select', options: [{ label: '拒绝', value: 'reject' }, { label: '替换', value: 'replace' }, { label: '警告', value: 'warn' }] },
  { key: 'replace_with', label: '替换内容' },
  { key: 'is_active', label: '启用', type: 'switch' },
]

const batchDialog = ref(false)
const batchText = ref('')
const crudRef = ref<InstanceType<typeof CrudTable> | null>(null)

async function batchImport() {
  const words = batchText.value.split('\n').map(s => s.trim()).filter(Boolean)
  if (!words.length) { ElMessage.warning('请输入词汇'); return }
  try {
    const res = await api.post('/admin/banned-words/batch', { words })
    ElMessage.success(`导入 ${res.data.imported} 条，跳过 ${res.data.skipped} 条`)
    batchDialog.value = false
    batchText.value = ''
    crudRef.value?.fetchList()
  } catch { /* handled */ }
}
</script>

<template>
  <div>
    <div class="mb-3 flex justify-end">
      <el-button @click="batchDialog = true">批量导入</el-button>
    </div>
    <CrudTable ref="crudRef" api-base="/admin/banned-words" :columns="columns" :form-fields="formFields" searchable search-placeholder="搜索词汇" />
    <el-dialog v-model="batchDialog" title="批量导入禁用词" width="500px">
      <el-input v-model="batchText" type="textarea" :rows="8" placeholder="每行一个词汇" />
      <template #footer>
        <el-button @click="batchDialog = false">取消</el-button>
        <el-button type="primary" @click="batchImport">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>
