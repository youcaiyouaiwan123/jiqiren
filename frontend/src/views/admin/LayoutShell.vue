<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAdminStore } from '@/stores/admin'
import { AlarmClock, Bell, ChatDotRound, CircleClose, Cpu, DataAnalysis, Document, EditPen, Key, Medal, Money, Setting, Ticket, TrendCharts, User } from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const adminStore = useAdminStore()
const collapsed = ref(false)

const menuItems = [
  { path: '/admin/dashboard', label: '数据分析', icon: DataAnalysis },
  { path: '/admin/users', label: '用户管理', icon: User },
  { path: '/admin/llm', label: '大模型配置', icon: Cpu },
  { path: '/admin/ai-config', label: 'AI 配置', icon: Setting },
  { path: '/admin/knowledge', label: '知识源配置', icon: Document },
  { path: '/admin/knowledge-files', label: '知识库文档', icon: EditPen },
  { path: '/admin/announcements', label: '公告管理', icon: Bell },
  { path: '/admin/banned-words', label: '禁用词管理', icon: CircleClose },
  { path: '/admin/redeem-codes', label: '兑换码管理', icon: Ticket },
  { path: '/admin/invite-codes', label: '邀请码管理', icon: Key },
  { path: '/admin/plans', label: '套餐管理', icon: Medal },
  { path: '/admin/feishu', label: '飞书配置', icon: Document },
  { path: '/admin/register', label: '注册设置', icon: EditPen },
  { path: '/admin/payment', label: '支付设置', icon: Money },
  { path: '/admin/payment-orders', label: '订单管理', icon: Ticket },
  { path: '/admin/wecom', label: '企微配置', icon: ChatDotRound },
  { path: '/admin/expire-reminders', label: '到期提醒', icon: AlarmClock },
  { path: '/admin/token-usage', label: 'Token 计费', icon: TrendCharts },
]

const activePath = computed(() => route.path)

function navigate(path: string) {
  router.push(path)
}

function handleLogout() {
  adminStore.logout()
  router.push('/admin/login')
}
</script>

<template>
  <div class="flex h-screen bg-gray-100">
    <aside class="flex shrink-0 flex-col bg-slate-800 text-white transition-all duration-200" :class="collapsed ? 'w-16' : 'w-56'">
      <div class="flex h-14 items-center justify-center border-b border-slate-700 shrink-0">
        <span v-if="!collapsed" class="text-base font-bold tracking-wide">管理后台</span>
        <el-icon v-else :size="20"><Setting /></el-icon>
      </div>
      <nav class="flex-1 overflow-y-auto py-2">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="mx-2 my-0.5 flex cursor-pointer items-center rounded-lg px-3 py-2.5 text-sm transition-colors"
          :class="activePath === item.path ? 'bg-blue-600 text-white' : 'text-slate-300 hover:bg-slate-700'"
          @click="navigate(item.path)"
        >
          <el-icon class="shrink-0" :size="18"><component :is="item.icon" /></el-icon>
          <span v-if="!collapsed" class="ml-3 truncate">{{ item.label }}</span>
        </div>
      </nav>
      <div class="border-t border-slate-700 p-3 shrink-0">
        <button class="w-full py-1 text-xs text-slate-400 hover:text-white" @click="collapsed = !collapsed">
          {{ collapsed ? '>' : '< 收起' }}
        </button>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header class="flex h-14 shrink-0 items-center justify-between border-b bg-white px-6 shadow-sm">
        <h1 class="text-base font-semibold text-gray-700">
          {{ menuItems.find(m => m.path === activePath)?.label || '管理后台' }}
        </h1>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500">{{ adminStore.admin?.username || 'admin' }}</span>
          <el-button size="small" text type="danger" @click="handleLogout">退出</el-button>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>
