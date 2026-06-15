"""
seed_admin.py
Run once to create the first admin user.

    python seed_admin.py
"""

import asyncio
import sys

from sqlalchemy import select

sys.path.insert(0, ".")

from app.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.models.institute import Institute
from app.services.auth_service import hash_password


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        # ── Default institute ──────────────────────────
        inst_result = await db.execute(
            select(Institute).where(Institute.name == "Academica Secondary School")
        )
        institute: Institute | None = inst_result.scalar_one_or_none()

        if not institute:
            institute = Institute(
                name="Academica Secondary School",
                address="Ghorahi-15, Dang",
                phone="085-123456",
                email="school@academia.edu.np",
            )
            db.add(institute)
            await db.flush()
            await db.refresh(institute)
            print(f"✅  Created institute: {institute.name}")
        else:
            print(f"ℹ️   Institute already exists: {institute.name}")

        # ── Admin user ─────────────────────────────────
        admin_email = "admin@academia.edu.np"
        user_result = await db.execute(
            select(User).where(User.email == admin_email)
        )
        existing: User | None = user_result.scalar_one_or_none()

        if not existing:
            admin = User(
                email=admin_email,
                full_name="System Administrator",
                hashed_password=hash_password("Admin@1234"),
                role=UserRole.admin,
                institute_id=institute.id,
                is_active=True,
            )
            db.add(admin)
            await db.flush()
            print(f"✅  Created admin user: {admin_email}")
            print(f"    Default password : Admin@1234")
            print(f"    ⚠️  Change this password immediately after first login!")
        else:
            print(f"ℹ️   Admin user already exists: {admin_email}")

        await db.commit()
        print("\n🎉  Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())