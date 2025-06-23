# Claude Multi-Instance Coordination

## Current Active Instances

| Instance | Branch | Primary Focus | Status |
|----------|--------|---------------|--------|
| Claude-Instance-1 | `claude-instance-1` | Backend/API (main.py, config.py) | Active |
| Claude-Instance-2 | `claude-migration` | AI/Tools (prompts.py, tools.py) | Active |

## File Ownership Assignments

### Instance 1 - Backend/Infrastructure
- `main.py` - FastAPI application and endpoints
- `config.py` - Configuration and environment settings
- `requirements.txt` - Dependencies management
- `static/index.html` - Frontend interface

### Instance 2 - AI/Tools System  
- `prompts.py` - System prompts and templates
- `tools.py` - Tool definitions and implementations
- `guests.json` - Guest data management
- `bookings.json` - Booking data management
- `villa_azul.txt` - Property information

### Shared Files (Coordinate Before Editing)
- `README.md` - Documentation updates
- `.env` - Environment configuration
- `chroma_db/` - Vector database (coordinate data changes)

## Git Workflow

### Branch Strategy
```bash
# Main development branch
claude-migration (current shared branch)

# Instance-specific branches
claude-instance-1 (Backend/API focus)
claude-instance-2 (AI/Tools focus)
```

### Commit Message Convention
```
[CLAUDE-X] Type: Brief description

Types: feat, fix, refactor, docs, test, style
Examples:
[CLAUDE-1] feat: add new API endpoint for guest preferences
[CLAUDE-2] fix: improve tool response handling
```

### Sync Protocol
1. Pull latest changes before starting work: `git pull origin claude-migration`
2. Work on assigned files in your branch
3. Commit frequently with descriptive messages
4. Push to your branch regularly
5. Create PR to merge back to `claude-migration`

## Communication Protocol

### Status Updates
- Update this file when starting/completing major tasks
- Use commit messages for progress communication
- Note any cross-file dependencies or conflicts

### Conflict Resolution
1. If editing shared files, announce in commit message
2. Pull latest changes before working on shared files
3. Use feature flags for experimental changes
4. Coordinate through git commit messages

## Current Work Status

### Instance 1 Tasks
- [ ] API endpoint optimization
- [ ] Configuration management
- [ ] Frontend improvements

### Instance 2 Tasks  
- [ ] Tool system enhancement
- [ ] Prompt optimization
- [ ] Guest data management

## Notes
- Created: 2025-06-23
- Last Updated: 2025-06-23
- Coordination established by Claude Instance 1