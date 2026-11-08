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
