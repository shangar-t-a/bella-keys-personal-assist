import { Link as RouterLink } from 'react-router-dom';
import { Box, Typography, Container, Card, CardContent, Button, Grid } from '@mui/material';
import { TrendingUp, ArrowForward as ArrowRight, BarChart as BarChart3, AccountBalanceWallet } from '@mui/icons-material';

export default function DashboardPage() {
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
                background: 'linear-gradient(135deg, #1e5067 0%, #108cc6 100%)',
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
        <Grid container spacing={4} sx={{ maxWidth: '1200px', mx: 'auto' }}>
          {/* Spending Account Dashboard */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card
              sx={{
                height: '100%',
                borderRadius: 3,
                boxShadow: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 8,
                },
              }}
            >
              <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', gap: 3, mb: 4, flexGrow: 1 }}>
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
                    <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
                      Spending Summary
                    </Typography>
                    <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                      Track your daily expenses, view spending patterns, and manage your account balances.
                    </Typography>
                  </Box>
                </Box>
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
                    },
                  }}
                >
                  Open Dashboard
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Savings Fund Segregator Dashboard */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card
              sx={{
                height: '100%',
                borderRadius: 3,
                boxShadow: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 8,
                },
              }}
            >
              <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', gap: 3, mb: 4, flexGrow: 1 }}>
                  <Box
                    sx={{
                      width: 56,
                      height: 56,
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: 3,
                    }}
                  >
                    <AccountBalanceWallet sx={{ color: 'white', fontSize: 28 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
                      Savings Segregator
                    </Typography>
                    <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                      Segregate and track allocations in your savings accounts for goals, bills, and insurance.
                    </Typography>
                  </Box>
                </Box>
                <Button
                  component={RouterLink}
                  to="/dashboard/savings-fund-segregator"
                  variant="contained"
                  fullWidth
                  endIcon={<ArrowRight />}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    textTransform: 'none',
                    fontSize: '1rem',
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #8b5cf6 0%, #6366f1 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #7c3aed 0%, #4f46e5 100%)',
                    },
                  }}
                >
                  Manage Funds
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Monthly Planner Dashboard */}
          <Grid size={{ xs: 12, md: 4 }}>
            <Card
              sx={{
                height: '100%',
                borderRadius: 3,
                boxShadow: 3,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 8,
                },
              }}
            >
              <CardContent sx={{ p: 4, height: '100%', display: 'flex', flexDirection: 'column' }}>
                <Box sx={{ display: 'flex', gap: 3, mb: 4, flexGrow: 1 }}>
                  <Box
                    sx={{
                      width: 56,
                      height: 56,
                      borderRadius: 3,
                      background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      boxShadow: 3,
                    }}
                  >
                    <BarChart3 sx={{ color: 'white', fontSize: 28 }} />
                  </Box>
                  <Box sx={{ flex: 1 }}>
                    <Typography variant="h5" sx={{ fontWeight: 700, fontFamily: '"Space Grotesk", sans-serif', mb: 1 }}>
                      Monthly Planner
                    </Typography>
                    <Typography variant="body1" sx={{ color: 'text.secondary', lineHeight: 1.6 }}>
                      Plan your monthly budget, track recurring expenses, and visualize your financial allocation.
                    </Typography>
                  </Box>
                </Box>
                <Button
                  component={RouterLink}
                  to="/dashboard/monthly-planner"
                  variant="contained"
                  fullWidth
                  endIcon={<ArrowRight />}
                  sx={{
                    py: 1.5,
                    borderRadius: 2,
                    textTransform: 'none',
                    fontSize: '1rem',
                    fontWeight: 600,
                    background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
                    '&:hover': {
                      background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
                    },
                  }}
                >
                  Open Planner
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}
