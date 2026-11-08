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
          <div class="sess-label">今天</div>
          <div class="sess active">
            <b>睡前那些停不下来的念头</b>
            <span>刚刚</span>
          </div>
          <div class="sess">
            <b>工作汇报前的紧绷</b>
            <span>今天 09:12</span>
          </div>
          <div class="sess-label">过去 7 天</div>
          <div class="sess">
            <b>和朋友的那次不愉快</b>
            <span>昨天</span>
          </div>
          <div class="sess">
            <b>我好像很久没有开心过了</b>
            <span>11月3日</span>
          </div>
          <div class="sess">
            <b>关于「我够不够好」</b>
            <span>11月1日</span>
          </div>
        </div>

        <div class="chat">
          <div class="chat-head">
            <div class="lamp-ava">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"><path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5.9 1.2.9 1.9v.3h5.4v-.3c0-.7.3-1.4.9-1.9A6 6 0 0 0 12 3z"/></svg>
            </div>
            <div>
              <h4>屿灯</h4>
              <span><i></i>在线 · 正在听</span>
            </div>
            <button class="icon-btn" style="margin-left:auto" title="更多">
              <svg width="15" height="15" viewBox="0 0 24 24" fill="currentColor"><circle cx="5" cy="12" r="1.8"/><circle cx="12" cy="12" r="1.8"/><circle cx="19" cy="12" r="1.8"/></svg>
            </button>
          </div>

          <div class="chat-body" id="chatBody">
            <div class="msg ai">
              <div class="mini">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>
              </div>
              <div class="bubble">晚上好，林深。今天过得怎么样？
如果一时说不清楚，也可以只告诉我一个词。</div>
            </div>
            <div class="msg me">
              <div class="mini">林</div>
              <div class="bubble">有点累，说不上来为什么。事情其实都做完了。</div>
            </div>
            <div class="msg ai">
              <div class="mini">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"><path d="M12 3a6 6 0 0 0-3.6 10.8"/><path d="M15.6 13.8A6 6 0 0 0 12 3"/><path d="M9 18h6M10 21h4"/></svg>
              </div>
              <div class="bubble">"事情都做完了，却还是累"——这种累通常不是身体欠的觉，而是心里一直在待命。

你最近是不是很久没有那种"完全不用负责"的时刻了？</div>
            </div>
            <div class="msg me">
              <div class="mini">林</div>
              <div class="bubble">好像是。周末也总觉得该做点什么。</div>
            </div>
          </div>

          <div class="chat-foot">
            <div class="chips">
              <button class="chip" data-chip="我有点焦虑">我有点焦虑</button>
              <button class="chip" data-chip="我睡不好">我睡不好</button>
              <button class="chip" data-chip="觉得很空">觉得很空</button>
              <button class="chip" data-chip="今天还不错">今天还不错</button>
            </div>
            <div class="composer">
              <input id="chatInput" placeholder="写下此刻的感受，随便多少都行…">
              <button class="send" id="chatSend" title="发送">
                <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 12h14M12.5 5.5 19 12l-6.5 6.5"/></svg>
              </button>
            </div>
            <p style="font-size:11px;color:var(--ink-3);margin-top:10px;text-align:center">
              屿灯不是医生。如果你正处于危机中，请立即联系专业机构或拨打心理援助热线。
            </p>
          </div>
        </div>
      </div>
    
</section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getChatList, createChat, getChatDetail, sendMessage } from '@/api/chat'
import { pickList, pickData, setHtml, sessCard, msgCard, go, toast } from '../workspace'

const rootEl = ref(null)
const router = useRouter()
let sessions = []
let activeId = null

onMounted(async () => {
  try {
    sessions = pickList(await getChatList())
    if (!sessions.length) {
      const c = pickData(await createChat({ title: '新的对话' }))
      sessions = [{ id: c.id, title: c.title || '新的对话', created_at: c.created_at }]
    }
    activeId = sessions[0].id
    renderSessions()
    await open(activeId)
  } catch (e) {
    toast('对话加载失败')
  }
})

function renderSessions() {
  setHtml(rootEl.value, '[data-list="sessions"]',
    '<div class="sess-label">最近对话</div>' + sessions.map(s => sessCard(s, activeId)).join(''))
}

async function open(id) {
  activeId = id
  renderSessions()
  try {
    const d = pickData(await getChatDetail(id))
    const box = rootEl.value.querySelector('#chatBody')
    if (box) {
      box.innerHTML = (d.messages || []).map(msgCard).join('')
      box.scrollTop = box.scrollHeight
    }
  } catch (e) {
    toast('消息加载失败')
  }
}

async function send(text) {
  if (!text || !activeId) return
  const box = rootEl.value.querySelector('#chatBody')
  if (box) {
    box.insertAdjacentHTML('beforeend', msgCard({ role: 'user', content: text }))
    box.scrollTop = box.scrollHeight
  }
  try {
    const reply = pickData(await sendMessage(activeId, { content: text }))
    if (box) {
      box.insertAdjacentHTML('beforeend', msgCard({ role: 'assistant', content: reply.content }))
      box.scrollTop = box.scrollHeight
    }
  } catch (e) {
    toast('发送失败')
  }
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
  const s = e.target.closest('[data-sess]')
  if (s) { open(s.getAttribute('data-sess')); return }
  const chip = e.target.closest('[data-chip]')
  if (chip) { send(chip.getAttribute('data-chip')); return }
  if (e.target.closest('#chatSend')) {
    const input = rootEl.value.querySelector('#chatInput')
    const v = input ? input.value.trim() : ''
    if (v) { send(v); if (input) input.value = '' }
  }
}

</script>
