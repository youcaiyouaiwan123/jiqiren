import { createRouter, createWebHistory } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/login' },
    { path: '/login', name: 'UserLogin', component: () => import('@/views/user/Login.vue') },
    { path: '/chat', name: 'Chat', component: () => import('@/views/user/Chat.vue'), meta: { requiresAuth: true } },
    { path: '/profile', name: 'UserProfile', component: () => import('@/views/user/Profile.vue'), meta: { requiresAuth: true } },
    { path: '/admin/login', name: 'AdminLogin', component: () => import('@/views/admin/Login.vue') },
    {
      path: '/admin',
      component: () => import('@/views/admin/LayoutShell.vue'),
      meta: { requiresAdmin: true },
      children: [
        { path: '', redirect: '/admin/dashboard' },
        { path: 'dashboard', name: 'AdminDashboard', component: () => import('@/views/admin/Dashboard.vue') },
        { path: 'users', name: 'AdminUsers', component: () => import('@/views/admin/Users.vue') },
        { path: 'llm', name: 'AdminLlm', component: () => import('@/views/admin/LlmProviders.vue') },
        { path: 'ai-config', name: 'AdminAiConfig', component: () => import('@/views/admin/AiConfig.vue') },
        { path: 'knowledge', name: 'AdminKnowledge', component: () => import('@/views/admin/KnowledgeConfig.vue') },
        { path: 'knowledge-files', name: 'AdminKnowledgeFiles', component: () => import('@/views/admin/KnowledgeFiles.vue') },
        { path: 'announcements', name: 'AdminAnnouncements', component: () => import('@/views/admin/Announcements.vue') },
        { path: 'banned-words', name: 'AdminBannedWords', component: () => import('@/views/admin/BannedWords.vue') },
        { path: 'redeem-codes', name: 'AdminRedeemCodes', component: () => import('@/views/admin/RedeemCodes.vue') },
        { path: 'invite-codes', name: 'AdminInviteCodes', component: () => import('@/views/admin/InviteCodes.vue') },
        { path: 'plans', name: 'AdminPlans', component: () => import('@/views/admin/SubscriptionPlans.vue') },
        { path: 'feishu', name: 'AdminFeishu', component: () => import('@/views/admin/FeishuRoutes.vue') },
        { path: 'register', name: 'AdminRegister', component: () => import('@/views/admin/RegisterConfig.vue') },
        { path: 'payment', name: 'AdminPayment', component: () => import('@/views/admin/PaymentChannels.vue') },
        { path: 'payment-orders', name: 'AdminPaymentOrders', component: () => import('@/views/admin/PaymentOrders.vue') },
        { path: 'wecom', name: 'AdminWecom', component: () => import('@/views/admin/WecomConfig.vue') },
        { path: 'expire-reminders', name: 'AdminExpireReminders', component: () => import('@/views/admin/ExpireReminders.vue') },
        { path: 'token-usage', name: 'AdminTokenUsage', component: () => import('@/views/admin/TokenUsage.vue') },
        { path: 'profile', name: 'AdminProfile', component: () => import('@/views/admin/Profile.vue') },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('token')) {
    return '/login'
  }
  if (to.meta.requiresAdmin && !localStorage.getItem('admin_token')) {
    return '/admin/login'
  }
})

export default router
