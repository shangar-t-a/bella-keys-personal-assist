import React, { useState } from 'react';
import axios from 'axios';
import { useAuth } from '../context/AuthContext';
import { getAuthBase } from '../api/config';
import { toast } from 'sonner';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Button,
  IconButton,
  InputAdornment,
  CircularProgress,
  Tabs,
  Tab,
  Zoom,
  useTheme,
} from '@mui/material';
import {
  AutoAwesome as Sparkles,
  Visibility,
  VisibilityOff,
  Person,
  Lock,
  VpnKey,
} from '@mui/icons-material';

const Login: React.FC = () => {
  const theme = useTheme();
  const { login } = useAuth();
  
  // Tabs: 0 = Login, 1 = Register
  const [tabValue, setTabValue] = useState<number>(0);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const brandGradient = `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`;

  const handleTabChange = (_event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
    // Reset validation/error states if needed
    setPassword('');
    setConfirmPassword('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;

    if (!username.trim() || !password) {
      toast.error('Please fill in all fields.');
      return;
    }

    if (tabValue === 1 && password !== confirmPassword) {
      toast.error('Passwords do not match.');
      return;
    }

    setLoading(true);
    const authBase = getAuthBase();

    try {
      if (tabValue === 0) {
        // --- LOGIN FLOW ---
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await axios.post(`${authBase}/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });
        
        const { access_token, refresh_token } = response.data;
        login(access_token, refresh_token);
        
        toast.success(`Welcome back, ${username}!`);
        // Force redirect to homepage
        setTimeout(() => {
          window.location.href = '/';
        }, 800);
      } else {
        // --- REGISTER FLOW ---
        await axios.post(`${authBase}/register`, {
          username: username,
          password: password
        });

        toast.success('Account created successfully! Logging you in...');

        // Auto-login after successful registration
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        const response = await axios.post(`${authBase}/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        });

        const { access_token, refresh_token } = response.data;
        login(access_token, refresh_token);

        setTimeout(() => {
          window.location.href = '/';
        }, 800);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || 'Authentication failed. Please try again.';
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: `radial-gradient(circle at 50% 50%, ${theme.palette.mode === 'dark' ? '#1e2d3d' : '#e2eaf2'} 0%, ${theme.palette.background.default} 100%)`,
        px: 2,
      }}
    >
      <Zoom in={true} style={{ transitionDelay: '100ms' }}>
        <Card
          sx={{
            width: '100%',
            maxWidth: 420,
            borderRadius: 3.5,
            boxShadow: theme.palette.mode === 'dark' 
              ? '0 12px 40px rgba(0, 0, 0, 0.6)' 
              : '0 12px 40px rgba(30, 80, 103, 0.12)',
            border: `1px solid ${theme.palette.divider}`,
            backdropFilter: 'blur(20px)',
            background: theme.palette.mode === 'dark'
              ? 'rgba(30, 45, 61, 0.85)'
              : 'rgba(255, 255, 255, 0.9)',
            overflow: 'hidden',
          }}
        >
          {/* Top Decorative Color Strip */}
          <Box sx={{ height: 6, background: brandGradient }} />

          <CardContent sx={{ p: 4, pt: 3.5 }}>
            {/* Logo and Brand Title */}
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 3 }}>
              <Box
                sx={{
                  width: 48,
                  height: 48,
                  borderRadius: 2,
                  background: brandGradient,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 4px 20px rgba(16, 140, 198, 0.3)',
                  mb: 1.5,
                }}
              >
                <Sparkles sx={{ color: 'white', fontSize: 24 }} />
              </Box>
              
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  fontFamily: '"Space Grotesk", sans-serif',
                  background: brandGradient,
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                }}
              >
                Bella
              </Typography>
              
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontFamily: '"DM Sans", sans-serif', fontSize: '0.85rem' }}
              >
                Keys' Personal Assistant
              </Typography>
            </Box>

            {/* Toggle Tabs */}
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              variant="fullWidth"
              sx={{
                mb: 4,
                borderBottom: `1px solid ${theme.palette.divider}`,
                '& .MuiTab-root': {
                  fontFamily: '"Space Grotesk", sans-serif',
                  fontWeight: 600,
                  fontSize: '0.9rem',
                }
              }}
            >
              <Tab label="Log In" icon={<Lock sx={{ fontSize: 18 }} />} iconPosition="start" />
              <Tab label="Sign Up" icon={<VpnKey sx={{ fontSize: 18 }} />} iconPosition="start" />
            </Tabs>

            {/* Input Form */}
            <Box component="form" onSubmit={handleSubmit} sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
              <TextField
                label="Username"
                variant="outlined"
                fullWidth
                required
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                disabled={loading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Person color="action" fontSize="small" />
                    </InputAdornment>
                  ),
                }}
              />

              <TextField
                label="Password"
                type={showPassword ? 'text' : 'password'}
                variant="outlined"
                fullWidth
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                InputProps={{
                  startAdornment: (
                    <InputAdornment position="start">
                      <Lock color="action" fontSize="small" />
                    </InputAdornment>
                  ),
                  endAdornment: (
                    <InputAdornment position="end">
                      <IconButton
                        onClick={() => setShowPassword(!showPassword)}
                        edge="end"
                        disabled={loading}
                      >
                        {showPassword ? <VisibilityOff fontSize="small" /> : <Visibility fontSize="small" />}
                      </IconButton>
                    </InputAdornment>
                  ),
                }}
              />

              {tabValue === 1 && (
                <Zoom in={tabValue === 1}>
                  <TextField
                    label="Confirm Password"
                    type={showPassword ? 'text' : 'password'}
                    variant="outlined"
                    fullWidth
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                    InputProps={{
                      startAdornment: (
                        <InputAdornment position="start">
                          <VpnKey color="action" fontSize="small" />
                        </InputAdornment>
                      ),
                    }}
                  />
                </Zoom>
              )}

              <Button
                type="submit"
                variant="contained"
                disabled={loading}
                sx={{
                  background: brandGradient,
                  color: '#ffffff',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  fontFamily: '"Space Grotesk", sans-serif',
                  py: 1.5,
                  mt: 1.5,
                  borderRadius: 2,
                  boxShadow: '0 4px 15px rgba(16, 140, 198, 0.25)',
                  '&:hover': {
                    boxShadow: '0 6px 20px rgba(16, 140, 198, 0.4)',
                    opacity: 0.95,
                  },
                }}
              >
                {loading ? (
                  <CircularProgress size={24} color="inherit" />
                ) : tabValue === 0 ? (
                  'Log In'
                ) : (
                  'Sign Up'
                )}
              </Button>
            </Box>
          </CardContent>
        </Card>
      </Zoom>
    </Box>
  );
};

export default Login;
