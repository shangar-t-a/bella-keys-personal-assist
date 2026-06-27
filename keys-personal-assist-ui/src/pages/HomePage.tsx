import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Container } from '@mui/material';
import { ArrowForward as ArrowRight } from '@mui/icons-material';
import { getAvailableServices } from '@/config/features';

export default function HomePage() {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    const services = getAvailableServices();
    if (services.expenseManager) {
      navigate('/dashboard/accounts');
    } else if (services.bellaChat) {
      navigate('/chat');
    } else {
      navigate('/settings');
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        position: 'relative',
        overflow: 'hidden',
        background: (theme) =>
          theme.palette.mode === 'light'
            ? `linear-gradient(160deg, ${theme.palette.background.default} 0%, #e8f0f8 50%, #dce8f2 100%)`
            : `linear-gradient(160deg, ${theme.palette.background.default} 0%, #0f2434 50%, #132d42 100%)`,
      }}
    >
      {/* Subtle animated gradient orb */}
      <Box
        sx={{
          position: 'absolute',
          top: '10%',
          right: '15%',
          width: 500,
          height: 500,
          borderRadius: '50%',
          background: (theme) =>
            theme.palette.mode === 'light'
              ? 'radial-gradient(circle, rgba(26,143,196,0.08) 0%, transparent 70%)'
              : 'radial-gradient(circle, rgba(72,177,224,0.06) 0%, transparent 70%)',
          animation: 'orbFloat 8s ease-in-out infinite',
          '@keyframes orbFloat': {
            '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
            '50%': { transform: 'translate(-30px, 20px) scale(1.05)' },
          },
          pointerEvents: 'none',
        }}
      />

      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: 14, position: 'relative', zIndex: 1 }}>
        <Box
          sx={{
            maxWidth: '780px',
            mx: 'auto',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            gap: 4,
            animation: 'slideIn 0.6s ease-out',
            '@keyframes slideIn': {
              '0%': { opacity: 0, transform: 'translateY(24px)' },
              '100%': { opacity: 1, transform: 'translateY(0)' },
            },
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2.5 }}>
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '3.75rem' },
                fontWeight: 700,
                fontFamily: '"Space Grotesk", sans-serif',
                background: (theme) =>
                  `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.info.main} 100%)`,
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.15,
                letterSpacing: '-0.02em',
              }}
            >
              Bella
            </Typography>

            <Typography
              variant="h2"
              sx={{
                fontSize: { xs: '1.4rem', md: '1.85rem' },
                fontWeight: 600,
                fontFamily: '"Space Grotesk", sans-serif',
                color: 'text.primary',
                letterSpacing: '-0.01em',
              }}
            >
              Keys' Personal Assistant
            </Typography>

            <Typography
              variant="h5"
              sx={{
                fontSize: { xs: '1.05rem', md: '1.15rem' },
                color: 'text.secondary',
                maxWidth: '560px',
                mx: 'auto',
                lineHeight: 1.7,
              }}
            >
              Manage your day, ask questions and more with your personal assistant.
            </Typography>
          </Box>

          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: 2,
              justifyContent: 'center',
              alignItems: 'center',
              pt: 1,
            }}
          >
            <Button
              onClick={handleGetStarted}
              variant="contained"
              size="large"
              endIcon={<ArrowRight />}
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.05rem',
                fontWeight: 600,
                textTransform: 'none',
                borderRadius: 2.5,
                background: (theme) =>
                  `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.info.main} 100%)`,
                '&:hover': {
                  background: (theme) =>
                    `linear-gradient(135deg, ${theme.palette.primary.dark} 0%, ${theme.palette.info.dark} 100%)`,
                  transform: 'translateY(-2px)',
                  boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
                },
                transition: 'all 250ms ease',
                '& .MuiButton-endIcon': {
                  transition: 'transform 250ms ease',
                },
                '&:hover .MuiButton-endIcon': {
                  transform: 'translateX(4px)',
                },
              }}
            >
              Get Started
            </Button>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}
