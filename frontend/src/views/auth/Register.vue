<template>
  <div class="rg-page">
    <!-- 左侧品牌区：沿用首页 LandingPage 的左侧版式（品牌 + 大标题 + 标语 + 标签 + 社会证明） -->
    <aside class="rg-side">
      <div class="rg-side-inner">
        <div class="lp-brand">
          <div class="lp-brand-mark">
            <svg width="23" height="23" viewBox="0 0 24 24" fill="none">
              <path d="M3 17.5c2.2 0 2.6-3.5 4.8-3.5s2.4 2.4 4.4 2.4 2.5-4.2 4.8-4.2c1.4 0 2.4.9 3 1.8" stroke="#fff" stroke-width="1.7" stroke-linecap="round"/>
              <circle cx="16.6" cy="7" r="2.1" fill="#F6D08A"/>
            </svg>
          </div>
          <div>
            <div class="lp-brand-name">心屿</div>
            <div class="lp-brand-en">Mindisle</div>
          </div>
          <span class="lp-brand-tag">心理健康 · 陪伴平台</span>
        </div>

        <div class="lp-hero">
          <div class="lp-eyebrow">A QUIET PLACE FOR YOUR MIND</div>
          <h1 class="lp-title">
            <span class="lp-title-zh">心屿</span>
            <span class="lp-title-en">Mindisle</span>
          </h1>
          <p class="lp-slogan">让每一种情绪，都有处可栖。</p>
          <p class="lp-desc">
            测评是一张地图，屿灯是一盏常亮的灯，咨询是一位愿意同行的人。<br />
            你不必先整理好自己才来到这里——慢慢来，我们等你。
          </p>
          <div class="lp-tags">
            <span class="lp-tag">心理测评</span>
            <span class="lp-tag">屿灯 · AI 情绪支持</span>
            <span class="lp-tag">咨询预约</span>
          </div>
          <div class="lp-social">
            <div class="lp-chips" aria-hidden="true">
              <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="rgc0"><path d="M16 2 A14 14 0 1 1 16 30 A14 14 0 1 1 16 2 Z"/></clipPath></defs><rect width="32" height="32" fill="#C36950" clip-path="url(#rgc0)"/></svg>
              <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="rgc1"><path d="M16 3 L27 8.5 L27 23.5 L16 29 L5 23.5 L5 8.5 Z"/></clipPath></defs><rect width="32" height="32" fill="#A57D46" clip-path="url(#rgc1)"/></svg>
              <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="rgc2"><path d="M16 3 L29 13 L24 28 L8 28 L3 13 Z"/></clipPath></defs><rect width="32" height="32" fill="#558C96" clip-path="url(#rgc2)"/></svg>
              <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="rgc3"><path d="M11 2 L21 2 L30 11 L30 21 L21 30 L11 30 L2 21 L2 11 Z"/></clipPath></defs><rect width="32" height="32" fill="#6E915A" clip-path="url(#rgc3)"/></svg>
              <svg width="28" height="28" viewBox="0 0 32 32"><defs><clipPath id="rgc4"><path d="M5 5 L27 5 L27 27 L5 27 Z"/></clipPath></defs><rect width="32" height="32" fill="#A56982" clip-path="url(#rgc4)"/></svg>
            </div>
            <p>已有 <b>12,000+</b> 人在这里停靠</p>
          </div>
        </div>
      </div>

      <div class="rg-glow rg-glow-a"></div>
      <div class="rg-glow rg-glow-b"></div>
    </aside>

    <!-- 右侧表单 -->
    <main class="rg-main">
      <div class="rg-card">
        <header class="rg-head">
          <h2>创建账户</h2>
          <p>用邮箱注册，几步就能开始</p>
        </header>

        <!-- novalidate：关闭浏览器原生校验，统一走自研校验以保持心屿风格提示 -->
        <form class="rg-form" novalidate @submit.prevent="handleRegister">
          <div class="rg-field">
            <label>邮箱</label>
            <input
              v-model.trim="registerForm.email"
              type="email"
              autocomplete="email"
              placeholder="请输入邮箱，用于接收验证码"
              :class="{ 'is-bad': errors.email }"
              @input="clearErr('email')"
            />
            <p v-if="errors.email" class="rg-err">{{ errors.email }}</p>
          </div>

          <div class="rg-field">
            <label>验证码</label>
            <div class="rg-row">
              <input
                v-model.trim="registerForm.code"
                inputmode="numeric"
                maxlength="6"
                placeholder="6 位数字验证码"
                :class="{ 'is-bad': errors.code }"
                @input="clearErr('code')"
              />
              <button
                type="button"
                class="rg-btn-code"
                :disabled="countdown > 0 || sendingCode"
                @click="sendVerificationCode"
              >
                {{ sendingCode ? '发送中…' : countdown > 0 ? `${countdown}s 后重发` : '获取验证码' }}
              </button>
            </div>
            <p v-if="errors.code" class="rg-err">{{ errors.code }}</p>
          </div>

          <div class="rg-field">
            <label>设置密码</label>
            <div class="rg-row">
              <input
                v-model="registerForm.password"
                :type="showPwd ? 'text' : 'password'"
                autocomplete="new-password"
                placeholder="6-20 位，建议字母+数字组合"
                :class="{ 'is-bad': errors.password }"
                @input="clearErr('password')"
              />
              <button type="button" class="rg-btn-eye" @click="showPwd = !showPwd">
                {{ showPwd ? '隐藏' : '显示' }}
              </button>
            </div>
            <div v-if="registerForm.password" class="rg-strength">
              <div class="rg-bar">
                <i :class="passwordStrength.class" :style="{ width: passwordStrength.width }"></i>
              </div>
              <span :class="passwordStrength.class">{{ passwordStrength.text }}</span>
            </div>
            <p v-if="errors.password" class="rg-err">{{ errors.password }}</p>
          </div>

          <div class="rg-field">
            <label>确认密码</label>
            <input
              v-model="registerForm.confirmPassword"
              :type="showPwd ? 'text' : 'password'"
              autocomplete="new-password"
              placeholder="请再次输入密码"
              :class="{ 'is-bad': errors.confirmPassword }"
              @input="clearErr('confirmPassword')"
            />
            <p v-if="errors.confirmPassword" class="rg-err">{{ errors.confirmPassword }}</p>
          </div>

          <label class="rg-agree" @click.prevent="toggleAgree">
            <span class="rg-cb" :class="{ on: registerForm.agreed }">
              <svg v-if="registerForm.agreed" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 12.5l5 5L20 6.5"/>
              </svg>
            </span>
            <span>我已阅读并同意 <a href="#" @click.stop>《用户协议》</a> 和 <a href="#" @click.stop>《隐私政策》</a></span>
          </label>
          <p v-if="errors.agreed" class="rg-err">{{ errors.agreed }}</p>

          <button type="submit" class="rg-submit" :disabled="loading">
            {{ loading ? '注册中…' : '创建账户' }}
          </button>
        </form>

        <footer class="rg-foot">
          已有账号？<a href="#" @click.prevent="goToLogin">直接登录</a>
        </footer>
      </div>

      <p class="rg-copy">© 2026 心屿 Mindisle · 公益心理健康支持</p>
    </main>

    <transition name="rg-tip">
      <div v-if="tip.show" class="rg-tip" :class="tip.type">{{ tip.text }}</div>
    </transition>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { sendEmailCode } from '@/api/auth'

const router = useRouter()
const userStore = useUserStore()

// 心屿风格轻提示，不依赖 Element Plus
const tip = reactive({ text: '', type: '', show: false })
let tipTimer = null
function toast(text, type = 'info') {
  tip.text = text
  tip.type = type
  tip.show = true
  clearTimeout(tipTimer)
  tipTimer = setTimeout(() => { tip.show = false }, 2600)
}
const tipWarn = (m) => toast(m, 'warn')
const tipOk = (m) => toast(m, 'ok')
const tipErr = (m) => toast(m, 'err')

const loading = ref(false)
const sendingCode = ref(false)
const countdown = ref(0)
const showPwd = ref(false)
let countdownTimer = null

const registerForm = reactive({
  email: '',
  code: '',
  password: '',
  confirmPassword: '',
  agreed: false
})

// 表单错误提示（自行校验，替代 el-form 的 rules）
const errors = reactive({ email: '', code: '', password: '', confirmPassword: '', agreed: '' })
function clearErr(k) { errors[k] = '' }

function toggleAgree() {
  registerForm.agreed = !registerForm.agreed
  if (registerForm.agreed) errors.agreed = ''
}

const passwordStrength = computed(() => {
  const password = registerForm.password
  if (!password) return { width: '0%', text: '', class: '' }
  let strength = 0
  if (password.length >= 6) strength++
  if (password.length >= 10) strength++
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++
  if (/\d/.test(password)) strength++
  if (/[^a-zA-Z0-9]/.test(password)) strength++
  if (strength <= 2) return { width: '33%', text: '弱', class: 'weak' }
  if (strength <= 3) return { width: '66%', text: '中', class: 'medium' }
  return { width: '100%', text: '强', class: 'strong' }
})

const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

function validate() {
  errors.email = ''
  errors.code = ''
  errors.password = ''
  errors.confirmPassword = ''
  errors.agreed = ''

  let ok = true
  if (!registerForm.email) { errors.email = '请输入邮箱'; ok = false }
  else if (!EMAIL_RE.test(registerForm.email)) { errors.email = '请输入正确的邮箱格式'; ok = false }

  if (!registerForm.code) { errors.code = '请输入验证码'; ok = false }
  else if (!/^\d{6}$/.test(registerForm.code)) { errors.code = '验证码应为 6 位数字'; ok = false }

  if (!registerForm.password) { errors.password = '请设置密码'; ok = false }
  else if (registerForm.password.length < 6 || registerForm.password.length > 20) {
    errors.password = '密码长度应为 6-20 位'; ok = false
  }

  if (!registerForm.confirmPassword) { errors.confirmPassword = '请再次输入密码'; ok = false }
  else if (registerForm.confirmPassword !== registerForm.password) {
    errors.confirmPassword = '两次输入的密码不一致'; ok = false
  }

  if (!registerForm.agreed) { errors.agreed = '请阅读并同意用户协议'; ok = false }
  return ok
}

const sendVerificationCode = async () => {
  if (!registerForm.email) { tipWarn('请先输入邮箱地址'); return }
  if (!EMAIL_RE.test(registerForm.email)) { tipErr('请输入正确的邮箱格式'); return }
  try {
    sendingCode.value = true
    await sendEmailCode(registerForm.email, 'register')
    tipOk('验证码已发送，请查收邮箱')
    countdown.value = 60
    countdownTimer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) { clearInterval(countdownTimer); countdownTimer = null }
    }, 1000)
  } catch (error) {
    console.error('发送验证码失败:', error)
  } finally {
    sendingCode.value = false
  }
}

const handleRegister = async () => {
  if (loading.value) return
  if (!validate()) return
  try {
    loading.value = true
    await userStore.register({
      email: registerForm.email,
      code: registerForm.code,
      password: registerForm.password
    })
    tipOk('注册成功，正在进入心屿…')
    setTimeout(() => router.push('/workspace/home'), 700)
  } catch (error) {
    console.error('注册失败:', error)
  } finally {
    loading.value = false
  }
}

const goToLogin = () => router.push('/login')

onBeforeUnmount(() => {
  if (countdownTimer) clearInterval(countdownTimer)
  if (tipTimer) clearTimeout(tipTimer)
})
</script>

<style scoped>
/* 与落地页/登录页同一套视觉：米色底 #F6F5F1、青绿主色 #2E6E68 */
.rg-page {
  display: flex;
  min-height: 100vh;
  background: #F6F5F1;
  color: #1B2A2C;
  font-family: inherit;
}

/* ---------- 左侧品牌区（版式与首页 LandingPage 左侧一致） ---------- */
.rg-side {
  flex: 0 0 46%;
  position: relative;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 56px 60px;
  overflow: hidden;
  background: linear-gradient(165deg, #FBFAF7 0%, #EAF2EF 52%, #F1EBE0 100%);
  --lp-serif: "Noto Serif SC", "Source Han Serif SC", "Songti SC", "STSong", "SimSun", serif;
  --lp-display: "Playfair Display", Georgia, "Times New Roman", serif;
  --lp-fg: #1B2A2C;
  --lp-fg-2: #56696D;
  --lp-fg-3: #93A3A5;
  --lp-line: #E4E2DA;
}
.rg-side-inner { position: relative; z-index: 1; max-width: 520px; }

/* 品牌行 */
.lp-brand { display: flex; align-items: center; gap: 12px; }
.lp-brand-mark {
  width: 40px; height: 40px; border-radius: 13px;
  display: flex; align-items: center; justify-content: center;
  background: linear-gradient(150deg, #3B837C, #22524E);
  box-shadow: 0 10px 22px -14px rgba(34, 82, 78, .9);
}
.lp-brand-name {
  font-family: var(--lp-serif);
  font-size: 19px; font-weight: 600;
  letter-spacing: .16em; line-height: 1.2;
  color: var(--lp-fg);
}
.lp-brand-en {
  font-family: var(--lp-display);
  font-style: italic; font-size: 12px;
  color: var(--lp-fg-3); letter-spacing: .14em; margin-top: 1px;
}
.lp-brand-tag {
  margin-left: 10px; padding-left: 14px;
  font-size: 11px; color: var(--lp-fg-3); letter-spacing: .14em;
  border-left: 1px solid var(--lp-line);
}

/* 主文案 */
.lp-hero { margin-top: 52px; }
.lp-eyebrow {
  font-size: 11px; font-weight: 600; letter-spacing: .2em;
  color: #2E6E68; margin-bottom: 16px;
  text-transform: uppercase;
}
.lp-title { display: flex; flex-direction: column; gap: 2px; margin-bottom: 22px; }
.lp-title-zh {
  font-family: var(--lp-serif);
  /* 首页用 clamp(67.2px, 8.4vw, 124.8px)，这里左栏更窄，取较小档但保留分量感 */
  font-size: clamp(46px, 4.6vw, 72px); font-weight: 500;
  letter-spacing: .04em; line-height: 1.04;
  color: var(--lp-fg);
}
.lp-title-en {
  font-family: var(--lp-display);
  font-style: italic; font-size: clamp(32px, 3.2vw, 50px); font-weight: 400;
  letter-spacing: .01em; line-height: 1.1;
  color: var(--lp-fg-2);
  opacity: .82;
}
.lp-slogan {
  font-family: var(--lp-serif);
  font-size: 17px; font-weight: 500;
  letter-spacing: .05em; color: var(--lp-fg);
  margin-bottom: 14px;
}
.lp-desc {
  font-size: 13px; line-height: 1.95;
  color: var(--lp-fg-2); max-width: 460px;
}

.lp-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 24px; }
.lp-tag {
  font-size: 11.5px; color: var(--lp-fg-2);
  padding: 5px 12px; border-radius: 999px;
  background: rgba(255, 255, 255, .62);
  border: 1px solid var(--lp-line);
}

.lp-social { display: flex; align-items: center; gap: 14px; margin-top: 34px; }
.lp-chips { display: flex; }
.lp-chips svg { margin-right: -7px; }
.lp-chips svg:last-child { margin-right: 0; }
.lp-social p { font-size: 12px; color: var(--lp-fg-3); }
.lp-social p b { color: var(--lp-fg-2); font-weight: 600; }

.rg-glow { position: absolute; border-radius: 50%; filter: blur(56px); pointer-events: none; }
.rg-glow-a { width: 320px; height: 320px; top: -90px; right: -80px; background: rgba(46, 110, 104, .14); }
.rg-glow-b { width: 220px; height: 220px; bottom: -60px; left: -60px; background: rgba(200, 178, 140, .2); }

/* ---------- 右侧表单 ---------- */
.rg-main {
  flex: 1;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  padding: 48px 32px;
  gap: 22px;
}

.rg-card {
  width: 100%; max-width: 408px;
  background: #fff;
  border: 1px solid #E7E5DE;
  border-radius: 20px;
  padding: 34px 32px 28px;
  box-shadow: 0 18px 44px -30px rgba(27, 42, 44, .35);
}

.rg-head { margin-bottom: 24px; }
.rg-head h2 { font-size: 20px; font-weight: 500; letter-spacing: .3px; }
.rg-head p { font-size: 12.5px; color: #7A8A8C; margin-top: 6px; }

.rg-form { display: flex; flex-direction: column; gap: 16px; }
.rg-field { display: flex; flex-direction: column; gap: 7px; }
.rg-field > label { font-size: 12.5px; color: #5F6E70; font-weight: 500; }

.rg-field input {
  width: 100%; height: 42px;
  padding: 0 13px;
  font-family: inherit; font-size: 13.5px; color: #1B2A2C;
  background: #FAF9F6;
  border: 1px solid #E7E5DE;
  border-radius: 11px;
  outline: none;
  transition: border-color .18s ease, background .18s ease, box-shadow .18s ease;
}
.rg-field input::placeholder { color: #A8B4B5; }
.rg-field input:focus {
  background: #fff;
  border-color: #2E6E68;
  box-shadow: 0 0 0 3px rgba(46, 110, 104, .1);
}
.rg-field input.is-bad { border-color: #C0554F; background: #FDF7F6; }
.rg-field input.is-bad:focus { box-shadow: 0 0 0 3px rgba(192, 85, 79, .1); }

.rg-row { display: flex; gap: 9px; align-items: stretch; }
.rg-row input { flex: 1 1 auto; min-width: 0; }

.rg-btn-code {
  flex: 0 0 auto;
  height: 42px;
  padding: 0 15px;
  font-family: inherit; font-size: 12.5px; font-weight: 500;
  color: #22524E;
  background: rgba(46, 110, 104, .09);
  border: 1px solid rgba(46, 110, 104, .18);
  border-radius: 11px;
  cursor: pointer;
  white-space: nowrap;
  transition: background .18s ease, opacity .18s ease;
}
.rg-btn-code:hover:not(:disabled) { background: rgba(46, 110, 104, .15); }
.rg-btn-code:disabled { opacity: .5; cursor: not-allowed; }

.rg-btn-eye {
  flex: 0 0 auto;
  padding: 0 12px;
  font-family: inherit; font-size: 12.5px;
  color: #7A8A8C;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 11px;
  cursor: pointer;
  transition: color .18s ease;
}
.rg-btn-eye:hover { color: #2E6E68; }

.rg-strength { display: flex; align-items: center; gap: 9px; margin-top: 2px; }
.rg-bar { flex: 1; height: 4px; border-radius: 3px; background: #EDEBE4; overflow: hidden; }
.rg-bar i { display: block; height: 100%; border-radius: 3px; transition: width .25s ease, background .25s ease; }
.rg-bar i.weak { background: #C0554F; }
.rg-bar i.medium { background: #C79A4E; }
.rg-bar i.strong { background: #2E6E68; }
.rg-strength > span { font-size: 11.5px; min-width: 28px; }
.rg-strength > span.weak { color: #C0554F; }
.rg-strength > span.medium { color: #C79A4E; }
.rg-strength > span.strong { color: #2E6E68; }

.rg-err { font-size: 11.5px; color: #C0554F; margin-top: 1px; }

.rg-agree {
  display: flex; align-items: flex-start; gap: 9px;
  font-size: 12.5px; line-height: 1.6; color: #5F6E70;
  cursor: pointer; user-select: none;
  margin-top: 2px;
}
.rg-cb {
  width: 17px; height: 17px; flex: 0 0 17px; margin-top: 1px;
  border-radius: 5px;
  border: 1.5px solid #D8D5CC;
  background: #fff;
  display: inline-flex; align-items: center; justify-content: center;
  color: #fff;
  transition: all .16s ease;
}
.rg-cb.on { background: #2E6E68; border-color: #2E6E68; }
.rg-agree a { color: #2E6E68; text-decoration: none; }
.rg-agree a:hover { text-decoration: underline; }

.rg-submit {
  width: 100%; height: 44px;
  margin-top: 4px;
  font-family: inherit; font-size: 14px; font-weight: 500;
  color: #fff;
  background: linear-gradient(160deg, #357B74, #22524E);
  border: 0; border-radius: 12px;
  cursor: pointer;
  box-shadow: 0 10px 24px -14px rgba(34, 82, 78, .9);
  transition: transform .16s ease, box-shadow .16s ease, opacity .16s ease;
}
.rg-submit:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 14px 30px -14px rgba(34, 82, 78, .85); }
.rg-submit:disabled { opacity: .55; cursor: not-allowed; transform: none; }

.rg-foot { margin-top: 20px; text-align: center; font-size: 12.5px; color: #7A8A8C; }
.rg-foot a { color: #2E6E68; font-weight: 500; text-decoration: none; margin-left: 3px; }
.rg-foot a:hover { text-decoration: underline; }

.rg-copy { font-size: 11.5px; color: #A8B4B5; }

/* ---------- 轻提示 ---------- */
.rg-tip {
  position: fixed; left: 50%; top: 28px; transform: translateX(-50%);
  padding: 11px 20px;
  font-size: 13px;
  color: #fff;
  background: rgba(34, 82, 78, .95);
  border-radius: 11px;
  box-shadow: 0 14px 32px -18px rgba(0, 0, 0, .5);
  z-index: 99;
  white-space: nowrap;
}
.rg-tip.warn { background: rgba(199, 154, 78, .96); }
.rg-tip.err { background: rgba(192, 85, 79, .96); }
.rg-tip.ok { background: rgba(46, 110, 104, .96); }
.rg-tip-enter-active, .rg-tip-leave-active { transition: opacity .22s ease, transform .22s ease; }
.rg-tip-enter-from, .rg-tip-leave-to { opacity: 0; transform: translate(-50%, -8px); }

/* ---------- 移动端 ---------- */
@media (max-width: 1024px) {
  .rg-side { flex: 0 0 44%; padding: 44px 36px; }
  .lp-title-zh { font-size: 44px; }
  .lp-title-en { font-size: 32px; }
  .lp-hero { margin-top: 36px; }
  .lp-brand-tag { display: none; }
}
@media (max-width: 900px) {
  .rg-page { flex-direction: column; }
  .rg-side { flex: 0 0 auto; padding: 34px 26px 28px; }
  .rg-side-inner { max-width: 100%; }
  .lp-hero { margin-top: 26px; }
  .lp-title { margin-bottom: 16px; }
  .lp-title-zh { font-size: 34px; }
  .lp-title-en { font-size: 25px; }
  .lp-slogan { font-size: 15px; margin-bottom: 10px; }
  .lp-desc { font-size: 12.5px; line-height: 1.8; }
  .lp-tags { margin-top: 16px; }
  .lp-social { margin-top: 20px; }
  .rg-main { padding: 26px 18px 40px; }
  .rg-card { padding: 26px 20px 22px; border-radius: 18px; }
}
</style>
