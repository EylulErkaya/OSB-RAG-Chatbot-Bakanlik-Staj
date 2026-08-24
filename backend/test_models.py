from app.db.base import Base
from app.models import Conversation, Message


print("✓ Conversation modeli:", Conversation.__tablename__)
print("✓ Message modeli:", Message.__tablename__)

print("\n✓ Base tabloları:")
for table in Base.metadata.tables:
    print(f"  - {table}")