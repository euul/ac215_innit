from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.videos import router as videos_router

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Change this to the frontend's address
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the videos route
app.include_router(videos_router)
