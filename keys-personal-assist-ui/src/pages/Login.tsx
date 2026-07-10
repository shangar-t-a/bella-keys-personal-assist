import React, { useState } from 'react';
import { getAuthBase } from '@/api/config';
import { toast } from 'sonner';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  CircularProgress,
  Zoom,
  useTheme,
} from '@mui/material';
import {
  AutoAwesome as Sparkles,
  Login as LoginIcon,
} from '@mui/icons-material';

// Helper functions for PKCE Code Challenge generation using standard Web Crypto API
function dec2hex(dec: number): string {
  return dec.toString(16).padStart(2, '0');
}

function generateCodeVerifier(): string {
  const array = new Uint32Array(56 / 2);
  window.crypto.getRandomValues(array);
  return Array.from(array, dec2hex).join('');
}

async function sha256(plain: string): Promise<ArrayBuffer> {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  return window.crypto.subtle.digest('SHA-256', data);
}

function base64urlencode(a: ArrayBuffer): string {
  let str = '';
  const bytes = new Uint8Array(a);
  const len = bytes.byteLength;
  for (let i = 0; i < len; i++) {
    str += String.fromCharCode(bytes[i]);
  }
  return btoa(str)
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

async function generateCodeChallenge(v: string): Promise<string> {
  const hashed = await sha256(v);
  return base64urlencode(hashed);
}

const Login: React.FC = () => {
  const theme = useTheme();
  const [loading, setLoading] = useState(false);

  const brandGradient = `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.info.main} 100%)`;

  const handleSSOLogin = async () => {
    if (loading) return;
    setLoading(true);

    try {
      const codeVerifier = generateCodeVerifier();
      const codeChallenge = await generateCodeChallenge(codeVerifier);
      
      // Store code_verifier locally to execute exchange later
      localStorage.setItem('pkce_code_verifier', codeVerifier);

      const authBase = getAuthBase();
      const clientId = 'keys-personal-assist-ui';
      const redirectUri = `${window.location.origin}/callback`;
      const state = Math.random().toString(36).substring(2, 15);

      // Build OAuth 2.1 authorization URL
      const authorizeUrl = `${authBase}/oauth/authorize?client_id=${encodeURIComponent(
        clientId
      )}&redirect_uri=${encodeURIComponent(
        redirectUri
      )}&response_type=code&code_challenge=${encodeURIComponent(
        codeChallenge
      )}&code_challenge_method=S256&state=${encodeURIComponent(
        state
      )}&scope=openid%20profile%20email`;

      // Redirect client browser to central IdP Login Consent Page
      window.location.href = authorizeUrl;
    } catch (err: any) {
      console.error('SSO Initialization Error:', err);
      toast.error('Failed to initialize SSO authentication flow.');
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
        background: `radial-gradient(circle at 50% 50%, ${theme.palette.mode === 'dark' ? '#152232' : '#e8f0f8'} 0%, ${theme.palette.background.default} 100%)`,
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
            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mb: 4 }}>
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
                Bella Keys
              </Typography>
              
              <Typography
                variant="body2"
                color="text.secondary"
                sx={{ fontFamily: '"DM Sans", sans-serif', fontSize: '0.85rem' }}
              >
                Personal Assistant Platform
              </Typography>
            </Box>

            <Box sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3, textAlign: 'center', mb: 2 }}>
              <Typography variant="body1" color="text.secondary" sx={{ fontFamily: '"DM Sans", sans-serif', fontSize: '0.95rem' }}>
                Secure Single Sign-On (SSO) login. You will be redirected to your centralized authentication portal.
              </Typography>

              <Button
                variant="contained"
                disabled={loading}
                onClick={handleSSOLogin}
                startIcon={!loading && <LoginIcon />}
                sx={{
                  background: brandGradient,
                  color: '#ffffff',
                  fontWeight: 600,
                  fontSize: '0.95rem',
                  fontFamily: '"Space Grotesk", sans-serif',
                  py: 1.5,
                  px: 4,
                  width: '100%',
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
                ) : (
                  'Sign In with SSO'
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
