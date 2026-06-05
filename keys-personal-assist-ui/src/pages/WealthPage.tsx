import { useState } from 'react';
import { Box, Container, Typography, Tab, Tabs } from '@mui/material';
import AssetsTab from '@/components/wealth/AssetsTab';

export default function WealthPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [assetCount, setAssetCount] = useState<number | null>(null);

  return (
    <Box
      sx={{
        flexGrow: 1,
        bgcolor: 'background.default',
        py: 4,
        px: { xs: 2, md: 4 },
        backgroundImage: (theme) =>
          theme.palette.mode === 'dark'
            ? 'radial-gradient(circle at 10% 20%, rgba(30, 41, 59, 0.4) 0%, rgba(17, 24, 39, 0.95) 90%)'
            : 'none',
        transition: 'background-color 0.3s ease',
      }}
    >
      <Container maxWidth="xl">
        {/* Page Header */}
        <Box sx={{ mb: 2, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography
              variant="h4"
              sx={{
                fontWeight: 700,
                fontFamily: '"Space Grotesk", sans-serif',
                color: 'text.primary',
              }}
            >
              Assets
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ fontWeight: 500 }}>
              {assetCount !== null ? `${assetCount} assets` : 'Loading assets...'}
            </Typography>
          </Box>
        </Box>

        {/* Tab Selection */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={(_e, newValue) => setActiveTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
            sx={{
              '& .MuiTab-root': {
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                fontSize: '0.95rem',
                textTransform: 'none',
                minWidth: 100,
                px: 1,
                mr: 3,
              },
            }}
          >
            <Tab label="Assets" id="wealth-tab-assets" />
            <Tab label="Liabilities" disabled id="wealth-tab-liabilities" />
            <Tab label="Net Worth" disabled id="wealth-tab-networth" />
            <Tab label="Allocation" disabled id="wealth-tab-allocation" />
          </Tabs>
        </Box>

        {/* Tab Contents */}
        {activeTab === 0 && <AssetsTab onAssetsLoad={setAssetCount} />}
      </Container>
    </Box>
  );
}
