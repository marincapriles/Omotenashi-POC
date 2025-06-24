# 🔄 Git Workflow for Multi-Claude Instance Development

## Overview
This document defines the Git workflow for efficient parallel development between Concierge-san (Backend/Infrastructure) and Ryokan-chan (AI/Tools & Guest Experience) Claude instances.

## Core Principles
1. **Minimize Conflicts**: Work in separate areas of the codebase
2. **Frequent Integration**: Daily syncs to catch issues early
3. **Clear Communication**: Use CLAUDE_SYNC.md for coordination
4. **Clean History**: Meaningful commits with proper prefixes

## Branch Strategy

### Main Branch
- **Purpose**: Production-ready code, always stable
- **Protection**: Never force push, all changes via PR/merge
- **Deployment**: Tagged releases from main only

### Feature Branches
```
concierge-backend-infra    # Concierge-san's primary branch
ryokan-guest-experience    # Ryokan-chan's primary branch
```

### Naming Convention
```
[instance]-[feature]-[ticket]

Examples:
concierge-monitoring-setup
ryokan-spanish-fixes
concierge-gcp-deployment
ryokan-vip-enhancements
```

## Daily Workflow

### 🌅 Session Start Protocol (BOTH INSTANCES)
```bash
# 1. Update main branch
git checkout main
git pull origin main

# 2. Update your feature branch
git checkout [your-branch]
git merge main  # Get latest changes

# 3. Read coordination files
# - CONCIERGE_SAN_SYSTEM_INSTRUCTION.md or RYOKAN_SYSTEM_INSTRUCTION.md
# - HUMAN_DECISIONS.txt
# - CLAUDE_SYNC.md
```

### 🔨 During Development
```bash
# 1. Work in your branch
git checkout [your-branch]

# 2. Commit frequently with proper prefixes
git add [files]
git commit -m "[CONCIERGE-SAN] feat: implement Redis caching layer"
git commit -m "[RYOKAN-CHAN] fix: Spanish language tool classification"

# 3. Push regularly
git push origin [your-branch]
```

### 🌆 Session End Protocol
```bash
# 1. Update CLAUDE_SYNC.md with decisions/progress
git add CLAUDE_SYNC.md
git commit -m "[CONCIERGE-SAN] sync: document infrastructure decisions"

# 2. Push all changes
git push origin [your-branch]

# 3. Create merge request if feature complete
```

## Merge Protocol

### Pre-Merge Checklist
- [ ] All tests passing
- [ ] No merge conflicts with main
- [ ] CLAUDE_SYNC.md updated with changes
- [ ] Coordination with other instance if needed
- [ ] Human decisions incorporated

### Merge Process
```bash
# 1. Update and test
git checkout main
git pull origin main
git checkout [your-branch]
git merge main  # Resolve any conflicts

# 2. Run tests
python -m pytest  # or appropriate test command

# 3. Merge to main
git checkout main
git merge [your-branch] --no-ff
git push origin main

# 4. Clean up
git branch -d [your-branch]  # Delete local branch
git push origin --delete [your-branch]  # Delete remote
```

## Conflict Resolution

### Typical Conflict Areas
| File | Concierge-san Owns | Ryokan-chan Owns |
|------|-------------------|------------------|
| main.py | Infrastructure, deployment config | Agent initialization, routes |
| tools.py | Tool infrastructure, error handling | Tool logic, prompts |
| config.py | Environment variables, infrastructure | Model settings, tool config |
| prompts.py | - | All prompt engineering |
| database_schema.sql | All database changes | - |
| docker-compose.yml | All container configuration | - |

### Conflict Resolution Process
1. **Communication First**: Check CLAUDE_SYNC.md for context
2. **Ownership Respect**: Defer to owner for their areas
3. **Test Everything**: Ensure both features still work
4. **Document Decision**: Update CLAUDE_SYNC.md

## Commit Message Format

### Structure
```
[INSTANCE] type: description

Body (optional)

Refs: #ticket
```

### Types
- **feat**: New feature
- **fix**: Bug fix
- **perf**: Performance improvement
- **refactor**: Code restructuring
- **docs**: Documentation only
- **test**: Test additions/changes
- **sync**: Coordination updates

### Examples
```
[CONCIERGE-SAN] feat: implement JWT authentication system

- Phone number verification via Twilio
- 15-minute token expiration
- Refresh token support

Refs: #AUTH-001
```

```
[RYOKAN-CHAN] fix: Spanish meal_delivery tool responses

- Updated prompt with explicit Spanish examples
- Fixed tool classification for Spanish queries
- Added Spanish-specific error messages
```

## Integration Windows

### Daily Sync Points (Pacific Time)
- **9:00 AM**: Morning sync - review overnight changes
- **2:00 PM**: Midday sync - coordinate afternoon work
- **6:00 PM**: Evening sync - prepare for next day

### Weekly Integration
- **Monday**: Plan week, assign focus areas
- **Wednesday**: Mid-week integration test
- **Friday**: Full merge to main, tag if stable

## File Ownership Matrix

### Concierge-san (Backend/Infrastructure)
```
Primary ownership:
- Dockerfile, docker-compose.yml
- nginx.conf
- database_schema.sql
- migration_strategy.py
- AUTH_API_CONTRACT.md
- Requirements.txt (infrastructure packages)
- .env.example
- deployment/
- monitoring/
- scripts/
```

### Ryokan-chan (AI/Tools & Guest Experience)
```
Primary ownership:
- prompts.py
- tools.py (tool logic)
- evaluation*.py
- comprehensive_*.py
- guests.json
- bookings.json
- static/index.html
- Requirements.txt (AI/ML packages)
```

### Shared Ownership (Coordinate Changes)
```
Both must coordinate:
- main.py
- config.py
- CLAUDE_SYNC.md
- README.md
- CLAUDE.md
```

## Emergency Procedures

### Production Hotfix
```bash
# 1. Create hotfix branch from main
git checkout main
git pull origin main
git checkout -b hotfix-[issue]

# 2. Fix and test
# ... make changes ...
git commit -m "[HOTFIX] fix: description"

# 3. Merge directly to main
git checkout main
git merge hotfix-[issue] --no-ff
git push origin main

# 4. Update other branches
git checkout [your-branch]
git merge main
```

### Rollback Process
```bash
# Find last stable commit
git log --oneline -10

# Revert to stable state
git checkout main
git revert [bad-commit]
git push origin main
```

## Best Practices

### DO's
- ✅ Commit early and often
- ✅ Write descriptive commit messages
- ✅ Update CLAUDE_SYNC.md for major decisions
- ✅ Test before merging
- ✅ Respect file ownership boundaries
- ✅ Communicate blocking changes immediately

### DON'Ts
- ❌ Force push to main
- ❌ Merge with failing tests
- ❌ Work directly in main (except hotfixes)
- ❌ Ignore merge conflicts
- ❌ Make changes outside your expertise area
- ❌ Commit sensitive data or API keys

## Integration Timeline (8-Week Pilot)

### Weeks 1-2: Foundation
- Separate branches for major infrastructure
- Daily syncs for coordination

### Weeks 3-4: Feature Development
- Feature branches for new capabilities
- Integration tests every 2 days

### Weeks 5-6: Integration
- Merge to main for integrated testing
- Feature freeze at end of week 6

### Weeks 7-8: Hardening
- Work in main for final fixes
- Tag release candidates
- Production deployment prep

---

**Last Updated**: 2025-06-24
**Status**: Active workflow for 8-week pilot development
**Next Review**: After first week of usage