# UI Guidelines

> Established patterns from the **Wealth → Assets tab** redesign (branch `users/shangar/wealth-manager-assets`).
> All new tabs and pages **must** follow these patterns to maintain visual consistency.

---

## 1. Typography & Fonts

| Token | Value | Usage |
|---|---|---|
| Primary heading font | `"Space Grotesk", sans-serif` | Page titles, section labels, key numbers |
| Body font | DM Sans (MUI default) | General text, table cells, descriptions |
| Page title | `variant="h5"`, `fontWeight: 700` | Top-level page heading |
| Section labels | `variant="caption"`, `textTransform: 'uppercase'`, `letterSpacing: 0.8`, `fontSize: '0.68rem'` | Labels above metric numbers |
| Metric numbers | `variant="h5"`, `fontSize: '1.3rem'`, `fontWeight: 700` | Summary card values |
| Table header | `fontSize: '0.78rem'`, `fontWeight: 700`, `textTransform: 'uppercase'`, `letterSpacing: 0.5` | Column headers |
| Table body | `variant="body2"`, `fontWeight: 600` | Asset name |
| Sub-text | `variant="caption"`, `color="text.secondary"` | Notes, counts, subtitles |

```tsx
// Page title
<Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', lineHeight: 1.2 }}>
  Assets
</Typography>

// Metric number
<Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', color: 'primary.main', fontSize: '1.3rem' }}>
  {formatCompactRupees(value)}
</Typography>
```

---

## 2. Spacing System

Use MUI's spacing scale. Do not use arbitrary `px` values in `sx` props.

| Context | Token | Approx px |
|---|---|---|
| Page outer padding | `py: 2.5, px: { xs: 2, md: 4 }` | 20px / 32px |
| Page header → tabs gap | `mb: 1.5` | 12px |
| Tabs → content gap | `mb: 2` | 16px |
| Section gap (flex column) | `gap: 2` | 16px |
| Card internal padding | `px: 2–3, py: 1.25–2` | varies |
| Table cell padding | `py: 1–1.25` | 8–10px |

---

## 3. Card Containers

Every distinct section lives inside a `Card variant="outlined"`. **Never use flat `Box` containers** for page-level sections.

### Base card style

```tsx
<Card
  variant="outlined"
  sx={{
    borderRadius: 2,
    border: '1px solid',
    borderColor: 'divider',
    boxShadow: 'none',
    overflow: 'hidden', // required for tables
  }}
>
```

### Three-card layout per tab

Every tab should follow this stacked structure:

```
┌─────────────────────────────────────────────────────┐
│  TOOLBAR CARD  (search + filters + primary action)  │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│  SUMMARY CARD  (3 prominent metric blocks)          │
└─────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────┐
│  TABLE / CONTENT CARD  (grouped data)               │
└─────────────────────────────────────────────────────┘
```

---

## 4. Toolbar Card Pattern

The toolbar is a bordered card containing: **search field | filter toggles | primary CTA button**.

```tsx
<Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none', px: 2, py: 1.25 }}>
  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1.5, justifyContent: 'space-between', alignItems: 'center' }}>
    {/* Left: search + filter toggles */}
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, flexGrow: 1, flexWrap: 'wrap' }}>
      <TextField
        size="small"
        placeholder="Search..."
        sx={{ width: 200, '& .MuiOutlinedInput-root': { borderRadius: 1.5, fontSize: '0.85rem' } }}
        InputProps={{ startAdornment: <SearchIcon color="action" sx={{ mr: 0.75, fontSize: 17 }} /> }}
      />
      {/* Filter toggles — see Section 5 */}
    </Box>
    {/* Right: primary CTA */}
    <Button
      variant="contained"
      color="primary"
      sx={{ py: 0.6, px: 2, fontWeight: 600, textTransform: 'none', borderRadius: 1.5, fontSize: '0.85rem', flexShrink: 0 }}
    >
      Add Item
    </Button>
  </Box>
</Card>
```

---

## 5. Color-Coded Filter Toggle Chips

Do **not** use MUI `<Chip>` for filter toggles. Use styled `<Box>` elements with the entity's own color palette for active state.

```tsx
// Color config (per entity, similar to CATEGORY_META)
const ENTITY_META = {
  KEY: { label: 'Label', color: '#108cc6', icon: SomeIcon, bg: 'rgba(16, 140, 198, 0.1)' },
  // ...
};

// Render toggle
{Object.entries(ENTITY_META).map(([code, meta]) => {
  const isActive = selectedCodes.includes(code);
  const IconComponent = meta.icon;
  return (
    <Box
      key={code}
      onClick={() => handleToggle(code)}
      sx={{
        display: 'flex', alignItems: 'center', gap: 0.5,
        px: 1.25, py: 0.4,
        borderRadius: '20px',
        border: '1.5px solid',
        borderColor: isActive ? meta.color : 'divider',
        bgcolor: isActive ? meta.bg : 'transparent',
        color: isActive ? meta.color : 'text.disabled',
        cursor: 'pointer',
        userSelect: 'none',
        transition: 'all 0.15s ease',
        '&:hover': { borderColor: meta.color, bgcolor: meta.bg, color: meta.color },
      }}
    >
      <IconComponent sx={{ fontSize: 12 }} />
      <Typography sx={{ fontSize: '0.72rem', fontWeight: 700, lineHeight: 1 }}>
        {meta.label}
      </Typography>
    </Box>
  );
})}
```

### Entity color palette (Wealth module)

| Entity | `color` | `bg` |
|---|---|---|
| Equity | `#108cc6` | `rgba(16, 140, 198, 0.1)` |
| Debt | `#1e5067` | `rgba(30, 80, 103, 0.1)` |
| Real Estate | `#f59e0b` | `rgba(245, 158, 11, 0.1)` |
| Commodities | `#fbbf24` | `rgba(251, 191, 36, 0.1)` |
| Cash & Bank | `#10b981` | `rgba(16, 185, 129, 0.1)` |

---

## 6. Summary Card Pattern

A **separate** Card (not embedded in the table card) with 3 metric blocks separated by vertical dividers.

```tsx
<Card variant="outlined" sx={{ borderRadius: 2, border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
  <Box sx={{ display: 'flex' }}>
    {/* Metric block */}
    <Box sx={{ flex: 1, px: 3, py: 2 }}>
      <Typography variant="caption" color="text.disabled" sx={{
        fontWeight: 600, textTransform: 'uppercase', letterSpacing: 0.8,
        fontSize: '0.68rem', display: 'block', mb: 0.5
      }}>
        Invested
      </Typography>
      <Typography variant="h5" sx={{
        fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif',
        color: 'text.primary', fontSize: '1.3rem'
      }}>
        {formatCompactRupees(value)}
      </Typography>
    </Box>
    <Divider orientation="vertical" flexItem />
    {/* Repeat for Current Value (color: 'primary.main') and Returns */}
  </Box>
</Card>
```

**Rules:**
- Always show: Invested → Current Value → Returns/P&L
- Current Value number uses `color: 'primary.main'`
- Returns renders using the `renderReturnsText` helper (green/red with trend icon)

---

## 7. Grouped Table Pattern

The **single grouped table** pattern replaces nested accordions. One shared column header, category group rows as styled dividers, asset rows beneath.

### Table Card wrapper

```tsx
<Card variant="outlined" sx={{ borderRadius: 2, overflow: 'hidden', border: '1px solid', borderColor: 'divider', boxShadow: 'none' }}>
  <TableContainer component={Paper} elevation={0} sx={{ borderRadius: 0, bgcolor: 'transparent' }}>
    <Table size="small">
      {/* One TableHead — appears only once at the top */}
      <TableHead sx={{ bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' }}>
        <TableRow>
          <TableCell sx={{ pl: 3, fontWeight: 700, py: 1.25, fontSize: '0.78rem', textTransform: 'uppercase', letterSpacing: 0.5, color: 'text.secondary' }}>
            Name
          </TableCell>
          {/* ... more columns ... */}
        </TableRow>
      </TableHead>
      <TableBody>
        {/* Category group rows + asset rows — see below */}
      </TableBody>
    </Table>
  </TableContainer>
</Card>
```

### Category group-divider row

```tsx
<TableRow
  key={`cat-${code}`}
  onClick={() => handleToggleCategory(code)}
  sx={{
    cursor: 'pointer',
    bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.3)' : '#f8fafc',
    borderLeft: `3px solid ${meta.color}`,   // ← colored left accent
    '&:hover': { bgcolor: (theme) => theme.palette.mode === 'dark' ? 'rgba(30, 41, 59, 0.5)' : '#f1f5f9' },
    borderTop: idx === 0 ? 'none' : '1px solid',
    borderTopColor: 'divider',
  }}
>
  {/* LEFT: chevron + icon + label + count chip — spans 4 cols */}
  <TableCell colSpan={4} sx={{ py: 1.5, pl: 2 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.25 }}>
      {/* Animated chevron */}
      <Box sx={{ transition: 'transform 0.2s', transform: isOpen ? 'rotate(0deg)' : 'rotate(-90deg)' }}>
        <ExpandMoreIcon sx={{ fontSize: 18 }} />
      </Box>
      {/* Category icon badge */}
      <Box sx={{ width: 28, height: 28, borderRadius: '50%', bgcolor: meta.bg, color: meta.color, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <IconComponent sx={{ fontSize: 15 }} />
      </Box>
      {/* Label */}
      <Typography variant="body2" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif' }}>
        {meta.label}
      </Typography>
      {/* Count chip */}
      <Chip label={count} size="small" sx={{ height: 18, fontSize: '0.68rem', fontWeight: 700, bgcolor: meta.bg, color: meta.color, '& .MuiChip-label': { px: 0.75 } }} />
    </Box>
  </TableCell>
  {/* RIGHT: current value + returns — spans remaining 2 cols */}
  <TableCell colSpan={2} align="right" sx={{ pr: 3, py: 1.5 }}>
    <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 2 }}>
      <Typography variant="body2" sx={{ fontWeight: 700, color: 'primary.main', fontFamily: '"Space Grotesk", sans-serif', fontSize: '0.95rem' }}>
        {formatCompactRupees(current)}
      </Typography>
      {renderReturnsText(returns, pctReturns)}
    </Box>
  </TableCell>
</TableRow>
```

### Asset data rows (with zebra striping)

```tsx
catAssets.map((asset, assetIdx) => (
  <TableRow
    key={asset.id}
    sx={{
      display: isOpen ? undefined : 'none',           // hide when collapsed
      '& td': { py: 1 },
      bgcolor: assetIdx % 2 === 0                     // zebra stripe
        ? 'transparent'
        : (theme) => theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.018)' : 'rgba(0,0,0,0.018)',
      '&:hover': { bgcolor: 'action.hover' },
    }}
  >
    <TableCell sx={{ pl: 4 }}>{/* asset name + notes */}</TableCell>
    {/* ... */}
  </TableRow>
))
```

**Rules:**
- Asset name cell: `pl: 4` (indented to align under the category label)
- Sub-category chip: MUI `<Chip size="small" sx={{ fontSize: '0.7rem', fontWeight: 500, height: 20 }} />`
- Action buttons: `<IconButton size="small">` with Tooltip. Order: **History → Edit → Delete**

---

## 8. Returns Display Helper

Use a shared helper for all returns/P&L cells. Green for positive, red for negative, with trend icon.

```tsx
const renderReturnsText = (absVal: number, pctVal: number) => {
  const isPositive = absVal >= 0;
  return (
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, color: isPositive ? 'success.main' : 'error.main' }}>
      {isPositive ? <TrendingUpIcon fontSize="small" /> : <TrendingDownIcon fontSize="small" />}
      <Typography variant="body2" sx={{ fontWeight: 700, whiteSpace: 'nowrap' }}>
        {isPositive ? '+' : ''}{formatCurrency(absVal)} ({isPositive ? '+' : ''}{pctVal.toFixed(2)}%)
      </Typography>
    </Box>
  );
};
```

---

## 9. Currency Formatter

Use `formatCompactRupees` for **summary cards and category group rows** where space is limited.
Use `formatCurrency` for **individual asset rows** where full precision is expected.

```tsx
// Compact: ₹12.00L, ₹1.50Cr, ₹90,000.00
export const formatCompactRupees = (value: number): string => {
  if (value === 0) return '₹0.00';
  const isNegative = value < 0;
  const absVal = Math.abs(value);
  let result = '';
  if (absVal >= 10000000) {
    result = `₹${(absVal / 10000000).toFixed(2)} Cr`;
  } else if (absVal >= 100000) {
    result = `₹${(absVal / 100000).toFixed(2)}L`;
  } else {
    result = formatCurrency(absVal);
    return isNegative ? `-${result}` : result;
  }
  return isNegative ? `-${result}` : result;
};
```

---

## 10. Page Wrapper Pattern

All data pages use the same outer `Box` + `Container` structure.

```tsx
<Box
  sx={{
    flexGrow: 1,
    bgcolor: 'background.default',
    py: 2.5,
    px: { xs: 2, md: 4 },
    backgroundImage: (theme) =>
      theme.palette.mode === 'dark'
        ? 'radial-gradient(circle at 10% 20%, rgba(30, 41, 59, 0.4) 0%, rgba(17, 24, 39, 0.95) 90%)'
        : 'none',
    transition: 'background-color 0.3s ease',
  }}
>
  <Container maxWidth="xl">
    {/* Page Header */}
    <Box sx={{ mb: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
      <Box>
        <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', lineHeight: 1.2 }}>
          Page Title
        </Typography>
        <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
          Subtitle / count
        </Typography>
      </Box>
    </Box>

    {/* Tabs */}
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
      <Tabs value={activeTab} onChange={...} sx={{
        minHeight: 36,
        '& .MuiTab-root': { fontFamily: '"Space Grotesk", sans-serif', fontWeight: 600, fontSize: '0.875rem', textTransform: 'none', minHeight: 36, px: 0, mr: 3, py: 0.5 },
      }}>
        <Tab label="Primary" />
        <Tab label="Secondary" disabled />
      </Tabs>
    </Box>

    {/* Content */}
    {activeTab === 0 && <PrimaryTab />}
  </Container>
</Box>
```

**Rules:**
- `Container maxWidth="xl"` — always xl for wide data tables
- Tabs: `minHeight: 36`, `textTransform: 'none'`, no `px` on tabs (padding handled by `mr: 3`)
- Disabled tabs (future features) are allowed — they communicate roadmap

---

## 11. Confirmation Dialog Pattern

Use a **custom in-app dialog** for destructive actions. **Never use `window.confirm()`**.

```tsx
const [confirmDialog, setConfirmDialog] = useState({
  open: false, title: '', message: '', onConfirm: () => {},
});

// Trigger
openConfirm(
  'Delete Asset',
  `Are you sure you want to delete "${asset.name}"? This action cannot be undone.`,
  async () => {
    await emsClient.deleteAsset(asset.id);
    toast.success('Asset deleted');
    fetchData();
  }
);

// Render
<Dialog open={confirmDialog.open} onClose={closeConfirm} maxWidth="xs" fullWidth>
  <DialogTitle sx={{ fontWeight: 700 }}>{confirmDialog.title}</DialogTitle>
  <DialogContent>
    <Typography variant="body2">{confirmDialog.message}</Typography>
  </DialogContent>
  <DialogActions>
    <Button onClick={closeConfirm} variant="outlined" color="inherit">Cancel</Button>
    <Button onClick={() => { confirmDialog.onConfirm(); closeConfirm(); }} variant="contained" color="error">
      Confirm Delete
    </Button>
  </DialogActions>
</Dialog>
```

---

## 12. Dark Mode Compatibility

Every bg/color that differs between light/dark must use the theme callback:

```tsx
// ✅ Correct
bgcolor: (theme) => theme.palette.mode === 'dark'
  ? 'rgba(30, 41, 59, 0.3)'
  : '#f8fafc'

// ❌ Wrong — hardcoded color breaks dark mode
bgcolor: '#f8fafc'
```

Established pairs:

| Purpose | Light | Dark |
|---|---|---|
| Category group row | `#f8fafc` | `rgba(30, 41, 59, 0.3)` |
| Category row hover | `#f1f5f9` | `rgba(30, 41, 59, 0.5)` |
| Table header | `#f1f5f9` | `rgba(30, 41, 59, 0.5)` |
| Zebra stripe (odd rows) | `rgba(0,0,0,0.018)` | `rgba(255,255,255,0.018)` |

---

## 13. Action Icon Button Order

Within table rows, action buttons always follow this order, left to right:

| Order | Action | Icon | Color |
|---|---|---|---|
| 1 | View/History | `HistoryIcon` | `primary` |
| 2 | Edit | `EditIcon` | `secondary` |
| 3 | Delete | `DeleteIcon` | `error` |

```tsx
<TableCell align="center" sx={{ pr: 3, whiteSpace: 'nowrap' }}>
  <Tooltip title="Transaction History">
    <IconButton onClick={() => handleOpenLedger(item)} size="small" color="primary">
      <HistoryIcon fontSize="small" />
    </IconButton>
  </Tooltip>
  <Tooltip title="Edit">
    <IconButton onClick={() => handleOpenEdit(item)} size="small" color="secondary">
      <EditIcon fontSize="small" />
    </IconButton>
  </Tooltip>
  <Tooltip title="Delete">
    <IconButton onClick={() => handleDelete(item)} size="small" color="error">
      <DeleteIcon fontSize="small" />
    </IconButton>
  </Tooltip>
</TableCell>
```

---

## 14. Reference Files

| File | Role |
|---|---|
| [AssetsTab.tsx](file:///c:/Users/shang/sandbox/repos/bella-keys-personal-assist/keys-personal-assist-ui/src/components/wealth/AssetsTab.tsx) | Canonical reference — all patterns live here |
| [WealthPage.tsx](file:///c:/Users/shang/sandbox/repos/bella-keys-personal-assist/keys-personal-assist-ui/src/pages/WealthPage.tsx) | Page wrapper + tabs pattern |
