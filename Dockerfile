# ----------------------------------------------------
# 1단계: 빌드 환경 (Build Stage)
# ----------------------------------------------------
FROM python:3.14-alpine AS builder

# 작업 디렉토리 설정
WORKDIR /app

# Alpine 환경에서 C extension을 컴파일해야 하는 라이브러리가 있을 경우를 대비해 빌드 도구 설치
RUN apk add --no-cache \
    gcc \
    g++ \
    musl-dev \
    libffi-dev \
    unixodbc-dev

# 가상환경(venv) 생성 및 활성화 설정
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"

COPY pyproject.toml uv.lock* ./

# pip 업그레이드 및 라이브러리 설치
RUN pip install --no-cache-dir uv && uv pip install .

# ----------------------------------------------------
# 2단계: 실행 환경 (Runtime Stage)
# ----------------------------------------------------
FROM python:3.14-alpine AS runner

# 작업 디렉토리 설정
WORKDIR /app

# 빌드 단계에서 생성된 가상환경(venv)만 복사하여 이미지 용량 최적화
COPY --from=builder /opt/venv /opt/venv

# 컨테이너 내에서 항상 가상환경이 활성화되도록 PATH 설정
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app"
ENV PYTHONUNBUFFERED=1

# 애플리케이션 소스 코드 복사
COPY . .

# SSE 포트 노출
EXPOSE 8080

# 컨테이너 실행 시 가상환경 내의 python으로 

CMD ["python", "-m", "main"]