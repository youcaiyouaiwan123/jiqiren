<script setup lang="ts">
import { ref, onMounted } from 'vue'
import api from '@/utils/api'
import { ElMessage } from 'element-plus'

interface ConfigItem { id: number; config_key: string; config_value: string; description: string | null }

interface ConfigMeta {
  label: string
  type: 'textarea' | 'select' | 'input'
  options?: Array<{ label: string; value: string }>
}

const configs = ref<ConfigItem[]>([])
const form = ref<Record<string, string>>({})

const configMeta: Record<string, ConfigMeta> = {
  system_prompt: { label: 'System Prompt', type: 'textarea' },
  temperature: { label: 'Temperature', type: 'input' },
  max_tokens: { label: 'Max Tokens', type: 'input' },
  faq_enabled: {
    label: 'FAQ 匹配',
    type: 'select',
    options: [
      { label: '开启', value: 'true' },
      { label: '关闭', value: 'false' },
    ],
  },
  doc_recommend: {
    label: '文档推荐',
    type: 'select',
    options: [
      { label: '开启', value: 'true' },
      { label: '关闭', value: 'false' },
    ],
  },
  knowledge_enabled: {
    label: '知识库检索',
    type: 'select',
    options: [
      { label: '开启', value: 'true' },
      { label: '关闭', value: 'false' },
    ],
  },
  knowledge_top_k: { label: '知识召回数量', type: 'input' },
  knowledge_min_score: { label: '知识最低分数', type: 'input' },
  knowledge_embedding_provider: {
    label: 'Embedding 厂商',
    type: 'select',
    options: [
      { label: 'OpenAI', value: 'openai' },
      { label: 'Gemini', value: 'gemini' },
      { label: '智谱', value: 'zhipu' },
    ],
  },
  knowledge_embedding_model: { label: 'Embedding 模型', type: 'input' },
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
  try {
    await api.put(`/admin/ai/config/${key}`, { value: form.value[key] })
    ElMessage.success(`${configMeta[key]?.label || key} 已更新`)
  } catch { /* handled */ }
}

onMounted(fetchConfigs)
</script>

<template>
  <div class="mx-auto max-w-6xl space-y-5 pb-5">
    <div class="rounded-[28px] border border-slate-200 bg-white px-5 py-4 shadow-[0_18px_50px_-34px_rgba(15,23,42,0.16)] sm:px-6">
      <h2 class="text-xl font-semibold tracking-tight text-slate-900">AI 配置</h2>
    </div>

    <div class="grid grid-cols-1 gap-3.5 xl:grid-cols-2">
      <div v-for="key in configOrder" :key="key" class="rounded-[22px] border border-slate-200 bg-white p-4 shadow-sm" :class="key === 'system_prompt' ? 'xl:col-span-2' : ''">
        <div class="flex items-center justify-between gap-2.5">
          <label class="text-sm font-semibold text-slate-700">{{ configMeta[key]?.label }}</label>
          <el-button size="small" type="primary" plain @click="save(key)">保存</el-button>
        </div>
        <div class="mt-2.5">
          <el-input v-if="configMeta[key]?.type === 'textarea'" v-model="form[key]" type="textarea" :rows="3" resize="vertical" />
          <el-select v-else-if="configMeta[key]?.type === 'select'" v-model="form[key]" class="w-full">
            <el-option v-for="option in configMeta[key]?.options || []" :key="option.value" :label="option.label" :value="option.value" />
          </el-select>
          <el-input v-else v-model="form[key]" />
        </div>
      </div>
    </div>
  </div>
</template>
