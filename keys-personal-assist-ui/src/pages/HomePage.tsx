import { useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Container } from '@mui/material';
import { ArrowForward as ArrowRight } from '@mui/icons-material';

export default function HomePage() {
  const navigate = useNavigate();

  const handleGetStarted = () => {
    navigate('/dashboard');
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: (theme) =>
          theme.palette.mode === 'light'
            ? 'linear-gradient(135deg, #f5f8fa 0%, #e0eef7 100%)'
            : 'linear-gradient(135deg, #111827 0%, #0b2d47 100%)',
      }}
    >
      {/* Hero Section */}
      <Container maxWidth="lg" sx={{ py: 12 }}>
        <Box
          sx={{
            maxWidth: '800px',
            mx: 'auto',
            textAlign: 'center',
            display: 'flex',
            flexDirection: 'column',
            gap: 4,
            animation: 'slideIn 0.6s ease-out',
            '@keyframes slideIn': {
              '0%': {
                opacity: 0,
                transform: 'translateY(20px)',
              },
              '100%': {
                opacity: 1,
                transform: 'translateY(0)',
              },
            },
          }}
        >
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Typography
              variant="h1"
              sx={{
                fontSize: { xs: '2.5rem', md: '4rem' },
                fontWeight: 700,
                fontFamily: '"Space Grotesk", sans-serif',
                background: 'linear-gradient(135deg, #1e5067 0%, #108cc6 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                lineHeight: 1.2,
              }}
            >
              Bella
            </Typography>

            <Typography
              variant="h2"
              sx={{
                fontSize: { xs: '1.5rem', md: '2rem' },
                fontWeight: 600,
                fontFamily: '"Space Grotesk", sans-serif',
                color: 'text.primary',
              }}
            >
              Keys' Personal Assistant
            </Typography>

            <Typography
              variant="h5"
              sx={{
                fontSize: { xs: '1.125rem', md: '1.25rem' },
                color: 'text.secondary',
                maxWidth: '600px',
                mx: 'auto',
                lineHeight: 1.6,
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
                fontSize: '1.125rem',
                fontWeight: 600,
                textTransform: 'none',
                borderRadius: 2,
                background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #059669 0%, #0891b2 100%)',
                  transform: 'translateY(-2px)',
                  boxShadow: 6,
                },
                transition: 'all 0.3s ease',
                '& .MuiButton-endIcon': {
                  transition: 'transform 0.3s ease',
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
