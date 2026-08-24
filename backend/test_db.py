from app.db.database import engine


try:
    with engine.connect() as connection:
        print("✓ PostgreSQL bağlantısı başarılı!")
        print(f"✓ Database: {connection.engine.url.database}")

except Exception as error:
    print("❌ PostgreSQL bağlantısı başarısız!")
    print(error)