### Version 0.0.3 - 2024-07-30
- **Changed**: `AddEntryModal.tsx`, `EditEntryModal.tsx`
- **What**: Removed the redundant close ('x') button from the header of the Add Entry and Edit Entry modals.
- **Why**: The modal overlay click and the "Cancel" button already provide sufficient ways to close the modal, making the 'x' button redundant and visually cluttered.

### Version 0.0.2 - 2024-07-30
- **Changed**: `index.css`
- **What**: Modified CSS to apply dark mode variables based on `body.dark-mode` class instead of `prefers-color-scheme`.
- **Why**: Fixed issue where theme toggling was not visually apparent, ensuring the application's colors change correctly when the dark mode button is toggled.
