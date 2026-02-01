import { useState } from 'react';
import { Link as RouterLink, useLocation } from 'react-router-dom';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Drawer,
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  useMediaQuery,
  useTheme,
} from '@mui/material';
import {
  Home,
  BarChart as BarChart3,
  Chat as MessageCircle,
  AutoAwesome as Sparkles,
  LightMode as Sun,
  DarkMode as Moon,
  Menu,
  Close as X,
} from '@mui/icons-material';
import { useThemeMode } from '@/theme/ThemeProvider';

const navigation = [
  { name: 'Home', href: '/', icon: Home },
  { name: 'Dashboard', href: '/dashboard', icon: BarChart3 },
  { name: 'Chat', href: '/chat', icon: MessageCircle },
];

export default function ModernHeader() {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const location = useLocation();
  const { mode, toggleTheme } = useThemeMode();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleMobileMenuToggle = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const handleMobileMenuClose = () => {
    setIsMobileMenuOpen(false);
  };

  return (
    <>
      <AppBar
        position="sticky"
        color="default"
        elevation={0}
        sx={{
          bgcolor: 'background.default',
          backdropFilter: 'blur(8px)',
          borderBottom: 1,
          borderColor: 'divider',
        }}
      >
        <Toolbar sx={{ justifyContent: 'space-between' }}>
          {/* Logo */}
          <Button
            component={RouterLink}
            to="/"
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              textTransform: 'none',
              color: 'primary.main',
              '&:hover': {
                bgcolor: 'transparent',
              },
            }}
          >
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: 1.5,
                background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Sparkles sx={{ color: 'white', fontSize: 20 }} />
            </Box>
            <Typography
              variant="h6"
              component="span"
              sx={{
                fontWeight: 700,
                fontFamily: '"Space Grotesk", sans-serif',
                background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Bella (Keys' Assist)
            </Typography>
          </Button>

          {/* Desktop Navigation */}
          {!isMobile && (
            <Box sx={{ display: 'flex', gap: 0.5 }}>
              {navigation.map((item) => {
                const Icon = item.icon;
                const isActive = location.pathname === item.href;

                return (
                  <Button
                    key={item.name}
                    component={RouterLink}
                    to={item.href}
                    startIcon={<Icon />}
                    sx={{
                      textTransform: 'none',
                      borderRadius: 1.5,
                      px: 2,
                      py: 1,
                      color: isActive ? 'secondary.main' : 'text.secondary',
                      bgcolor: isActive ? 'action.selected' : 'transparent',
                      '&:hover': {
                        bgcolor: 'action.hover',
                        color: 'text.primary',
                      },
                    }}
                  >
                    {item.name}
                  </Button>
                );
              })}
            </Box>
          )}

          {/* Right Side Actions */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <IconButton
              onClick={toggleTheme}
              aria-label={mode === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
              sx={{ borderRadius: '50%' }}
            >
              {mode === 'dark' ? <Sun /> : <Moon />}
            </IconButton>

            {/* Mobile Menu Button */}
            {isMobile && (
              <IconButton
                onClick={handleMobileMenuToggle}
                aria-label="Toggle mobile menu"
                sx={{ borderRadius: '50%' }}
              >
                {isMobileMenuOpen ? <X /> : <Menu />}
              </IconButton>
            )}
          </Box>
        </Toolbar>
      </AppBar>

      {/* Mobile Navigation Drawer */}
      <Drawer
        anchor="right"
        open={isMobileMenuOpen}
        onClose={handleMobileMenuClose}
        sx={{
          '& .MuiDrawer-paper': {
            width: 250,
            bgcolor: 'background.default',
          },
        }}
      >
        <Box sx={{ p: 2 }}>
          <IconButton onClick={handleMobileMenuClose} sx={{ mb: 2 }}>
            <X />
          </IconButton>
          <List>
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.href;

              return (
                <ListItem key={item.name} disablePadding>
                  <ListItemButton
                    component={RouterLink}
                    to={item.href}
                    onClick={handleMobileMenuClose}
                    selected={isActive}
                    sx={{
                      borderRadius: 1.5,
                      mb: 0.5,
                    }}
                  >
                    <ListItemIcon>
                      <Icon />
                    </ListItemIcon>
                    <ListItemText primary={item.name} />
                  </ListItemButton>
                </ListItem>
              );
            })}
          </List>
        </Box>
      </Drawer>
    </>
  );
}
