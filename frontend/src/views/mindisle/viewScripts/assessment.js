import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getTestList } from '@/api/test'
import { pickList, setHtml, scaleCard, filterPill, go, toast } from '../workspace'

const rootEl = ref(null)
const router = useRouter()
let all = []
let current = '全部'

onMounted(async () => {
  try {
    all = pickList(await getTestList({ page: 1, page_size: 50 }))
    const cats = ['全部'].concat(Array.from(new Set(all.map(t => t.category).filter(Boolean))))
    setHtml(rootEl.value, '[data-list="filters"]', cats.map(c => filterPill(c, c === '全部')).join(''))
    render()
  } catch (e) {
    toast('量表列表加载失败')
  }
})

function render() {
  const list = current === '全部' ? all : all.filter(t => t.category === current)
  setHtml(rootEl.value, '[data-list="scales"]', list.length
    ? list.map(scaleCard).join('')
    : '<div class="scale"><h4>暂无量表</h4></div>')
}

function onClick(e) {
  const g = e.target.closest('[data-go]')
  if (g) { go(g.getAttribute('data-go'), router); return }
  const p = e.target.closest('[data-filter]')
  if (p) {
    current = p.getAttribute('data-filter')
    rootEl.value.querySelectorAll('[data-filter]').forEach(x => x.classList.toggle('on', x === p))
    render()
    return
  }
  const s = e.target.closest('[data-start]')
  if (s) router.push('/workspace/quiz/' + s.getAttribute('data-start'))
}
