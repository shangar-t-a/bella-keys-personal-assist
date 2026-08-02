import React, { useState } from 'react';
import { getAuthBase, OAUTH_CLIENT_ID, PKCE_VERIFIER_STORAGE_KEY, isElectron } from '@/api/config';
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
import { APP_VERSION, COPYRIGHT_INFO } from '@/config/appInfo';

// Helper functions for PKCE Code Challenge generation (RFC 7636) using standard Web Crypto API.
// PKCE (Proof Key for Code Exchange) protects public clients (like SPAs) from Authorization Code interception.

const CODE_VERIFIER_BYTE_LENGTH = 28; // 56 characters when hex encoded (56 / 2)
const STATE_RANDOM_RADIX = 36;
const STATE_SUBSTRING_START = 2;
const STATE_SUBSTRING_END = 15;

// Converts a decimal number to a 2-character hexadecimal string
function dec2hex(dec: number): string {
  return dec.toString(16).padStart(2, '0');
}

// Generates a random high-entropy cryptographically secure string to serve as the code verifier.
// The code_verifier is a high-entropy cryptographic key that must be kept secret on the client.
function generateCodeVerifier(): string {
  const array = new Uint32Array(CODE_VERIFIER_BYTE_LENGTH);
  window.crypto.getRandomValues(array);
  return Array.from(array, dec2hex).join('');
}

// Computes the SHA-256 digest of the plaintext code verifier.
async function sha256(plain: string): Promise<ArrayBuffer> {
  const encoder = new TextEncoder();
  const data = encoder.encode(plain);
  return window.crypto.subtle.digest('SHA-256', data);
}

// Encodes an ArrayBuffer using Base64URL encoding (RFC 4648).
// It replaces '+' with '-', '/' with '_', and strips trailing '=' padding.
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

// Generates the code challenge by hashing the code verifier with SHA-256 and base64url-encoding the result.
// This is the S256 code challenge method defined in RFC 7636.
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
      localStorage.setItem(PKCE_VERIFIER_STORAGE_KEY, codeVerifier);

      const authBase = getAuthBase();
      const clientId = OAUTH_CLIENT_ID;
      const redirectUri = isElectron ? 'bella-app://callback' : `${window.location.origin}/callback`;
      const state = Math.random().toString(STATE_RANDOM_RADIX).substring(STATE_SUBSTRING_START, STATE_SUBSTRING_END);

      // Build OAuth 2.1 authorization URL
      const authorizeUrl = `${authBase}/oauth/authorize?client_id=${encodeURIComponent(
        clientId
      )}&redirect_uri=${encodeURIComponent(
        redirectUri
      )}&response_type=code&code_challenge=${encodeURIComponent(
        codeChallenge
      )}&code_challenge_method=S256&state=${encodeURIComponent(
        state
      )}&scope=openid%20profile%20email%20bella-ems%3Aread%20bella-ems%3Awrite%20bella-chat%3Aread%20bella-chat%3Awrite`;

      // For Electron desktop apps, open the IdP Login Consent Page in the external system browser.
      // For web/browser applications, redirect the active browser tab.
      if (isElectron) {
        window.open(authorizeUrl);
      } else {
        window.location.href = authorizeUrl;
      }
    } catch (err: unknown) {
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
            
            <Box sx={{ pt: 2, textAlign: 'center' }}>
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', fontSize: '0.75rem', fontWeight: 500 }}>
                v{APP_VERSION} • {COPYRIGHT_INFO}
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Zoom>
    </Box>
  );
};

export default Login;
