"""
创建管理员账户
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """哈希密码"""
    return pwd_context.hash(password)


def list_admins(db: Session):
    """列出所有管理员"""
    admins = db.query(User).filter(User.role == 'admin').all()
    print("\n=== 现有管理员账户 ===")
    if not admins:
        print("暂无管理员账户")
    else:
        for i, admin in enumerate(admins, 1):
            print(f"{i}. 邮箱: {admin.email}")
            print(f"   昵称: {admin.nickname}")
            print(f"   状态: {admin.status}")
            print(f"   验证: {'已验证' if admin.is_verified else '未验证'}")
            print(f"   创建时间: {admin.created_at}")
            print()


def create_admin(db: Session, email: str, password: str, nickname: str = "管理员"):
    """创建管理员账户"""
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == email).first()
    if existing_user:
        print(f"错误: 邮箱 {email} 已被使用")
        return False

    # 创建管理员
    admin = User(
        email=email,
        password=hash_password(password),
        nickname=nickname,
        role="admin",
        status="active",
        is_verified=True
    )
    db.add(admin)
    db.commit()

    print(f"\n[OK] 管理员账户创建成功！")
    print(f"  邮箱: {email}")
    print(f"  密码: {password}")
    print(f"  昵称: {nickname}")
    return True


def reset_admin_password(db: Session, email: str, new_password: str):
    """重置管理员密码"""
    admin = db.query(User).filter(User.email == email, User.role == 'admin').first()
    if not admin:
        print(f"错误: 找不到管理员账户 {email}")
        return False

    admin.password = hash_password(new_password)
    db.commit()

    print(f"\n[OK] 密码重置成功！")
    print(f"  邮箱: {email}")
    print(f"  新密码: {new_password}")
    return True


def main():
    """主函数"""
    print("=" * 60)
    print("管理员账户管理工具")
    print("=" * 60)

    db = SessionLocal()

    try:
        # 列出现有管理员
        list_admins(db)

        print("\n请选择操作:")
        print("1. 创建新管理员")
        print("2. 重置管理员密码")
        print("3. 仅查看现有管理员")
        print("0. 退出")

        choice = input("\n请输入选项 (0-3): ").strip()

        if choice == "1":
            print("\n=== 创建新管理员 ===")
            email = input("请输入邮箱: ").strip()
            password = input("请输入密码: ").strip()
            nickname = input("请输入昵称 (默认: 管理员): ").strip() or "管理员"
            create_admin(db, email, password, nickname)

        elif choice == "2":
            print("\n=== 重置管理员密码 ===")
            email = input("请输入管理员邮箱: ").strip()
            new_password = input("请输入新密码: ").strip()
            reset_admin_password(db, email, new_password)

        elif choice == "3":
            print("\n仅查看模式，不进行任何操作")

        elif choice == "0":
            print("退出")
            return

        else:
            print("无效选项")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] 操作失败: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    main()
