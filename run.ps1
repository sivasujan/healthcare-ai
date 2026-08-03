# Single command to run BOTH backend (FastAPI) and frontend (Next.js) together.
#
# Usage (from the project root):
#   .\run.ps1
#
# Ctrl+C stops both servers.
# Backend:  http://localhost:8000  (Swagger UI at /docs)
# Frontend: http://localhost:3000

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host ""
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  MediAssist - AI Healthcare Assistant" -ForegroundColor Cyan
Write-Host "  Starting backend + frontend together" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host ""

# ---------- Backend ----------
$backendVenv = Join-Path $root "backend\.venv\Scripts\python.exe"
if (-not (Test-Path $backendVenv)) {
    Write-Host "[1/3] Creating backend virtual environment..." -ForegroundColor Yellow
    Push-Location (Join-Path $root "backend")
    python -m venv .venv
    & ".\.venv\Scripts\python.exe" -m pip install -r requirements.txt --quiet
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
        Write-Host "      Created backend\.env from .env.example - add your OPENROUTER_API_KEY!" -ForegroundColor Yellow
    }
    Pop-Location
}

Write-Host "[2/3] Starting backend (FastAPI on :8000)..." -ForegroundColor Green
$backend = Start-Process -FilePath $backendVenv -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000" -WorkingDirectory (Join-Path $root "backend") -PassThru -NoNewWindow -RedirectStandardOutput (Join-Path $env:TEMP "hc_backend.log") -RedirectStandardError (Join-Path $env:TEMP "hc_backend_err.log")

# ---------- Frontend ----------
if (-not (Test-Path (Join-Path $root "frontend\node_modules"))) {
    Write-Host "      Installing frontend dependencies (first run only)..." -ForegroundColor Yellow
    Push-Location (Join-Path $root "frontend")
    npm install --silent
    Pop-Location
}

Write-Host "[3/3] Starting frontend (Next.js on :3000)..." -ForegroundColor Green
$frontend = Start-Process -FilePath "npm" -ArgumentList "run", "dev" -WorkingDirectory (Join-Path $root "frontend") -PassThru -NoNewWindow -RedirectStandardOutput (Join-Path $env:TEMP "hc_frontend.log") -RedirectStandardError (Join-Path $env:TEMP "hc_frontend_err.log")

Write-Host ""
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  Backend : http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host "  Press Ctrl+C to stop both." -ForegroundColor DarkGray
Write-Host ""

try {
    Wait-Process -Id $backend.Id, $frontend.Id -ErrorAction SilentlyContinue
} finally {
    Stop-Process -Id $backend.Id, $frontend.Id -Force -ErrorAction SilentlyContinue
    Write-Host "Both servers stopped." -ForegroundColor Yellow
}
