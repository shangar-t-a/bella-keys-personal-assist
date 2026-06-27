import { createTheme, type ThemeOptions, alpha } from '@mui/material/styles';

// Premium Palette
// Desaturated, sophisticated tones inspired by Azure Portal / Vercel Dashboard.
// Avoids raw primaries; uses curated HSL-derived variants.

const lightPalette = {
  mode: 'light' as const,
  primary: {
    main: '#1b4f72',
    light: '#2471a3',
    dark: '#154360',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#1a8fc4',
    light: '#48b1e0',
    dark: '#0e6d99',
    contrastText: '#ffffff',
  },
  background: {
    default: '#f4f6f8',
    paper: '#ffffff',
  },
  text: {
    primary: '#1c2b36',
    secondary: '#556b7e',
  },
  error: {
    main: '#d94052',
    light: '#ef5f6e',
    dark: '#b5283a',
  },
  warning: {
    main: '#e29624',
    light: '#f0b84a',
    dark: '#b87a1a',
  },
  info: {
    main: '#1a8fc4',
    light: '#48b1e0',
    dark: '#0e6d99',
  },
  success: {
    main: '#1a9a6b',
    light: '#34c48e',
    dark: '#137a54',
  },
  divider: 'rgba(0, 0, 0, 0.08)',
};

const darkPalette = {
  mode: 'dark' as const,
  primary: {
    main: '#48b1e0',
    light: '#7dcbee',
    dark: '#1a8fc4',
    contrastText: '#0d1b26',
  },
  secondary: {
    main: '#7dcbee',
    light: '#a8ddf5',
    dark: '#48b1e0',
    contrastText: '#0d1b26',
  },
  background: {
    default: '#0d1b26',
    paper: '#152232',
  },
  text: {
    primary: '#e4ecf2',
    secondary: '#8ba3b8',
  },
  error: {
    main: '#ef5f6e',
    light: '#f48d98',
    dark: '#d94052',
  },
  warning: {
    main: '#f0b84a',
    light: '#f5ce7a',
    dark: '#e29624',
  },
  info: {
    main: '#48b1e0',
    light: '#7dcbee',
    dark: '#1a8fc4',
  },
  success: {
    main: '#34c48e',
    light: '#5fd6a8',
    dark: '#1a9a6b',
  },
  divider: 'rgba(255, 255, 255, 0.08)',
};

// Shadow System
// 3-tier elevation: flush → soft ambient → pronounced float

const lightShadows = {
  card: '0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03)',
  cardHover: '0 4px 16px rgba(0,0,0,0.08), 0 1px 4px rgba(0,0,0,0.04)',
  elevated: '0 8px 32px rgba(0,0,0,0.08), 0 2px 8px rgba(0,0,0,0.04)',
  dialog: '0 24px 48px rgba(0,0,0,0.12), 0 8px 16px rgba(0,0,0,0.06)',
};

const darkShadows = {
  card: '0 1px 3px rgba(0,0,0,0.2), 0 4px 12px rgba(0,0,0,0.15)',
  cardHover: '0 4px 16px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.2)',
  elevated: '0 8px 32px rgba(0,0,0,0.4), 0 2px 8px rgba(0,0,0,0.2)',
  dialog: '0 24px 48px rgba(0,0,0,0.5), 0 8px 16px rgba(0,0,0,0.3)',
};

// Theme Builder

const getThemeOptions = (mode: 'light' | 'dark'): ThemeOptions => {
  const palette = mode === 'light' ? lightPalette : darkPalette;
  const shadows = mode === 'light' ? lightShadows : darkShadows;
  const isDark = mode === 'dark';

  return {
    palette,
    typography: {
      fontFamily: '"Space Grotesk", "DM Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
      h1: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 700,
      },
      h2: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 700,
      },
      h3: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 600,
      },
      h4: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 600,
      },
      h5: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 600,
      },
      h6: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 600,
      },
      subtitle1: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 600,
        fontSize: '1rem',
      },
      subtitle2: {
        fontFamily: '"Space Grotesk", sans-serif',
        fontWeight: 600,
        fontSize: '0.875rem',
      },
      body1: {
        fontFamily: '"DM Sans", sans-serif',
      },
      body2: {
        fontFamily: '"DM Sans", sans-serif',
      },
      caption: {
        fontFamily: '"DM Sans", sans-serif',
        fontSize: '0.75rem',
      },
      button: {
        fontFamily: '"DM Sans", sans-serif',
        fontWeight: 500,
        textTransform: 'none' as const,
      },
    },
    shape: {
      borderRadius: 12,
    },
    components: {
      // Buttons
      MuiButton: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            padding: '8px 20px',
            fontSize: '0.85rem',
            fontWeight: 600,
            letterSpacing: '0.01em',
            transition: 'all 200ms ease',
          },
          contained: {
            boxShadow: 'none',
            '&:hover': {
              boxShadow: shadows.card,
              transform: 'translateY(-1px)',
            },
          },
          outlined: {
            borderColor: isDark ? 'rgba(255,255,255,0.12)' : 'rgba(0,0,0,0.12)',
            '&:hover': {
              borderColor: isDark ? 'rgba(255,255,255,0.24)' : 'rgba(0,0,0,0.24)',
              backgroundColor: isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.02)',
            },
          },
          text: {
            '&:hover': {
              backgroundColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.04)',
            },
          },
          sizeSmall: {
            padding: '5px 14px',
            fontSize: '0.8125rem',
          },
        },
      },

      // Cards
      MuiCard: {
        defaultProps: {
          elevation: 0,
        },
        styleOverrides: {
          root: {
            borderRadius: 14,
            border: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
            boxShadow: shadows.card,
            transition: 'box-shadow 200ms ease, transform 200ms ease, border-color 200ms ease',
            backgroundImage: 'none',
          },
        },
      },

      // Paper
      MuiPaper: {
        styleOverrides: {
          root: {
            borderRadius: 14,
            backgroundImage: 'none',
          },
          elevation0: {
            boxShadow: 'none',
          },
          elevation1: {
            boxShadow: shadows.card,
          },
          elevation2: {
            boxShadow: shadows.elevated,
          },
          elevation4: {
            boxShadow: shadows.dialog,
          },
        },
      },

      // Text Fields
      MuiTextField: {
        styleOverrides: {
          root: {
            '& .MuiOutlinedInput-root': {
              borderRadius: 10,
              transition: 'border-color 200ms ease, box-shadow 200ms ease',
              '&.Mui-focused': {
                boxShadow: `0 0 0 3px ${alpha(palette.primary.main, 0.12)}`,
              },
            },
          },
        },
      },

      // Select
      MuiOutlinedInput: {
        styleOverrides: {
          root: {
            borderRadius: 10,
            transition: 'border-color 200ms ease, box-shadow 200ms ease',
            '&.Mui-focused': {
              boxShadow: `0 0 0 3px ${alpha(palette.primary.main, 0.12)}`,
            },
          },
        },
      },

      // Dialogs
      MuiDialog: {
        styleOverrides: {
          paper: {
            borderRadius: 16,
            boxShadow: shadows.dialog,
            border: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
          },
        },
      },

      // Chips
      MuiChip: {
        styleOverrides: {
          root: {
            borderRadius: 8,
            fontWeight: 600,
            fontSize: '0.72rem',
            letterSpacing: '0.02em',
            transition: 'background-color 200ms ease',
          },
          sizeSmall: {
            height: 22,
            fontSize: '0.68rem',
          },
          outlined: {
            borderWidth: 1.5,
          },
        },
      },

      // Tables
      MuiTableHead: {
        styleOverrides: {
          root: {
            '& .MuiTableCell-head': {
              fontFamily: '"Space Grotesk", sans-serif',
              fontWeight: 600,
              fontSize: '0.72rem',
              textTransform: 'uppercase' as const,
              letterSpacing: '0.06em',
              color: palette.text.secondary,
              backgroundColor: isDark ? alpha('#1a2d3e', 0.6) : '#f8fafb',
              borderBottom: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
              paddingTop: 12,
              paddingBottom: 12,
            },
          },
        },
      },
      MuiTableRow: {
        styleOverrides: {
          root: {
            transition: 'background-color 150ms ease',
            '&:hover': {
              backgroundColor: isDark ? 'rgba(255,255,255,0.025)' : 'rgba(0,0,0,0.015)',
            },
            '&:last-child td, &:last-child th': {
              borderBottom: 0,
            },
          },
        },
      },
      MuiTableCell: {
        styleOverrides: {
          root: {
            borderBottom: `1px solid ${isDark ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)'}`,
            fontSize: '0.85rem',
            padding: '10px 16px',
          },
        },
      },
      MuiTablePagination: {
        styleOverrides: {
          root: {
            borderTop: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
          },
        },
      },

      // Tabs
      MuiTab: {
        styleOverrides: {
          root: {
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
            fontSize: '0.85rem',
            textTransform: 'none' as const,
            minHeight: 40,
            padding: '8px 0',
            marginRight: 24,
            transition: 'color 200ms ease',
          },
        },
      },
      MuiTabs: {
        styleOverrides: {
          root: {
            minHeight: 40,
          },
          indicator: {
            height: 2.5,
            borderRadius: 2,
          },
        },
      },

      // Linear Progress
      MuiLinearProgress: {
        styleOverrides: {
          root: {
            borderRadius: 6,
            height: 8,
            backgroundColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
          },
          bar: {
            borderRadius: 6,
          },
        },
      },

      // AppBar
      MuiAppBar: {
        styleOverrides: {
          root: {
            boxShadow: 'none',
            borderBottom: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
          },
        },
      },

      // Tooltip
      MuiTooltip: {
        styleOverrides: {
          tooltip: {
            borderRadius: 8,
            fontSize: '0.75rem',
            fontWeight: 500,
            padding: '6px 12px',
            backgroundColor: isDark ? '#1a2d3e' : '#1c2b36',
            boxShadow: shadows.elevated,
          },
          arrow: {
            color: isDark ? '#1a2d3e' : '#1c2b36',
          },
        },
      },

      // Divider
      MuiDivider: {
        styleOverrides: {
          root: {
            borderColor: isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
          },
        },
      },

      // Drawer
      MuiDrawer: {
        styleOverrides: {
          paper: {
            borderRight: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
            backgroundImage: 'none',
          },
        },
      },

      // Menu
      MuiMenu: {
        styleOverrides: {
          paper: {
            borderRadius: 12,
            boxShadow: shadows.elevated,
            border: `1px solid ${isDark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)'}`,
            backgroundImage: 'none',
          },
        },
      },

      // Checkbox
      MuiCheckbox: {
        styleOverrides: {
          root: {
            transition: 'color 150ms ease',
          },
        },
      },

      // IconButton
      MuiIconButton: {
        styleOverrides: {
          root: {
            transition: 'all 200ms ease',
            '&:hover': {
              transform: 'scale(1.05)',
            },
          },
        },
      },

      // List
      MuiListItemButton: {
        styleOverrides: {
          root: {
            transition: 'all 200ms ease',
          },
        },
      },

      // Avatar
      MuiAvatar: {
        styleOverrides: {
          root: {
            fontFamily: '"Space Grotesk", sans-serif',
            fontWeight: 600,
          },
        },
      },
    },
  };
};

export const createAppTheme = (mode: 'light' | 'dark') => {
  return createTheme(getThemeOptions(mode));
};
