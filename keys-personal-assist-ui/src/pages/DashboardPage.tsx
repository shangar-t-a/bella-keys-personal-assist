import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Container, Card, CardContent, Button } from '@mui/material';
import { TrendingUp, ArrowForward as ArrowRight } from '@mui/icons-material';
import ModernHeader from '@/components/ModernHeader';

export default function DashboardPage() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        background: (theme) =>
          theme.palette.mode === 'light'
            ? 'linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%)'
            : 'linear-gradient(135deg, #1f2937 0%, #064e3b 100%)',
      }}
    >
      <ModernHeader />

      <Container maxWidth="lg" sx={{ py: 12 }}>
        {/* Header Section */}
        <Box sx={{ textAlign: 'center', maxWidth: '800px', mx: 'auto', mb: 12 }}>
          <Typography
            variant="h2"
            sx={{
              fontSize: { xs: '2rem', md: '3rem' },
              fontWeight: 700,
              fontFamily: '"Space Grotesk", sans-serif',
              mb: 3,
            }}
          >
            Your{' '}
            <Box
              component="span"
              sx={{
                background: 'linear-gradient(135deg, #10b981 0%, #06b6d4 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
              }}
            >
              Dashboards
            </Box>
          </Typography>
          <Typography variant="h5" sx={{ color: 'text.secondary', fontSize: { xs: '1rem', md: '1.25rem' } }}>
            Access your personal management tools and insights.
          </Typography>
        </Box>

        {/* Dashboard Grid */}
        <Box sx={{ maxWidth: '700px', mx: 'auto' }}>
          {/* Spending Account Dashboard */}
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: 3,
              transition: 'all 0.3s ease',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 8,
              },
            }}
          >
            <CardContent sx={{ p: 4 }}>
              {/* Icon and Title */}
              <Box sx={{ display: 'flex', gap: 3, mb: 4 }}>
                <Box
                  sx={{
                    width: 56,
                    height: 56,
                    borderRadius: 3,
                    background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    boxShadow: 3,
                  }}
                >
                  <TrendingUp sx={{ color: 'white', fontSize: 28 }} />
                </Box>
                <Box sx={{ flex: 1 }}>
                  <Typography
                    variant="h5"
                    sx={{
                      fontWeight: 700,
                      fontFamily: '"Space Grotesk", sans-serif',
                      mb: 1,
                    }}
                  >
                    Spending Account Summary
                  </Typography>
                  <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                    Track your expenses, view spending patterns, and manage your budget with detailed analytics.
                  </Typography>
                </Box>
              </Box>

              {/* Action Button */}
              <Button
                component={RouterLink}
                to="/dashboard/spending-account-summary"
                variant="contained"
                fullWidth
                endIcon={<ArrowRight />}
                sx={{
                  py: 1.5,
                  borderRadius: 2,
                  textTransform: 'none',
                  fontSize: '1rem',
                  fontWeight: 600,
                  background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
                  '&:hover': {
                    background: 'linear-gradient(135deg, #059669 0%, #047857 100%)',
                    transform: 'translateY(-2px)',
                    boxShadow: 4,
                  },
                  transition: 'all 0.2s ease',
                  '& .MuiButton-endIcon': {
                    transition: 'transform 0.3s ease',
                  },
                  '&:hover .MuiButton-endIcon': {
                    transform: 'translateX(4px)',
                  },
                }}
              >
                Open Dashboard
              </Button>
            </CardContent>
          </Card>
        </Box>
      </Container>
    </Box>
  );
}
