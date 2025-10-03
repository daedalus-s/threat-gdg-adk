# Home Threat Detection System

ADK-based AI-powered home security monitoring application.

## Quick Start (Windows)

1. Install dependencies:
```powershell
.\setup.ps1
```

2. Configure environment:
```powershell
copy .env.sample .env
# Edit .env with your API keys
```

3. Add video files to data\videos\ folder:
   - camera_1.mp4
   - camera_2.mp4
   - camera_3.mp4
   - camera_4.mp4
   - camera_5.mp4

4. Run local server:
```powershell
uv run uvicorn app.server:app --host 0.0.0.0 --port 8000 --reload
```

5. Open http://localhost:8000/docs

## Documentation

- See QUICKSTART_CHECKLIST.md for detailed setup
- See DEPLOYMENT_GUIDE.md for cloud deployment
- See IMPLEMENTATION_SUMMARY.md for architecture

## Development

Run tests:
```powershell
uv run pytest tests/
```

Run demo:
```powershell
uv run python scripts/run_demo.py
```
