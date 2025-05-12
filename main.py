from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import user
from app.database import register_db
from app.routes import subscription_route
app = FastAPI(title="Summit API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Register database
register_db(app)

# Include routers
app.include_router(user.router, prefix="/api/v1")
app.include_router(subscription_route.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Summit API"}
