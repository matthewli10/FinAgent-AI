from app.database import engine
from app import models
from app.database import Base
from app.models import Summary

print("Dropping all tables...")
models.Base.metadata.drop_all(bind=engine)
print("Creating database tables...")
models.Base.metadata.create_all(bind=engine)
Base.metadata.create_all(bind=engine)
print("Done.")
