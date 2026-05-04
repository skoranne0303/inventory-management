---
description: Redesign a Vue 3 app's UI from top nav to vertical sidebar SaaS layout with polished professional styling
---

Transform this Vue 3 application from its current top navigation bar layout into a modern SaaS-style interface with a fixed vertical sidebar on the left, consistent spacing, and a polished professional look.

## Phase 1 — Audit Current Structure

Before making any changes, read and understand:
1. `client/src/App.vue` — identify the top nav markup, global CSS classes, and `<main>` layout
2. `client/src/main.js` — list all routes and their component imports
3. `client/src/components/` — identify which components live inside the nav bar (filter bars, profile menus, language switchers, etc.)
4. `client/src/views/` — skim each view to find any hardcoded nav-dependent layout assumptions

Summarize what you found before proceeding.

## Phase 2 — Design Tokens

Establish these CSS custom properties. They will be the single source of truth for the new design system. Add them to the `:root` block in `App.vue`'s `<style>`:

```css
:root {
  /* Sidebar */
  --sidebar-width: 240px;
  --sidebar-bg: #0f172a;
  --sidebar-border: #1e293b;
  --sidebar-text: #94a3b8;
  --sidebar-text-active: #f1f5f9;
  --sidebar-accent: #3b82f6;
  --sidebar-accent-bg: rgba(59, 130, 246, 0.12);
  --sidebar-hover-bg: rgba(255, 255, 255, 0.05);

  /* Content area */
  --content-bg: #f8fafc;
  --content-padding: 2rem;

  /* Surface */
  --surface-white: #ffffff;
  --surface-border: #e2e8f0;
  --surface-border-hover: #cbd5e1;
  --surface-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.06), 0 1px 2px -1px rgba(0, 0, 0, 0.06);
  --surface-shadow-md: 0 4px 12px 0 rgba(0, 0, 0, 0.08);

  /* Typography */
  --text-primary: #0f172a;
  --text-secondary: #475569;
  --text-muted: #94a3b8;
  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;

  /* Spacing scale (8px base) */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.25rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-10: 2.5rem;

  /* Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;

  /* Status colors (unchanged — keep existing badge/stat semantics) */
  --color-success: #059669;
  --color-success-bg: #d1fae5;
  --color-warning: #d97706;
  --color-warning-bg: #fef3c7;
  --color-danger: #dc2626;
  --color-danger-bg: #fee2e2;
  --color-info: #2563eb;
  --color-info-bg: #dbeafe;
}
```

## Phase 3 — New App Shell Layout

**Delegate this step entirely to the `vue-expert` subagent.** Brief it with the full context below.

Rewrite `client/src/App.vue` with this layout architecture:

### Template structure

```
<div class="app-shell">
  <aside class="sidebar">
    <div class="sidebar-brand">      ← logo + app name
    <nav class="sidebar-nav">        ← all router-links as nav items
    <div class="sidebar-footer">     ← language switcher + profile menu
  </aside>
  <div class="app-body">
    <div class="topbar">             ← filter bar only (no nav links)
    <main class="main-content">
      <router-view />
    </main>
  </div>
</div>
```

### Sidebar nav item markup pattern

Replace every `<router-link>` with this pattern:
```vue
<router-link to="/path" class="nav-item" :class="{ active: $route.path === '/path' }">
  <span class="nav-icon"><!-- SVG icon --></span>
  <span class="nav-label">Link Label</span>
</router-link>
```

Use inline SVG icons appropriate to each section (overview/dashboard → grid, inventory → box/cube, orders → clipboard, finance/spending → chart-bar, demand → trending-up, reports → document, restocking → refresh/arrow-path). Keep icons at 18×18px, `stroke-width="1.75"`, `fill="none"`, using Heroicons-style paths.

### Sidebar CSS

```css
.app-shell {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: var(--sidebar-width);
  min-height: 100vh;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--sidebar-border);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  z-index: 200;
}

.sidebar-brand {
  padding: var(--space-6) var(--space-5);
  border-bottom: 1px solid var(--sidebar-border);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.sidebar-brand .brand-icon {
  width: 32px;
  height: 32px;
  background: var(--sidebar-accent);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
}

.sidebar-brand .brand-name {
  font-size: 0.938rem;
  font-weight: 700;
  color: var(--sidebar-text-active);
  letter-spacing: -0.01em;
}

.sidebar-brand .brand-subtitle {
  font-size: 0.688rem;
  color: var(--sidebar-text);
  margin-top: 1px;
}

.sidebar-nav {
  flex: 1;
  padding: var(--space-4) var(--space-3);
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.nav-section-label {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--sidebar-text);
  opacity: 0.5;
  padding: var(--space-4) var(--space-3) var(--space-2);
}

.nav-item {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-2) var(--space-3);
  border-radius: var(--radius-md);
  color: var(--sidebar-text);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: background 0.15s ease, color 0.15s ease;
}

.nav-item:hover {
  background: var(--sidebar-hover-bg);
  color: var(--sidebar-text-active);
}

.nav-item.active {
  background: var(--sidebar-accent-bg);
  color: var(--sidebar-accent);
}

.nav-item.active .nav-icon svg {
  stroke: var(--sidebar-accent);
}

.nav-icon {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.nav-icon svg {
  stroke: currentColor;
}

.sidebar-footer {
  padding: var(--space-4) var(--space-3);
  border-top: 1px solid var(--sidebar-border);
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.app-body {
  margin-left: var(--sidebar-width);
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.topbar {
  background: var(--surface-white);
  border-bottom: 1px solid var(--surface-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.main-content {
  flex: 1;
  padding: var(--content-padding);
  background: var(--content-bg);
  max-width: 1360px;
  width: 100%;
}
```

### Preserving existing components

- Move `<FilterBar />` into `.topbar` (keep its props/events intact)
- Move `<LanguageSwitcher />` into `.sidebar-footer`
- Move `<ProfileMenu />` into `.sidebar-footer`
- Keep all existing `<ProfileDetailsModal />` and `<TasksModal />` overlay components in the root `<div>` — they use fixed positioning and are unaffected by layout changes
- Keep all existing `setup()` logic (tasks, auth, i18n) unchanged — only touch the template and styles

## Phase 4 — Update Global Styles

Update the existing global CSS in `App.vue`'s `<style>` (not scoped) to use the new design tokens:

**Cards** — update `.card` to use the new shadow and radius variables:
```css
.card {
  background: var(--surface-white);
  border-radius: var(--radius-lg);
  padding: var(--space-6);
  border: 1px solid var(--surface-border);
  box-shadow: var(--surface-shadow);
  margin-bottom: var(--space-5);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
.card:hover {
  border-color: var(--surface-border-hover);
  box-shadow: var(--surface-shadow-md);
}
```

**Stat cards** — keep existing color variants but update base:
```css
.stat-card {
  background: var(--surface-white);
  padding: var(--space-5);
  border-radius: var(--radius-lg);
  border: 1px solid var(--surface-border);
  box-shadow: var(--surface-shadow);
  transition: box-shadow 0.2s ease, border-color 0.2s ease;
}
```

**Page header** — tighten spacing:
```css
.page-header {
  margin-bottom: var(--space-6);
}
.page-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  letter-spacing: -0.02em;
  margin-bottom: var(--space-1);
}
.page-header p {
  color: var(--text-secondary);
  font-size: 0.875rem;
}
```

**Table** — tighten and refine:
```css
thead {
  background: #f8fafc;
  border-top: none;
  border-bottom: 2px solid var(--surface-border);
}
th {
  padding: var(--space-3) var(--space-4);
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
td {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid #f1f5f9;
  color: var(--text-primary);
  font-size: 0.875rem;
}
tbody tr:hover {
  background: #f8fafc;
}
```

**Remove** the old `.top-nav`, `.nav-container`, `.nav-tabs`, `.subtitle` rules — they are fully replaced by the sidebar CSS.

## Phase 5 — Polish FilterBar Component

**Delegate to `vue-expert`.** Update `client/src/components/FilterBar.vue` so it fits inside the new `.topbar` container:

- Change the wrapper to `display: flex; align-items: center; gap: 1rem; padding: 0.75rem 2rem; flex-wrap: wrap`
- Remove any outer margin or padding that assumed it was at the very top of the viewport
- Add a subtle label "Filters:" in `var(--text-muted)` before the filter controls if not already present

## Phase 6 — Verify

After all changes are complete:

1. Start the dev server: `cd client && npm run dev`
2. Use Playwright (`mcp__playwright__*`) to screenshot each route: `/`, `/inventory`, `/orders`, `/spending`, `/demand`, `/reports`, `/restocking`
3. Check that:
   - Sidebar is visible on all pages with correct active highlight
   - No horizontal overflow or layout breaks
   - Filter bar appears in topbar strip below the sidebar top
   - Cards, tables, and badges render with updated styles
   - All modals (profile, tasks) still open correctly
4. If any visual regressions are found, fix them before reporting done

## Important Constraints

- **Do NOT change any API calls, data loading logic, computed properties, or business logic** — only structural HTML/CSS changes
- **Do NOT rename or remove any existing CSS classes** that are used in child view components (`.badge`, `.card`, `.stat-card`, `.loading`, `.error`, `.table-container`, `.stats-grid`) — only update their style definitions
- Use the `vue-expert` subagent for all `.vue` file edits
- The old `.top-nav` CSS block must be completely replaced; leaving dead CSS will cause confusion
- All SVG icons must use `stroke="currentColor"` so they inherit the nav item's text color
