from fastapi import FastAPI
from routes import auth, todo
from database import engine, Base
from models.todo import Todo
from models.user import User

app = FastAPI()

# Create tables in the database based on models
print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Tables created.")

# Register routers with prefixes
app.include_router(auth.router, prefix="/auth")
app.include_router(todo.router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to the Todo app!"}
