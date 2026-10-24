# WindSight UK Energy Intelligence Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current visual world with an evaluator-first UK wind energy intelligence dashboard while preserving every analytical behavior and API contract.

**Architecture:** Retain the current React Query orchestration and component boundaries. Reshape semantic markup in the existing layout/chart/table/evolution components, introduce project-specific overview and navigation structure, and replace the CSS token/composition system. Use self-hosted IBM Plex Sans Variable through the frontend package.

**Tech Stack:** React 19, TypeScript, TanStack Query, Recharts, CSS, Vitest, Testing Library, `@fontsource-variable/ibm-plex-sans`.

---

### Task 1: Lock product and design authority

**Files:**
- Create: `PRODUCT.md`
- Create: `docs/superpowers/specs/2026-10-24-energy-intelligence-redesign.md`
- Create: `docs/superpowers/plans/2026-10-24-energy-intelligence-redesign.md`

- [ ] Record confirmed audience, mechanism, evidence, constraints, and brand commitments in `PRODUCT.md`.
- [ ] Record the North Sea Forecast Briefing direction contract and implementation sequence.
- [ ] Commit the product/design milestone before application edits.

### Task 2: Add evaluator-first structure with TDD

**Files:**
- Modify: `frontend/src/App.test.tsx`
- Modify: `frontend/src/Dashboard.test.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/Layout.tsx`

- [ ] Add failing tests for section navigation, the January review heading, the D-1 09:50 GMT no-hindsight rule, and direct links between overview and evidence sections.
- [ ] Run `npm test -- App.test.tsx Dashboard.test.tsx`; confirm failures are caused by missing structure.
- [ ] Add semantic section IDs, evaluator-first overview copy, navigation anchors, evidence status, and restructured KPI hierarchy.
- [ ] Re-run the targeted tests and confirm they pass.

### Task 3: Make charts and evidence read as one product

**Files:**
- Modify: `frontend/src/components/ForecastChart.tsx`
- Modify: `frontend/src/components/DailyTable.tsx`
- Modify: `frontend/src/components/EvolutionPanel.tsx`
- Modify: `frontend/src/lib/format.ts` only if a shared display formatter is required.

- [ ] Preserve all controls and queries while revising headings, annotations, chart chrome, table hierarchy, and selected-revision evidence.
- [ ] Keep Forecast, Actual, Error, Published time, Cutoff, and eligibility semantics visible and accessible.
- [ ] Run the targeted dashboard tests and fix only behavior regressions.

### Task 4: Replace the visual system

**Files:**
- Modify: `frontend/package.json`
- Modify: `pnpm-lock.yaml`
- Modify: `frontend/src/main.tsx`
- Replace: `frontend/src/dashboard.css`
- Modify: `frontend/src/index.css`

- [ ] Add and import self-hosted IBM Plex Sans Variable.
- [ ] Implement North Sea navy, fog, wind teal, ink, and cutoff amber tokens.
- [ ] Build the sticky product shell, asymmetric overview, metric hierarchy, evidence panels, cutoff ribbon, technical methodology, and authored browser states.
- [ ] Implement wide, intermediate, and 390px responsive compositions without hiding data.
- [ ] Preserve accessible focus, 44px touch targets, reduced motion, contrast, and standard control behavior.

### Task 5: Verify and review the complete surface

**Files:**
- Create/update: `.impeccable/review/desktop.png`
- Create/update: `.impeccable/review/mobile.png`
- Create after approval: `DESIGN.md`
- Create after approval: `.impeccable/design.json`

- [ ] Run frontend tests, lint, typecheck, production build, and Docker Compose smoke test.
- [ ] Capture and inspect full-page 1440px and 390px renders; exercise filters, focus/reset, hour navigation, loading, error, empty, and responsive states.
- [ ] Run the Impeccable detector exactly once after the final changed UI is ready.
- [ ] Send the screenshots and direction contract to a fresh Impeccable finish reviewer; batch-fix its material findings and recapture once when requested.
- [ ] Document the accepted visual system in `DESIGN.md` and `.impeccable/design.json`.
- [ ] Review the final diff, rerun verification after the last edit, and create the redesign milestone commit.

