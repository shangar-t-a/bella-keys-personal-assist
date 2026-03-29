import { createTheme, type ThemeOptions } from '@mui/material/styles';

// Palette derived from personal brand CSS variables
// Light: deep teal primary (#1e5067), medium blue secondary (#108cc6)
// Dark:  sky blue primary (#108cc6), lighter blue secondary (#29afee)
const lightPalette = {
  mode: 'light' as const,
  primary: {
    main: '#1e5067',
    light: '#235c76',
    dark: '#153848',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#108cc6',
    light: '#29afee',
    dark: '#0b628b',
    contrastText: '#ffffff',
  },
  background: {
    default: '#f5f8fa',
    paper: '#ffffff',
  },
  text: {
    primary: '#1a2e3b',
    secondary: '#4a6578',
  },
  error: {
    main: '#ef4444',
  },
  warning: {
    main: '#f59e0b',
  },
  info: {
    main: '#108cc6',
  },
  success: {
    main: '#10b981',
  },
  divider: '#dde6ed',
};

const darkPalette = {
  mode: 'dark' as const,
  primary: {
    main: '#108cc6',
    light: '#29afee',
    dark: '#0b628b',
    contrastText: '#ffffff',
  },
  secondary: {
    main: '#29afee',
    light: '#67e8f9',
    dark: '#108cc6',
    contrastText: '#1a2e3b',
  },
  background: {
    default: '#111827',
    paper: '#1e2d3d',
  },
  text: {
    primary: '#e2eaf2',
    secondary: '#8aa3b8',
  },
  error: {
    main: '#f87171',
  },
  warning: {
    main: '#fbbf24',
  },
  info: {
    main: '#29afee',
  },
  success: {
    main: '#34d399',
  },
  divider: '#2d4157',
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
          borderBottom: mode === 'light' ? '1px solid #dde6ed' : '1px solid #2d4157',
        },
      },
    },
  },
});

export const createAppTheme = (mode: 'light' | 'dark') => {
  return createTheme(getThemeOptions(mode));
};
