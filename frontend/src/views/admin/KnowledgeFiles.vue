<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/utils/api'
import type { ApiResponse } from '@/types'
import { ElMessage, ElMessageBox } from 'element-plus'

interface KnowledgeFileRow {
  path: string
  name: string
  title: string
  status: string
  tags: string[]
  aliases: string[]
  summary: string
  size: number
  updated_at: string
}

interface KnowledgeFileDetail extends KnowledgeFileRow {
  content: string
}

interface KnowledgeFileListPayload {
  list: KnowledgeFileRow[]
  total: number
  page: number
  page_size: number
  vault_path: string
  stats: KnowledgeFileListStats
}

interface KnowledgeFileListStats {
  total: number
  published: number
  draft: number
  archived: number
  total_size: number
  latest_updated_at: string | null
}

interface ImportSkippedItem {
  filename: string
  path?: string
  reason: string
}

interface ImportResult {
  target_dir: string
  total: number
  imported_count: number
  skipped_count: number
  imported: string[]
  skipped: ImportSkippedItem[]
}

interface ReindexResult {
  files: number
  published_files: number
  skipped_files: number
  chunks: number
  vault_path: string
  index_dir: string
  embedding_provider: string
  embedding_model: string
}

const loading = ref(false)
const saving = ref(false)
const reindexing = ref(false)
const importSubmitting = ref(false)
const detailLoading = ref(false)

const vaultPath = ref('')
const list = ref<KnowledgeFileRow[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(8)
const keyword = ref('')
const statusFilter = ref('all')
const stats = ref<KnowledgeFileListStats>({ total: 0, published: 0, draft: 0, archived: 0, total_size: 0, latest_updated_at: null })

const dialogVisible = ref(false)
const isEdit = ref(false)
const originalPath = ref('')
const form = ref({ path: '', content: '' })

const importDialogVisible = ref(false)
const importInput = ref<HTMLInputElement>()
const selectedImportFiles = ref<File[]>([])
const importTargetDir = ref('')
const importOverwrite = ref(false)
const lastImportResult = ref<ImportResult | null>(null)
const lastReindexResult = ref<ReindexResult | null>(null)

const statusOptions = computed(() => {
  const values = Array.from(new Set(['published', 'draft', 'archived', statusFilter.value, ...list.value.map(item => item.status)].filter(item => item && item !== 'all')))
  return ['all', ...values]
})

const publishedCount = computed(() => stats.value.published)
const draftCount = computed(() => stats.value.draft)
const archivedCount = computed(() => stats.value.archived)
const totalSize = computed(() => stats.value.total_size)
const latestUpdatedAt = computed(() => formatDateTime(stats.value.latest_updated_at))
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const hasFilters = computed(() => !!keyword.value.trim() || statusFilter.value !== 'all')

function formatDateTime(value?: string | null) {
  if (!value) return '-'
  return value.replace('T', ' ').slice(0, 19)
}

function formatSize(size: number) {
  if (size < 1024) return `${size} B`
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`
  return `${(size / 1024 / 1024).toFixed(1)} MB`
}

function statusTagType(status: string): 'success' | 'info' | 'warning' {
  if (status === 'published') return 'success'
  if (status === 'draft') return 'info'
  if (status === 'archived') return 'warning'
  return 'info'
}

async function fetchList() {
  loading.value = true
  try {
    const res = await api.get('/admin/knowledge/files', {
      params: {
        page: page.value,
        page_size: pageSize.value,
        keyword: keyword.value.trim(),
        status: statusFilter.value,
      },
    }) as ApiResponse<KnowledgeFileListPayload>
    list.value = res.data.list ?? []
    total.value = res.data.total ?? 0
    page.value = res.data.page ?? page.value
    pageSize.value = res.data.page_size ?? pageSize.value
    vaultPath.value = res.data.vault_path ?? ''
    stats.value = res.data.stats ?? { total: 0, published: 0, draft: 0, archived: 0, total_size: 0, latest_updated_at: null }
  } catch {
  } finally {
    loading.value = false
  }
}

async function applyFilters() {
  page.value = 1
  await fetchList()
}

async function resetFilters() {
  keyword.value = ''
  statusFilter.value = 'all'
  page.value = 1
  await fetchList()
}

async function handlePageChange(nextPage: number) {
  page.value = nextPage
  await fetchList()
}

async function handlePageSizeChange(nextPageSize: number) {
  pageSize.value = nextPageSize
  page.value = 1
  await fetchList()
}

function openCreate() {
  isEdit.value = false
  originalPath.value = ''
  form.value = {
    path: 'new-doc.md',
    content: '---\ntitle: 新文档\nstatus: published\ntags: []\naliases: []\n---\n\n',
  }
  dialogVisible.value = true
}

async function openEdit(row: KnowledgeFileRow) {
  detailLoading.value = true
  try {
    const res = await api.get('/admin/knowledge/files/detail', { params: { path: row.path } }) as ApiResponse<KnowledgeFileDetail>
    isEdit.value = true
    originalPath.value = res.data.path
    form.value = { path: res.data.path, content: res.data.content }
    dialogVisible.value = true
  } catch {
  } finally {
    detailLoading.value = false
  }
}

async function handleSave() {
  const payload = { path: form.value.path.trim(), content: form.value.content }
  if (!payload.path || !payload.content.trim()) {
    ElMessage.warning('请填写文件路径和文档内容')
    return
  }
  saving.value = true
  try {
    if (isEdit.value) {
      const res = await api.put('/admin/knowledge/files', {
        path: originalPath.value,
        new_path: payload.path,
        content: payload.content,
      }) as ApiResponse<KnowledgeFileDetail>
      ElMessage.success(res.message || '文档已保存')
    } else {
      const res = await api.post('/admin/knowledge/files', payload) as ApiResponse<KnowledgeFileDetail>
      ElMessage.success(res.message || '文档已创建')
    }
    dialogVisible.value = false
    page.value = 1
    await fetchList()
  } catch {
  } finally {
    saving.value = false
  }
}

async function handleDelete(row: KnowledgeFileRow) {
  try {
    await ElMessageBox.confirm(`确定删除文档 ${row.path}？`, '提示', { type: 'warning' })
    const res = await api.delete('/admin/knowledge/files', { params: { path: row.path } }) as ApiResponse<{ path: string }>
    ElMessage.success(res.message || '文档已删除')
    if (list.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    await fetchList()
  } catch {
  }
}

function triggerImportSelect() {
  if (importInput.value) importInput.value.value = ''
  importInput.value?.click()
}

function handleImportChange(event: Event) {
  const input = event.target as HTMLInputElement
  const files = Array.from(input.files ?? [])
  if (!files.length) return
  selectedImportFiles.value = files
  importDialogVisible.value = true
}

async function submitImport() {
  if (!selectedImportFiles.value.length) {
    ElMessage.warning('请先选择 Markdown 文件')
    return
  }
  importSubmitting.value = true
  try {
    const formData = new FormData()
    selectedImportFiles.value.forEach((file) => formData.append('files', file))
    formData.append('target_dir', importTargetDir.value.trim())
    formData.append('overwrite', String(importOverwrite.value))
    const res = await api.post('/admin/knowledge/files/import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    }) as ApiResponse<ImportResult>
    lastImportResult.value = res.data
    ElMessage.success(res.message || '导入完成')
    importDialogVisible.value = false
    selectedImportFiles.value = []
    if (importInput.value) importInput.value.value = ''
    page.value = 1
    await fetchList()
  } catch {
  } finally {
    importSubmitting.value = false
  }
}

async function runReindex() {
  try {
    await ElMessageBox.confirm('文档变更后建议重建索引，是否现在执行？', '重建索引', { type: 'warning' })
    reindexing.value = true
    const res = await api.post('/admin/knowledge/config/reindex') as ApiResponse<ReindexResult>
    lastReindexResult.value = res.data
    ElMessage.success(res.message || '索引重建完成')
  } catch {
  } finally {
    reindexing.value = false
  }
}

onMounted(fetchList)
</script>

<template>
  <div class="mx-auto max-w-7xl space-y-8 pb-6">
    <input ref="importInput" type="file" accept=".md,text/markdown" multiple class="hidden" @change="handleImportChange" />

    <div class="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-slate-950 via-slate-900 to-cyan-900 p-[1px] shadow-[0_24px_80px_-28px_rgba(15,23,42,0.6)]">
      <div class="relative overflow-hidden rounded-[27px] bg-[radial-gradient(circle_at_top_right,_rgba(34,211,238,0.18),_transparent_28%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(30,41,59,0.96))] px-6 py-7 sm:px-8">
        <div class="relative flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div class="max-w-3xl">
            <span class="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium tracking-wide text-slate-200">
              Knowledge Document Console
            </span>
            <h2 class="mt-4 text-2xl font-semibold tracking-tight text-white sm:text-3xl">知识库文档管理</h2>
            <p class="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
              在后台直接维护 Markdown 知识文档，支持新增、编辑、删除与批量导入。关键词兜底会直接读取这些文件；如果要刷新向量检索结果，请在变更后手动重建索引。
            </p>
            <div class="mt-4 rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-xs text-slate-200">
              当前知识库目录：{{ vaultPath || '未配置' }}
            </div>
          </div>
          <div class="grid grid-cols-2 gap-3 sm:grid-cols-4 xl:min-w-[520px]">
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">文档总数</div>
              <div class="mt-2 text-2xl font-semibold text-white">{{ list.length }}</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">已发布</div>
              <div class="mt-2 text-2xl font-semibold text-white">{{ publishedCount }}</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">累计大小</div>
              <div class="mt-2 text-sm font-semibold text-white">{{ formatSize(totalSize) }}</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">最近更新</div>
              <div class="mt-2 text-sm font-semibold text-white">{{ latestUpdatedAt }}</div>
            </div>
          </div>
        </div>
        <div class="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
          <el-button type="primary" size="large" class="!ml-0 sm:min-w-[160px]" @click="openCreate">新建文档</el-button>
          <el-button plain size="large" class="!ml-0 sm:min-w-[160px]" @click="triggerImportSelect">导入 Markdown</el-button>
          <el-button plain size="large" class="!ml-0 sm:min-w-[160px]" :loading="reindexing" @click="runReindex">重建索引</el-button>
          <el-button plain size="large" class="!ml-0 sm:min-w-[160px]" @click="fetchList">刷新列表</el-button>
        </div>
      </div>
    </div>

    <div class="grid gap-6 xl:grid-cols-[minmax(0,1.35fr)_360px]">
      <div class="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_24px_60px_-32px_rgba(15,23,42,0.25)]">
        <div class="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 px-6 py-5 sm:px-7">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white">文档列表</h3>
              <p class="mt-1 text-sm text-slate-300">按更新时间倒序展示，方便优先处理刚导入或刚修改的知识文档。</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span class="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-medium text-slate-200">已发布 {{ publishedCount }}</span>
              <span class="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-medium text-slate-200">草稿 {{ draftCount }}</span>
              <span class="rounded-full border border-white/10 bg-white/10 px-3 py-1 text-xs font-medium text-slate-200">归档 {{ archivedCount }}</span>
            </div>
          </div>
        </div>
        <div class="p-6 sm:p-7">
          <div class="grid grid-cols-1 gap-3 xl:grid-cols-[minmax(0,1fr)_180px_240px]">
            <el-input v-model="keyword" clearable placeholder="搜索路径 / 标题 / 标签 / 摘要" size="large" @keyup.enter="applyFilters" @clear="applyFilters" />
            <el-select v-model="statusFilter" size="large" @change="applyFilters">
              <el-option v-for="item in statusOptions" :key="item" :label="item === 'all' ? '全部状态' : item" :value="item" />
            </el-select>
            <div class="flex gap-3">
              <el-button type="primary" size="large" class="!ml-0 flex-1" @click="applyFilters">查询</el-button>
              <el-button v-if="hasFilters" size="large" class="!ml-0" @click="resetFilters">重置</el-button>
            </div>
          </div>
          <div class="mt-4 rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3 text-xs leading-6 text-slate-500">
            当前第 {{ page }} / {{ totalPages }} 页，共 {{ total }} 个结果。你可以通过路径、标题、标签、别名或摘要快速定位目标文档。
          </div>

          <div class="mt-6 space-y-4" v-loading="loading || detailLoading">
            <div v-if="!list.length" class="rounded-[24px] border border-dashed border-slate-300 bg-slate-50 px-6 py-12 text-center">
              <div class="text-base font-semibold text-slate-700">没有找到匹配的知识文档</div>
              <div class="mt-2 text-sm text-slate-500">试试清空筛选条件，或者直接新建一篇 Markdown 文档。</div>
            </div>

            <div v-for="row in list" :key="row.path" class="group rounded-[24px] border border-slate-200 bg-white px-5 py-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-cyan-200 hover:shadow-[0_20px_45px_-28px_rgba(6,182,212,0.35)] sm:px-6">
              <div class="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                <div class="min-w-0 flex-1">
                  <div class="flex flex-wrap items-center gap-2">
                    <el-tag :type="statusTagType(row.status)">{{ row.status }}</el-tag>
                    <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ formatSize(row.size) }}</span>
                    <span class="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">{{ formatDateTime(row.updated_at) }}</span>
                  </div>
                  <div class="mt-3 text-lg font-semibold text-slate-900">{{ row.title }}</div>
                  <div class="mt-2 break-all font-mono text-xs text-slate-500">{{ row.path }}</div>
                  <div class="mt-4 text-sm leading-6 text-slate-600">{{ row.summary || '暂无摘要，建议补充正文内容。' }}</div>
                  <div class="mt-4 flex flex-wrap gap-2">
                    <el-tag v-for="tag in row.tags" :key="`tag-${row.path}-${tag}`" size="small" effect="light" type="info">{{ tag }}</el-tag>
                    <el-tag v-for="alias in row.aliases" :key="`alias-${row.path}-${alias}`" size="small" effect="plain" type="warning">别名：{{ alias }}</el-tag>
                    <span v-if="!row.tags.length && !row.aliases.length" class="text-xs text-slate-400">暂无标签或别名</span>
                  </div>
                </div>
                <div class="flex shrink-0 flex-wrap gap-2 xl:w-[132px] xl:flex-col">
                  <el-button type="primary" plain size="large" class="!ml-0 xl:w-full" @click="openEdit(row)">编辑</el-button>
                  <el-button type="danger" plain size="large" class="!ml-0 xl:w-full" @click="handleDelete(row)">删除</el-button>
                </div>
              </div>
            </div>

            <div v-if="total > 0" class="pt-2">
              <el-pagination
                :current-page="page"
                :page-size="pageSize"
                :page-sizes="[8, 12, 20, 40]"
                :total="total"
                layout="total, sizes, prev, pager, next"
                background
                @current-change="handlePageChange"
                @size-change="handlePageSizeChange"
              />
            </div>
          </div>
        </div>
      </div>

      <div class="space-y-6">
        <div class="overflow-hidden rounded-[28px] border border-cyan-200 bg-white shadow-[0_24px_60px_-32px_rgba(14,165,233,0.28)]">
          <div class="bg-gradient-to-r from-cyan-500 via-sky-500 to-indigo-500 px-6 py-5 text-white">
            <div class="flex items-start justify-between gap-4">
              <div>
                <div class="text-lg font-semibold">快捷维护</div>
                <div class="mt-1 text-sm text-white/80">常见操作集中在这里，适合日常补充 FAQ、产品说明和 SOP。</div>
              </div>
              <span class="rounded-full bg-white/15 px-3 py-1 text-xs font-medium">Admin</span>
            </div>
          </div>
          <div class="space-y-4 p-6">
            <div class="rounded-2xl border border-sky-100 bg-sky-50 px-4 py-4 text-sm leading-6 text-sky-800">
              推荐流程：先新建或导入 Markdown，确认 <code>title / status / tags / aliases</code> 后，再点击一次“重建索引”。
            </div>
            <div class="grid gap-3">
              <el-button type="primary" size="large" class="!ml-0" @click="openCreate">写一篇新文档</el-button>
              <el-button plain size="large" class="!ml-0" @click="triggerImportSelect">批量导入 Markdown</el-button>
              <el-button plain size="large" class="!ml-0" :loading="reindexing" @click="runReindex">立即重建索引</el-button>
            </div>
          </div>
        </div>

        <div class="overflow-hidden rounded-[28px] border border-emerald-200 bg-white shadow-[0_24px_60px_-32px_rgba(16,185,129,0.24)]">
          <div class="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 px-6 py-5 text-white">
            <div class="text-lg font-semibold">导入结果</div>
            <div class="mt-1 text-sm text-white/80">导入完成后，这里会显示成功与跳过的文件明细。</div>
          </div>
          <div v-if="lastImportResult" class="space-y-4 p-6 text-sm text-slate-600">
            <div class="grid grid-cols-3 gap-3">
              <div class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3">
                <div class="text-xs text-emerald-600">总数</div>
                <div class="mt-2 text-lg font-semibold text-emerald-900">{{ lastImportResult.total }}</div>
              </div>
              <div class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-3">
                <div class="text-xs text-emerald-600">成功导入</div>
                <div class="mt-2 text-lg font-semibold text-emerald-900">{{ lastImportResult.imported_count }}</div>
              </div>
              <div class="rounded-2xl border border-amber-100 bg-amber-50 px-4 py-3">
                <div class="text-xs text-amber-600">跳过</div>
                <div class="mt-2 text-lg font-semibold text-amber-900">{{ lastImportResult.skipped_count }}</div>
              </div>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs leading-6 text-slate-600">
              导入目录：{{ lastImportResult.target_dir || '知识库根目录' }}
            </div>
            <div v-if="lastImportResult.imported.length" class="rounded-2xl border border-emerald-100 bg-emerald-50 px-4 py-4 text-xs text-emerald-700">
              <div class="mb-2 font-medium">已导入</div>
              <div v-for="item in lastImportResult.imported" :key="item" class="py-0.5 break-all">{{ item }}</div>
            </div>
            <div v-if="lastImportResult.skipped.length" class="rounded-2xl border border-amber-100 bg-amber-50 px-4 py-4 text-xs text-amber-700">
              <div class="mb-2 font-medium">已跳过</div>
              <div v-for="item in lastImportResult.skipped" :key="`${item.filename}-${item.reason}`" class="py-0.5 break-all">{{ item.filename || item.path }}：{{ item.reason }}</div>
            </div>
          </div>
          <div v-else class="p-6 text-sm text-slate-400">还没有执行导入。</div>
        </div>

        <div class="overflow-hidden rounded-[28px] border border-violet-200 bg-white shadow-[0_24px_60px_-32px_rgba(124,58,237,0.2)]">
          <div class="bg-gradient-to-r from-violet-500 via-indigo-500 to-slate-800 px-6 py-5 text-white">
            <div class="text-lg font-semibold">最近一次索引重建</div>
            <div class="mt-1 text-sm text-white/80">方便确认最新的扫描范围、分块数量和 Embedding 配置。</div>
          </div>
          <div v-if="lastReindexResult" class="space-y-4 p-6 text-sm text-slate-600">
            <div class="grid grid-cols-2 gap-3">
              <div class="rounded-2xl border border-violet-100 bg-violet-50 px-4 py-3">
                <div class="text-xs text-violet-600">扫描文件</div>
                <div class="mt-2 text-lg font-semibold text-violet-900">{{ lastReindexResult.files }}</div>
              </div>
              <div class="rounded-2xl border border-violet-100 bg-violet-50 px-4 py-3">
                <div class="text-xs text-violet-600">生成分块</div>
                <div class="mt-2 text-lg font-semibold text-violet-900">{{ lastReindexResult.chunks }}</div>
              </div>
              <div class="rounded-2xl border border-violet-100 bg-violet-50 px-4 py-3">
                <div class="text-xs text-violet-600">已发布</div>
                <div class="mt-2 text-lg font-semibold text-violet-900">{{ lastReindexResult.published_files }}</div>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3">
                <div class="text-xs text-slate-500">跳过文件</div>
                <div class="mt-2 text-lg font-semibold text-slate-800">{{ lastReindexResult.skipped_files }}</div>
              </div>
            </div>
            <div class="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4 text-xs leading-6 text-slate-600">
              Embedding：{{ lastReindexResult.embedding_provider }} / {{ lastReindexResult.embedding_model || '默认模型' }}
            </div>
          </div>
          <div v-else class="p-6 text-sm text-slate-400">还没有在本页触发过索引重建。</div>
        </div>
      </div>
    </div>

    <el-dialog v-model="dialogVisible" :title="isEdit ? '编辑知识文档' : '新建知识文档'" width="960px" top="4vh" destroy-on-close>
      <div class="mb-5 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm leading-6 text-slate-600">
        支持直接编辑完整 Markdown 内容。建议保留 frontmatter 中的 <code>title / status / tags / aliases</code>，保存后如需刷新向量检索，请再手动重建索引。
      </div>
      <el-form label-position="top">
        <el-form-item label="相对路径" required>
          <el-input v-model="form.path" size="large" placeholder="例如：01-FAQ/常见问题.md" />
        </el-form-item>
        <el-form-item label="Markdown 内容" required>
          <el-input v-model="form.content" type="textarea" :rows="22" resize="vertical" placeholder="请输入完整 Markdown 内容，支持 frontmatter。" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="!ml-0" @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" class="!ml-0" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importDialogVisible" title="导入 Markdown 文档" width="680px" top="8vh" destroy-on-close>
      <div class="mb-5 rounded-2xl border border-cyan-100 bg-cyan-50 px-4 py-3 text-sm leading-6 text-cyan-700">
        支持一次选择多个 <code>.md</code> 文件导入。导入完成后，关键词检索会直接读取这些文档；如需刷新向量索引，请再点击页面上的“重建索引”。
      </div>
      <el-form label-position="top">
        <el-form-item label="已选择文件">
          <div class="max-h-56 w-full overflow-y-auto rounded-2xl bg-slate-50 px-4 py-3 text-sm text-slate-600">
            <div v-for="file in selectedImportFiles" :key="`${file.name}-${file.size}`" class="py-1">{{ file.name }} ({{ formatSize(file.size) }})</div>
            <div v-if="!selectedImportFiles.length" class="text-slate-400">请先选择要导入的 Markdown 文件。</div>
          </div>
        </el-form-item>
        <el-form-item label="导入到子目录">
          <el-input v-model="importTargetDir" placeholder="例如：04-运营手册，留空表示导入到根目录" />
        </el-form-item>
        <el-form-item label="覆盖同名文件">
          <el-switch v-model="importOverwrite" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button class="!ml-0" @click="importDialogVisible = false">取消</el-button>
        <el-button plain class="!ml-0" @click="triggerImportSelect">重新选择文件</el-button>
        <el-button type="primary" class="!ml-0" :loading="importSubmitting" @click="submitImport">开始导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>
