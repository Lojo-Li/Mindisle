<template>
<section class="view active" data-view="lamp" ref="rootEl" @click="onClick">

      <div class="page-head" style="padding-bottom:18px">
        <div>
          <div class="eyebrow">AI Companion</div>
          <h1>屿灯</h1>
          <p>岛上那盏一直亮着的灯。不评判，不催促，你说多久都可以。</p>
        </div>
      </div>

      <div class="lamp-shell">
        <div class="sess-list" data-list="sessions">
          <div class="sess-head">
            <div class="sess-label">最近对话</div>
            <button class="sess-new" type="button" @click="newChat" title="开启一段新的对话">＋ 新建</button>
          </div>
          <div
            v-for="s in sessions"
            :key="s.id"
            class="sess"
            :class="{ active: s.id === activeId }"
            @click="open(s.id)"
          >
            <b>{{ s.title || '新的对话' }}</b>
            <span>{{ s.last_message || fmtDate(s.created_at) }}</span>
          </div>
          <div v-if="!sessions.length" class="sess-label">暂无对话</div>
        </div>

        <div class="chat">
          <div class="chat-head">
            <div class="lamp-ava">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>
            </div>
            <div>
              <h4>屿灯</h4>
              <span><i></i>{{ statusText }}</span>
            </div>
            <button class="icon-btn" style="margin-left:auto" title="对话列表"
                    :class="{ on: showSessPanel }" @click="showSessPanel = !showSessPanel">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>
            </button>
          </div>

          <!-- 对话切换面板：窄屏下左侧列表被隐藏，这里是唯一的会话入口 -->
          <div class="sess-panel" v-if="showSessPanel">
            <div class="sp-head">
              <b>最近对话</b>
              <button type="button" @click="newChat">＋ 新建</button>
            </div>
            <div class="sp-list">
              <button v-for="s in sessions" :key="s.id" type="button"
                      class="sp-item" :class="{ active: s.id === activeId }"
                      @click="pickSession(s.id)">
                <b>{{ s.title || '新的对话' }}</b>
                <span>{{ s.last_message || fmtDate(s.created_at) }}</span>
              </button>
              <p class="sp-empty" v-if="!sessions.length">还没有对话</p>
            </div>
          </div>

          <!-- 风险提示：L2 常驻提示卡 / L3 强调卡
               设计原则：不用鲜红和感叹号。危机场景里，刺激的颜色会加剧恐慌，
               这里要传递的是"有人在"而不是"出事了"。 -->
          <div class="risk-slot" v-if="risk && risk.level >= 2 && !(risk.level === 2 && riskDismissed)">
            <div class="risk-note" :class="'l' + risk.level">
              <div class="risk-head">
                <span class="risk-mark" aria-hidden="true">
                  <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/><path d="M9 18h6M10 21h4"/></svg>
                </span>
                <div class="risk-copy">
                  <div class="rt">{{ risk.level >= 3 ? '我先陪你把这一刻稳住' : '听起来你现在不太轻松' }}</div>
                  <div class="rs">
                    {{ risk.level >= 3
                      ? '如果你有伤害自己的念头，先不用一个人扛。下面这些电话 24 小时有人接，不需要你解释太多。'
                      : '这些热线 24 小时免费，随时可以打。也可以先看看，此刻能为自己做点什么。' }}
                  </div>
                </div>
              </div>

              <div class="risk-calls">
                <a v-for="h in hotlines.slice(0, 2)" :key="h.number" class="risk-call" :href="'tel:' + h.number">
                  <i>{{ h.name }}</i><b>{{ h.number }}</b>
                </a>
              </div>

              <div class="risk-act">
                <button class="risk-btn" data-go="booking">找人聊聊</button>
                <button class="risk-btn ghost" @click="showHelps = !showHelps">
                  {{ showHelps ? '收起' : '看看能做什么' }}
                </button>
                <button v-if="risk.level >= 3" class="risk-btn ghost" @click="showModal = true">全部求助方式</button>
              </div>

              <div class="risk-help" v-if="showHelps">
                <p>现在就能做的三件小事，选一件就行：</p>
                <ol>
                  <li><b>把脚踩实。</b>感受脚底和地面的接触，慢慢数 10 次呼吸。</li>
                  <li><b>喝口温水。</b>让身体先慢下来，情绪会跟着松一点。</li>
                  <li><b>写下此刻。</b>一句话就够，写完不用给任何人看。</li>
                </ol>
              </div>

              <!-- L2 允许"先自己待会儿"，但把热线缩成一行留在原地，
                   尊重自主性的同时不撤掉求助通道 -->
              <button class="risk-later" v-if="risk.level === 2" @click="riskDismissed = true">先自己待会儿</button>
            </div>
          </div>
          <div class="risk-slot" v-else-if="risk && risk.level === 2 && riskDismissed">
            <div class="risk-mini">
              <span>需要的时候，这两个号码一直都在</span>
              <a :href="'tel:' + hotlines[0].number">{{ hotlines[0].number }}</a>
              <button @click="riskDismissed = false">展开</button>
            </div>
          </div>
          <div class="risk-slot" v-else-if="risk && risk.level === 1">
            <div class="risk-note l1">
              如果这种状态已经持续两周以上，找专业咨询师聊一次会比独自扛着更好。
            </div>
          </div>

          <div class="chat-body" id="chatBody" ref="chatBodyEl">
            <div v-for="(m, i) in messages" :key="i" class="msg" :class="m.role === 'user' ? 'me' : 'ai'">
              <div class="mini">
                <template v-if="m.role === 'user'">{{ userInitial }}</template>
                <svg v-else width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>
              </div>
              <div class="msg-body">
                <div class="bubble" :class="{ typing: m.typing }">
                  <template v-if="m.typing"><i></i><i></i><i></i></template>
                  <template v-else>{{ m.content }}</template>
                </div>
                <!-- 等待本身会让人焦虑，首字超过 3 秒时先给一句话 -->
                <p class="slow-hint" v-if="m.typing && m.slowHint">我在，慢慢说，不用急着组织语言。</p>

                <!-- 引用来源：能核对到原文，才算"有依据"。
                     历史消息的来源按需拉取，所以即使还没加载也要给入口，
                     否则"点开才加载"的按钮永远不会出现。 -->
                <template v-if="m.sources.length || (m.canLoadSrc && !m.srcLoaded)">
                  <button class="src-toggle" type="button" @click="toggleSources(m)">
                    <span class="dot"></span>
                    <template v-if="m.sources.length">依据 · <b>{{ m.sources.length }}</b> 条
                      <span class="src-avg">{{ avgScore(m) }}%</span>
                    </template>
                    <template v-else>查看依据</template>
                  </button>
                  <div class="src-panel" v-show="m.showSrc">
                    <div class="src-item" v-for="(s, j) in m.sources" :key="j">
                      <div class="src-top">
                        <b>{{ s.title || '心理知识片段' }}</b>
                        <span class="src-score">{{ Math.round((s.score || 0) * 100) }}%</span>
                      </div>
                      <div class="src-bar"><i :style="{ width: Math.round((s.score || 0) * 100) + '%' }"></i></div>
                      <p>{{ s.snippet }}</p>
                    </div>
                    <div class="src-foot">回答由 AI 转述知识库条目，可对照原文核对。</div>
                  </div>
                </template>
                <!-- 负向证明：没检索到依据时直接说，不假装有 -->
                <div class="src-none" v-else-if="m.noSource">
                  <span class="dot"></span>这条回答没有检索到直接依据，是通用回应
                </div>

                <!-- 答案反馈：点"没有"再问一句哪里不对，否则数据进库也没法用 -->
                <div class="msg-fb" v-if="m.messageId && !m.typing">
                  <span v-if="m.feedback" class="done">谢谢你的反馈，会用来改进</span>
                  <template v-else-if="m.askReason">
                    <span>哪里不太对</span>
                    <button v-for="r in FEEDBACK_REASONS" :key="r" type="button"
                            @click="sendFeedback(m, -1, r)">{{ r }}</button>
                    <button type="button" class="skip" @click="m.askReason = false">跳过</button>
                  </template>
                  <template v-else>
                    <span>这条回答有帮助吗</span>
                    <button type="button" @click="sendFeedback(m, 1)">有</button>
                    <button type="button" @click="m.askReason = true">没有</button>
                  </template>
                </div>
              </div>
            </div>

            <!-- 空态：情绪困扰的人最难的是"开口"，空白输入框是最高的门槛 -->
            <div v-if="!messages.length && !loading" class="empty-state">
              <div class="empty-lead">
                <h3>不用先想好怎么开口</h3>
                <p>选一个最接近此刻的，剩下的我们慢慢说。</p>
              </div>
              <div class="entry-list">
                <button v-for="e in ENTRIES" :key="e.key" class="entry" type="button" @click="send(e.opener)">
                  <span class="entry-ico" v-html="e.icon"></span>
                  <span class="entry-text"><b>{{ e.title }}</b><i>{{ e.desc }}</i></span>
                  <span class="entry-arrow">→</span>
                </button>
              </div>
              <p class="empty-note" v-if="lastSessionTitle">
                上次你聊到「{{ lastSessionTitle }}」，也可以接着说。
              </p>
            </div>
          </div>

          <div class="chat-foot">
            <div class="chips">
              <button class="chip" v-for="c in chips" :key="c" @click="send(c)">{{ c }}</button>
            </div>
            <div class="composer">
              <input
                id="chatInput"
                v-model="draft"
                placeholder="写下此刻的感受，随便多少都行…"
                @keyup.enter="sendDraft"
              >
              <button class="send" id="chatSend" title="发送" @click="sendDraft">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12h14M12.5 5.5 19 12l-6.5 6.5"/></svg>
              </button>
            </div>
            <p class="ai-disclaimer">
              屿灯不是医生。如果你正处于危机中，请立即联系专业机构或拨打
              <a :href="'tel:' + hotlines[0].number">{{ hotlines[0].name }} {{ hotlines[0].number }}</a>。
            </p>
          </div>
        </div>
      </div>

      <!-- L3 阻塞弹层：必须确认才能关闭 -->
      <Teleport to="body">
        <div class="risk-mask" v-if="showModal" role="dialog" aria-modal="true">
          <div class="risk-modal">
            <div class="ico">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <path d="M12 9v4M12 17h.01"/><path d="M10.3 3.9 1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/>
              </svg>
            </div>
            <h3>你的安全最重要</h3>
            <p>你刚才说的话让我有点担心你。在继续之前，先把几个能立刻联系到人的方式放在这里。</p>
            <p class="strong">这些电话 24 小时有人接，不需要你说明太多，也不用先想好怎么开口。</p>
            <div class="risk-calls">
              <a v-for="h in hotlines" :key="h.number" class="risk-call" :href="'tel:' + h.number">
                <i>{{ h.name }}</i><b>{{ h.number }}</b>
              </a>
            </div>
            <label class="confirm">
              <input type="checkbox" v-model="modalConfirmed">
              <span>我知道了，可以先看这些求助方式</span>
            </label>
            <button class="ok" :disabled="!modalConfirmed" @click="closeModal">
              {{ modalConfirmed ? '继续对话' : '请先确认你已看到上面的信息' }}
            </button>
            <p class="fine">AI 无法替代专业帮助。若你正处于危险中，请立即拨打 110 或 120。</p>
          </div>
        </div>
      </Teleport>

</section>
</template>

<script setup>
import { ref, reactive, computed, onMounted, nextTick } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { getChatList, createChat, getChatDetail } from '@/api/chat'
import { streamChat, getMessageSources, submitFeedback } from '@/api/aiSupport'
import { pickList, pickData, fmtDate, toast, go } from '../workspace'

/* ---------------- 常量 ---------------- */
const CHIPS = ['我有点焦虑', '我睡不好', '觉得很空', '今天还不错']

// 空态的三个入口：点一下直接带一句开场，省掉"不知道说什么"这一步
const ENTRIES = [
  {
    key: 'sleep',
    title: '睡不着',
    desc: '躺下以后脑子停不下来',
    opener: '最近总是睡不着，一躺下脑子就停不下来，越想睡越清醒。',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 13.3A8.5 8.5 0 1 1 10.7 3.5a6.8 6.8 0 0 0 9.8 9.8z"/></svg>'
  },
  {
    key: 'messy',
    title: '心里很乱',
    desc: '说不清在烦什么，就是静不下来',
    opener: '心里很乱，说不清具体在烦什么，但就是静不下来，坐也坐不住。',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9c2.5-3 5-3 7.5 0s5 3 7.5 0 3-1.5 3-1.5"/><path d="M3 15c2.5-3 5-3 7.5 0s5 3 7.5 0 3-1.5 3-1.5"/></svg>'
  },
  {
    key: 'stuck',
    title: '不知道从哪说起',
    desc: '没准备好也没关系',
    opener: '我不知道该从哪里说起，可能只是需要有人陪我说说话。',
    icon: '<svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12a8 8 0 0 1-11.6 7.1L4 20.5l1.4-5A8 8 0 1 1 21 12z"/></svg>'
  }
]

// 点"没有"之后追问原因，这些是能反哺知识库的信号
const FEEDBACK_REASONS = ['太长', '不相关', '不像在跟我说话']

// 后端不可达或事件缺失时的兜底热线
const HOTLINES = [
  { name: '全国心理援助热线', number: '12356' },
  { name: '北京心理危机研究与干预中心', number: '010-82951332' },
  { name: '希望 24 热线', number: '400-161-9995' }
]

/* ---------------- 本地风险兜底判定 ----------------
 * 后端会下发 risk 事件，但网络异常时不能什么都等后端。
 * 规则与后端 crisis_service 同源，只保留最小必要集。
 */
const L3 = ['自杀', '自尽', '轻生', '割腕', '服毒', '上吊', '跳楼', '跳河', '跳江',
  '卧轨', '结束生命', '结束自己', '了结自己', '不想活了', '活不下去了', '不想活']
const L2 = ['自残', '自伤', '伤害自己', '想死', '死了算了', '死了好',
  '撑不下去', '撑不住了', '熬不下去', '扛不住', '受不了了',
  '绝望', '崩溃', '生不如死', '痛不欲生', '生无可恋']
const L1 = ['没有希望', '看不到希望', '一片黑暗', '毫无意义', '活着没意思',
  '没有意义', '一无所有', '麻木']
const FALSE_POSITIVE = ['笑死', '累死', '气死', '热死', '冷死', '困死', '吓死', '烦死', '饿死']
const NEGATIONS = ['不', '没', '没有', '别', '未曾', '尚未', '并未', '并不', '不再']
const SEPARATORS = '，,。.！!？?；;、\n'

function isNegated(text, start) {
  let w = text.slice(Math.max(0, start - 8), start)
  for (const sep of SEPARATORS) {
    const idx = w.lastIndexOf(sep)
    if (idx >= 0) w = w.slice(idx + 1)
  }
  return NEGATIONS.some(n => w.includes(n))
}

function detectRisk(raw) {
  if (!raw) return { level: 0, keywords: [] }
  let text = raw.replace(/\s/g, '')
  FALSE_POSITIVE.forEach(p => { text = text.split(p).join('') })
  let level = 0
  const hits = []
  for (const [lv, list] of [[3, L3], [2, L2], [1, L1]]) {
    for (const kw of list) {
      const idx = text.indexOf(kw)
      if (idx < 0) continue
      if (isNegated(text, idx)) continue
      if (!hits.includes(kw)) hits.push(kw)
      if (lv > level) level = lv
    }
  }
  return { level, keywords: hits }
}

/* ---------------- 状态 ---------------- */
const rootEl = ref(null)
const chatBodyEl = ref(null)
const router = useRouter()
const route = useRoute()

const sessions = ref([])
const activeId = ref(null)
const messages = ref([])
const draft = ref('')
const loading = ref(false)
const chips = CHIPS

const risk = ref(null)          // { level, keywords, hotlines }
const showModal = ref(false)
const modalConfirmed = ref(false)
const hotlines = ref(HOTLINES)
const riskDismissed = ref(false)  // L2：用户选了"先自己待会儿"
const showHelps = ref(false)      // 自助动作是否展开
const ackedLevel = ref(0)         // 本轮消息里用户已确认过的风险等级
const userInitial = ref('我')
const sending = ref(false)
const showSessPanel = ref(false)   // 对话切换面板

const statusText = computed(() => (sending.value ? '正在回应…' : '在线 · 正在听'))

// 空态里提示"上次聊到…"，让空白页有一点延续感
const lastSessionTitle = computed(() => {
  const s = sessions.value.find(
    x => x.id !== activeId.value && x.title && x.title !== '新的对话'
  )
  return s ? s.title : ''
})

/* ---------------- 会话 ---------------- */
onMounted(async () => {
  try {
    sessions.value = pickList(await getChatList())
    if (!sessions.value.length) {
      const c = pickData(await createChat({ title: '新的对话' }))
      sessions.value = [{ id: c.id, title: c.title || '新的对话', created_at: c.created_at }]
    }
    await open(sessions.value[0].id)
    applyContextFromQuery()
  } catch (e) {
    toast('对话加载失败，请确认后端已启动')
  }
})

async function open(id) {
  activeId.value = id
  showSessPanel.value = false
  loading.value = true
  messages.value = []
  risk.value = null
  riskDismissed.value = false
  showHelps.value = false
  try {
    const d = pickData(await getChatDetail(id))
    messages.value = (d.messages || []).map(m => ({
      role: m.role,
      content: m.content,
      messageId: m.role === 'assistant' ? m.id : null,
      sources: [],
      showSrc: false,
      // 历史消息的来源还没拉取，先给"查看依据"入口
      canLoadSrc: m.role === 'assistant' && !!m.id,
      srcLoaded: false,
      noSource: false,
      feedback: 0,
      askReason: false,
      typing: false
    }))
    scrollBottom()
  } catch (e) {
    toast('消息加载失败')
  } finally {
    loading.value = false
  }
}

/* ---------------- 新建 / 切换对话 ---------------- */
async function newChat() {
  showSessPanel.value = false
  // 当前这段对话本来就是空的，直接复用，避免连点几次堆出一堆空会话
  if (activeId.value && messages.value.length === 0) {
    focusInput()
    return
  }
  try {
    const c = pickData(await createChat({ title: '新的对话' }))
    sessions.value.unshift({
      id: c.id,
      title: c.title || '新的对话',
      created_at: c.created_at
    })
    await open(c.id)
    focusInput()
  } catch (e) {
    toast('新建对话失败，请稍后再试')
  }
}

function pickSession(id) {
  showSessPanel.value = false
  if (id !== activeId.value) open(id)
}

function focusInput() {
  nextTick(() => rootEl.value?.querySelector('#chatInput')?.focus())
}

/* ---------------- 发送 ---------------- */
async function send(text) {
  const content = String(text || '').trim()
  if (!content || !activeId.value || sending.value) return

  // ① 本地同步判定：危险信号先上屏，不等网络
  ackedLevel.value = 0
  const local = detectRisk(content)
  if (local.level) applyRisk({ level: local.level, keywords: local.keywords, hotlines: HOTLINES })

  messages.value.push({ role: 'user', content, messageId: null, sources: [] })
  const reply = reactive({
    role: 'assistant', content: '', messageId: null,
    sources: [], showSrc: false, feedback: 0, askReason: false,
    typing: true, slowHint: false, noSource: false
  })
  messages.value.push(reply)
  scrollBottom()

  // 首字超过 3 秒先给一句安抚，避免干等三个点
  const slowTimer = setTimeout(() => {
    if (reply.typing) reply.slowHint = true
  }, 3000)

  sending.value = true
  try {
    await streamChat(activeId.value, content, {
      onRisk(r) { applyRisk(r) },
      onSources(list) {
        reply.sources = list || []
        reply.gotSources = true
      },
      onContent(chunk) {
        if (reply.typing) reply.typing = false
        reply.content += chunk
        scrollBottom()
      },
      onDone(done) {
        clearTimeout(slowTimer)
        reply.typing = false
        reply.slowHint = false
        if (done.message_id) reply.messageId = done.message_id
        if (!reply.content) reply.content = '我在。慢慢说，不着急。'
        // 后端在无命中时也会下发空的 sources 事件，据此如实标注"无依据"
        if (reply.gotSources && !reply.sources.length && done.message_id) reply.noSource = true
        scrollBottom()
      },
      onTitle(t) {
        const s = sessions.value.find(x => x.id === activeId.value)
        if (s) s.title = t
      }
    })
  } catch (e) {
    clearTimeout(slowTimer)
    reply.typing = false
    reply.slowHint = false
    if (!reply.content) reply.content = '刚才没能连上服务，请稍后再试一次。'
    toast('发送失败：' + (e.message || '网络异常'))
  } finally {
    sending.value = false
    scrollBottom()
  }
}

function sendDraft() {
  const v = draft.value.trim()
  if (!v) return
  draft.value = ''
  send(v)
}

/* ---------------- 风险 ---------------- */
function applyRisk(r) {
  if (!r || !r.level) return
  // 只升不降：已经 L3 就不被后续轻提示覆盖
  if (risk.value && r.level < risk.value.level) return

  const prevLevel = risk.value ? risk.value.level : 0
  risk.value = r
  if (r.hotlines && r.hotlines.length) hotlines.value = r.hotlines
  // 新的风险信号进来时，把"先自己待会儿"的折叠状态复位
  riskDismissed.value = false
  showHelps.value = false

  if (r.level >= 3) {
    // 同一条消息里，本地判定会先开弹层、后端 risk 事件随后再到一次。
    // 用户已经确认过的同类风险，不再重复弹出、也不清掉勾选。
    const duplicate = prevLevel === r.level && ackedLevel.value >= r.level
    if (!duplicate) {
      modalConfirmed.value = false
      showModal.value = true
    }
  }
}

function closeModal() {
  if (!modalConfirmed.value) return
  showModal.value = false
  ackedLevel.value = risk.value ? risk.value.level : 0
}

/* ---------------- 引用与反馈 ---------------- */
// 平均相似度：让"这条回答有多靠得住"一眼可见
function avgScore(m) {
  if (!m.sources || !m.sources.length) return 0
  const sum = m.sources.reduce((a, s) => a + (s.score || 0), 0)
  return Math.round((sum / m.sources.length) * 100)
}

async function toggleSources(m) {
  m.showSrc = !m.showSrc
  if (m.showSrc && !m.srcLoaded && m.messageId) {
    try {
      const res = await getMessageSources(m.messageId)
      m.sources = res?.data?.sources || []
    } catch (e) {
      m.sources = []
    }
    m.srcLoaded = true
    // 拉回来是空的，就如实说没有依据，而不是留一个空面板
    if (!m.sources.length) m.noSource = true
    scrollBottom()
  }
}

async function sendFeedback(m, rating, reason) {
  if (!m.messageId) return
  try {
    await submitFeedback({
      message_id: Number(m.messageId),
      rating,
      reason: reason || null
    })
    m.feedback = rating
    m.askReason = false
  } catch (e) {
    toast('反馈提交失败')
  }
}

/* ---------------- 测评上下文 ---------------- */
function applyContextFromQuery() {
  const scale = route.query.scale
  if (!scale) return
  const score = route.query.score
  const label = route.query.label
  draft.value = `我刚做完${scale}${score ? '，' + score + ' 分' : ''}${label ? '（' + label + '）' : ''}。想聊聊这个结果背后具体是什么。`
  nextTick(() => {
    const el = rootEl.value?.querySelector('#chatInput')
    if (el) el.focus()
  })
}

/* ---------------- 事件 ---------------- */
function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) {
    go(g.getAttribute('data-go'), router)
    return
  }
  // 点面板以外的地方收起，避免它一直挡着对话
  if (showSessPanel.value &&
      !e.target.closest('.sess-panel') &&
      !e.target.closest('.chat-head .icon-btn')) {
    showSessPanel.value = false
  }
}

function scrollBottom() {
  nextTick(() => {
    const box = chatBodyEl.value || rootEl.value?.querySelector('#chatBody')
    if (box) box.scrollTop = box.scrollHeight
  })
}
</script>
