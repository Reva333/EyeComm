# GitHub Issue Backlog

This file contains project-specific GitHub issue drafts based on the current repository state, source code, and production build output.

## 1. Fix broken ESLint flat-config setup

Title: Fix ESLint config so Next.js rules load correctly

Labels: bug, tooling

Description:
The current ESLint flat config fails to resolve `next/core-web-vitals` during production builds. `npm run build` completes, but it reports an ESLint configuration error instead of running a clean lint pass.

Evidence:
- `npm run build` reports: `ESLint: Failed to load config "next/core-web-vitals" to extend from.`
- Current config uses `FlatCompat` in `eslint.config.mjs`.

Impact:
- Linting is not trustworthy.
- CI can pass with hidden lint regressions.
- Contributors do not have a reliable local lint workflow.

Suggested fix:
- Update the flat-config setup to use a Next.js 15 compatible ESLint configuration.
- Verify whether `eslint-config-next` needs to be added explicitly.
- Ensure `npm run lint` and `npm run build` both run without config errors.

Acceptance criteria:
- `npm run lint` completes successfully.
- `npm run build` completes without any ESLint config error.
- Next.js core web vitals and TypeScript lint rules are still applied.

## 2. Prevent Paper Shaders from rendering on the server

Title: Stop shader components from initializing during server render

Labels: bug, frontend, performance

Description:
The landing page renders shader components in a way that triggers server-side warnings during static generation.

Evidence:
- `npm run build` logs: `Paper Shaders: can’t create a texture on the server`.
- Shader usage lives in `components/shader-background.tsx`.

Impact:
- Build output contains runtime warnings.
- Server rendering is doing work that should stay client-only.
- This can become a production stability or hydration issue if the shader package behavior changes.

Suggested fix:
- Gate shader rendering behind client-only mount state or dynamic import with SSR disabled.
- Confirm the landing page still renders correctly after hydration.

Acceptance criteria:
- `npm run build` no longer logs the shader server warning.
- The landing page visuals still work in the browser.
- No hydration warnings appear in the console.

## 3. Unify project branding across app metadata, package name, and docs

Title: Standardize project naming and metadata across the repository

Labels: documentation, cleanup

Description:
The repository currently mixes several product names and generated metadata values.

Evidence:
- `package.json` name is `my-v0-project`.
- `README.md` uses `EyeComm`.
- `README copy.md` uses `GazeType` and references `ai-gazetype` paths.
- `app/layout.tsx` title is `AI GazeType`.
- `app/keyboard/layout.tsx` still contains `generator: "v0.app"`.

Impact:
- The project identity is unclear.
- Package metadata and documentation look unfinished.
- GitHub, deployment, and release artifacts can present inconsistent branding.

Suggested fix:
- Decide on the canonical product name.
- Update package metadata, page metadata, README content, and setup instructions to match.
- Remove leftover generator and scaffold-specific naming.

Acceptance criteria:
- One project name is used consistently across source, package metadata, and docs.
- Setup instructions reference the correct repository name and directory.
- No scaffold-specific names remain.

## 4. Connect or remove the orphaned Python launcher API

Title: Audit `/api/start` and either wire it into the product or remove it

Labels: bug, backend, cleanup

Description:
The project includes an API route that spawns `scripts/gazeType.py`, but there is no visible client usage of this endpoint in the current app.

Evidence:
- Route exists at `app/api/start/route.ts`.
- No matching `/api/start` client call is present in the current app source.
- The route uses `spawn("python", [scriptPath])` with no process lifecycle management.

Impact:
- Dead code increases maintenance cost.
- If exposed, the route can create unmanaged Python processes.
- The current implementation is platform-dependent and difficult to deploy safely.

Suggested fix:
- Decide whether Python launching is still part of the product architecture.
- If yes, add an authenticated and observable execution flow with proper process handling.
- If no, remove the route and related documentation.

Acceptance criteria:
- The endpoint is either removed or actively used by the app.
- Any remaining process launch flow is documented and safe to run.
- Cross-platform behavior and deployment expectations are defined.

## 5. Replace hard navigation redirects with Next.js routing primitives

Title: Use Next.js router or Link instead of `window.location.href`

Labels: frontend, cleanup

Description:
Navigation to the keyboard page is currently handled through direct `window.location.href` assignments.

Evidence:
- `components/header.tsx` uses `window.location.href = "/keyboard"`.
- `components/hero-content.tsx` uses `window.location.href = "/keyboard"`.

Impact:
- Navigation forces full document reload behavior.
- Client-side transitions and prefetching are bypassed.
- The code is harder to test and less idiomatic for App Router.

Suggested fix:
- Replace imperative redirects with `Link` or `useRouter().push()`.
- Preserve the existing button behavior and loading state.

Acceptance criteria:
- Navigation to `/keyboard` uses App Router primitives.
- Keyboard page transitions without full page reload semantics.
- Existing UX remains unchanged or improves.

## 6. Add explicit fallback UI for unsupported speech and media APIs

Title: Handle unsupported browser APIs and permission failures in the keyboard app

Labels: bug, accessibility, frontend

Description:
The keyboard page assumes availability of webcam, speech synthesis, and speech recognition features, but it does not surface clear UI feedback when those APIs are unavailable or blocked.

Evidence:
- `app/keyboard/page.tsx` silently skips speech recognition setup if the API is unavailable.
- Webcam initialization logs errors to the console, but there is no user-facing error state.
- Speech synthesis is invoked without feature detection or cancellation handling.

Impact:
- Users can land on a broken interaction flow without understanding why.
- Accessibility is reduced on unsupported browsers and restricted devices.
- Debugging user reports becomes harder.

Suggested fix:
- Add support checks for `SpeechRecognition`, `speechSynthesis`, and camera permissions.
- Show clear status messages and recovery actions.
- Disable unavailable controls instead of leaving them active.

Acceptance criteria:
- Unsupported APIs produce visible, user-friendly messaging.
- Permission denial states are handled without silent failure.
- Voice and webcam buttons reflect actual availability.

## 7. Refactor the keyboard page into smaller typed modules

Title: Break up the monolithic keyboard page and remove loose `any` usage

Labels: tech-debt, frontend, typescript

Description:
The keyboard experience is implemented inside a single large client component that mixes gaze tracking, speech input, speech output, DOM polling, and rendering. It also relies on multiple `any`-typed refs and callbacks.

Evidence:
- `app/keyboard/page.tsx` contains several unrelated responsibilities in one component.
- `recognitionRef`, `faceMeshRef`, and multiple callback inputs use `any`.

Impact:
- The file is hard to test and reason about.
- Type safety is weak around critical browser API integrations.
- Future changes to gaze tracking or voice input will be risky.

Suggested fix:
- Extract gaze tracking, speech input, and hover-selection logic into dedicated hooks or modules.
- Introduce concrete TypeScript types for external APIs and refs.
- Reduce the page component to orchestration and rendering.

Acceptance criteria:
- `app/keyboard/page.tsx` is split into smaller units with clear responsibilities.
- The number of `any` usages is reduced substantially or eliminated.
- Behavior remains unchanged after refactor.

## 8. Audit unused dependencies and dead components

Title: Remove unused packages and components left from scaffolding

Labels: cleanup, dependencies

Description:
The repository includes a large dependency surface and at least one component that appears unused in the current app flow.

Evidence:
- `components/webcam-feed.tsx` exists but is not referenced in the current app source.
- `package.json` includes many UI and utility dependencies that do not appear tied to current routes.
- The package name and metadata suggest scaffold leftovers are still present.

Impact:
- Install time and dependency maintenance cost are higher than necessary.
- Security and upgrade surface area are larger.
- Contributors have a harder time identifying the actual runtime dependencies.

Suggested fix:
- Run an import audit for all dependencies and components.
- Remove unused packages, code paths, and assets.
- Rebuild after cleanup to confirm no regressions.

Acceptance criteria:
- Unused components and packages are removed.
- `npm install` and `npm run build` still succeed.
- The dependency list better reflects the actual product.

## 9. Add end-to-end coverage for core communication flows

Title: Add automated tests for text entry, voice controls, and keyboard interactions

Labels: testing, quality

Description:
The app currently has no visible automated coverage for its highest-risk user flows.

Evidence:
- No test files are present in the current workspace structure.
- Core interactions depend on browser APIs, timers, and DOM-driven selection logic.

Impact:
- Regressions in typing, speech, and gaze selection can slip into production.
- Refactors are costly because behavior is only validated manually.

Suggested fix:
- Add browser-level tests for basic text entry, clear/backspace behavior, and unsupported API states.
- Mock browser speech and media APIs where needed.
- Start with a small critical-path suite before expanding coverage.

Acceptance criteria:
- A test framework is configured for end-to-end or integration coverage.
- Core keyboard actions are covered by automated tests.
- Unsupported API and permission-denied flows are exercised in tests.