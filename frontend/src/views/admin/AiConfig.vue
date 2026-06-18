<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

interface ConfigItem { id: number; config_key: string; config_value: string; description: string | null }

interface ConfigMeta {
  label: string
  type: 'textarea' | 'select' | 'input'
  options?: Array<{ label: string; value: string }>
  group: 'basic' | 'knowledge'
  fullWidth?: boolean
  hint?: string
}

const configs = ref<ConfigItem[]>([])
const form = ref<Record<string, string>>({})
const savingKey = ref('')

const configMeta: Record<string, ConfigMeta> = {
  system_prompt:     { label: '系统提示词',    type: 'textarea', group: 'basic',     fullWidth: true,  hint: '为 AI 设置全局人设和回答规则' },
  temperature:       { label: 'Temperature',  type: 'input',    group: 'basic',     hint: '0-1，越大回答越发散，建议 0.3-0.7' },
  max_tokens:        { label: '最大回复 Token', type: 'input',   group: 'basic',     hint: '单次回复的最大 token 数' },
  faq_enabled:       { label: 'FAQ 匹配',     type: 'select',   group: 'basic',     hint: '关闭后忽略 FAQ 类知识',
    options: [{ label: '开启', value: 'true' }, { label: '关闭', value: 'false' }] },
  doc_recommend:     { label: '文档推荐',     type: 'select',   group: 'basic',     hint: '关闭后回答不再附带参考文档列表',
    options: [{ label: '开启', value: 'true' }, { label: '关闭', value: 'false' }] },
  knowledge_enabled: { label: '知识库检索',   type: 'select',   group: 'knowledge', hint: '关闭后 AI 不再查询知识库',
    options: [{ label: '开启', value: 'true' }, { label: '关闭', value: 'false' }] },
  knowledge_top_k:           { label: '召回数量 (top_k)', type: 'input', group: 'knowledge', hint: '每次检索取前 N 段相关文档' },
  knowledge_min_score:       { label: '最低相似度',       type: 'input', group: 'knowledge', hint: '0-1，低于此值的文档将被过滤' },
  knowledge_embedding_provider: { label: 'Embedding 厂商', type: 'select', group: 'knowledge', hint: '生成文本向量的厂商',
    options: [{ label: 'OpenAI / 兼容', value: 'openai' }, { label: 'Gemini', value: 'gemini' }, { label: '智谱 GLM', value: 'zhipu' }, { label: '本地模型', value: 'local' }] },
  knowledge_embedding_model: { label: 'Embedding 模型', type: 'input', group: 'knowledge', hint: '如 text-embedding-v4 / text-embedding-3-small' },
}

const configOrder = [
  'system_prompt',
  'temperature',
  'max_tokens',
  'faq_enabled',
  'doc_recommend',
  'knowledge_enabled',
  'knowledge_top_k',
  'knowledge_min_score',
  'knowledge_embedding_provider',
  'knowledge_embedding_model',
]

const basicKeys = computed(() => configOrder.filter(k => configMeta[k]?.group === 'basic'))
const knowledgeKeys = computed(() => configOrder.filter(k => configMeta[k]?.group === 'knowledge'))

async function fetchConfigs() {
  try {
    const res = await api.get('/admin/ai/config')
    configs.value = res.data.list
    for (const c of configs.value) {
      form.value[c.config_key] = c.config_value
    }
  } catch { /* handled */ }
}

async function save(key: string) {
  savingKey.value = key
  try {
    await api.put(`/admin/ai/config/${key}`, { value: form.value[key] })
    ElMessage.success(`${configMeta[key]?.label || key} 已更新`)
  } catch { /* handled */ } finally {
    savingKey.value = ''
  }
}

async function saveAll() {
  for (const key of configOrder) {
    if (form.value[key] !== undefined) {
      try { await api.put(`/admin/ai/config/${key}`, { value: form.value[key] }) } catch { /* ignore */ }
    }
  }
  ElMessage.success('全部配置已保存')
}

onMounted(fetchConfigs)
</script>

<template>
  <div class="space-y-4">
    <!-- 顶部操作栏 -->
    <div class="ac-toolbar">
      <div class="ac-toolbar-title">AI 配置</div>
      <div class="ac-toolbar-actions">
        <el-button size="default" @click="fetchConfigs">重置</el-button>
        <el-button size="default" type="primary" @click="saveAll">保存全部</el-button>
      </div>
    </div>

    <!-- 基础配置 -->
    <div class="ac-card">
      <div class="ac-card-header">
        <div class="ac-card-title">基础配置</div>
        <div class="ac-card-subtitle">对话推理相关参数</div>
      </div>
      <div class="ac-grid">
        <div v-for="key in basicKeys" :key="key" class="ac-field" :class="configMeta[key]?.fullWidth ? 'ac-field-full' : ''">
          <div class="ac-field-label">
            <span>{{ configMeta[key]?.label }}</span>
            <span class="ac-field-key">{{ key }}</span>
          </div>
          <el-input v-if="configMeta[key]?.type === 'textarea'" v-model="form[key]" type="textarea" :rows="4" resize="vertical" />
          <el-select v-else-if="configMeta[key]?.type === 'select'" v-model="form[key]" class="w-full">
            <el-option v-for="opt in configMeta[key]?.options || []" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-input v-else v-model="form[key]" />
          <div class="ac-field-hint">{{ configMeta[key]?.hint }}</div>
          <div class="ac-field-actions">
            <el-button size="small" :loading="savingKey === key" @click="save(key)">保存</el-button>
          </div>
        </div>
      </div>
    </div>

    <!-- 知识库配置 -->
    <div class="ac-card">
      <div class="ac-card-header">
        <div class="ac-card-title">知识库配置</div>
        <div class="ac-card-subtitle">向量检索与 Embedding 参数</div>
      </div>
      <div class="ac-grid">
        <div v-for="key in knowledgeKeys" :key="key" class="ac-field">
          <div class="ac-field-label">
            <span>{{ configMeta[key]?.label }}</span>
            <span class="ac-field-key">{{ key }}</span>
          </div>
          <el-select v-if="configMeta[key]?.type === 'select'" v-model="form[key]" class="w-full">
            <el-option v-for="opt in configMeta[key]?.options || []" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
          <el-input v-else v-model="form[key]" />
          <div class="ac-field-hint">{{ configMeta[key]?.hint }}</div>
          <div class="ac-field-actions">
            <el-button size="small" :loading="savingKey === key" @click="save(key)">保存</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ac-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  background: #fff; border: 1px solid #e5e7eb; border-radius: 8px;
  padding: 10px 16px;
}
.ac-toolbar-title { font-size: 14px; font-weight: 600; color: #1f2937; }
.ac-toolbar-actions { display: flex; gap: 8px; }

.ac-card {
  background: #fff;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  overflow: hidden;
}
.ac-card-header {
  padding: 12px 16px;
  border-bottom: 1px solid #e5e7eb;
  background: #fafbfc;
}
.ac-card-title { font-size: 14px; font-weight: 600; color: #1f2937; }
.ac-card-subtitle { font-size: 12px; color: #94a3b8; margin-top: 2px; }

.ac-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.ac-field {
  padding: 14px 16px;
  border-bottom: 1px solid #f1f5f9;
  border-right: 1px solid #f1f5f9;
  position: relative;
}
.ac-field:nth-child(2n) { border-right: none; }
.ac-field-full {
  grid-column: 1 / -1;
  border-right: none;
}
.ac-field-label {
  display: flex; align-items: baseline; justify-content: space-between;
  font-size: 13px; font-weight: 600; color: #374151;
  margin-bottom: 6px;
}
.ac-field-key { font-size: 11px; color: #9ca3af; font-weight: 400; font-family: ui-monospace, monospace; }
.ac-field-hint { font-size: 11px; color: #9ca3af; margin-top: 4px; }
.ac-field-actions { margin-top: 8px; display: flex; justify-content: flex-end; }

@media (max-width: 1024px) {
  .ac-grid { grid-template-columns: 1fr; }
  .ac-field { border-right: none; }
}
</style>
