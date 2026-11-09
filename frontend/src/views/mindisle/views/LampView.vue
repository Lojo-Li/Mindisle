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
          <div class="sess-label">最近对话</div>
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
            <button class="icon-btn" style="margin-left:auto" title="更多">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>
            </button>
          </div>

          <!-- 风险提示：L2 常驻黄条 / L3 红条 -->
          <div class="risk-slot" v-if="risk && risk.level >= 2">
            <div class="risk-note" :class="'l' + risk.level">
              <div class="rt">{{ risk.level >= 3 ? '你的安全最重要' : '我们注意到你现在可能不太好受' }}</div>
              <div>
                {{ risk.level >= 3
                  ? '如果你现在有伤害自己的念头，请先停一停。下面这些电话 24 小时有人接，不需要你解释太多。'
                  : '这些热线 24 小时免费，可以直接打。也可以预约一位咨询师当面聊聊。' }}
              </div>
              <div class="risk-calls">
                <a v-for="h in hotlines" :key="h.number" class="risk-call" :href="'tel:' + h.number">
                  <i>{{ h.name }}</i><b>{{ h.number }}</b>
                </a>
              </div>
              <div class="risk-act">
                <button class="risk-btn" data-go="booking">预约咨询师</button>
                <button v-if="risk.level >= 3" class="risk-btn ghost" @click="showModal = true">查看求助方式</button>
              </div>
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

                <!-- 引用来源 -->
                <template v-if="m.sources && m.sources.length">
                  <button class="src-toggle" type="button" @click="toggleSources(m)">
                    <span class="dot"></span>参考 <b>{{ m.sources.length }}</b> 条知识
                  </button>
                  <div class="src-panel" v-show="m.showSrc">
                    <div class="src-item" v-for="(s, j) in m.sources" :key="j">
                      <b>{{ s.title || '心理知识片段' }}</b>
                      <p>{{ s.snippet }}</p>
                      <span>相似度 {{ Math.round((s.score || 0) * 100) }}%</span>
                    </div>
                    <div class="src-foot">以上为检索到的知识条目，回答由 AI 转述，可对照原文核对。</div>
                  </div>
                </template>

                <!-- 答案反馈 -->
                <div class="msg-fb" v-if="m.messageId && !m.typing">
                  <span v-if="m.feedback" class="done">感谢反馈，会用来改进知识库</span>
                  <template v-else>
                    <span>这条回答有帮助吗</span>
                    <button type="button" @click="sendFeedback(m, 1)">有</button>
                    <button type="button" @click="sendFeedback(m, -1)">没有</button>
                  </template>
                </div>
              </div>
            </div>

            <div v-if="!messages.length && !loading" class="empty-hint">
              说说此刻的感受，随便多少都行。
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
const userInitial = ref('我')
const sending = ref(false)

const statusText = computed(() => (sending.value ? '正在回应…' : '在线 · 正在听'))

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
  loading.value = true
  messages.value = []
  risk.value = null
  try {
    const d = pickData(await getChatDetail(id))
    messages.value = (d.messages || []).map(m => ({
      role: m.role,
      content: m.content,
      messageId: m.role === 'assistant' ? m.id : null,
      sources: [],
      showSrc: false,
      feedback: 0,
      typing: false
    }))
    scrollBottom()
  } catch (e) {
    toast('消息加载失败')
  } finally {
    loading.value = false
  }
}

/* ---------------- 发送 ---------------- */
async function send(text) {
  const content = String(text || '').trim()
  if (!content || !activeId.value || sending.value) return

  // ① 本地同步判定：危险信号先上屏，不等网络
  const local = detectRisk(content)
  if (local.level) applyRisk({ level: local.level, keywords: local.keywords, hotlines: HOTLINES })

  messages.value.push({ role: 'user', content, messageId: null, sources: [] })
  const reply = reactive({
    role: 'assistant', content: '', messageId: null,
    sources: [], showSrc: false, feedback: 0, typing: true
  })
  messages.value.push(reply)
  scrollBottom()

  sending.value = true
  try {
    await streamChat(activeId.value, content, {
      onRisk(r) { applyRisk(r) },
      onSources(list) {
        reply.sources = list || []
      },
      onContent(chunk) {
        if (reply.typing) reply.typing = false
        reply.content += chunk
        scrollBottom()
      },
      onDone(done) {
        reply.typing = false
        if (done.message_id) reply.messageId = done.message_id
        if (!reply.content) reply.content = '我在。慢慢说，不着急。'
        scrollBottom()
      },
      onTitle(t) {
        const s = sessions.value.find(x => x.id === activeId.value)
        if (s) s.title = t
      }
    })
  } catch (e) {
    reply.typing = false
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
  risk.value = r
  if (r.hotlines && r.hotlines.length) hotlines.value = r.hotlines
  if (r.level >= 3) {
    modalConfirmed.value = false
    showModal.value = true
  }
}

function closeModal() {
  if (!modalConfirmed.value) return
  showModal.value = false
}

/* ---------------- 引用与反馈 ---------------- */
async function toggleSources(m) {
  m.showSrc = !m.showSrc
  if (m.showSrc && !m.sources.length && m.messageId) {
    try {
      const res = await getMessageSources(m.messageId)
      m.sources = res?.data?.sources || []
    } catch (e) { /* 历史消息无来源时静默 */ }
  }
}

async function sendFeedback(m, rating) {
  if (!m.messageId) return
  try {
    await submitFeedback({ message_id: Number(m.messageId), rating })
    m.feedback = rating
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
  if (g) { go(g.getAttribute('data-go'), router) }
}

function scrollBottom() {
  nextTick(() => {
    const box = chatBodyEl.value || rootEl.value?.querySelector('#chatBody')
    if (box) box.scrollTop = box.scrollHeight
  })
}
</script>
