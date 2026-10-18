# CPGRAMS Personal Workbench - PowerShell Launcher
# Ministry of Electronics and Information Technology (MeitY)

Write-Host "=========================================================================" -ForegroundColor Cyan
Write-Host "   CPGRAMS PERSONAL WORKBENCH - LOCAL AUTOMATION & GRIEVANCE MANAGEMENT" -ForegroundColor Yellow
Write-Host "   AI & Emerging Technologies Division, MeitY, Government of India" -ForegroundColor White
Write-Host "=========================================================================" -ForegroundColor Cyan

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

$pyExe = "C:\Users\Hp\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path $pyExe)) {
    $pyExe = "python.exe"
}

Write-Host "`n[1/3] Checking Python runtime..." -ForegroundColor Green
& $pyExe --version

Write-Host "`n[2/3] Performing local database initialization..." -ForegroundColor Green
& $pyExe -c "import backend.main; print('Database and models initialized.')"

Write-Host "`n[3/3] Launching Workbench on http://127.0.0.1:8000..." -ForegroundColor Green
Start-Process "http://127.0.0.1:8000"
& $pyExe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
