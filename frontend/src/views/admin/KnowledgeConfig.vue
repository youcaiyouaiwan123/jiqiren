<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import api from '@/utils/api'
import { ElMessage, ElMessageBox } from 'element-plus'

interface ConfigItem {
  id: number
  config_key: string
  config_value: string
  description: string | null
}

interface EffectiveKnowledgeConfig {
  vault_path: string
  index_dir: string
  git_repo_url: string
  git_branch: string
}

interface ReindexResult extends EffectiveKnowledgeConfig {
  embedding_provider: string
  embedding_model: string
  files: number
  published_files: number
  skipped_files: number
  chunks: number
}

interface GitResult {
  action: string
  repo_url: string
  branch: string
  vault_path: string
  output: string
}

interface SyncResult {
  git: GitResult
  reindex: ReindexResult
}

interface KnowledgeConfigPayload {
  list?: ConfigItem[]
  effective?: EffectiveKnowledgeConfig
}

interface AiConfigPayload {
  list?: ConfigItem[]
}

interface ApiResponse<T> {
  message?: string
  data: T
}

function createEmptyForm(): EffectiveKnowledgeConfig {
  return {
    vault_path: '',
    index_dir: '',
    git_repo_url: '',
    git_branch: 'main',
  }
}

const configs = ref<ConfigItem[]>([])
const form = ref<EffectiveKnowledgeConfig>(createEmptyForm())
const effective = ref<EffectiveKnowledgeConfig>(createEmptyForm())
const saving = ref(false)
const reindexing = ref(false)
const syncing = ref(false)
const knowledgeEnabled = ref(false)
const savingKnowledgeEnabled = ref(false)
const lastReindexResult = ref<ReindexResult | null>(null)
const lastSyncResult = ref<SyncResult | null>(null)

const gitConfigured = computed(() => Boolean((form.value.git_repo_url || '').trim()))
const indexPathChanged = computed(() => form.value.index_dir.trim() !== effective.value.index_dir.trim())
const vaultPathChanged = computed(() => form.value.vault_path.trim() !== effective.value.vault_path.trim())

function applyConfig(payload?: KnowledgeConfigPayload) {
  configs.value = payload?.list ?? []
  const nextEffective = payload?.effective ?? createEmptyForm()
  effective.value = {
    vault_path: nextEffective.vault_path || '',
    index_dir: nextEffective.index_dir || '',
    git_repo_url: nextEffective.git_repo_url || '',
    git_branch: nextEffective.git_branch || 'main',
  }
  form.value = {
    vault_path: effective.value.vault_path,
    index_dir: effective.value.index_dir,
    git_repo_url: effective.value.git_repo_url,
    git_branch: effective.value.git_branch,
  }
  for (const item of configs.value) {
    if (item.config_key in form.value) {
      (form.value as Record<string, string>)[item.config_key] = item.config_value || ''
    }
  }
  if (!form.value.git_branch) {
    form.value.git_branch = effective.value.git_branch || 'main'
  }
}

function applyAiConfig(payload?: AiConfigPayload) {
  const item = (payload?.list ?? []).find((row) => row.config_key === 'knowledge_enabled')
  knowledgeEnabled.value = item?.config_value === 'true'
}

async function fetchConfig() {
  try {
    const [knowledgeRes, aiRes] = await Promise.all([
      api.get('/admin/knowledge/config') as Promise<ApiResponse<KnowledgeConfigPayload>>,
      api.get('/admin/ai/config') as Promise<ApiResponse<AiConfigPayload>>,
    ])
    applyConfig(knowledgeRes.data)
    applyAiConfig(aiRes.data)
  } catch { /* handled */ }
}

async function save() {
  saving.value = true
  try {
    const res = await api.put('/admin/knowledge/config', form.value) as ApiResponse<KnowledgeConfigPayload>
    applyConfig(res.data)
    ElMessage.success('知识源配置已保存')
  } catch { /* handled */ }
  saving.value = false
}

async function saveKnowledgeEnabled() {
  savingKnowledgeEnabled.value = true
  try {
    await api.put('/admin/ai/config/knowledge_enabled', { value: knowledgeEnabled.value ? 'true' : 'false' })
    ElMessage.success(`知识库检索已${knowledgeEnabled.value ? '开启' : '关闭'}`)
  } catch { /* handled */ }
  savingKnowledgeEnabled.value = false
}

async function runReindex() {
  try {
    await ElMessageBox.confirm(
      '将按当前知识源配置重新扫描 Markdown 并重建向量索引，是否继续？',
      '重建知识索引',
      { type: 'warning' },
    )
    reindexing.value = true
    const res = await api.post('/admin/knowledge/config/reindex') as ApiResponse<ReindexResult>
    lastReindexResult.value = res.data as ReindexResult
    await fetchConfig()
    ElMessage.success(res.message || '索引重建完成')
  } catch { /* handled */ }
  reindexing.value = false
}

async function runSync() {
  if (!gitConfigured.value) {
    ElMessage.warning('请先填写并保存 Git 仓库地址')
    return
  }
  try {
    await ElMessageBox.confirm(
      '将执行 Git pull 同步知识仓库到本地 Vault 目录，然后自动重建向量索引。是否继续？',
      'Git 同步 + 重建索引',
      { type: 'warning' },
    )
    syncing.value = true
    const res = await api.post('/admin/knowledge/config/sync') as ApiResponse<SyncResult>
    lastSyncResult.value = res.data
    lastReindexResult.value = res.data.reindex
    await fetchConfig()
    ElMessage.success(res.message || '同步并重建完成')
  } catch { /* handled */ }
  syncing.value = false
}

onMounted(fetchConfig)
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-8 pb-6">
    <div class="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-900 p-[1px] shadow-[0_24px_80px_-28px_rgba(15,23,42,0.55)]">
      <div class="relative overflow-hidden rounded-[27px] bg-[radial-gradient(circle_at_top_right,_rgba(16,185,129,0.18),_transparent_28%),linear-gradient(135deg,rgba(15,23,42,0.98),rgba(30,41,59,0.96))] px-6 py-7 sm:px-8">
        <div class="relative flex flex-col gap-6 xl:flex-row xl:items-end xl:justify-between">
          <div class="max-w-2xl">
            <span class="inline-flex rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-medium tracking-wide text-slate-200">
              Knowledge Source Console
            </span>
            <h2 class="mt-4 text-2xl font-semibold tracking-tight text-white sm:text-3xl">知识源配置中心</h2>
            <p class="mt-3 max-w-xl text-sm leading-6 text-slate-300">
              在后台直接维护 Obsidian Vault 路径、索引目录和 Git 仓库信息。保存后，聊天检索和手动重建索引都会优先使用这里的配置。
            </p>
          </div>
          <div class="grid grid-cols-2 gap-3 sm:grid-cols-4 xl:min-w-[520px]">
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">知识目录</div>
              <div class="mt-2 text-sm font-semibold text-white">{{ effective.vault_path ? '已配置' : '未配置' }}</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">索引目录</div>
              <div class="mt-2 text-sm font-semibold text-white">{{ effective.index_dir ? '已配置' : '未配置' }}</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">Git 仓库</div>
              <div class="mt-2 text-sm font-semibold text-white">{{ gitConfigured ? '已记录' : '未记录' }}</div>
            </div>
            <div class="rounded-2xl border border-white/10 bg-white/10 px-4 py-3 backdrop-blur-sm">
              <div class="text-xs text-slate-300">默认分支</div>
              <div class="mt-2 text-sm font-semibold text-white">{{ form.git_branch || 'main' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 gap-6 xl:grid-cols-[1.1fr_0.9fr]">
      <div class="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_24px_60px_-32px_rgba(15,23,42,0.25)]">
        <div class="bg-gradient-to-r from-slate-900 via-slate-800 to-slate-700 px-6 py-5 sm:px-7">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h3 class="text-lg font-semibold text-white">运行时路径</h3>
              <p class="mt-1 text-sm text-slate-300">这里的值会覆盖 `.env` 默认值，供聊天检索和重建索引直接使用。</p>
            </div>
            <div class="flex flex-wrap gap-2">
              <span class="rounded-full border border-white/10 px-3 py-1 text-xs font-medium" :class="vaultPathChanged ? 'bg-amber-400/15 text-amber-200' : 'bg-white/5 text-slate-300'">
                {{ vaultPathChanged ? '知识目录待保存' : '知识目录已生效' }}
              </span>
              <span class="rounded-full border border-white/10 px-3 py-1 text-xs font-medium" :class="indexPathChanged ? 'bg-amber-400/15 text-amber-200' : 'bg-white/5 text-slate-300'">
                {{ indexPathChanged ? '索引目录待保存' : '索引目录已生效' }}
              </span>
            </div>
          </div>
        </div>
        <div class="p-6 sm:p-7">
          <el-form label-position="top">
            <el-form-item label="Obsidian Vault 路径">
              <el-input v-model="form.vault_path" placeholder="例如：D:\\ObsidianVault 或 E:\\knowledge" />
            </el-form-item>
            <el-form-item label="知识索引目录">
              <el-input v-model="form.index_dir" placeholder="例如：D:\\abaojie-data\\chroma\\knowledge" />
            </el-form-item>
            <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-4">
                <div class="text-xs font-medium uppercase tracking-wide text-slate-500">当前生效的 Vault</div>
                <div class="mt-2 break-all text-sm text-slate-700">{{ effective.vault_path || '--' }}</div>
              </div>
              <div class="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-4">
                <div class="text-xs font-medium uppercase tracking-wide text-slate-500">当前生效的索引目录</div>
                <div class="mt-2 break-all text-sm text-slate-700">{{ effective.index_dir || '--' }}</div>
              </div>
            </div>
          </el-form>
        </div>
      </div>

      <div class="overflow-hidden rounded-[28px] border border-slate-200 bg-white shadow-[0_24px_60px_-32px_rgba(16,185,129,0.22)]">
        <div class="bg-gradient-to-r from-emerald-500 via-teal-500 to-cyan-500 px-6 py-5 sm:px-7 text-white">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <h3 class="text-lg font-semibold">Git 预留配置</h3>
              <p class="mt-1 text-sm text-white/80">当前用于记录仓库来源和分支，后续做自动拉取时可直接沿用这里的配置。</p>
            </div>
            <span class="rounded-full bg-white/15 px-3 py-1 text-xs font-medium">{{ gitConfigured ? '支持一键同步' : '待配置' }}</span>
          </div>
        </div>
        <div class="p-6 sm:p-7">
          <el-form label-position="top">
            <el-form-item label="Git 仓库地址">
              <el-input v-model="form.git_repo_url" placeholder="例如：https://github.com/your-org/knowledge-base.git" />
            </el-form-item>
            <el-form-item label="Git 分支">
              <el-input v-model="form.git_branch" placeholder="main" />
            </el-form-item>
            <div class="rounded-2xl border border-cyan-100 bg-cyan-50 px-4 py-4 text-sm leading-6 text-cyan-700">
              填写并保存 Git 仓库地址后，可点击下方“同步并重建”按钮执行 <code>git clone/pull</code> 并自动重建索引。服务器需已安装 Git 并配置好访问权限。
            </div>
          </el-form>
        </div>
      </div>
    </div>

    <div class="rounded-[28px] border border-indigo-200 bg-white px-6 py-5 shadow-[0_18px_50px_-34px_rgba(99,102,241,0.28)]">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <div class="text-sm font-semibold text-slate-900">聊天知识库检索开关</div>
          <div class="mt-1 text-xs leading-6 text-slate-500">关闭后，即使已经同步并重建索引，聊天回答也不会使用知识库内容。</div>
        </div>
        <div class="flex flex-col gap-3 sm:flex-row sm:items-center">
          <el-tag :type="knowledgeEnabled ? 'success' : 'info'" size="large">{{ knowledgeEnabled ? '已开启' : '已关闭' }}</el-tag>
          <el-switch v-model="knowledgeEnabled" inline-prompt active-text="开" inactive-text="关" />
          <el-button type="primary" plain :loading="savingKnowledgeEnabled" @click="saveKnowledgeEnabled">保存检索开关</el-button>
        </div>
      </div>
    </div>

    <div class="flex flex-col gap-4 rounded-[28px] border border-slate-200 bg-white/95 px-6 py-5 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.35)] sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div class="text-sm font-medium text-slate-800">保存后立即影响运行时配置</div>
        <div class="mt-1 text-xs text-slate-500">聊天检索和手动重建索引都会优先读取这里保存的知识源配置；如果还没保存，则继续使用 `.env` 默认值。</div>
      </div>
      <div class="flex flex-col gap-3 sm:flex-row">
        <el-button size="large" class="sm:min-w-[160px]" :loading="syncing" :disabled="!gitConfigured" @click="runSync">同步并重建</el-button>
        <el-button size="large" class="sm:min-w-[160px]" :loading="reindexing" @click="runReindex">重建知识索引</el-button>
        <el-button type="primary" size="large" class="sm:min-w-[160px]" :loading="saving" @click="save">保存知识源配置</el-button>
      </div>
    </div>

    <div v-if="lastSyncResult" class="rounded-[24px] border border-blue-200 bg-blue-50 px-6 py-5 shadow-[0_18px_50px_-34px_rgba(59,130,246,0.3)] mb-6">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div class="text-sm font-semibold text-blue-800">Git 同步已完成</div>
          <div class="mt-1 text-xs text-blue-700">以下是本次同步的 Git 详情。</div>
        </div>
        <el-tag type="primary" size="large">{{ lastSyncResult.git.action === 'clone' ? '已克隆' : '已拉取' }}</el-tag>
      </div>
      <div class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-2xl border border-blue-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-blue-600">操作</div>
          <div class="mt-1 text-sm font-semibold text-blue-900">{{ lastSyncResult.git.action }}</div>
        </div>
        <div class="rounded-2xl border border-blue-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-blue-600">分支</div>
          <div class="mt-1 text-sm font-semibold text-blue-900">{{ lastSyncResult.git.branch }}</div>
        </div>
        <div class="rounded-2xl border border-blue-200 bg-white/80 px-4 py-3 md:col-span-2">
          <div class="text-xs text-blue-600">仓库地址</div>
          <div class="mt-1 break-all text-sm font-medium text-blue-900">{{ lastSyncResult.git.repo_url }}</div>
        </div>
      </div>
      <div v-if="lastSyncResult.git.output" class="mt-3 rounded-2xl border border-blue-200 bg-white/80 px-4 py-3">
        <div class="text-xs text-blue-600">Git 输出</div>
        <pre class="mt-1 max-h-32 overflow-auto whitespace-pre-wrap break-all text-xs text-blue-800">{{ lastSyncResult.git.output }}</pre>
      </div>
    </div>

    <div v-if="lastReindexResult" class="rounded-[24px] border border-emerald-200 bg-emerald-50 px-6 py-5 shadow-[0_18px_50px_-34px_rgba(16,185,129,0.35)]">
      <div class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div>
          <div class="text-sm font-semibold text-emerald-800">最近一次知识索引重建已完成</div>
          <div class="mt-1 text-xs text-emerald-700">重建使用的 Vault、索引目录和 Embedding 配置如下。</div>
        </div>
        <el-tag type="success" size="large">索引完成</el-tag>
      </div>
      <div class="mt-4 grid grid-cols-1 gap-3 md:grid-cols-2 xl:grid-cols-4">
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">扫描文件数</div>
          <div class="mt-1 text-lg font-semibold text-emerald-900">{{ lastReindexResult.files }}</div>
        </div>
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">已发布文件</div>
          <div class="mt-1 text-lg font-semibold text-emerald-900">{{ lastReindexResult.published_files }}</div>
        </div>
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">跳过文件</div>
          <div class="mt-1 text-lg font-semibold text-emerald-900">{{ lastReindexResult.skipped_files }}</div>
        </div>
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">索引分片数</div>
          <div class="mt-1 text-lg font-semibold text-emerald-900">{{ lastReindexResult.chunks }}</div>
        </div>
      </div>
      <div class="mt-4 grid grid-cols-1 gap-3 lg:grid-cols-2">
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">Vault 路径</div>
          <div class="mt-1 break-all text-sm font-medium text-emerald-900">{{ lastReindexResult.vault_path }}</div>
        </div>
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">索引目录</div>
          <div class="mt-1 break-all text-sm font-medium text-emerald-900">{{ lastReindexResult.index_dir }}</div>
        </div>
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">Embedding 厂商</div>
          <div class="mt-1 text-sm font-medium text-emerald-900">{{ lastReindexResult.embedding_provider || '--' }}</div>
        </div>
        <div class="rounded-2xl border border-emerald-200 bg-white/80 px-4 py-3">
          <div class="text-xs text-emerald-600">Embedding 模型</div>
          <div class="mt-1 break-all text-sm font-medium text-emerald-900">{{ lastReindexResult.embedding_model || '使用默认模型' }}</div>
        </div>
      </div>
    </div>
  </div>
</template>
