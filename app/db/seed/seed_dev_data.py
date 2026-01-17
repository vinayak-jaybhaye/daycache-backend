import random
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.entry import Entry
from app.db.models.day import Day
from app.core.security import hash_password

random.seed(42)

ENTRY_PARAGRAPHS = [
    "Spent focused time working through implementation details and edge cases. Progress was steady, though a few things required revisiting earlier assumptions.",
    "Hit a small blocker mid-session, but stepping away briefly helped clarify the issue. Simplifying the approach made the solution cleaner.",
    "Energy levels fluctuated today, but pushing through the slower moments still resulted in meaningful progress.",
    "Reviewed existing logic and removed unnecessary complexity. This made future changes easier to reason about.",
    "Learned something new that will likely save time later. Not everything shipped today, but the understanding gained was valuable.",
]

ENTRY_OPENERS = [
    "Morning session:",
    "Midday update:",
    "Evening reflection:",
    "Late-night thoughts:",
]

DAY_SUMMARIES = [
    """Today was productive overall, with consistent forward movement.

There were a few moments where decisions required extra thought, but nothing blocked progress entirely. Breaking work into smaller steps helped maintain momentum.

Ending the day with clarity around next actions made it feel well spent.""",

    """The day started slowly, with some difficulty getting into the right mindset.

Once momentum picked up, work became smoother and more focused. A few lessons emerged around pacing and avoiding unnecessary detours.

Despite the slow start, the day ended on a positive note.""",

    """This was a mentally demanding day that required sustained attention.

Several small issues accumulated into larger challenges, but tackling them one at a time kept things manageable. Not everything was completed, but progress was solid.

Learning and problem-solving were the main wins today.""",

    """Focus and energy aligned well today.

Work flowed naturally with minimal context switching. Tasks that previously felt heavy were completed more easily.

Days like this highlight the value of clear priorities and uninterrupted time.""",
]

TAG_POOL = [
    "work",
    "coding",
    "backend",
    "learning",
    "debugging",
    "productivity",
    "focus",
    "planning",
    "reflection",
    "deep-work",
    "cleanup",
]


def generate_entry_content() -> str:
    paragraphs = random.sample(ENTRY_PARAGRAPHS, random.randint(2, 4))
    opener = random.choice(ENTRY_OPENERS)
    return opener + "\n\n" + "\n\n".join(paragraphs)

min_date = date(2024, 1, 1)
max_date = date.today()
max_days = (max_date - min_date).days
min_days = 500
min_entries_per_day = 2
max_entries_per_day = 10
summary_probability = 0.9



def seed():
    db: Session = SessionLocal()

    try:
        # --- wipe existing dev data ---
        db.query(Entry).delete()
        db.query(Day).delete()
        db.query(User).delete()
        db.commit()

        # --- hash password once ---
        password_hash = hash_password("devpassword")

        users = []
        for i in range(1, 6):
            user = User(
                email=f"dev{i}@example.com",
                password_hash=password_hash,
            )
            db.add(user)
            users.append(user)

        db.flush()  # get user IDs

        for user in users:
            num_days = random.randint(500, 700)

            possible_days = (
                min_date + timedelta(days=i)
                for i in range((max_date - min_date).days)
            )

            day_dates = random.sample(
                list(possible_days),
                num_days,
            )

            for d in day_dates:
                if random.random() < summary_probability:
                    day = Day(
                        user_id=user.id,
                        date=d,
                        summary=random.choice(DAY_SUMMARIES),
                        tags=random.sample(TAG_POOL, random.randint(2, 5)),
                    )
                    db.add(day)

                # --- entries ---
                entries_today = random.randint(min_entries_per_day, max_entries_per_day)
                for _ in range(entries_today):
                    entry = Entry(
                        user_id=user.id,
                        entry_date=d,
                        content=generate_entry_content(),
                    )
                    db.add(entry)

        db.commit()
        print("Dev seed completed successfully")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
