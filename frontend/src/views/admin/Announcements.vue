<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface Announce {
  id: number; title: string; content: string; type: string
  status: string; is_pinned: number; publish_at: string | null
  expire_at: string | null; created_at: string
}

const list = ref<Announce[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const loading = ref(false)

const dialogVisible = ref(false)
const isEdit = ref(false)
const editId = ref<number | null>(null)
const form = ref({ title: '', content: '', type: 'notice', status: 'draft', is_pinned: 0 })

const typeMap: Record<string, { label: string; tagType: string }> = {
  notice: { label: '通知', tagType: '' },
  maintenance: { label: '维护', tagType: 'warning' },
  update: { label: '更新', tagType: 'success' },
}
const statusMap: Record<string, { label: string; tagType: string }> = {
  draft: { label: '草稿', tagType: 'info' },
  published: { label: '已发布', tagType: 'success' },
  archived: { label: '归档', tagType: '' },
}

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/announcements', { params: { page: page.value, page_size: pageSize.value } })
    list.value = res.data.list ?? res.data ?? []
    total.value = res.data.total ?? list.value.length
  } catch { /* handled */ }
  loading.value = false
}

function openCreate() {
  isEdit.value = false; editId.value = null
  form.value = { title: '', content: '', type: 'notice', status: 'draft', is_pinned: 0 }
  dialogVisible.value = true
}

function openEdit(row: Announce) {
  isEdit.value = true; editId.value = row.id
  form.value = { title: row.title, content: row.content, type: row.type, status: row.status, is_pinned: row.is_pinned }
  dialogVisible.value = true
}

async function handleSubmit() {
  try {
    if (isEdit.value && editId.value) {
      await api.put(`/admin/announcements/${editId.value}`, form.value)
      ElMessage.success('更新成功')
    } else {
      await api.post('/admin/announcements', form.value)
      ElMessage.success('创建成功')
    }
    dialogVisible.value = false
    fetchList()
  } catch { /* handled */ }
}

async function handlePublish(row: Announce) {
  try {
    await api.put(`/admin/announcements/${row.id}/publish`)
    ElMessage.success('发布成功')
    fetchList()
  } catch { /* handled */ }
}

async function handleArchive(row: Announce) {
  try {
    await api.put(`/admin/announcements/${row.id}`, { status: 'archived' })
    ElMessage.success('已归档')
    fetchList()
  } catch { /* handled */ }
}

async function handleDelete(id: number) {
  try {
    await ElMessageBox.confirm('确定删除该公告？', '提示', { type: 'warning' })
    await api.delete(`/admin/announcements/${id}`)
    ElMessage.success('删除成功')
    fetchList()
  } catch { /* cancel */ }
}

watch(page, fetchList)
onMounted(fetchList)
</script>

<template>
  <div>
    <div class="flex justify-between mb-4">
      <span class="text-sm text-gray-400">共 {{ total }} 条公告</span>
      <el-button type="primary" @click="openCreate">新建公告</el-button>
    </div>

    <el-table :data="list" v-loading="loading" border stripe style="width: 100%" class="rounded-lg">
      <el-table-column prop="id" label="ID" width="60" />
      <el-table-column prop="title" label="标题" min-width="180" show-overflow-tooltip />
      <el-table-column prop="type" label="类型" width="90">
        <template #default="{ row }">
          <el-tag :type="(typeMap[row.type]?.tagType as any) || 'info'" size="small">{{ typeMap[row.type]?.label || row.type }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="90">
        <template #default="{ row }">
          <el-tag :type="(statusMap[row.status]?.tagType as any) || 'info'" size="small">{{ statusMap[row.status]?.label || row.status }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="is_pinned" label="置顶" width="70">
        <template #default="{ row }">
          <el-tag :type="row.is_pinned ? 'success' : 'info'" size="small">{{ row.is_pinned ? '是' : '否' }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="created_at" label="创建时间" width="170">
        <template #default="{ row }">{{ row.created_at?.replace('T', ' ').slice(0, 19) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status === 'draft'" size="small" type="success" text @click="handlePublish(row)">发布</el-button>
          <el-button v-if="row.status === 'published'" size="small" type="warning" text @click="handleArchive(row)">归档</el-button>
          <el-button size="small" type="primary" text @click="openEdit(row)">编辑</el-button>
          <el-button size="small" type="danger" text @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <div class="mt-4 flex justify-end" v-if="total > pageSize">
      <el-pagination v-model:current-page="page" :page-size="pageSize" :total="total" layout="prev, pager, next" background />
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑公告' : '新建公告'" width="560px" destroy-on-close>
      <el-form label-width="80px">
        <el-form-item label="标题" required>
          <el-input v-model="form.title" placeholder="公告标题" />
        </el-form-item>
        <el-form-item label="内容" required>
          <el-input v-model="form.content" type="textarea" :rows="5" placeholder="公告内容" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" class="w-full">
            <el-option label="通知" value="notice" />
            <el-option label="维护" value="maintenance" />
            <el-option label="更新" value="update" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-select v-model="form.status" class="w-full">
            <el-option label="草稿" value="draft" />
            <el-option label="已发布" value="published" />
            <el-option label="归档" value="archived" />
          </el-select>
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_pinned" :active-value="1" :inactive-value="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>
