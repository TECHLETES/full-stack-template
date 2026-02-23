---
description: Create, review, and test database migrations for backend schema changes. Handles model changes, relationships, and data transformations.
name: Database Migration Helper
argument-hint: "Model name and change description (e.g., 'Project model, add priority field')"
agent: agent
[vscode/askQuestions, execute, read, agent/askQuestions, edit, search, todo, ms-ossdata.vscode-pgsql/pgsql_listServers, ms-ossdata.vscode-pgsql/pgsql_connect, ms-ossdata.vscode-pgsql/pgsql_disconnect, ms-ossdata.vscode-pgsql/pgsql_open_script, ms-ossdata.vscode-pgsql/pgsql_visualizeSchema, ms-ossdata.vscode-pgsql/pgsql_query, ms-ossdata.vscode-pgsql/pgsql_modifyDatabase, ms-ossdata.vscode-pgsql/database, ms-ossdata.vscode-pgsql/pgsql_listDatabases, ms-ossdata.vscode-pgsql/pgsql_describeCsv, ms-ossdata.vscode-pgsql/pgsql_bulkLoadCsv, ms-ossdata.vscode-pgsql/pgsql_getDashboardContext, ms-ossdata.vscode-pgsql/pgsql_getMetricData, ms-ossdata.vscode-pgsql/pgsql_migration_oracle_app, ms-ossdata.vscode-pgsql/pgsql_migration_show_report]
---

# Database Migration Helper

Help with creating, reviewing, and testing Alembic migrations for schema changes.

## What This Helps With

- ✅ **Generate migrations** from model changes
- ✅ **Review** auto-generated migrations for safety
- ✅ **Test** apply/rollback workflows
- ✅ **Handle** data transformations and custom migrations
- ✅ **Validate** migration against existing models
- ✅ **Track** dependencies between migrations

## Input Parameters

Provide these details for the best results:

1. **Model/Table**: Which model is changing? (e.g., `Project`, `Item`, `User`)
2. **Change Type**: What's the change? (e.g., "add column", "modify field", "add relationship")
3. **Specific Changes**: Details of what's changing (e.g., "add `priority: int` (1-10), add `status: ProjectStatus` enum")
4. **Current State**: Original field definitions (if clarification needed)
5. **New State**: New field definitions from your model

## Common Migration Scenarios

### Scenario 1: Add a New Column

**Changes in `backend/models.py`:**
```python
class Project(ProjectBase, table=True):
    # ...existing fields...
    priority: int = Field(default=1, ge=1, le=10)  # NEW FIELD
```

**Steps to execute:**
```bash
cd backend
# Generate migration
alembic revision --autogenerate -m "add priority field to project"

# Review: alembic/versions/xxxx_add_priority_field_to_project.py
# Should contain: op.add_column('project', sa.Column('priority', sa.Integer(), nullable=False, server_default='1'))

# Test it
alembic upgrade head        # Apply
alembic downgrade -1        # Rollback (should remove column)
alembic upgrade head        # Re-apply
```

### Scenario 2: Add a Relationship

**Changes in `backend/models.py`:**
```python
class Project(ProjectBase, table=True):
    # ...existing fields...
    owner_id: uuid.UUID = Field(foreign_key="user.id", ondelete="CASCADE")  # NEW FK
    owner: User | None = Relationship(back_populates="projects")  # NEW RELATIONSHIP

class User(UserBase, table=True):
    # ...existing fields...
    projects: list["Project"] = Relationship(back_populates="owner", cascade_delete=True)  # NEW
```

**Steps:**
```bash
cd backend
alembic revision --autogenerate -m "add user-project relationship"
# Review the migration - should add FK constraint and index
alembic upgrade head
alembic downgrade -1
alembic upgrade head
```

### Scenario 3: Modify a Column (Nullable → Not Null)

**Before:**
```python
description: str | None = Field(default=None)  # Optional
```

**After:**
```python
description: str = Field(min_length=1)  # Required
```

**Manual migration (auto-generated may not be complete):**
```python
# alembic/versions/xxxx_make_project_description_required.py
def upgrade():
    # Step 1: Populate existing NULLs with default value
    op.execute("UPDATE project SET description = 'No description' WHERE description IS NULL")
    
    # Step 2: Add constraint
    op.alter_column('project', 'description', existing_type=sa.String(), nullable=False)

def downgrade():
    op.alter_column('project', 'description', existing_type=sa.String(), nullable=True)
```

**Test:**
```bash
alembic upgrade head        # Apply
# Verify: SELECT * FROM project WHERE description IS NULL;  (should be empty)
alembic downgrade -1        # Rollback
alembic upgrade head        # Re-apply
```

### Scenario 4: Add an Enum Type

**Before:**
```python
status: str  # Just string
```

**After:**
```python
from enum import Enum
class ProjectStatus(str, Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"

# In model:
status: ProjectStatus = ProjectStatus.ACTIVE
```

**Manual migration (enums need explicit DDL):**
```python
def upgrade():
    # Create enum type (PostgreSQL specific)
    op.execute("CREATE TYPE projectstatus AS ENUM ('active', 'archived')")
    
    # Add column with enum type
    op.add_column('project', sa.Column('status', sa.String(), server_default='active'))

def downgrade():
    op.drop_column('project', 'status')
    op.execute("DROP TYPE projectstatus")
```

### Scenario 5: Data Transformation

**Before:** `full_name` field stores "John Doe"
**After:** Split into `first_name` and `last_name`

**Steps:**
```python
def upgrade():
    # Step 1: Add new columns
    op.add_column('user', sa.Column('first_name', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('last_name', sa.String(length=255), nullable=True))
    
    # Step 2: Migrate data
    op.execute("""
        UPDATE "user"
        SET 
            first_name = SUBSTRING(full_name FROM 1 FOR POSITION(' ' IN full_name) - 1),
            last_name = SUBSTRING(full_name FROM POSITION(' ' IN full_name) + 1)
        WHERE full_name IS NOT NULL
    """)
    
    # Step 3: Make new columns required
    op.alter_column('user', 'first_name', existing_type=sa.String(), nullable=False)
    op.alter_column('user', 'last_name', existing_type=sa.String(), nullable=False)
    
    # Step 4: Drop old column
    op.drop_column('user', 'full_name')

def downgrade():
    op.add_column('user', sa.Column('full_name', sa.String(length=255), nullable=True))
    op.execute("""
        UPDATE "user"
        SET full_name = CONCAT(first_name, ' ', last_name)
    """)
    op.drop_column('user', 'first_name')
    op.drop_column('user', 'last_name')
```

**Test data transformation:**
```bash
# Before applying, check count:
psql -d app -c "SELECT COUNT(*) FROM \"user\";"

# Apply migration
alembic upgrade head

# Verify data integrity
psql -d app -c "SELECT id, first_name, last_name FROM \"user\" LIMIT 5;"

# Should have data in both fields, not NULL
psql -d app -c "SELECT COUNT(*) FROM \"user\" WHERE first_name IS NULL;"  # Should be 0
```

## Workflow: Create → Review → Test

### Step 1: Generate

After editing `backend/models.py`:

```bash
cd backend
alembic revision --autogenerate -m "descriptive message"
```

**Message format:** `<verb> <noun>` (lowercase, no period)
- ✅ "add priority field to project"
- ✅ "make description required on item"
- ✅ "create user-project relationship"
- ❌ "update models" (too vague)

### Step 2: Review

Open generated migration file: `backend/alembic/versions/xxxx_<message>.py`

Check for:
- ✅ Correct table name (lowercase table names)
- ✅ Correct column types (`sa.Integer()`, `sa.String()`, etc.)
- ✅ Proper constraints (`nullable=False`, `unique=True`)
- ✅ Foreign keys with `ondelete="CASCADE"`
- ✅ Server defaults where appropriate
- ❌ Missing down() function (always provide rollback)
- ❌ Data loss without migration path
- ❌ Unsafe assumptions about existing data

**If auto-generated migration looks wrong**, manually fix it (see Scenario 3-5 examples above).

### Step 3: Test Locally

```bash
cd backend

# Apply to current database
alembic upgrade head
# Should succeed without errors

# Verify schema change
psql -d app -c "\d project"  # Check new columns exist

# Rollback
alembic downgrade -1
# Should succeed, remove the change

# Verify it's gone
psql -d app -c "\d project"  # New columns should be gone

# Re-apply (to be ready for commit)
alembic upgrade head
```

### Step 4: Verify Models Match

```bash
cd backend

# After migration applied, verify models match DB:
alembic current       # Should show applied migration
alembic history -v    # Should show full history

# Type check
mypy

# No import errors
cd backend && uv sync
```

## Interactive Migration Creation

When asking for migration help, provide:

**Scenario:** "I need to add a new field `tags` (list of strings) to the Item model"

**What I'll help with:**
1. Suggest the SQLModel field definition
2. Show the YAML frontmatter to include
3. Generate the migration command
4. Review the auto-generated migration
5. Provide test steps
6. Troubleshoot if it fails

## Pre-Migration Checklist

Before running a migration in production:

- [ ] New field has `server_default` if `nullable=False` (prevents NULL constraint violation)
- [ ] Foreign keys include `ondelete` clause (CASCADE, SET NULL, RESTRICT)
- [ ] Cascading deletes tested (`delete parent → children deleted`)
- [ ] Data transformation script verified on backup
- [ ] Migration tested locally (upgrade + downgrade)
- [ ] Model file updated to match migration
- [ ] Lint passes: `./scripts/lint.sh`
- [ ] Tests pass: `./scripts/test.sh`
- [ ] No uncommitted changes in alembic/versions/

## Common Issues & Fixes

| Issue | Cause | Fix |
|-------|-------|-----|
| **Migration not generated** | Model doesn't have `table=True` | Add `table=True` to model class |
| **"Target database is not up to date"** | Migration applied manually, state mismatch | Run `alembic stamp <revision>` |
| **NULL constraint violation** | Adding NOT NULL field without default | Add `server_default` or populate before constraint |
| **Foreign key error** | Child records exist, can't set constraint | Handle existing data or use `ondelete` clause |
| **Alembic can't auto-detect change** | Complex structural change | Write migration manually with `op.execute()` |
| **Schema changes don't apply** | Alembic stuck on earlier version | Check `alembic_version` table, may need `downgrade` |
| **Git conflict in versions** | Two migrations with same timestamp | Rename one: `xxxx_... → xxxx_a_...` |

## References

- **Backend Instructions**: [../instructions/backend.instructions.md#database-migrations-alembic](../instructions/backend.instructions.md#database-migrations-alembic)
- **Scaffold Skill**: [./skills/scaffold-api-endpoint/SKILL.md](./skills/scaffold-api-endpoint/SKILL.md) — step 3 covers migrations
- **Alembic Docs**: https://alembic.sqlalchemy.org/
- **SQLAlchemy Column Types**: https://docs.sqlalchemy.org/en/20/core/types.html
- **PostgreSQL Docs**: https://www.postgresql.org/docs/

## Quick Reference: Alembic Commands

```bash
# Generate migration from model changes
alembic revision --autogenerate -m "descriptive message"

# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade +1

# Rollback one migration
alembic downgrade -1

# See history
alembic history -v

# See current head
alembic current

# Downgrade to specific revision
alembic downgrade 1975ea83b712
```

## Next: Ask for Specific Help

Describe your schema change and I'll provide:
1. SQLModel field changes (if needed)
2. Migration generation command
3. Review of auto-generated migration
4. Test procedure
5. Troubleshooting if needed

Or paste a specific error/migration file for review.
