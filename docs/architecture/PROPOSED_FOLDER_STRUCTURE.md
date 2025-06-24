# 📁 Proposed Folder Structure for Omotenashi POC

## Overview
Clean, intuitive organization that separates concerns and makes the project easily digestible for external viewers, investors, and developers.

## Proposed Structure

```
omotenashi-poc/
│
├── README.md                    # Main project overview (investor-friendly)
├── LICENSE                      # MIT or proprietary license
├── .gitignore                   # Git ignore file
├── .env.example                 # Environment variables template
│
├── 📂 src/                      # Source code
│   ├── 📂 api/                  # API layer
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration management
│   │   └── __init__.py
│   │
│   ├── 📂 agents/               # AI agent logic
│   │   ├── tools.py             # Tool implementations
│   │   ├── prompts.py           # Prompt engineering
│   │   └── __init__.py
│   │
│   ├── 📂 models/               # Data models
│   │   ├── guest.py             # Guest data structures
│   │   ├── booking.py           # Booking models
│   │   └── __init__.py
│   │
│   └── 📂 utils/                # Utilities
│       ├── database.py          # Database connections
│       ├── auth.py              # Authentication helpers
│       └── __init__.py
│
├── 📂 infrastructure/           # Infrastructure as Code
│   ├── 📂 docker/               # Container configuration
│   │   ├── Dockerfile           # Application container
│   │   ├── docker-compose.yml   # Local development
│   │   └── docker-compose.prod.yml
│   │
│   ├── 📂 kubernetes/           # K8s manifests (future)
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── ingress.yaml
│   │
│   ├── 📂 terraform/            # Cloud infrastructure (future)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   │
│   └── 📂 nginx/                # Web server config
│       └── nginx.conf
│
├── 📂 data/                     # Data files
│   ├── 📂 demo/                 # Demo/test data
│   │   ├── guests.json          # Sample guests
│   │   ├── bookings.json        # Sample bookings
│   │   └── villa_azul.txt       # Property info
│   │
│   ├── 📂 migrations/           # Database migrations
│   │   ├── 001_initial_schema.sql
│   │   └── migration_strategy.py
│   │
│   └── 📂 vector_store/         # ChromaDB files
│       └── chroma_db/
│
├── 📂 tests/                    # Test suite
│   ├── 📂 unit/                 # Unit tests
│   │   ├── test_tools.py
│   │   └── test_api.py
│   │
│   ├── 📂 integration/          # Integration tests
│   │   ├── test_guest_journey.py
│   │   └── test_multilingual.py
│   │
│   └── 📂 evaluation/           # Performance evaluation
│       ├── comprehensive_evaluation.py
│       ├── fixed_tool_evaluation.py
│       └── results/
│           ├── tool_evaluation_results.txt
│           └── guest_journey_results.txt
│
├── 📂 frontend/                 # Web interface
│   ├── index.html               # Chat interface
│   ├── static/
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── serve_frontend.py        # Dev server
│
├── 📂 docs/                     # Documentation
│   ├── 📂 architecture/         # System design
│   │   ├── SYSTEM_OVERVIEW.md
│   │   ├── API_DESIGN.md
│   │   └── DATABASE_SCHEMA.md
│   │
│   ├── 📂 api/                  # API documentation
│   │   ├── AUTH_API_CONTRACT.md
│   │   └── TOOL_API_REFERENCE.md
│   │
│   ├── 📂 deployment/           # Deployment guides
│   │   ├── DEPLOYMENT_GUIDE.md
│   │   ├── MONITORING_SETUP.md
│   │   └── SECURITY_BEST_PRACTICES.md
│   │
│   └── 📂 development/          # Developer docs
│       ├── GIT_WORKFLOW.md
│       ├── CONTRIBUTING.md
│       └── TESTING_GUIDE.md
│
├── 📂 management/               # Project management
│   ├── 📂 claude_coordination/  # Multi-Claude workflow
│   │   ├── CLAUDE_SYNC.md
│   │   ├── CONCIERGE_SAN_SYSTEM_INSTRUCTION.md
│   │   ├── RYOKAN_SYSTEM_INSTRUCTION.md
│   │   └── PROTOCOL_UPDATE.md
│   │
│   ├── 📂 planning/             # Project planning
│   │   ├── CONCIERGE_SAN_PILOT_WORKPLAN.md
│   │   ├── RYOKAN_PILOT_WORKPLAN.md
│   │   ├── DAILY_PILOT_DASHBOARD.md
│   │   └── HUMAN_DECISIONS.txt
│   │
│   └── 📂 analysis/             # Analysis & reports
│       ├── COORDINATION_ANALYSIS.md
│       ├── TOOL_EXPANSION_ANALYSIS.txt
│       └── PERFORMANCE_REPORTS.md
│
├── 📂 scripts/                  # Utility scripts
│   ├── setup.sh                 # Environment setup
│   ├── migrate.sh               # Run migrations
│   ├── deploy.sh                # Deployment script
│   └── reorganize_project.py    # File reorganization
│
└── 📂 config/                   # Configuration files
    ├── requirements.txt         # Python dependencies
    ├── .env.example             # Environment template
    └── logging.yaml             # Logging config
```

## Benefits of This Structure

### 🎯 For External Viewers/Investors
- **Clear entry point**: README.md at root with executive summary
- **Logical separation**: Business logic (src) vs infrastructure vs docs
- **Easy navigation**: Intuitive folder names with clear purposes
- **Professional appearance**: Industry-standard structure

### 👨‍💻 For Developers
- **Modular design**: Easy to find and modify specific components
- **Test organization**: Clear separation of test types
- **Infrastructure as Code**: All deployment configs in one place
- **Documentation proximity**: Docs near related code

### 🚀 For Deployment
- **Container-ready**: Docker files properly organized
- **Cloud-agnostic**: Infrastructure folder supports multiple platforms
- **CI/CD friendly**: Scripts folder for automation
- **Environment management**: Clear config separation

## Migration Plan

### Phase 1: Core Structure (Immediate)
1. Create main directories: src, infrastructure, docs, tests
2. Move Python files to appropriate src subdirectories
3. Move infrastructure files (Docker, nginx) to infrastructure/
4. Move documentation to docs/

### Phase 2: Test Organization (Week 1)
1. Create test subdirectories
2. Move evaluation scripts to tests/evaluation/
3. Move results to tests/evaluation/results/

### Phase 3: Project Management (Week 1)
1. Create management/ structure
2. Organize Claude coordination files
3. Move planning documents

### Phase 4: Cleanup (Week 2)
1. Update all import paths
2. Update Docker configurations
3. Test everything still works
4. Update documentation

## Key Files to Highlight

### For Investors/Business
- `README.md` - Polished project overview
- `docs/architecture/SYSTEM_OVERVIEW.md` - High-level architecture
- `management/analysis/PERFORMANCE_REPORTS.md` - Success metrics

### For Technical Evaluation
- `src/agents/tools.py` - Core AI functionality
- `infrastructure/docker/` - Deployment readiness
- `tests/evaluation/results/` - Performance validation

### For Developers
- `docs/development/GIT_WORKFLOW.md` - Contribution guide
- `src/api/main.py` - API entry point
- `config/requirements.txt` - Dependencies

---

**Next Steps**:
1. Review and approve structure
2. Run migration script to reorganize
3. Update all documentation paths
4. Test that everything still works
5. Commit with clear message about reorganization