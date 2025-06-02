from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, watchlist, summaries, fetch

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, tags=["authentication"])
app.include_router(watchlist.router, tags=["watchlist"])
app.include_router(summaries.router, tags=["summaries"])
app.include_router(fetch.router, tags=["fetch"])

@app.get("/")
def read_root():
    return {"message": "Welcome to FinAgent API"}
