# Claude Multi-Instance Synchronization Protocol

## Communication Strategy

### 📋 Decision Capture Framework

All architectural and design decisions must be logged in this file using the following format:

```markdown
## [DECISION-ID] [TIMESTAMP] Decision Title
**Decided by**: Claude-Instance-X
**Impact**: High/Medium/Low
**Files Affected**: list of files
**Description**: What was decided and why
**Implementation**: How it was implemented
**Next Actions**: Required follow-up tasks for other instances
```

### 🔄 Sync Triggers

**Mandatory Sync Points**:
1. Before major architectural changes
2. After completing feature implementations  
3. Before production deployments
4. When encountering cross-file dependencies
5. Daily sync at session start

**Sync Commands**:
```bash
# Pull latest changes and sync context
git pull origin claude-migration
git merge claude-instance-2  # or appropriate branch
# Read CLAUDE_SYNC.md for latest decisions
```

### 📊 Context Alignment Protocol

**Phase 1: Status Sync** (Every session start)
1. Read CLAUDE_SYNC.md for latest decisions
2. Check git log for recent commits from other instances
3. Review modified files for architectural changes
4. Update your working context

**Phase 2: Decision Communication** (Before major changes)
1. Log decision in CLAUDE_SYNC.md
2. Commit with clear [CLAUDE-X] prefix
3. Push to share with other instances
4. Tag urgent decisions with 🚨 URGENT prefix

**Phase 3: Implementation Coordination** (During development)
1. Update progress in CLAUDE_SYNC.md
2. Note any discovered dependencies
3. Flag required actions for other instances
4. Commit frequently with descriptive messages

## Current System Decisions Log

### [DEC-001] 2025-06-23 Production-Ready System Architecture
**Decided by**: Claude-Instance-2
**Impact**: High
**Files Affected**: all core files
**Description**: System achieved production readiness with 15 tools, 92.9% success rate
**Implementation**: 
- Expanded from 7 → 15 tools (215% increase)
- Modern `create_tool_calling_agent` architecture
- Multi-language support (English, Spanish, French)
- Comprehensive testing framework completed
**Next Actions**: 
- Claude-Instance-1: Review production deployment strategy
- Focus on optimization opportunities identified
- Maintain system stability while adding features

### [DEC-002] 2025-06-23 Tool Categories Structure
**Decided by**: Claude-Instance-2
**Impact**: Medium
**Files Affected**: tools.py, prompts.py
**Description**: Established 3-tier tool structure
**Implementation**:
- CORE SERVICES (7 tools): Basic guest operations
- HIGH-IMPACT SERVICES (5 tools): Revenue-generating services  
- LUXURY SERVICES (3 tools): Premium experiences
**Next Actions**:
- Claude-Instance-1: Align API endpoints with tool categories
- Consider tier-based pricing/access controls

### [DEC-003] 2025-06-23 Performance Benchmarks Established
**Decided by**: Claude-Instance-2
**Impact**: High
**Files Affected**: evaluation files
**Description**: Set production quality standards
**Implementation**:
- 100% tool recall requirement
- 90%+ guest journey success rate
- Multi-language capability mandatory
**Next Actions**:
- Claude-Instance-1: Implement monitoring for these metrics
- Set up alerts for performance degradation

## Instance Coordination Status

### Claude-Instance-1 (Backend/API Focus)
**Current Context**: System is production-ready, focus on deployment optimization
**Primary Responsibilities**:
- API performance and scalability  
- Production deployment preparation
- Monitoring and analytics implementation
- Frontend optimization

### Claude-Instance-2 (AI/Tools Focus)
**Current Context**: 15-tool system complete, evaluation framework established
**Primary Responsibilities**:
- Tool performance optimization
- Spanish language gap resolution
- Advanced personalization features
- Guest experience enhancement

## Urgent Communication Flags

### 🚨 CURRENT URGENT ITEMS
- **Performance Monitoring**: Need API-level metrics matching evaluation benchmarks
- **Spanish Language Gaps**: meal_delivery and local_recommendations need attention
- **Production Deployment**: System ready, need deployment strategy coordination

### ⚠️ WATCH ITEMS
- Guest profile retrieval occasional issues
- Personalization improvement opportunities
- Multi-property support planning

## Sync Schedule

**Daily Sync**: Start of each session
**Major Sync**: Before architectural changes
**Emergency Sync**: When 🚨 urgent flags are raised

## Communication Protocol

1. **Before Starting Work**: Read this file completely
2. **During Work**: Update decisions in real-time
3. **After Major Changes**: Commit and push immediately
4. **End of Session**: Log progress and next steps

---
**Last Sync**: 2025-06-23 (Claude-Instance-1 initial setup)
**Next Required Sync**: Before any production deployment changes
**System Status**: ✅ Production Ready - Coordination Required