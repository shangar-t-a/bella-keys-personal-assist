# Frontend & UI Guidelines

Established patterns for the React SPA. All new UI tabs, components, and pages **must** follow these standards.

For a full working implementation of these patterns, refer to the canonical reference files:

* **Tab/Card Layout, Tables, and Forms:** [AssetsTab.tsx](../../keys-personal-assist-ui/src/components/wealth/AssetsTab.tsx)
* **Page Wrapper & Navigation:** [WealthPage.tsx](../../keys-personal-assist-ui/src/pages/WealthPage.tsx)

---

## 1. Design System & Typography

| Element | Specification |
| --- | --- |
| **Primary Font** | `"Space Grotesk", sans-serif` (for numeric metrics, titles, page headers) |
| **Body Font** | `DM Sans` (MUI default) for descriptions, body text, table cells |
| **Page Title** | `variant="h5"`, `fontWeight: 700`, line height `1.2` |
| **Section Labels** | `variant="caption"`, uppercase, letter spacing `0.8`, font size `0.68rem` |
| **Metric Numbers** | `variant="h5"`, font size `1.3rem`, `fontWeight: 700` |
| **Table Headers** | Font size `0.78rem`, `fontWeight: 700`, uppercase, letter spacing `0.5` |
| **Table Body Text** | `variant="body2"`, `fontWeight: 600` |
| **Sub-text/Caption** | `variant="caption"`, color `text.secondary` |

---

## 2. Spacing System

Use MUI's spacing scale (e.g. `sx={{ gap: 2 }}`). Avoid arbitrary hardcoded `px` values.

* **Page padding:** `py: 2.5, px: { xs: 2, md: 4 }`
* **Page header → tabs gap:** `mb: 1.5`
* **Tabs → content gap:** `mb: 2`
* **Section gap (flex column):** `gap: 2`
* **Table cell padding:** `py: 1` to `py: 1.25`

---

## 3. UI Layout Patterns

### Cards

Every page-level section lives inside an outlined Card:

```tsx
<Card variant="outlined" sx={{ borderRadius: 2, borderColor: 'divider', boxShadow: 'none' }}>
```

### Tab Layout

Every main page tab uses a 3-tier stacked structure:

1. **Toolbar Card:** Search input, category filter toggles, and primary action button (e.g. "Add Asset").
2. **Summary Card:** Exactly 3 metric blocks (Invested, Current Value, Returns/P&L) separated by vertical dividers.
3. **Table/Content Card:** Data presentation.

### Tables

* **Grouped Table Pattern:** Replace nested accordions with a single grouped table containing category-group headers.
* **Zebra Striping:** Use alternating transparent and shaded rows on table data.
* **Left Accent Border:** Category group headers must have a `borderLeft: '3px solid <category_color>'`.
* **Action Buttons:** Standard order from left to right: **History** (`HistoryIcon`, primary) → **Edit** (`EditIcon`, secondary) → **Delete** (`DeleteIcon`, error).

---

## 4. Theme & Color Standards

### Categorized Color Palette

For entity-specific cards, chips, or states, use the established palette:

| Category | Primary Color | Light Background (transparency) |
| --- | --- | --- |
| **Equity** | `#108cc6` | `rgba(16, 140, 198, 0.1)` |
| **Debt** | `#1e5067` | `rgba(30, 80, 103, 0.1)` |
| **Real Estate** | `#f59e0b` | `rgba(245, 158, 11, 0.1)` |
| **Commodities** | `#fbbf24` | `rgba(251, 191, 36, 0.1)` |
| **Cash & Bank** | `#10b981` | `rgba(16, 185, 129, 0.1)` |

### Dark Mode Adaptation

Avoid hardcoded background colors. Always use conditional theme functions:

```tsx
bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.3)' : '#f8fafc'
```

---

## 5. Coding & Formatting Standards

### Currency Formatting

* Use **`formatCompactRupees`** for summary cards and category group totals (e.g. `₹12.00L`, `₹1.50Cr`, `₹90,000.00`).
* Use **`formatCurrency`** for individual row items where full precision is required.

### Form Inputs & Dialogs

* **Layout clipping:** Wrap inputs inside `<DialogContent>` in a `<Box>` to prevent MUI floating label clipping.
* **Required fields:** Do not add manual asterisks to `label`. Let MUI `<TextField required>` handle it automatically.
* **Confirmations:** Always use a custom in-app `<Dialog>` (see `AssetsTab.tsx` for recipe). **Never use `window.confirm` or `window.alert`**.

---

## 6. Frontend Architecture & State

### API Client

* **Never use raw `fetch` or `axios`.** Always use `fetchWithAuth` from `src/api/clients/fetchClient.ts`.
* `fetchWithAuth` automatically handles Bearer token injection, silent token refreshes on `401`, and retries.

### Authentication State

* `AuthContext` (`src/context/AuthContext.tsx`) is the single source of truth for React auth state. `localStorage` is only the persistence layer.
* Syncing across layers is performed via the custom window event bus:
  * `window.dispatchEvent(new Event('auth-logout'))` triggers logout.
  * `window.dispatchEvent(new CustomEvent('auth-refresh', { detail: { access_token } }))` updates tokens.

### Verification

* **TypeScript compilation:** The React app must compile with **zero errors** before staging files. Suppressions using `any` must include an inline justification comment.
* Run UI build verification before staging:

  ```bash
  npm run build:web
  ```
