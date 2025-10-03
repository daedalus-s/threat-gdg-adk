# Windows Setup Script for Home Threat Detection System
# Run this in PowerShell

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "Home Threat Detection System Setup" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Create base directory
$projectName = "home-threat-detection"
Write-Host "Creating project directory: $projectName" -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $projectName | Out-Null
Set-Location $projectName

# Create directory structure
$directories = @(
    "app",
    "app\agents",
    "app\agents\ingestion",
    "app\agents\detection",
    "app\agents\decision",
    "app\tools",
    "app\utils",
    "app\simulators",
    "data",
    "data\videos",
    "data\sample_sensor_data",
    "frontend\src",
    "frontend\src\components",
    "frontend\src\pages",
    "tests\unit",
    "tests\integration",
    "deployment\terraform",
    "notebooks",
    "scripts"
)

Write-Host "Creating directory structure..." -ForegroundColor Yellow
foreach ($dir in $directories) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    Write-Host "  Created: $dir" -ForegroundColor Green
}

# Create __init__.py files
$initFiles = @(
    "app\__init__.py",
    "app\agents\__init__.py",
    "app\agents\ingestion\__init__.py",
    "app\agents\detection\__init__.py",
    "app\agents\decision\__init__.py",
    "app\tools\__init__.py",
    "app\utils\__init__.py",
    "app\simulators\__init__.py",
    "tests\__init__.py",
    "tests\unit\__init__.py",
    "tests\integration\__init__.py"
)

Write-Host "`nCreating Python package files..." -ForegroundColor Yellow
foreach ($file in $initFiles) {
    New-Item -ItemType File -Force -Path $file | Out-Null
    Write-Host "  Created: $file" -ForegroundColor Green
}

# Create .env.sample
Write-Host "`nCreating configuration files..." -ForegroundColor Yellow
$envSample = @"
# Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=True

# Optional: Pinecone Vector Database
PINECONE_API_KEY=your-pinecone-key

# Optional: For AI Studio instead of Vertex AI (development only)
# GOOGLE_API_KEY=your-api-key
# GOOGLE_GENAI_USE_VERTEXAI=False
"@
Set-Content -Path ".env.sample" -Value $envSample
Write-Host "  Created: .env.sample" -ForegroundColor Green

# Create .gitignore
$gitignore = @"
__pycache__/
*.pyc
*.pyo
*.pyd
.venv
venv/
env/
.env
*.log
data/videos/*.mp4
.pytest_cache/
.coverage
*.egg-info/
dist/
build/
.DS_Store
Thumbs.db
"@
Set-Content -Path ".gitignore" -Value $gitignore
Write-Host "  Created: .gitignore" -ForegroundColor Green

# Create README.md
$readme = @"
# Home Threat Detection System

ADK-based AI-powered home security monitoring application.

## Quick Start (Windows)

1. Install dependencies:
``````powershell
.\setup.ps1
``````

2. Configure environment:
``````powershell
copy .env.sample .env
# Edit .env with your API keys
``````

3. Add video files to data\videos\ folder:
   - camera_1.mp4
   - camera_2.mp4
   - camera_3.mp4
   - camera_4.mp4
   - camera_5.mp4

4. Run local server:
``````powershell
uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
``````

5. Open http://localhost:8000/docs

## Documentation

- See QUICKSTART_CHECKLIST.md for detailed setup
- See DEPLOYMENT_GUIDE.md for cloud deployment
- See IMPLEMENTATION_SUMMARY.md for architecture

## Development

Run tests:
``````powershell
uv run pytest tests/
``````

Run demo:
``````powershell
uv run python scripts/run_demo.py
``````
"@
Set-Content -Path "README.md" -Value $readme
Write-Host "  Created: README.md" -ForegroundColor Green

# Create requirements.txt
$requirements = @"
google-adk[a2a]>=1.15.1
fastapi>=0.115.0
uvicorn>=0.34.0
opencv-python>=4.10.0
pillow>=10.4.0
pinecone-client>=5.0.0
pydantic>=2.9.0
python-multipart>=0.0.12
python-dotenv>=1.0.0
google-cloud-storage>=2.18.0
google-cloud-aiplatform>=1.106.0
numpy>=1.26.0
pytest>=8.3.0
pytest-asyncio>=0.23.0
"@
Set-Content -Path "requirements.txt" -Value $requirements
Write-Host "  Created: requirements.txt" -ForegroundColor Green

# Create setup.ps1 for dependency installation
$setupScript = @"
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

Write-Host "`nDependencies installed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Copy .env.sample to .env and add your API keys" -ForegroundColor White
Write-Host "2. Add 5 video files to data\videos\" -ForegroundColor White
Write-Host "3. Activate venv: .venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "4. Run: uv run uvicorn app.server:app --reload" -ForegroundColor White
"@
Set-Content -Path "setup.ps1" -Value $setupScript
Write-Host "  Created: setup.ps1" -ForegroundColor Green

Write-Host "`n======================================" -ForegroundColor Cyan
Write-Host "Project structure created successfully!" -ForegroundColor Green
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "`nLocation: $PWD" -ForegroundColor Yellow
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Run: .\setup.ps1  (to install dependencies)" -ForegroundColor White
Write-Host "2. Copy .env.sample to .env and configure" -ForegroundColor White
Write-Host "3. Add video files to data\videos\" -ForegroundColor White
Write-Host "`nNote: You'll need to copy the Python code files from" -ForegroundColor Yellow
Write-Host "the artifacts I provided earlier into the appropriate directories." -ForegroundColor Yellow