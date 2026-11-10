// 路由配置
import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
const HomePage = () => import('@/views/HomePage.vue')

// 用户认证
const Login = () => import('@/views/auth/Login.vue')
const Register = () => import('@/views/auth/Register.vue')
const ForgotPassword = () => import('@/views/auth/ForgotPassword.vue')

// 智能问答
const ChatIndex = () => import('@/views/chat/ChatIndex.vue')
const ChatDetail = () => import('@/views/chat/ChatDetail.vue')
const TagManage = () => import('@/views/chat/TagManage.vue')

// 心理测试
const TestList = () => import('@/views/test/TestList.vue')
const TestTaking = () => import('@/views/test/TestTaking.vue')
const TestResult = () => import('@/views/test/TestResult.vue')
const TestTrend = () => import('@/views/test/TestTrend.vue')
const ComprehensiveAnalysis = () => import('@/views/test/ComprehensiveAnalysis.vue')

// 个人中心
const Profile = () => import('@/views/profile/Profile.vue')
const ProfileEdit = () => import('@/views/profile/ProfileEdit.vue')
const PrivacySettings = () => import('@/views/profile/PrivacySettings.vue')
const DataStatistics = () => import('@/views/profile/DataStatistics.vue')
const MyFavorites = () => import('@/views/profile/MyFavorites.vue')
const AccountSettings = () => import('@/views/profile/AccountSettings.vue')

// 咨询师预约
const CounselorList = () => import('@/views/counselor/CounselorList.vue')
const CounselorDetail = () => import('@/views/counselor/CounselorDetail.vue')
const CounselorRegister = () => import('@/views/counselor/CounselorRegister.vue')
const CounselorApply = () => import('@/views/counselor/CounselorApply.vue')
const AppointmentForm = () => import('@/views/counselor/AppointmentForm.vue')
const AppointmentManage = () => import('@/views/counselor/AppointmentManage.vue')
const ReviewForm = () => import('@/views/counselor/ReviewForm.vue')
const InquiryChat = () => import('@/views/counselor/InquiryChat.vue')

// 咨询对话
const CounselorOrders = () => import('@/views/consultation/CounselorOrders.vue')
const ConsultationChatUser = () => import('@/views/consultation/ConsultationChatUser.vue')
const ConsultationChatCounselor = () => import('@/views/consultation/ConsultationChatCounselor.vue')

// 心理知识
const KnowledgeList = () => import('@/views/knowledge/KnowledgeList.vue')
const KnowledgeDetail = () => import('@/views/knowledge/KnowledgeDetail.vue')

// 通知
const NotificationCenter = () => import('@/views/notification/NotificationCenter.vue')

// 后台管理
const AdminLayout = () => import('@/layouts/AdminLayout.vue')
const Dashboard = () => import('@/views/admin/Dashboard.vue')
const CounselorReview = () => import('@/views/admin/CounselorReview.vue')
const CounselorManage = () => import('@/views/admin/CounselorManage.vue')
const KnowledgeManage = () => import('@/views/admin/KnowledgeManage.vue')
const ArticleEditor = () => import('@/views/admin/ArticleEditor.vue')
const UserManage = () => import('@/views/admin/UserManage.vue')
const OrderManage = () => import('@/views/admin/OrderManage.vue')
const TestManage = () => import('@/views/admin/TestManage.vue')
const DialogueManage = () => import('@/views/admin/DialogueManage.vue')
const RiskManage = () => import('@/views/admin/RiskManage.vue')
const SystemManage = () => import('@/views/admin/SystemManage.vue')

// 心屿 Mindisle 设计稿组件
const MindisleLanding = () => import('@/views/mindisle/LandingPage.vue')
const MindislePortal = () => import('@/views/mindisle/PortalPage.vue')
const MindisleLogin = () => import('@/views/auth/MindisleLogin.vue')

// 心屿工作台（阶段四：路由级组件 + 真实接口）
const MindisleShell = () => import('@/views/mindisle/MindisleShell.vue')
const OverviewView = () => import('@/views/mindisle/views/OverviewView.vue')
const AssessmentView = () => import('@/views/mindisle/views/AssessmentView.vue')
const QuizView = () => import('@/views/mindisle/views/QuizView.vue')
const ResultView = () => import('@/views/mindisle/views/ResultView.vue')
const LampView = () => import('@/views/mindisle/views/LampView.vue')
const BookingView = () => import('@/views/mindisle/views/BookingView.vue')
const RecordsView = () => import('@/views/mindisle/views/RecordsView.vue')
const TrendView = () => import('@/views/mindisle/views/TrendView.vue')
const CounselorOverview = () => import('@/views/mindisle/views/CounselorOverview.vue')

const routes = [
  {
    // 默认入口：心屿登录首页（全屏 LandingPage，隐藏通用顶部导航）
    path: '/',
    name: 'HomePage',
    component: MindisleLogin,
    meta: { title: '心屿 Mindisle · 欢迎回来', hideHeader: true }
  },
  {
    // 保留原营销首页，供其他成员继续测试，不影响其余板块
    path: '/home',
    name: 'MarketingHome',
    component: HomePage,
    meta: { title: '首页 - 心屿 Mindisle' }
  },
  {
    path: '/workspace',
    component: MindisleShell,
    props: { role: 'user' },
    meta: { requiresAuth: true, hideHeader: true, crumb: '概览' },
    children: [
      { path: '', redirect: '/workspace/home' },
      { path: 'home', name: 'WorkspaceHome', component: OverviewView, meta: { title: '概览 - 心屿 Mindisle', crumb: '概览' } },
      { path: 'assess', name: 'WorkspaceAssess', component: AssessmentView, meta: { title: '心理测评 - 心屿 Mindisle', crumb: '心理测评' } },
      { path: 'quiz/:id', name: 'WorkspaceQuiz', component: QuizView, meta: { title: '正在测评 - 心屿 Mindisle', crumb: '心理测评' } },
      { path: 'result/:id', name: 'WorkspaceResult', component: ResultView, meta: { title: '测评结果 - 心屿 Mindisle', crumb: '测评结果' } },
      { path: 'lamp', name: 'WorkspaceLamp', component: LampView, meta: { title: '屿灯 - 心屿 Mindisle', crumb: '屿灯' } },
      { path: 'booking', name: 'WorkspaceBooking', component: BookingView, meta: { title: '咨询预约 - 心屿 Mindisle', crumb: '咨询预约' } },
      { path: 'records', name: 'WorkspaceRecords', component: RecordsView, meta: { title: '我的记录 - 心屿 Mindisle', crumb: '我的记录' } },
      { path: 'trend/:id?', name: 'WorkspaceTrend', component: TrendView, meta: { title: '测评趋势 - 心屿 Mindisle', crumb: '测评趋势' } }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: MindisleLogin,
    meta: { title: '登录 - 心屿 Mindisle', requiresGuest: true, hideHeader: true }
  },
  {
    path: '/register',
    name: 'Register',
    component: Register,
    meta: { title: '注册 - 心屿 Mindisle', requiresGuest: true, hideHeader: true }
  },
  {
    path: '/forgot-password',
    name: 'ForgotPassword',
    component: ForgotPassword,
    meta: { title: '忘记密码 - 心屿 Mindisle', requiresGuest: true, hideHeader: true }
  },
  {
    path: '/chat',
    name: 'ChatIndex',
    component: ChatIndex,
    meta: { title: '智能问答 - 心屿 Mindisle', requiresAuth: true, hideHeader: true }
  },
  {
    path: '/chat/:id',
    name: 'ChatDetail',
    component: ChatDetail,
    meta: { title: '对话详情 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/chat/tags',
    name: 'TagManage',
    component: TagManage,
    meta: { title: '标签管理 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/test',
    name: 'TestList',
    component: TestList,
    meta: { title: '心理测试 - 心屿 Mindisle' }
  },
  {
    path: '/test/:id/taking',
    name: 'TestTaking',
    component: TestTaking,
    meta: { title: '进行测试 - 心屿 Mindisle', requiresAuth: true, hideHeader: true }
  },
  {
    path: '/test/:id/result',
    name: 'TestResult',
    component: TestResult,
    meta: { title: '测试结果 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/test/trend',
    name: 'TestTrend',
    component: TestTrend,
    meta: { title: '测试趋势 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/test/analysis',
    name: 'ComprehensiveAnalysis',
    component: ComprehensiveAnalysis,
    meta: { title: '综合分析 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/profile',
    name: 'Profile',
    component: Profile,
    meta: { title: '个人中心 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/profile/edit',
    name: 'ProfileEdit',
    component: ProfileEdit,
    meta: { title: '编辑资料 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/profile/privacy',
    name: 'PrivacySettings',
    component: PrivacySettings,
    meta: { title: '隐私设置 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/profile/statistics',
    name: 'DataStatistics',
    component: DataStatistics,
    meta: { title: '数据统计 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/profile/favorites',
    name: 'MyFavorites',
    component: MyFavorites,
    meta: { title: '我的收藏 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/profile/account',
    name: 'AccountSettings',
    component: AccountSettings,
    meta: { title: '账号设置 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/counselor',
    name: 'CounselorList',
    component: CounselorList,
    meta: { title: '找咨询师 - 心屿 Mindisle' }
  },
  {
    path: '/counselor/register',
    name: 'CounselorRegister',
    component: CounselorRegister,
    meta: { title: '咨询师入驻 - 心屿 Mindisle', requiresAuth: true, hideHeader: true }
  },
  {
    path: '/counselor/apply',
    name: 'CounselorApply',
    component: CounselorApply,
    meta: { title: '加入我们 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/counselor/dashboard',
    component: MindisleShell,
    props: { role: 'counselor' },
    meta: { title: '咨询师工作台 - 心屿 Mindisle', requiresAuth: true, requiresCounselor: true, hideHeader: true, crumb: '咨询师工作台' },
    children: [
      { path: '', name: 'CounselorOverview', component: CounselorOverview, meta: { title: '咨询师工作台 - 心屿 Mindisle', crumb: '咨询师工作台' } }
    ]
  },
  {
    path: '/counselor/:id',
    name: 'CounselorDetail',
    component: CounselorDetail,
    meta: { title: '咨询师详情 - 心屿 Mindisle' }
  },  {
    path: '/counselor/:counselorId/inquiry',
    name: 'InquiryChat',
    component: InquiryChat,
    meta: { title: '联系咋询师 - 心理咋询平台', requiresAuth: true }
  },  {
    path: '/counselor/appointment',
    name: 'AppointmentForm',
    component: AppointmentForm,
    meta: { title: '预约咨询 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/counselor/orders',
    name: 'AppointmentManage',
    component: AppointmentManage,
    meta: { title: '我的预约 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/counselor/review/:id',
    name: 'ReviewForm',
    component: ReviewForm,
    meta: { title: '评价咨询 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/consultation/counselor/orders',
    name: 'CounselorOrders',
    component: CounselorOrders,
    meta: { title: '咨询师工作台 - 心屿 Mindisle', requiresAuth: true, requiresCounselor: true }
  },
  {
    path: '/consultation/user/:id',
    name: 'ConsultationChatUser',
    component: ConsultationChatUser,
    meta: { title: '咨询对话 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/consultation/counselor/:id',
    name: 'ConsultationChatCounselor',
    component: ConsultationChatCounselor,
    meta: { title: '咨询对话 - 心屿 Mindisle', requiresAuth: true, requiresCounselor: true }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeList',
    component: KnowledgeList,
    meta: { title: '心理知识 - 心屿 Mindisle' }
  },
  {
    path: '/knowledge/:id',
    name: 'KnowledgeDetail',
    component: KnowledgeDetail,
    meta: { title: '知识详情 - 心屿 Mindisle' }
  },
  {
    path: '/notifications',
    name: 'NotificationCenter',
    component: NotificationCenter,
    meta: { title: '消息通知 - 心屿 Mindisle', requiresAuth: true }
  },
  {
    path: '/preview/landing',
    name: 'MindisleLandingPreview',
    component: MindisleLanding,
    meta: { title: '心屿 Mindisle · 界面预览', hideHeader: true }
  },
  {
    path: '/preview/portal',
    name: 'MindislePortalPreview',
    component: MindislePortal,
    meta: { title: '心屿 Mindisle · 工作台预览', hideHeader: true }
  },
  {
    path: '/admin',
    component: AdminLayout,
    meta: { requiresAdmin: true, hideHeader: true },
    children: [
      {
        path: '',
        redirect: '/admin/dashboard'
      },
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '后台管理 - 心屿 Mindisle' }
      },
      {
        path: 'users',
        name: 'UserManage',
        component: UserManage,
        meta: { title: '用户管理 - 心屿 Mindisle' }
      },
      {
        path: 'counselor-review',
        name: 'CounselorReview',
        component: CounselorReview,
        meta: { title: '咨询师审核 - 心屿 Mindisle' }
      },
      {
        path: 'counselors',
        name: 'CounselorManage',
        component: CounselorManage,
        meta: { title: '咨询师管理 - 心屿 Mindisle' }
      },
      {
        path: 'orders',
        name: 'OrderManage',
        component: OrderManage,
        meta: { title: '订单管理 - 心屿 Mindisle' }
      },
      {
        path: 'knowledge',
        name: 'KnowledgeManage',
        component: KnowledgeManage,
        meta: { title: '知识管理 - 心屿 Mindisle' }
      },
      {
        path: 'tests',
        name: 'TestManage',
        component: TestManage,
        meta: { title: '测试管理 - 心屿 Mindisle' }
      },
      {
        path: 'dialogues',
        name: 'DialogueManage',
        component: DialogueManage,
        meta: { title: '对话管理 - 心屿 Mindisle' }
      },
      {
        path: 'risks',
        name: 'RiskManage',
        component: RiskManage,
        meta: { title: '风险工单 - 心理咨询平台' }
      },
      {
        path: 'article-editor',
        name: 'ArticleEditor',
        component: ArticleEditor,
        meta: { title: '文章编辑 - 心屿 Mindisle' }
      },
      {
        path: 'system',
        name: 'SystemManage',
        component: SystemManage,
        meta: { title: '系统设置 - 心屿 Mindisle' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title || '心屿 Mindisle'

  // 取出完整匹配链上的 meta（子路由的 meta 会覆盖父路由，
  // 例如 /admin/dashboard 自身没有 requiresAdmin，需要从父路由继承）
  const metas = to.matched.map((record) => record.meta || {})
  const has = (key) => metas.some((m) => m[key])

  // 获取token和角色（仅从 sessionStorage 读取，保证标签页隔离）
  const token = sessionStorage.getItem('token')
  let userRole = sessionStorage.getItem('userRole')
  if (!userRole) {
    try {
      userRole = JSON.parse(sessionStorage.getItem('userInfo') || 'null')?.role || null
    } catch {
      userRole = null
    }
  }

  // 登录后落地页：按角色进入各自工作台（游客仍看到营销首页）
  if (to.path === '/' && token) {
    if (userRole === 'admin') { next('/admin/dashboard'); return }
    if (userRole === 'counselor') { next('/counselor/dashboard'); return }
    next('/workspace/home')
    return
  }

  // 需要登录的页面
  if (has('requiresAuth') && !token) {
    next('/login')
    return
  }

  // 需要咨询师角色的页面
  if (has('requiresCounselor') && userRole !== 'counselor') {
    next('/')
    return
  }

  // 需要管理员角色的页面
  if (has('requiresAdmin') && userRole !== 'admin') {
    next('/login')
    return
  }

  // 已登录用户访问登录/注册页，跳转首页
  if (to.meta.requiresGuest && token) {
    next('/')
    return
  }

  next()
})

export default router
