# Setup script for installing dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow

# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Host "uv not found. Installing uv..." -ForegroundColor Red
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    Write-Host "Please restart your terminal and run this script again." -ForegroundColor Yellow
    exit
}

# Create virtual environment and install dependencies
uv venv
uv pip sync requirements.txt

Write-Host "
Dependencies installed successfully!" -ForegroundColor Green
Write-Host "
Next steps:" -ForegroundColor Cyan
Write-Host "1. Copy .env.sample to .env and add your API keys" -ForegroundColor White
Write-Host "2. Add 5 video files to data\videos\" -ForegroundColor White
Write-Host "3. Activate venv: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "4. Run: uv run uvicorn app.server:app --reload" -ForegroundColor White
