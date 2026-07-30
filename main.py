import uvicorn
from fastapi import FastAPI
from api.alm_router import router as alm_router
from config.dependencies import lifespan

# 1. FastAPI 인스턴스 생성
app = FastAPI(
    title="ALM Dashboard REST API Server",
    version="1.0.0",
    description="Multi-DB Query Engine API",
    lifespan=lifespan,
)

# 2. 분리한 라우터 등록
app.include_router(alm_router)

# 3. 헬스체크용 루트 엔드포인트
@app.get("/")
async def root():
    return {"message": "FastAPI Server is running"}


# 4. python main.py 로 직접 실행할 수 있도록 진입점 구성
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=False)
