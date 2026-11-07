"""
添加更多测试用户和咨询师账号
"""
import sys
import os
import random

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


def create_more_users(db: Session):
    """创建更多普通用户"""

    users_data = [
        {
            "email": "student1@test.com",
            "nickname": "小李",
            "password": hash_password("123456"),
            "gender": "male",
            "phone": "13900001111",
            "bio": "大学生，面临就业压力，希望能得到职业规划指导。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "student2@test.com",
            "nickname": "小张",
            "password": hash_password("123456"),
            "gender": "female",
            "phone": "13900002222",
            "bio": "研究生，经常感到焦虑和失眠，希望改善睡眠质量。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "worker1@test.com",
            "nickname": "王先生",
            "password": hash_password("123456"),
            "gender": "male",
            "phone": "13900003333",
            "bio": "职场新人，工作压力大，想学习压力管理技巧。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "worker2@test.com",
            "nickname": "刘女士",
            "password": hash_password("123456"),
            "gender": "female",
            "phone": "13900004444",
            "bio": "职场妈妈，平衡工作与家庭感到力不从心。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "parent1@test.com",
            "nickname": "陈爸爸",
            "password": hash_password("123456"),
            "gender": "male",
            "phone": "13900005555",
            "bio": "孩子青春期叛逆，希望改善亲子关系。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "parent2@test.com",
            "nickname": "赵妈妈",
            "password": hash_password("123456"),
            "gender": "female",
            "phone": "13900006666",
            "bio": "孩子学习压力大，希望帮助孩子缓解焦虑。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "young1@test.com",
            "nickname": "小林",
            "password": hash_password("123456"),
            "gender": "secret",
            "phone": "13900007777",
            "bio": "刚步入社会，对未来感到迷茫，需要人生规划指导。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "senior1@test.com",
            "nickname": "周先生",
            "password": hash_password("123456"),
            "gender": "male",
            "phone": "13900008888",
            "bio": "即将退休，面临角色转换，希望调整心态。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "relationship1@test.com",
            "nickname": "吴女士",
            "password": hash_password("123456"),
            "gender": "female",
            "phone": "13900009999",
            "bio": "婚恋问题困扰，希望在感情方面得到指导。",
            "status": "active",
            "role": "user",
            "is_verified": True
        },
        {
            "email": "selfgrowth1@test.com",
            "nickname": "郑同学",
            "password": hash_password("123456"),
            "gender": "male",
            "phone": "13900001010",
            "bio": "想要提升自信，改善社交能力。",
            "status": "active",
            "role": "user",
            "is_verified": True
        }
    ]

    count = 0
    for user_data in users_data:
        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.email == user_data["email"]).first()
        if existing_user:
            print(f"  [SKIP] {user_data['email']} 已存在")
            continue

        user = User(**user_data)
        db.add(user)
        count += 1
        print(f"  [OK] 创建用户: {user_data['email']} ({user_data['nickname']})")

    db.commit()
    print(f"\n新增普通用户: {count} 个")


def create_more_counselors(db: Session):
    """创建更多咨询师账号"""

    counselors_data = [
        {
            "email": "counselor5@test.com",
            "nickname": "孙医生",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "孙医生",
                "gender": "female",
                "title": "主任医师",
                "specialties": "婚姻咨询,家庭治疗,情感问题",
                "consultation_types": "video,voice,offline",
                "experience_years": 20,
                "education": "心理学博士",
                "qualifications": "国家一级心理咨询师、婚姻家庭治疗师",
                "price_video": 600,
                "price_voice": 400,
                "price_offline": 1000,
                "rating": 4.9,
                "review_count": 320,
                "consultation_count": 580,
                "bio": "20年心理咨询经验，专注婚姻家庭治疗，帮助数千个家庭重建和谐关系。",
                "approach": "系统家庭治疗、情绪聚焦疗法(EFT)、叙事疗法",
                "achievements": "出版《幸福家庭的秘密》等专著，获得'全国优秀心理咨询师'称号",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor6@test.com",
            "nickname": "许老师",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "许老师",
                "gender": "male",
                "title": "职业规划师",
                "specialties": "职业规划,职场压力,人际关系",
                "consultation_types": "video,voice",
                "experience_years": 10,
                "education": "工商管理硕士",
                "qualifications": "国家二级心理咨询师、职业规划师",
                "price_video": 350,
                "price_voice": 220,
                "price_offline": 500,
                "rating": 4.7,
                "review_count": 150,
                "consultation_count": 280,
                "bio": "10年职场咨询经验，曾任企业HR总监，深谙职场规则。",
                "approach": "认知行为疗法、解决方案导向疗法",
                "achievements": "帮助500+职场人成功转型，满意度98%",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor7@test.com",
            "nickname": "马医生",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "马医生",
                "gender": "female",
                "title": "儿童心理专家",
                "specialties": "儿童心理,亲子教育,学习困难",
                "consultation_types": "video,voice,offline",
                "experience_years": 18,
                "education": "发展心理学博士",
                "qualifications": "国家二级心理咨询师、儿童心理治疗师",
                "price_video": 450,
                "price_voice": 300,
                "price_offline": 700,
                "rating": 4.8,
                "review_count": 210,
                "consultation_count": 390,
                "bio": "18年儿童心理工作经验，擅长儿童行为问题和学习困难矫正。",
                "approach": "游戏治疗、行为疗法、亲子互动疗法",
                "achievements": "治疗儿童案例1000+，举办亲子教育讲座200余场",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor8@test.com",
            "nickname": "林老师",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "林老师",
                "gender": "male",
                "title": "睡眠心理专家",
                "specialties": "失眠治疗,焦虑症,恐惧症",
                "consultation_types": "video,voice",
                "experience_years": 12,
                "education": "临床心理学硕士",
                "qualifications": "国家二级心理咨询师、催眠治疗师",
                "price_video": 380,
                "price_voice": 250,
                "price_offline": 600,
                "rating": 4.6,
                "review_count": 175,
                "consultation_count": 320,
                "bio": "12年失眠焦虑治疗经验，采用催眠疗法和正念疗法。",
                "approach": "催眠治疗、正念疗法、认知行为疗法",
                "achievements": "成功治愈失眠患者800+例",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor9@test.com",
            "nickname": "赵医生",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "赵医生",
                "gender": "female",
                "title": "创伤心理专家",
                "specialties": "PTSD,创伤治疗,心理危机干预",
                "consultation_types": "video,voice",
                "experience_years": 15,
                "education": "创伤心理学博士",
                "qualifications": "国家二级心理咨询师、EMDR治疗师",
                "price_video": 500,
                "price_voice": 350,
                "price_offline": 800,
                "rating": 4.9,
                "review_count": 140,
                "consultation_count": 260,
                "bio": "15年创伤治疗经验，擅长处理各种心理创伤和PTSD。",
                "approach": "EMDR疗法、体感疗法、创伤聚焦认知行为疗法",
                "achievements": "参与灾难心理援助多次，发表论文30余篇",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor10@test.com",
            "nickname": "钱老师",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "钱老师",
                "gender": "male",
                "title": "心理咨询师",
                "specialties": "自卑治疗,自信提升,社交恐惧",
                "consultation_types": "video,voice",
                "experience_years": 7,
                "education": "应用心理学硕士",
                "qualifications": "国家二级心理咨询师",
                "price_video": 280,
                "price_voice": 180,
                "price_offline": 400,
                "rating": 4.5,
                "review_count": 95,
                "consultation_count": 180,
                "bio": "7年心理咨询经验，温暖耐心，专注个人成长和自信提升。",
                "approach": "人本主义疗法、认知行为疗法、正念疗法",
                "achievements": "帮助众多来访者重建自信，获得'青年咨询师'称号",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor11@test.com",
            "nickname": "周医生",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "周医生",
                "gender": "female",
                "title": "老年心理专家",
                "specialties": "老年心理,退休适应,丧亲辅导",
                "consultation_types": "video,voice,offline",
                "experience_years": 14,
                "education": "老年心理学硕士",
                "qualifications": "国家二级心理咨询师、老年精神卫生师",
                "price_video": 320,
                "price_voice": 200,
                "price_offline": 500,
                "rating": 4.7,
                "review_count": 120,
                "consultation_count": 230,
                "bio": "14年老年心理工作经验，理解老年人心理需求。",
                "approach": "怀旧疗法、人生回顾疗法、支持性心理治疗",
                "achievements": "服务老年人群体3000+小时，社区心理服务先进个人",
                "status": "active",
                "is_verified": True
            }
        },
        {
            "email": "counselor12@test.com",
            "nickname": "吴老师",
            "password": hash_password("123456"),
            "role": "counselor",
            "is_verified": True,
            "counselor_data": {
                "name": "吴老师",
                "gender": "male",
                "title": "心理咨询师",
                "specialties": "网络成瘾,游戏成瘾,手机依赖",
                "consultation_types": "video,voice",
                "experience_years": 9,
                "education": "心理学硕士",
                "qualifications": "国家二级心理咨询师、成瘾心理治疗师",
                "price_video": 350,
                "price_voice": 220,
                "price_offline": 550,
                "rating": 4.6,
                "review_count": 165,
                "consultation_count": 290,
                "bio": "9年成瘾行为治疗经验，擅长网络成瘾和行为矫正。",
                "approach": "认知行为疗法、动机访谈、家庭治疗",
                "achievements": "成功戒除网瘾案例500+，开发青少年网瘾干预课程",
                "status": "active",
                "is_verified": True
            }
        }
    ]

    count = 0
    for counselor_info in counselors_data:
        email = counselor_info["email"]

        # 检查用户是否已存在
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            print(f"  [SKIP] {email} 已存在")
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
        db.flush()

        # 创建咨询师档案
        counselor_data = counselor_info["counselor_data"].copy()
        counselor_data["user_id"] = user.id
        counselor = Counselor(**counselor_data)
        db.add(counselor)
        count += 1
        print(f"  [OK] 创建咨询师: {email} ({counselor_data['name']} - {counselor_data['specialties'][:10]}...)")

    db.commit()
    print(f"\n新增咨询师: {count} 个")


def main():
    """主函数"""
    print("=" * 70)
    print("添加更多测试用户和咨询师账号")
    print("=" * 70)

    # 获取数据库会话
    db = SessionLocal()

    try:
        print("\n【创建普通用户】")
        create_more_users(db)

        print("\n" + "-" * 70 + "\n")

        print("【创建咨询师】")
        create_more_counselors(db)

        print("\n" + "=" * 70)
        print("[OK] 账号添加完成！")
        print("=" * 70)

        # 显示统计信息
        user_count = db.query(User).filter(User.role == 'user').count()
        counselor_count = db.query(Counselor).count()
        admin_count = db.query(User).filter(User.role == 'admin').count()

        print(f"\n账号统计：")
        print(f"  - 总用户数: {user_count}")
        print(f"  - 咨询师数: {counselor_count}")
        print(f"  - 管理员数: {admin_count}")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] 创建失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
