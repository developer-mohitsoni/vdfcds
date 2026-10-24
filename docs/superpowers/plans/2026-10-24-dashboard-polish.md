# WindSight UK Dashboard Polish Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Resolve every priority issue in the saved Impeccable critique while preserving the existing WindSight UK visual identity and product scope.

**Architecture:** Keep the current React Query data flow and split responsibility across the existing dashboard components. App owns range/focus state, DailyTable owns its explicit focus action, EvolutionPanel derives compact day/hour navigation from available points, and ForecastChart exposes one concise accessible summary.

**Tech Stack:** React 19, TypeScript, TanStack Query, Recharts, Vitest, Testing Library, CSS.

---

### Task 1: Date-range and focused-day clarity

**Files:**
- Modify: `frontend/src/Dashboard.test.tsx`
- Modify: `frontend/src/App.tsx`
- Modify: `frontend/src/components/Layout.tsx`

- [ ] Add tests proving an invalid draft range explains the problem and focusing a day exposes a “Back to January” action.
- [ ] Run `npm test -- Dashboard.test.tsx` from `frontend/`; confirm both new assertions fail for the missing UI.
- [ ] Add an inline range error linked with `aria-describedby`, focused-range status text, and a reset action that restores `2026-01-01` through `2026-01-31`.
- [ ] Re-run `npm test -- Dashboard.test.tsx`; confirm the tests pass.

### Task 2: Scalable delivery-hour navigation and recovery

**Files:**
- Modify: `frontend/src/Dashboard.test.tsx`
- Modify: `frontend/src/components/EvolutionPanel.tsx`

- [ ] Add tests proving day/hour selection changes the evolution request, previous/next navigation works, and a failed evolution request exposes a retry button.
- [ ] Run the targeted tests and confirm failure because the split selectors, navigation, and retry action do not exist.
- [ ] Derive unique day options and per-day hour options from `points`; add labelled day/hour selectors and 44px previous/next buttons; use Query `refetch()` for retry.
- [ ] Add `role="status"` to loading and `role="alert"` to the error recovery block.
- [ ] Re-run the targeted tests and confirm they pass.

### Task 3: Accessible chart summary and explicit daily action

**Files:**
- Modify: `frontend/src/Dashboard.test.tsx`
- Modify: `frontend/src/components/ForecastChart.tsx`
- Modify: `frontend/src/components/DailyTable.tsx`

- [ ] Add tests proving the chart exposes one concise summary instead of one list item per point and the daily control has an explicit “Focus day” name.
- [ ] Run the tests and confirm expected failures against the current hidden list and arrow-only control.
- [ ] Replace the hidden list with a single descriptive summary and rename the row action to visible “Focus day” copy.
- [ ] Re-run the tests and confirm they pass.

### Task 4: Whole-path visual polish

**Files:**
- Modify: `frontend/src/components/Layout.tsx`
- Modify: `frontend/src/dashboard.css`
- Modify: `frontend/src/index.css`

- [ ] Add local KPI definitions and consistent GMT copy.
- [ ] Tighten hero scale/spacing; raise muted contrast and type floors; add focus rings, 44px targets, browser-surface styling, and tabular numerals.
- [ ] Keep every daily column on mobile using horizontal scroll and a sticky first column.
- [ ] Scope reduced-motion rules to reveal/shimmer effects and delete obsolete starter-screen CSS.
- [ ] Run `npm test`, `npm run lint`, `npm run typecheck`, and `npm run build`; all must exit 0.

### Task 5: Render verification and Impeccable closure

**Files:**
- Modify only if browser verification reveals a concrete defect in the files above.

- [ ] Run the app with production-like frontend/backend services and inspect wide, intermediate, and phone layouts.
- [ ] Verify mouse, keyboard, focus, date validation, focused-day reset, day/hour navigation, loading/error recovery, no horizontal page overflow, and no console errors.
- [ ] Run the required manual detector exactly once over the changed frontend targets and fix any material findings without re-running the detector.
- [ ] Review `git diff` for accidental churn and rerun all frontend verification commands after any correction.
- [ ] Close `2026-10-24T12-24-26Z__frontend-src-app-tsx.md` only after every adopted priority issue is cleared.
- [ ] Commit the verified milestone as `feat: polish dashboard usability and accessibility`.

