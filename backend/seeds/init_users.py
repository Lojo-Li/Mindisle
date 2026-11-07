"""
创建测试用户和咨询师账号
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal, Base
from app.models.user import User
from app.models.counselor import Counselor
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def create_users(db: Session):
    """创建普通用户"""

    users_data = [
        {
            "email": "user1@test.com",
            "nickname": "小明",
            "password": hash_password("123456"),
            "gender": "male",
            "phone": "13800138001",
            "bio": "我是一名大学生，最近感到有些焦虑。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "user2@test.com",
            "nickname": "小红",
            "password": hash_password("123456"),
            "gender": "female",
            "phone": "13800138002",
            "bio": "希望在这里找到专业的心理咨询师。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "user3@test.com",
            "nickname": "小华",
            "password": hash_password("123456"),
            "gender": "secret",
            "phone": "13800138003",
            "bio": "想了解自己的心理健康状况。",
            "status": "active",
            "role": "user",
            "is_verified": True
        }
    ]

    for user_data in users_data:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"用户 {user_data['email']} 已存在，跳过")
            continue

        user = User(**user_data)
        db.add(user)
        print(f"[OK] 创建用户: {user_data['email']} (密码: 123456)")

    db.commit()
    print(f"\n普通用户创建完成！")


def create_counselors(db: Session):
    """创建咨询师账号"""

    counselors_data = [
        {
            "email": "counselor1@test.com",
            "nickname": "李医生",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "李医生",
                "gender": "female",
                "title": "心理咨询师",
                "specialties": "焦虑,抑郁,情绪管理",
                "consultation_types": "video,voice",
                "experience_years": 8,
                "education": "心理学硕士",
                "qualifications": "国家二级心理咨询师",
                "price_video": 300,
                "price_voice": 200,
                "price_offline": 500,
                "rating": 4.8,
                "review_count": 120,
                "consultation_count": 200,
                "bio": "拥有8年心理咨询经验，擅长焦虑、抑郁等情绪问题的咨询，采用认知行为疗法。",
                "approach": "认知行为疗法(CBT)、人本主义疗法",
                "achievements": "帮助超过200名来访者走出心理困境",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor2@test.com",
            "nickname": "王老师",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "王老师",
                "gender": "male",
                "title": "高级心理咨询师",
                "specialties": "婚恋家庭,亲子关系,职业规划",
                "consultation_types": "video,voice,offline",
                "experience_years": 12,
                "education": "心理学博士",
                "qualifications": "国家二级心理咨询师、婚姻家庭咨询师",
                "price_video": 500,
                "price_voice": 300,
                "price_offline": 800,
                "rating": 4.9,
                "review_count": 280,
                "consultation_count": 450,
                "bio": "12年心理咨询经验，专注于婚恋家庭、亲子关系咨询，拥有丰富的家庭治疗经验。",
                "approach": "家庭治疗、系统式家庭治疗、沙盘疗法",
                "achievements": "出版心理学著作3部，举办讲座100余场",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor3@test.com",
            "nickname": "张医生",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "张医生",
                "gender": "male",
                "title": "资深心理医生",
                "specialties": "青少年心理,学习压力,网络成瘾",
                "consultation_types": "video,voice",
                "experience_years": 15,
                "education": "精神医学硕士",
                "qualifications": "精神科医师、国家二级心理咨询师",
                "price_video": 400,
                "price_voice": 250,
                "price_offline": 600,
                "rating": 4.7,
                "review_count": 180,
                "consultation_count": 320,
                "bio": "15年青少年心理咨询经验，擅长处理学习压力、网络成瘾、青春期心理问题。",
                "approach": "认知行为疗法、家庭治疗、游戏治疗",
                "achievements": "治疗成功案例超过500例",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor4@test.com",
            "nickname": "陈老师",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "陈老师",
                "gender": "female",
                "title": "心理咨询师",
                "specialties": "情绪管理,压力调节,自我成长",
                "consultation_types": "video,voice",
                "experience_years": 6,
                "education": "应用心理学硕士",
                "qualifications": "国家二级心理咨询师",
                "price_video": 300,
                "price_voice": 200,
                "price_offline": 400,
                "rating": 4.6,
                "review_count": 85,
                "consultation_count": 150,
                "bio": "6年心理咨询经验，温暖专业，帮助来访者实现自我成长。",
                "approach": "人本主义疗法、正念疗法",
                "achievements": "获得'优秀心理咨询师'称号",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "admin@test.com",
            "nickname": "管理员",
            "password": hash_password("123456"),
            "role": "admin",
            "is_verified": True
        }
    ]

    for counselor_info in counselors_data:
        email = counselor_info["email"]

        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"用户 {email} 已存在，跳过")
            continue

        # 创建用户账号
        user_data = {
            "email": email,
            "nickname": counselor_info["nickname"],
            "password": counselor_info["password"],
            "role": counselor_info["role"],
            "is_verified": counselor_info["is_verified"]
        }
        user = User(**user_data)
        db.add(user)
        db.flush()  # 获取用户ID

        # 如果是咨询师，创建咨询师档案
        if counselor_info["role"] == "counselor" and "counselor_data" in counselor_info:
            counselor_data = counselor_info["counselor_data"].copy()
            counselor_data["user_id"] = user.id
            counselor = Counselor(**counselor_data)
            db.add(counselor)
            print(f"[OK] 创建咨询师: {email} (密码: 123456, 姓名: {counselor_data['name']})")
        else:
            print(f"[OK] 创建管理员: {email} (密码: 123456)")

    db.commit()
    print(f"\n咨询师和管理员创建完成！")


def main():
    """主函数"""
    print("=" * 60)
    print("创建测试用户和咨询师账号")
    print("=" * 60)

    # 创建数据库表
    print("\n正在创建数据库表...")
    Base.metadata.create_all(bind=engine)
    print("[OK] 数据库表创建完成")

    # 获取数据库会话
    db = SessionLocal()

    try:
        print("\n开始创建测试账号...\n")

        # 创建普通用户
        print("【创建普通用户】")
        create_users(db)

        print("\n" + "-" * 60 + "\n")

        # 创建咨询师和管理员
        print("【创建咨询师和管理员】")
        create_counselors(db)

        print("\n" + "=" * 60)
        print("[OK] 测试账号创建完成！")
        print("=" * 60)

        # 显示统计信息
        user_count = db.query(User).count()
        counselor_count = db.query(Counselor).count()

        print(f"\n账号统计：")
        print(f"  - 总用户数: {user_count}")
        print(f"  - 咨询师数: {counselor_count}")

        print(f"\n测试账号列表：")
        print(f"\n【普通用户】(密码均为: 123456)")
        print(f"  - user1@test.com (小明)")
        print(f"  - user2@test.com (小红)")
        print(f"  - user3@test.com (小华)")

        print(f"\n【咨询师】(密码均为: 123456)")
        print(f"  - counselor1@test.com (李医生 - 擅长焦虑、抑郁)")
        print(f"  - counselor2@test.com (王老师 - 擅长婚恋家庭)")
        print(f"  - counselor3@test.com (张医生 - 擅长青少年心理)")
        print(f"  - counselor4@test.com (陈老师 - 擅长情绪管理)")

        print(f"\n【管理员】(密码均为: 123456)")
        print(f"  - admin@test.com")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
