from app.models.database import Base, engine
from app.models.storage import Storage
from app.models.wine import Wine

def init_db():
    """Create database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

if __name__ == "__main__":
    init_db()