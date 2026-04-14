<script setup lang="ts">
import CrudTable from '@/components/CrudTable.vue'

const providerOptions = [
  { label: 'Claude', value: 'claude' },
  { label: 'OpenAI / GPT', value: 'openai' },
  { label: 'Gemini', value: 'gemini' },
  { label: '智谱 GLM', value: 'zhipu' },
]

const columns = [
  { prop: 'id', label: 'ID', width: 60 },
  { prop: 'name', label: '名称', width: 120 },
  { prop: 'provider', label: '厂商', width: 100 },
  { prop: 'model', label: '模型', width: 180 },
  { prop: 'api_url', label: 'API 地址' },
  { prop: 'input_price', label: '输入价格', width: 110 },
  { prop: 'output_price', label: '输出价格', width: 110 },
  { prop: 'is_default', label: '默认', width: 70, type: 'switch' as const },
  { prop: 'is_active', label: '启用', width: 70, type: 'switch' as const },
]

const formFields = [
  { key: 'name', label: '名称', required: true },
  { key: 'provider', label: '厂商', type: 'select', options: providerOptions, required: true },
  { key: 'api_url', label: 'API 地址', required: true },
  { key: 'api_key', label: 'API Key', type: 'password' },
  { key: 'model', label: '模型', required: true },
  { key: 'input_price', label: '输入价格 (USD/百万tokens)', placeholder: '如 3.0' },
  { key: 'output_price', label: '输出价格 (USD/百万tokens)', placeholder: '如 15.0' },
  { key: 'is_default', label: '设为默认', type: 'switch' },
  { key: 'is_active', label: '启用', type: 'switch' },
]
</script>

<template>
  <CrudTable api-base="/admin/llm-providers" :columns="columns" :form-fields="formFields" create-btn-label="添加模型" />
</template>
