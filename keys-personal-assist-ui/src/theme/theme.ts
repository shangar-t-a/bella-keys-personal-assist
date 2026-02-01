import { createTheme, type ThemeOptions } from '@mui/material/styles';

// Define color palette matching the original emerald/cyan scheme
const lightPalette = {
  mode: 'light' as const,
  primary: {
    main: '#10b981', // emerald-500
    light: '#34d399', // emerald-400
    dark: '#059669', // emerald-600
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#06b6d4', // cyan-500
    light: '#22d3ee', // cyan-400
    dark: '#0891b2', // cyan-600
    contrastText: '#ffffff',
  },
  background: {
    default: '#ffffff',
    paper: '#ffffff',
  },
  text: {
    primary: '#1f2937', // gray-800
    secondary: '#6b7280', // gray-500
  },
  error: {
    main: '#ef4444', // red-500
  },
  warning: {
    main: '#f59e0b', // amber-500
  },
  info: {
    main: '#3b82f6', // blue-500
  },
  success: {
    main: '#10b981', // emerald-500
  },
  divider: '#e5e7eb', // gray-200
};

const darkPalette = {
  mode: 'dark' as const,
  primary: {
    main: '#34d399', // emerald-400 (lighter for dark mode)
    light: '#6ee7b7', // emerald-300
    dark: '#10b981', // emerald-500
    contrastText: '#1f2937',
  },
  secondary: {
    main: '#22d3ee', // cyan-400
    light: '#67e8f9', // cyan-300
    dark: '#06b6d4', // cyan-500
    contrastText: '#1f2937',
  },
  background: {
    default: '#1f2937', // gray-800
    paper: '#374151', // gray-700
  },
  text: {
    primary: '#f9fafb', // gray-50
    secondary: '#9ca3af', // gray-400
  },
  error: {
    main: '#f87171', // red-400
  },
  warning: {
    main: '#fbbf24', // amber-400
  },
  info: {
    main: '#60a5fa', // blue-400
  },
  success: {
    main: '#34d399', // emerald-400
  },
  divider: '#4b5563', // gray-600
};

const getThemeOptions = (mode: 'light' | 'dark'): ThemeOptions => ({
  palette: mode === 'light' ? lightPalette : darkPalette,
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
    body1: {
      fontFamily: '"DM Sans", sans-serif',
    },
    body2: {
      fontFamily: '"DM Sans", sans-serif',
    },
    button: {
      fontFamily: '"DM Sans", sans-serif',
      fontWeight: 500,
      textTransform: 'none' as const,
    },
  },
  shape: {
    borderRadius: 10, // 0.625rem = 10px for modern rounded feel
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          padding: '10px 20px',
          fontSize: '0.875rem',
          fontWeight: 500,
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 10,
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 10,
        },
        elevation1: {
          boxShadow: '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 10,
          },
        },
      },
    },
    MuiDialog: {
      styleOverrides: {
        paper: {
          borderRadius: 10,
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          boxShadow: 'none',
          borderBottom: mode === 'light' ? '1px solid #e5e7eb' : '1px solid #4b5563',
        },
      },
    },
  },
});

export const createAppTheme = (mode: 'light' | 'dark') => {
  return createTheme(getThemeOptions(mode));
};
