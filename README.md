# Home Threat Detection System

An intelligent, multi-modal threat detection system using Google's Agent Development Kit (ADK), computer vision, and temporal analytics. The system analyzes video feeds from multiple cameras and sensor data to detect and respond to home security threats in real-time.

Agent generated with [`googleCloudPlatform/agent-starter-pack`](https://github.com/GoogleCloudPlatform/agent-starter-pack) version `0.15.7`

## 🌟 Key Features

### Multi-Modal Threat Detection
- **5-Camera System**: Simultaneous analysis of multiple video feeds
- **Sensor Integration**: Smartwatch vitals, accelerometer, audio, and smoke detectors
- **AI-Powered Analysis**: Gemini 2.5 models for vision and decision-making
- **Threat Classification**: Weapon detection, fall detection, fire detection, intrusion detection

### Temporal Storage & Querying
- **Automatic Storage**: All insights automatically saved to Pinecone vector database
- **Natural Language Queries**: Ask questions like "What happened between 15-20 seconds?"
- **Semantic Search**: Find events by description (e.g., "weapon detection")
- **Timeline Retrieval**: Complete chronological history for any camera
- **Session Tracking**: Group related analyses for easy review

### Intelligent Orchestration
- **Multi-Agent System**: Specialized agents for vision, sensors, and orchestration
- **Decision Engine**: AI-powered threat assessment with evidence-based reasoning
- **Escalation Logic**: Automatic 911 alerting for critical threats
- **Iterative Refinement**: Quality checks with follow-up analysis

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Video Input (5 Cameras)                  │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│              Vision Analysis Agent (Gemini 2.5)             │
│  - Weapon detection    - People counting                    │
│  - Face recognition    - Threat classification              │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│           Temporal Vector Store (Pinecone)                  │
│  - Automatic storage   - Semantic search                    │
│  - Time-range queries  - Session tracking                   │
└───────────────────────┬─────────────────────────────────────┘
                        │
    ┌───────────────────┴───────────────────┐
    ▼                                       ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│  Sensor Data Analysis   │   │   Query Agent (NLU)     │
│  - Heart rate           │   │  "What happened at      │
│  - Accelerometer        │   │   15 seconds?"          │
│  - Audio detection      │   │                         │
│  - Smoke detection      │   └─────────────────────────┘
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────┐
│              Orchestrator Agent (Decision Maker)            │
│  - Threat correlation  - Evidence evaluation                │
│  - Action determination - Alert generation                  │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
home-threat-detection/
├── app/                              # Core application code
│   ├── agent.py                      # Base agent configuration
│   ├── server.py                     # FastAPI server
│   ├── comprehensive_pipeline_auto.py # Main pipeline with auto-storage
│   │
│   ├── agents/                       # Specialized AI agents
│   │   ├── vision_agent.py          # Camera frame analysis
│   │   ├── sensor_agent.py          # Sensor data analysis
│   │   └── orchestrator_agent.py    # Final decision making
│   │
│   ├── temporal/                     # 🆕 Temporal storage system
│   │   ├── vector_store.py          # Pinecone integration
│   │   ├── query_agent.py           # Natural language queries
│   │   └── integration_demo.py      # Usage examples
│   │
│   ├── video/                        # Video processing
│   │   ├── full_video_analyzer.py   # Complete video analysis
│   │   ├── real_video_processor.py  # Frame extraction
│   │   └── vision_analyzer.py       # Frame-by-frame analysis
│   │
│   ├── sensors/                      # Sensor simulation
│   │   ├── simulator.py             # Mock sensor data
│   │   └── models.py                # Data models
│   │
│   └── utils/                        # Utility functions
│       ├── tracing.py               # Observability
│       └── gcs.py                   # Cloud storage
│
├── videos/                           # Video files directory
│   ├── weapon.mp4                   # Weapon threat scenario
│   ├── fall.mp4                     # Fall detection scenario
│   ├── fire.mp4                     # Fire detection scenario
│   └── normal.mp4                   # Normal scenario baseline
│
├── tests/                            # Test suite
│   ├── unit/                        # Unit tests
│   └── integration/                 # Integration tests
│
├── deployment/                       # Infrastructure as code
│   └── terraform/                   # Terraform configurations
│
├── notebooks/                        # Jupyter notebooks
│   ├── adk_app_testing.ipynb       # Testing guide
│   └── evaluating_adk_agent.ipynb  # Evaluation guide
│
├── Makefile                         # Common commands
├── pyproject.toml                   # Dependencies
├── GEMINI.md                        # AI development guide
└── README.md                        # This file
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+**
- **uv package manager** - [Install](https://docs.astral.sh/uv/getting-started/installation/)
- **Google Cloud SDK** - [Install](https://cloud.google.com/sdk/docs/install)
- **Pinecone Account** (Free tier) - [Sign up](https://www.pinecone.io/)
- **Google API Key** - [Get key](https://aistudio.google.com/app/apikey)

### Installation

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd home-threat-detection

# 2. Install dependencies
make install

# 3. Set up environment variables
# PowerShell:
$env:GOOGLE_API_KEY="your-google-api-key"
$env:PINECONE_API_KEY="your-pinecone-api-key"
$env:PINECONE_ENVIRONMENT="gcp-starter"

# Or create .env file:
echo "GOOGLE_API_KEY=your-google-api-key" >> .env
echo "PINECONE_API_KEY=your-pinecone-api-key" >> .env
echo "PINECONE_ENVIRONMENT=gcp-starter" >> .env

# 4. Add video files (optional)
# Place your test videos in the videos/ directory
```

### Run the System

```bash
# Option 1: Run complete pipeline with auto-storage
uv run python app/comprehensive_pipeline_auto.py

# Option 2: Launch interactive playground
make playground

# Option 3: Run specific scenario
make demo-intrusion  # Weapon detection scenario
make demo-fall       # Fall detection scenario
make demo-fire       # Fire detection scenario
```

## 💡 Usage Examples

### 1. Analyze Videos with Automatic Storage

```python
import asyncio
from app.comprehensive_pipeline_auto import ComprehensiveThreatDetectionPipeline

async def main():
    # Configure your video files
    video_files = {
        1: r"videos\weapon.mp4",
        2: r"videos\fall.mp4",
        3: r"videos\normal.mp4",
    }
    
    # Initialize pipeline with auto-storage
    pipeline = ComprehensiveThreatDetectionPipeline(
        enable_temporal_storage=True  # ✅ Auto-stores all insights
    )
    
    # Run analysis
    result = await pipeline.run_complete_analysis(
        scenario="weapon_threat",
        video_files=video_files
    )
    
    print(f"✅ Analysis complete!")
    print(f"Session ID: {result['session_id']}")
    print(f"Threat Level: {result['decision']['threat_level']}")
    print(f"Call 911: {result['decision']['call_911']}")

asyncio.run(main())
```

### 2. Query Stored Insights

```python
from app.temporal.vector_store import TemporalVectorStore

# Initialize vector store
store = TemporalVectorStore()

# Query by time range
insights = store.query_by_time_range(
    camera_id=1,
    start_time=15.0,
    end_time=20.0
)

for insight in insights:
    print(f"{insight['timestamp']:.1f}s: {insight['threat_level']} - {insight['description']}")

# Semantic search
results = store.query_by_semantic_search(
    query_text="weapon detection",
    camera_id=1,
    top_k=5
)

# Query by threat level
critical_events = store.query_by_threat_level(
    threat_level="critical",
    camera_id=1
)
```

### 3. Natural Language Queries

```python
import asyncio
from app.temporal.integration_demo import query_temporal_data

async def main():
    queries = [
        "What happened in camera 1 between 15 and 20 seconds?",
        "Show me all weapon detections",
        "When did someone fall?",
        "Give me a timeline for camera 3"
    ]
    
    for query in queries:
        response = await query_temporal_data(query)
        print(f"\nQuery: {query}")
        print(f"Response: {response}\n")

asyncio.run(main())
```

## 🎯 Threat Detection Scenarios

### Intrusion Detection
- **Triggers**: Weapon detected + Unfamiliar face
- **Actions**: Immediate 911 call
- **Evidence**: Camera frames, facial recognition, weapon type

### Fall Detection
- **Triggers**: Accelerometer spike + Vital anomalies + Person on ground
- **Actions**: Check-in → Emergency contact → 911
- **Evidence**: Accelerometer data, heart rate, camera confirmation

### Fire Detection
- **Triggers**: Smoke detector + Audio alarm + Visual smoke
- **Actions**: Immediate 911 call + Evacuation alert
- **Evidence**: Smoke levels, temperature, camera visuals

### Suspicious Activity
- **Triggers**: Camera tampering + Unknown person + Odd hours
- **Actions**: Alert owner → Review footage → Escalate if needed
- **Evidence**: Motion patterns, time of day, behavior analysis

## 🛠️ Available Commands

```bash
# Development
make install          # Install dependencies
make playground       # Launch ADK web UI
make local-backend    # Run local development server

# Demo scenarios
make demo             # Run all scenarios
make demo-intrusion   # Weapon detection demo
make demo-fall        # Fall detection demo
make demo-fire        # Fire detection demo

# Testing
make test             # Run all tests
make lint             # Run code quality checks

# Deployment
make backend          # Deploy to Cloud Run
make setup-dev-env    # Setup GCP development environment

# Cleanup
make clean            # Remove build artifacts
```

## 🔧 Configuration

### Video Configuration

Edit `app/comprehensive_pipeline_auto.py`:

```python
video_config = {
    1: r"videos\camera1.mp4",    # Front door
    2: r"videos\camera2.mp4",    # Living room
    3: r"videos\camera3.mp4",    # Kitchen
    4: r"videos\camera4.mp4",    # Bedroom
    5: r"videos\camera5.mp4",    # Backyard
}
```

### Enable/Disable Temporal Storage

```python
# Enabled (default) - stores all insights
pipeline = ComprehensiveThreatDetectionPipeline(
    enable_temporal_storage=True
)

# Disabled - no storage
pipeline = ComprehensiveThreatDetectionPipeline(
    enable_temporal_storage=False
)
```

### Model Configuration

Edit `app/agents/*.py` to change models:

```python
# Use different Gemini models
vision_agent = Agent(
    model="gemini-2.5-pro",  # More capable but slower
    # model="gemini-2.5-flash",  # Faster but less capable
    ...
)
```

## 📊 Temporal Storage Features

### What Gets Stored

For each analyzed frame:
- **Timestamp**: Exact time in video
- **Threat Level**: none, low, medium, high, critical
- **Detections**: Weapons, people count, unfamiliar faces
- **Description**: AI-generated scene description
- **Metadata**: Camera ID, session ID, video path

### Query Capabilities

**Time-based queries:**
- "between 15 and 20 seconds"
- "first 30 seconds"
- "from 1:15 to 1:45"
- "at 45 seconds"

**Semantic queries:**
- "weapon detection"
- "unfamiliar person"
- "people on the ground"
- "critical threats"

**Timeline queries:**
- "complete timeline for camera 1"
- "all high-threat events"
- "chronological event list"

## 🧪 Testing

### Run All Tests

```bash
make test
```

### Test Temporal Storage

```bash
# Test vector store functionality
uv run python test_temporal_system.py

# Run integration demo
uv run python -m app.temporal.integration_demo
```

### Test Specific Scenario

```python
# Test single video analysis
uv run python test_single_video.py videos/weapon.mp4
```

## 📈 Performance Metrics

- **Frame Analysis**: ~2-3 seconds per frame (Gemini 2.5 Flash)
- **Video Processing**: ~30-60 seconds for 60-second video
- **Storage Insertion**: ~50-100ms per frame insight
- **Time-Range Query**: ~100-200ms
- **Semantic Search**: ~200-300ms
- **Vector Store**: ~2KB per frame insight

## 🔐 Security & Privacy

### Data Storage
- All video data processed locally
- Only insights (text descriptions) stored in Pinecone
- No raw video frames uploaded to vector database
- Session-based data isolation

### API Keys
- Store in environment variables or `.env` file
- Never commit API keys to version control
- Use separate keys for dev/staging/production

### Access Control
- IAP (Identity-Aware Proxy) for deployed services
- Role-based access for Cloud Run
- Private Pinecone indexes

## 🚀 Deployment

### Local Development

```bash
# Run locally with hot-reload
make playground
# Open http://localhost:8501
```

### Google Cloud Run

```bash
# Deploy to Cloud Run
gcloud config set project YOUR_PROJECT_ID
make backend

# Deploy with IAP enabled
make backend IAP=true
```

### CI/CD Setup

```bash
# One-command CI/CD setup
uvx agent-starter-pack setup-cicd \
  --staging-project your-staging-project \
  --prod-project your-prod-project \
  --repository-name your-repo-name \
  --auto-approve
```

See [deployment/README.md](deployment/README.md) for detailed instructions.

## 🐛 Troubleshooting

### Error: GOOGLE_API_KEY not found
```bash
# Set in PowerShell
$env:GOOGLE_API_KEY="your-key"

# Or add to .env file
echo "GOOGLE_API_KEY=your-key" >> .env
```

### Error: PINECONE_API_KEY not found
```bash
# Get key from https://www.pinecone.io/
$env:PINECONE_API_KEY="your-key"
$env:PINECONE_ENVIRONMENT="gcp-starter"
```

### Error: Video file not found
```bash
# Check video directory
ls videos/

# Use absolute paths in video_config
video_config = {
    1: r"C:\full\path\to\video.mp4"
}
```

### Temporal storage disabled
```
ℹ️  Temporal storage DISABLED
```
This is normal if Pinecone is not configured. Install dependencies:
```bash
uv add pinecone sentence-transformers
```

### Model timeout errors
```python
# Increase timeout in agent configuration
generate_content_config = types.GenerateContentConfig(
    timeout=120  # Increase from default 60s
)
```

## 📚 Documentation

- [ADK Documentation](https://google.github.io/adk-docs/)
- [Temporal Storage Guide](app/temporal/README.md)
- [GEMINI.md](GEMINI.md) - AI-assisted development guide
- [Deployment Guide](deployment/README.md)
- [Agent Evaluation](notebooks/evaluating_adk_agent.ipynb)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [Google Agent Development Kit (ADK)](https://github.com/google/adk-python)
- Vector storage powered by [Pinecone](https://www.pinecone.io/)
- LLM capabilities from [Google Gemini](https://deepmind.google/technologies/gemini/)
- Embeddings by [Sentence Transformers](https://www.sbert.net/)

## 📞 Support

For issues and questions:
- 📖 Check the [documentation](https://google.github.io/adk-docs/)
- 🐛 [Open an issue](https://github.com/your-repo/issues)
- 💬 [Discussions](https://github.com/your-repo/discussions)

---

**Built using Google ADK**