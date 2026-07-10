import React, { useEffect, useRef } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';
import { useAuth } from '@/context/AuthContext';
import { getAuthBase } from '@/api/config';
import { toast } from 'sonner';
import { Box, CircularProgress, Typography } from '@mui/material';

const OAuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const exchanged = useRef(false);

  useEffect(() => {
    if (exchanged.current) return;
    exchanged.current = true;

    const exchangeCode = async () => {
      const code = searchParams.get('code');
      const codeVerifier = localStorage.getItem('pkce_code_verifier');

      if (!code) {
        toast.error('No authorization code found in URL.');
        navigate('/login');
        return;
      }

      if (!codeVerifier) {
        toast.error('PKCE code verifier not found in storage.');
        navigate('/login');
        return;
      }

      try {
        const authBase = getAuthBase();
        const response = await axios.post(`${authBase}/oauth/token`, {
          grant_type: 'authorization_code',
          code,
          client_id: 'keys-personal-assist-ui',
          redirect_uri: `${window.location.origin}/callback`,
          code_verifier: codeVerifier,
        });

        const { access_token } = response.data;
        login(access_token);

        // Clean up PKCE storage
        localStorage.removeItem('pkce_code_verifier');

        toast.success('SSO Authentication successful!');
        navigate('/');
      } catch (err: any) {
        const desc = err.response?.data?.detail?.error_description || err.message;
        toast.error(`Token exchange failed: ${desc}`);
        navigate('/login');
      }
    };

    exchangeCode();
  }, [searchParams, navigate, login]);

  return (
    <Box
      display="flex"
      flexDirection="column"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      gap={2}
    >
      <CircularProgress />
      <Typography variant="body1">Completing SSO login, please wait...</Typography>
    </Box>
  );
};

export default OAuthCallback;
