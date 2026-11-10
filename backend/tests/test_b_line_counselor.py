"""
B 线（咨询师与排班）功能验收测试

覆盖任务分工表中归属 B 的四项：
1. 咨询师列表与详情
2. 资料审核（申请 / 状态 / 待审列表 / 通过 / 拒绝 / 重复审核）
3. 咨询师工作台（订单列表 / 接单 / 拒单）
4. 时段发布与冲突校验（发布拆分 / 重叠拦截 / 非整点 / 过去时段 / 预约锁定 / 取消释放）

运行：cd backend && ./.venv/Scripts/python.exe -m pytest tests/test_b_line_counselor.py -v
使用内存 SQLite，不依赖 MySQL / Redis / SMTP。
"""
from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# SQLite 下让 BIGINT 主键自增（MySQL 环境无需此补丁）
@compiles(BigInteger, "sqlite")
def _bigint_as_integer(type_, compiler, **kw):
    return "INTEGER"


from app.core.database import Base, get_db
from app.core.security import create_access_token
import app.models as _models  # noqa: F401  注册全部模型
from app.main import app
from app.models.admin import Admin
from app.models.counselor import Counselor
from app.models.user import User
from app.services.email_service import EmailService

FUTURE = (date.today() + timedelta(days=30)).isoformat()


def _silence_emails():
    """测试中不真的发邮件"""
    for name in dir(EmailService):
        if name.startswith('send_') and callable(getattr(EmailService, name, None)):
            setattr(EmailService, name, staticmethod(lambda *a, **k: None))


@pytest.fixture(scope="module")
def ctx():
    _silence_emails()

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    # ---- 种子数据 ----
    admin = Admin(username='admin_t', password_hash='x', email='admin@test.com', role='admin')
    visitor = User(email='visitor@test.com', password_hash='x', nickname='来访者A', role='user')
    applicant = User(email='applicant@test.com', password_hash='x', nickname='申请者', role='user')
    c1_user = User(email='wangjy@test.com', password_hash='x', nickname='王静怡', role='counselor')
    db.add_all([admin, visitor, applicant, c1_user])
    db.commit()

    c1 = Counselor(
        user_id=c1_user.id,
        name='王静怡', gender='female', title='国家二级心理咨询师',
        specialties='焦虑,睡眠', consultation_types='video,voice',
        experience_years=8, education='心理学硕士', qualifications='国家二级证书',
        price_video=300, price_voice=200, rating=4.8, review_count=12, consultation_count=80,
        bio='擅长焦虑与睡眠议题的认知行为治疗，累计个案时长超过 3000 小时。',
        status='active', application_status='approved', is_verified=True,
    )
    c2 = Counselor(
        name='李明远', gender='male', title='资深心理治疗师',
        specialties='婚姻家庭,职场压力', consultation_types='video',
        experience_years=12, price_video=500, rating=4.9, review_count=5,
        bio='专注婚姻家庭与职场压力议题，系统式家庭治疗取向。',
        status='active', application_status='approved', is_verified=True,
    )
    c3 = Counselor(
        name='待审核咨询师', gender='female', specialties='青少年', consultation_types='video',
        experience_years=3, price_video=200, bio='等待审核的咨询师账号，用于验证审核列表。',
        status='pending_review', application_status='pending',
    )
    db.add_all([c1, c2, c3])
    db.commit()

    def override_get_db():
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    def token(user_id, role='user', admin_type=None):
        payload = {"sub": str(user_id), "role": role}
        if admin_type:
            payload["type"] = admin_type
        return create_access_token(payload)

    def auth(user_id, role='user', admin_type=None):
        return {"Authorization": f"Bearer {token(user_id, role, admin_type)}"}

    yield {
        "client": client,
        "db": db,
        "c1": c1, "c2": c2, "c3": c3,
        "visitor": visitor, "applicant": applicant, "admin": admin,
        "h_visitor": auth(visitor.id, 'user'),
        "h_applicant": auth(applicant.id, 'user'),
        "h_counselor": auth(c1_user.id, 'counselor'),
        "h_admin": auth(admin.id, 'admin', admin_type='admin'),
    }

    app.dependency_overrides.clear()


# ============================================================
# 1. 咨询师列表与详情
# ============================================================
def test_01_list_basic(ctx):
    r = ctx["client"].get('/api/counselor/list')
    assert r.status_code == 200
    data = r.json()['data']
    assert data['total'] >= 2
    names = [i['name'] for i in data['items']]
    assert '王静怡' in names
    assert '待审核咨询师' not in names, '未通过审核的咨询师不应出现在列表'


def test_02_list_search_and_filter(ctx):
    client = ctx["client"]

    r = client.get('/api/counselor/list', params={'keyword': '王静怡'})
    assert [i['name'] for i in r.json()['data']['items']] == ['王静怡']

    r = client.get('/api/counselor/list', params={'keyword': '不存在的关键词xyz'})
    assert r.json()['data']['total'] == 0

    r = client.get('/api/counselor/list', params={'specialties': '婚姻家庭'})
    assert [i['name'] for i in r.json()['data']['items']] == ['李明远']

    r = client.get('/api/counselor/list', params={'price_max': 400})
    assert '王静怡' in [i['name'] for i in r.json()['data']['items']]
    assert '李明远' not in [i['name'] for i in r.json()['data']['items']]

    r = client.get('/api/counselor/list', params={'sort': 'price-asc', 'page_size': 10})
    prices = [i.get('price_video') or 0 for i in r.json()['data']['items']]
    assert prices == sorted(prices), '价格升序排序不生效'


def test_03_detail_and_404(ctx):
    client = ctx["client"]
    r = client.get(f'/api/counselor/{ctx["c1"].id}')
    assert r.status_code == 200
    d = r.json()['data']
    assert d['name'] == '王静怡'
    assert d['price_video'] == 300
    assert d['bio']

    assert client.get('/api/counselor/999999').status_code == 404

    r = client.get(f'/api/counselor/{ctx["c1"].id}/reviews')
    assert r.status_code == 200
    assert r.json()['data']['total'] == 0


# ============================================================
# 2. 资料审核
# ============================================================
APPLY_PAYLOAD = {
    "name": "新申请咨询师",
    "gender": "female",
    "title": "心理咨询师",
    "specialties": ["焦虑", "睡眠"],
    "consultation_types": ["video", "voice"],
    "experience_years": 5,
    "education": "应用心理学硕士",
    "qualifications": "国家二级心理咨询师证书",
    "price_video": 260,
    "price_voice": 180,
    "bio": "从业五年，主要处理焦虑、睡眠与情绪管理议题，累计个案时长一千小时以上，长期接受系统督导与个人体验，擅长认知行为疗法与正念减压训练。",
    "approach": "认知行为疗法",
}


def test_10_apply_and_status(ctx):
    client = ctx["client"]
    r = client.post('/api/counselor/apply', json=APPLY_PAYLOAD, headers=ctx["h_applicant"])
    assert r.status_code == 200, r.text
    ctx["applied_id"] = r.json()['data']['id']

    r = client.get('/api/counselor/application/status', headers=ctx["h_applicant"])
    d = r.json()['data']
    assert d['has_applied'] is True
    assert d['application_status'] == 'pending'
    assert d['can_edit'] is True

    # 重复提交应被拒绝
    r = client.post('/api/counselor/apply', json=APPLY_PAYLOAD, headers=ctx["h_applicant"])
    assert r.status_code == 400
    assert '审核中' in r.json()['detail']


def test_11_pending_list(ctx):
    r = ctx["client"].get('/api/counselor/application/pending', params={'page_size': 50})
    assert r.status_code == 200
    ids = [i['id'] for i in r.json()['data']['items']]
    assert ctx["applied_id"] in ids
    assert ctx["c3"].id in ids


def test_12_review_requires_admin(ctx):
    """审核接口必须校验管理员权限（本次修复的鉴权缺口）"""
    r = ctx["client"].post(
        f'/api/counselor/application/{ctx["applied_id"]}/review',
        params={'action': 'approve'}, headers=ctx["h_applicant"]
    )
    assert r.status_code == 401
    assert '管理员' in r.json()['detail']

    # 未携带 token 直接访问
    r = ctx["client"].post(
        f'/api/counselor/application/{ctx["applied_id"]}/review',
        params={'action': 'approve'}
    )
    assert r.status_code in (401, 403)


def test_13_reject_requires_reason(ctx):
    r = ctx["client"].post(
        f'/api/counselor/application/{ctx["applied_id"]}/review',
        params={'action': 'reject'}, headers=ctx["h_admin"]
    )
    assert r.status_code == 400
    assert '拒绝原因' in r.json()['detail']


def test_14_reject_then_reapply_then_approve(ctx):
    client = ctx["client"]
    r = client.post(
        f'/api/counselor/application/{ctx["applied_id"]}/review',
        params={'action': 'reject', 'reason': '资质材料不完整'}, headers=ctx["h_admin"]
    )
    assert r.status_code == 200

    d = client.get('/api/counselor/application/status', headers=ctx["h_applicant"]).json()['data']
    assert d['application_status'] == 'rejected'
    assert d['rejection_reason'] == '资质材料不完整'

    # 被拒绝后可重新提交
    r = client.post('/api/counselor/apply', json=APPLY_PAYLOAD, headers=ctx["h_applicant"])
    assert r.status_code == 200, r.text
    d = client.get('/api/counselor/application/status', headers=ctx["h_applicant"]).json()['data']
    assert d['application_status'] == 'pending'

    r = client.post(
        f'/api/counselor/application/{ctx["applied_id"]}/review',
        params={'action': 'approve'}, headers=ctx["h_admin"]
    )
    assert r.status_code == 200

    d = client.get('/api/counselor/application/status', headers=ctx["h_applicant"]).json()['data']
    assert d['application_status'] == 'approved'

    # 审核通过的咨询师应出现在公开列表
    names = [i['name'] for i in client.get('/api/counselor/list', params={'page_size': 50}).json()['data']['items']]
    assert '新申请咨询师' in names

    # 已审核的申请不能重复审核
    r = client.post(
        f'/api/counselor/application/{ctx["applied_id"]}/review',
        params={'action': 'approve'}, headers=ctx["h_admin"]
    )
    assert r.status_code == 400
    assert '已处理' in r.json()['detail']


# ============================================================
# 4. 时段发布与冲突校验
# ============================================================
def test_20_publish_splits_into_hours(ctx):
    r = ctx["client"].post(
        '/api/counselor/schedule/publish',
        json={"slots": [{"date": FUTURE, "start_time": "09:00", "end_time": "12:00"}]},
        headers=ctx["h_counselor"],
    )
    assert r.status_code == 200, r.text
    d = r.json()['data']
    assert d['created'] == 3, '09:00-12:00 应拆成 3 个 1 小时时段'


def test_21_publish_conflicts(ctx):
    client = ctx["client"]
    r = client.post(
        '/api/counselor/schedule/publish',
        json={"slots": [{"date": FUTURE, "start_time": "11:00", "end_time": "13:00"}]},
        headers=ctx["h_counselor"],
    )
    d = r.json()['data']
    assert d['created'] == 1 and d['skipped'] == 1, '11-12 与已发布时段重叠应跳过，12-13 可发布'
    assert '重叠' in d['conflicts'][0]

    r = client.post(
        '/api/counselor/schedule/publish',
        json={"slots": [{"date": FUTURE, "start_time": "14:30", "end_time": "16:00"}]},
        headers=ctx["h_counselor"],
    )
    d = r.json()['data']
    assert d['skipped'] == 1 and '整点' in d['conflicts'][0]

    past = (date.today() - timedelta(days=2)).isoformat()
    r = client.post(
        '/api/counselor/schedule/publish',
        json={"slots": [{"date": past, "start_time": "09:00", "end_time": "10:00"}]},
        headers=ctx["h_counselor"],
    )
    d = r.json()['data']
    assert d['skipped'] == 1 and '过去' in d['conflicts'][0]


def test_22_non_counselor_cannot_publish(ctx):
    r = ctx["client"].post(
        '/api/counselor/schedule/publish',
        json={"slots": [{"date": FUTURE, "start_time": "15:00", "end_time": "16:00"}]},
        headers=ctx["h_visitor"],
    )
    assert r.status_code == 400
    assert '未找到咨询师档案' in r.json()['detail']


def test_23_my_slots_list(ctx):
    client = ctx["client"]
    r = client.get('/api/counselor/schedule/list', headers=ctx["h_counselor"])
    assert r.status_code == 200
    slots = r.json()['data']
    assert len(slots) == 4  # 3 + 1
    assert all(s['slot_date'] == FUTURE for s in slots)
    assert [s['start_time'] for s in slots] == ['09:00', '10:00', '11:00', '12:00']

    r = client.get('/api/counselor/schedule/list', params={'date': FUTURE}, headers=ctx["h_counselor"])
    assert len(r.json()['data']) == 4

    r = client.get('/api/counselor/schedule/list', params={'date': '2030-12-31'}, headers=ctx["h_counselor"])
    assert r.json()['data'] == []


def test_24_public_slots_follow_schedule(ctx):
    """用户侧时段接口应只返回咨询师发布过的时段"""
    r = ctx["client"].get(f'/api/counselor/{ctx["c1"].id}/slots', params={'date': FUTURE})
    assert r.status_code == 200
    slots = r.json()['data']
    assert [s['time'] for s in slots] == ['09:00-10:00', '10:00-11:00', '11:00-12:00', '12:00-13:00']
    assert all(s['available'] for s in slots)


def test_25_fallback_when_no_schedule(ctx):
    """未发布排班的咨询师保留 09:00-18:00 默认时段，兼容旧数据"""
    r = ctx["client"].get(f'/api/counselor/{ctx["c2"].id}/slots', params={'date': FUTURE})
    assert r.status_code == 200
    assert len(r.json()['data']) == 10


def test_26_booking_conflicts_and_lock(ctx):
    client = ctx["client"]
    cid = ctx["c1"].id

    def book(t, name='来访者A'):
        return client.post('/api/appointment/create', json={
            "counselor_id": cid, "consultation_type": "video",
            "appointment_date": f"{FUTURE}T{t}:00",
            "user_name": name, "user_contact": "13800000000",
            "problem_description": "想聊聊最近的焦虑",
        }, headers=ctx["h_visitor"])

    r = book('09:00')
    assert r.status_code == 200, r.text
    ctx["apt_id"] = r.json()['data']['id']

    # 同一小时重复预约 -> 拒绝
    r = book('09:00')
    assert r.status_code == 400 and '已被预约' in r.json()['detail']

    # 未发布的时段 -> 拒绝
    r = book('20:00')
    assert r.status_code == 400 and '未开放' in r.json()['detail']

    # 非整点（跨两个 1 小时时段）-> 拒绝
    r = book('10:30')
    assert r.status_code == 400

    # 相邻小时 -> 成功
    r = book('10:00', '来访者B')
    assert r.status_code == 200, r.text
    ctx["apt2_id"] = r.json()['data']['id']

    # 用户侧该小时应显示为不可约
    slots = client.get(f'/api/counselor/{cid}/slots', params={'date': FUTURE}).json()['data']
    status = {s['time']: s['available'] for s in slots}
    assert status['09:00-10:00'] is False and status['10:00-11:00'] is False
    assert status['11:00-12:00'] is True


def test_27_booked_slot_cannot_be_deleted(ctx):
    client = ctx["client"]
    slots = client.get('/api/counselor/schedule/list', headers=ctx["h_counselor"]).json()['data']
    booked = [s for s in slots if s['start_time'] == '09:00'][0]
    free = [s for s in slots if s['start_time'] == '12:00'][0]

    r = client.delete(f'/api/counselor/schedule/{booked["id"]}', headers=ctx["h_counselor"])
    assert r.status_code == 400 and '无法删除' in r.json()['detail']

    r = client.delete(f'/api/counselor/schedule/{free["id"]}', headers=ctx["h_counselor"])
    assert r.status_code == 200
    assert len(client.get('/api/counselor/schedule/list', headers=ctx["h_counselor"]).json()['data']) == 3


def test_28_cancel_releases_slot(ctx):
    client = ctx["client"]
    r = client.post(f'/api/appointment/{ctx["apt_id"]}/cancel', headers=ctx["h_visitor"])
    assert r.status_code == 200

    slots = client.get('/api/counselor/schedule/list', headers=ctx["h_counselor"]).json()['data']
    by_time = {s['start_time']: s['status'] for s in slots}
    assert by_time['09:00'] == 'available', '取消预约后应释放时段'
    assert by_time['10:00'] == 'booked'


# ============================================================
# 3. 咨询师工作台
# ============================================================
def test_30_workbench_orders(ctx):
    client = ctx["client"]

    r = client.get('/api/consultation/counselor/orders', headers=ctx["h_counselor"])
    assert r.status_code == 200, r.text
    all_items = r.json()['data']['items']
    pending = [o for o in all_items if o['status'] == 'pending']
    assert len(pending) == 1, f'09:00 已取消，应只剩 10:00 一单待处理；实际: {[(o["id"], o["status"]) for o in all_items]}'
    ctx["order_id"] = pending[0]['id']

    r = client.get('/api/appointment/counselor/list', headers=ctx["h_counselor"])
    assert r.status_code == 200
    assert r.json()['data']['total'] >= 1

    # 非咨询师访问工作台订单 -> 403
    r = client.get('/api/consultation/counselor/orders', headers=ctx["h_admin"])
    assert r.status_code == 403


def test_31_handle_order_reject_releases_slot(ctx):
    client = ctx["client"]
    r = client.post(f'/api/consultation/order/{ctx["order_id"]}/handle',
                    json={"action": "reject", "reason": "时间冲突"},
                    headers=ctx["h_counselor"])
    assert r.status_code == 200, r.text

    slots = client.get('/api/counselor/schedule/list', headers=ctx["h_counselor"]).json()['data']
    by_time = {s['start_time']: s['status'] for s in slots}
    assert by_time['10:00'] == 'available', '咨询师拒单后应释放时段'

    detail = client.get(f'/api/appointment/{ctx["order_id"]}', headers=ctx["h_counselor"]).json()['data']
    assert detail['status'] == 'cancelled'


def test_32_handle_order_agree(ctx):
    client = ctx["client"]
    r = client.post('/api/appointment/create', json={
        "counselor_id": ctx["c1"].id, "consultation_type": "voice",
        "appointment_date": f"{FUTURE}T11:00:00",
        "user_name": "来访者A", "user_contact": "13800000000",
    }, headers=ctx["h_visitor"])
    assert r.status_code == 200, r.text
    aid = r.json()['data']['id']

    r = client.post(f'/api/consultation/order/{aid}/handle',
                    json={"action": "agree"}, headers=ctx["h_counselor"])
    assert r.status_code == 200, r.text

    detail = client.get(f'/api/appointment/{aid}', headers=ctx["h_counselor"]).json()['data']
    assert detail['status'] == 'confirmed'


def test_33_availability_flag(ctx):
    """列表里的"可预约/不可预约"取决于是否还有剩余时段"""
    from app.services.counselor_service import CounselorService
    from app.schemas.counselor import CounselorListQuery

    client = ctx["client"]
    cid = ctx["c1"].id
    day = (date.today() + timedelta(days=40)).isoformat()

    # 该咨询师此前发布过时段，且都还有空余 -> 可预约
    q = CounselorListQuery(keyword='王静怡', page=1, page_size=10)
    items = CounselorService.get_counselor_list(ctx["db"], q)["items"]
    assert items[0].has_available_slot is True

    # 只留一个时段并约满 -> 不可预约
    r = client.post('/api/counselor/schedule/publish',
                    json={"slots": [{"date": day, "start_time": "09:00", "end_time": "10:00"}]},
                    headers=ctx["h_counselor"])
    assert r.status_code == 200

    # 把之前发布的其余时段清掉，只保留这一个可约时段
    slots = client.get('/api/counselor/schedule/list', headers=ctx["h_counselor"]).json()['data']
    for s in slots:
        if s['status'] == 'available' and s['slot_date'] != day:
            client.delete(f'/api/counselor/schedule/{s["id"]}', headers=ctx["h_counselor"])

    r = client.post('/api/appointment/create', json={
        "counselor_id": cid, "consultation_type": "video",
        "appointment_date": f"{day}T09:00:00",
        "user_name": "来访者A", "user_contact": "13800000000",
    }, headers=ctx["h_visitor"])
    assert r.status_code == 200, r.text

    items = CounselorService.get_counselor_list(ctx["db"], CounselorListQuery(keyword='王静怡', page=1, page_size=10))["items"]
    assert items[0].has_available_slot is False, '时段约满后应显示不可预约'

    # 取消后恢复可预约
    client.post(f'/api/appointment/{r.json()["data"]["id"]}/cancel', headers=ctx["h_visitor"])
    items = CounselorService.get_counselor_list(ctx["db"], CounselorListQuery(keyword='王静怡', page=1, page_size=10))["items"]
    assert items[0].has_available_slot is True

    # 预约价格为 0（公益活动免费）
    detail = client.get(f'/api/appointment/{r.json()["data"]["id"]}', headers=ctx["h_visitor"]).json()['data']
    assert detail['price'] == 0
