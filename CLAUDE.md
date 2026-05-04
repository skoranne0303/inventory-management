# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Factory Inventory Management System Demo - Full-stack application with Vue 3 frontend, Python FastAPI backend, and in-memory mock data (no database).

## Critical Tool Usage Rules

### Subagents
Use the Task tool with these specialized subagents for appropriate tasks:

- **vue-expert**: Use for Vue 3 frontend features, UI components, styling, and client-side functionality
  - **MANDATORY RULE: ANY time you need to create or significantly modify a .vue file, you MUST delegate to vue-expert**
- **code-reviewer**: Use after writing significant code to review quality and best practices
- **Explore**: Use for understanding codebase structure, searching for patterns, or answering questions about how components work
- **general-purpose**: Use for complex multi-step tasks or when other agents don't fit

### Skills
- **backend-api-test** skill: Use when writing or modifying tests in `tests/backend` directory with pytest and FastAPI TestClient

### MCP Tools
- **ALWAYS use GitHub MCP tools** (`mcp__github__*`) for ALL GitHub operations
  - Exception: Local branches only - use `git checkout -b` instead of `mcp__github__create_branch`
- **ALWAYS use Playwright MCP tools** (`mcp__playwright__*`) for browser testing
  - Test against: `http://localhost:3000` (frontend), `http://localhost:8001` (API)

## Stack
- **Frontend**: Vue 3 + Composition API + Vite (port 3000)
- **Backend**: Python FastAPI (port 8001), managed with `uv`
- **Data**: JSON files in `server/data/` loaded at startup via `server/mock_data.py` (in-memory, restart to reload)

## Commands

```bash
# One-command start (kills ports 3000/8001, starts both servers in background)
./scripts/start.sh
./scripts/stop.sh

# Backend (manual)
cd server && uv run python main.py        # http://localhost:8001 (docs at /docs)

# Frontend (manual)
cd client && npm install && npm run dev   # http://localhost:3000

# Backend tests (run from tests/ directory)
cd tests && uv run pytest -v                                        # all tests
uv run pytest backend/test_inventory.py -v                          # single file
uv run pytest backend/test_inventory.py::TestInventoryEndpoints::test_get_all_inventory -v  # single test
uv run pytest --cov=../server --cov-report=html                     # with coverage

# Frontend build
cd client && npm run build
```

## Architecture

**Filter System**: `FilterBar.vue` → `useFilters` composable → `api.js` query params → FastAPI `apply_filters()` → filtered JSON response. Four filters: Time Period, Warehouse, Category, Order Status. Inventory does not support month filtering (no time dimension).

**Data Flow**: All views follow: `useFilters` composable provides reactive filter state → `api.js` attaches filters as query params → FastAPI filters in-memory JSON → Pydantic-validated response → `ref()` for raw data, `computed()` for derived values.

**Composables**: Three shared composables in `client/src/composables/`: `useFilters` (centralized filter state), `useAuth`, `useI18n`.

**Adding a backend endpoint**: Define Pydantic response model → add route in `server/main.py` → filter using `apply_filters()` / `filter_by_month()` helpers → raise `HTTPException` for 404/400 → add tests in `tests/backend/`.

**Adding a frontend view**: Create `client/src/views/*.vue` via vue-expert → add route in `client/src/main.js` → add API method to `client/src/api.js` → use `useFilters` composable for filter state.

## API Endpoints
- `GET /api/inventory` - Filters: warehouse, category
- `GET /api/orders` - Filters: warehouse, category, status, month
- `GET /api/dashboard/summary` - All filters
- `GET /api/demand`, `/api/backlog` - No filters
- `GET /api/spending/*` - Summary, monthly, categories, transactions

## Key Business Logic
- **Low stock**: `quantity_on_hand ≤ reorder_point`
- **Pending orders**: status in (Processing, Backordered)
- **Inventory value**: `quantity_on_hand × unit_cost`
- **Revenue goals**: $800K/month single warehouse, $9.6M YTD all months
- **Mock data date range**: 2025-01 through 2025-12; warehouses: San Francisco, London, Tokyo

## Code Style
- Always document non-obvious logic changes with comments

## Common Issues
1. Use unique keys in v-for (not `index`) — use `sku`, `month`, item ID, etc.
2. Validate dates before `.getMonth()` calls
3. Sync Pydantic models (`server/main.py`) when changing JSON data structure in `server/data/`
4. Filter comparisons use lowercase: always `.lower()` on both sides

## Design System
- Colors: Slate/gray (#0f172a, #64748b, #e2e8f0); status: green/blue/yellow/red
- Charts: Custom SVG; layouts: CSS Grid and Flexbox
- No emojis in UI
- Global styles in `client/src/App.vue`; component styles are scoped
