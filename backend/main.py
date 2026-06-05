from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from database import engine, Base
from routers import auth_router, chat_router, profile_router, interview_router, quiz_router, resume_router

Base.metadata.create_all(bind=engine)

app = FastAPI(title="INFERA API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    print("--- VALIDATION ERROR ---")
    print("Errors:", exc.errors())
    try:
        body = await request.body()
        print("Body:", body.decode('utf-8', errors='ignore'))
    except Exception as e:
        print("Could not read body:", e)
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()},
    )

app.include_router(auth_router.router)
app.include_router(chat_router.router)
app.include_router(profile_router.router)
app.include_router(interview_router.router)
app.include_router(quiz_router.router)
app.include_router(resume_router.router)

@app.get("/health")
def health_check():
    return {"status": "ok", "version": "2.0"}
