# Frontend Coding & UI Guidelines

This document details the React/TypeScript frontend coding patterns, authentication state management, MUI layout structures, and build verification procedures.

---

## 1. API Calls — Always Use `fetchWithAuth`

Never use raw `fetch` or `axios` for authenticated endpoints. Use `fetchWithAuth` from `src/api/clients/fetchClient.ts`:

```typescript
// ✅ Correct
const response = await fetchWithAuth(`${emsBase}/assets`);

// ❌ Wrong
const response = await fetch(`${emsBase}/assets`, {
  headers: { Authorization: `Bearer ${token}` },
});
```

- `fetchWithAuth` automatically attaches the Bearer token, handles silent token refresh on HTTP `401` unauthorized responses, and retries the original request.

---

## 2. Authentication Pattern

`AuthContext` (`src/context/AuthContext.tsx`) is the single source of truth for React authentication state. We avoid storing any active session tokens (like the access token or refresh token) in persistent browser storage (`localStorage` or `sessionStorage`). Instead, the `access_token` is stored strictly in application memory (using `tokenStore.ts`), and the `refresh_token` is stored securely in an `HttpOnly` cookie.

### App Mount Hook

1. Always attempt a silent refresh by calling `/refresh` with credentials included (the browser automatically transmits the `refresh_token` cookie).
2. On success: store the new access token in the in-memory `tokenStore`, and update the React `AuthContext` state.
3. On authentication failure (e.g. cookie expired, missing, or revoked): trigger `logout()` immediately to return to the Lock Screen.
4. On network connectivity failure (e.g. offline): log the connection error but do not log the user out.

### Cross-Layer Auth Sync

Use a custom window event bus to avoid circular or direct imports between the network/fetch client layer and React context:

- `window.dispatchEvent(new Event('auth-logout'))` → triggers `logout()` in `AuthContext`.
- `window.dispatchEvent(new CustomEvent('auth-refresh', { detail: { access_token } }))` → syncs new token into `AuthContext` state.

---

## 3. UI Component & Layout Standards

- **Destructive Actions Confirmations:** Never use browser-native `window.confirm` or `window.alert`. Always implement a custom in-app MUI `<Dialog>`.

### Custom Confirm Dialog Pattern

```tsx
const [confirmDialog, setConfirmDialog] = useState<{
  open: boolean;
  title: string;
  message: string;
  onConfirm: () => void;
}>({ open: false, title: '', message: '', onConfirm: () => {} });

const openConfirm = (title: string, message: string, onConfirm: () => void) => {
  setConfirmDialog({ open: true, title, message, onConfirm });
};

const closeConfirm = () => {
  setConfirmDialog((prev) => ({ ...prev, open: false }));
};
```

Render the dialog at the end of the component JSX (outside any primary dialog if nesting is needed).

- **DialogContent Padding and Layout:** Always wrap input fields in a `<Box>` to prevent MUI floating label clipping and layout alignment bugs:

```tsx
// ✅ Correct
<DialogContent>
  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5, pt: 1.5 }}>
    <TextField ... />
  </Box>
</DialogContent>

// ❌ Wrong (applies flex directly on DialogContent, which clips labels)
<DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
  <TextField ... />
</DialogContent>
```

- **Required Fields:** MUI `<TextField required>` auto-appends the asterisk. Do not manually append `*` to the `label` prop string:

```tsx
// ✅ Correct
<TextField required label="Asset Name" />

// ❌ Wrong
<TextField required label="Asset Name *" />
```

---

## 4. Build Verification

TypeScript compilation must run with **zero errors** before staging any UI file. No `any` suppressions are allowed without inline comment justification. Run the production build locally:

```bash
npm run build:web
```
