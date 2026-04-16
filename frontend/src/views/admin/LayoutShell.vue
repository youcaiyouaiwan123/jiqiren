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
  <div class="flex h-screen bg-slate-100">
    <aside class="admin-sidebar flex shrink-0 flex-col overflow-hidden text-white transition-all duration-200" :class="collapsed ? 'w-20' : 'w-64'">
      <div class="flex h-16 shrink-0 items-center border-b border-white/10" :class="collapsed ? 'justify-center px-0' : 'gap-3 px-4'">
        <div class="flex h-10 w-10 items-center justify-center rounded-2xl bg-blue-500/15 text-blue-100 ring-1 ring-white/10">
          <el-icon :size="20"><Setting /></el-icon>
        </div>
        <div v-if="!collapsed" class="min-w-0">
          <div class="truncate text-lg font-semibold tracking-wide text-white">管理后台</div>
          <div class="mt-0.5 text-[11px] text-slate-400">系统控制台</div>
        </div>
      </div>
      <nav class="admin-sidebar-nav flex-1 overflow-y-auto px-3 py-4">
        <div
          v-for="item in menuItems"
          :key="item.path"
          class="admin-menu-item group flex cursor-pointer items-center gap-3 rounded-2xl px-3 py-3 text-sm transition-all duration-200"
          :class="activePath === item.path ? 'is-active bg-gradient-to-r from-blue-500 to-blue-600 text-white shadow-lg ring-1 ring-white/10' : 'text-slate-300 hover:bg-white/5 hover:text-white'"
          @click="navigate(item.path)"
        >
          <span class="admin-menu-icon shrink-0">
            <el-icon :size="18"><component :is="item.icon" /></el-icon>
          </span>
          <span v-if="!collapsed" class="min-w-0 flex-1 truncate font-medium">{{ item.label }}</span>
        </div>
      </nav>
      <div class="shrink-0 border-t border-white/10 p-3">
        <button class="admin-collapse-btn w-full rounded-xl border border-white/10 bg-white/5 py-2.5 text-sm font-medium text-slate-300 transition hover:border-white/15 hover:bg-white/10 hover:text-white" @click="collapsed = !collapsed">
          {{ collapsed ? '展开' : '收起导航' }}
        </button>
      </div>
    </aside>

    <div class="flex min-w-0 flex-1 flex-col overflow-hidden">
      <header class="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 bg-white/90 px-6 shadow-sm backdrop-blur">
        <h1 class="text-base font-semibold text-gray-700">
          {{ menuItems.find(m => m.path === activePath)?.label || '管理后台' }}
        </h1>
        <div class="flex items-center gap-3">
          <span class="text-sm text-gray-500">{{ adminStore.admin?.username || 'admin' }}</span>
          <el-button size="small" text type="danger" @click="handleLogout">退出</el-button>
        </div>
      </header>
      <main class="flex-1 overflow-y-auto bg-slate-100 p-6">
        <RouterView />
      </main>
    </div>
  </div>
</template>

<style scoped>
.admin-sidebar {
  background: linear-gradient(180deg, #182337 0%, #0f172a 100%);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.22);
}

.admin-sidebar-nav {
  scrollbar-width: thin;
  scrollbar-color: rgba(148, 163, 184, 0.45) transparent;
}

.admin-sidebar-nav::-webkit-scrollbar {
  width: 8px;
}

.admin-sidebar-nav::-webkit-scrollbar-track {
  background: transparent;
}

.admin-sidebar-nav::-webkit-scrollbar-thumb {
  background: rgba(148, 163, 184, 0.42);
  border-radius: 9999px;
  border: 2px solid transparent;
  background-clip: content-box;
}

.admin-sidebar-nav::-webkit-scrollbar-thumb:hover {
  background: rgba(148, 163, 184, 0.62);
  border: 2px solid transparent;
  background-clip: content-box;
}

.admin-menu-item {
  margin-bottom: 6px;
}

.admin-menu-icon {
  display: flex;
  height: 36px;
  width: 36px;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  background: rgba(255, 255, 255, 0.04);
  transition: transform 0.2s ease, background 0.2s ease, border-color 0.2s ease;
}

.admin-menu-item:hover .admin-menu-icon {
  transform: translateY(-1px);
  border-color: rgba(255, 255, 255, 0.08);
  background: rgba(255, 255, 255, 0.08);
}

.admin-menu-item.is-active .admin-menu-icon {
  border-color: rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.14);
}

.admin-collapse-btn {
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
