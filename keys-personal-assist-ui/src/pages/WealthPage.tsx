import { useState } from 'react';
import { Box, Container, Typography, Tab, Tabs } from '@mui/material';
import AssetsTab from '@/components/wealth/AssetsTab';
import LiabilitiesTab from '@/components/wealth/LiabilitiesTab';

export default function WealthPage() {
  const [activeTab, setActiveTab] = useState(0);
  const [assetCount, setAssetCount] = useState<number | null>(null);
  const [liabilityCount, setLiabilityCount] = useState<number | null>(null);

  const getSubheaderText = () => {
    if (activeTab === 0) {
      return assetCount !== null ? `${assetCount} assets tracked` : 'Loading…';
    }
    if (activeTab === 1) {
      return liabilityCount !== null ? `${liabilityCount} liabilities tracked` : 'Loading…';
    }
    return '';
  };

  return (
    <Box
      sx={{
        flexGrow: 1,
        bgcolor: 'background.default',
        py: 2.5,
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
        <Box sx={{ mb: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography
              variant="h5"
              sx={{
                fontWeight: 700,
                fontFamily: '"Space Grotesk", sans-serif',
                color: 'text.primary',
                lineHeight: 1.2,
              }}
            >
              Wealth Manager
            </Typography>
            <Typography variant="caption" color="text.secondary" sx={{ fontWeight: 500 }}>
              {getSubheaderText()}
            </Typography>
          </Box>
        </Box>

        {/* Tab Selection */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs
            value={activeTab}
            onChange={(_e, newValue) => setActiveTab(newValue)}
            indicatorColor="primary"
            textColor="primary"
            sx={{
              minHeight: 36,
              '& .MuiTab-root': {
                fontFamily: '"Space Grotesk", sans-serif',
                fontWeight: 600,
                fontSize: '0.875rem',
                textTransform: 'none',
                minWidth: 80,
                minHeight: 36,
                px: 0,
                mr: 3,
                py: 0.5,
              },
            }}
          >
            <Tab label="Assets" id="wealth-tab-assets" />
            <Tab label="Liabilities" id="wealth-tab-liabilities" />
            <Tab label="Net Worth" disabled id="wealth-tab-networth" />
            <Tab label="Allocation" disabled id="wealth-tab-allocation" />
          </Tabs>
        </Box>

        {/* Tab Contents */}
        {activeTab === 0 && <AssetsTab onAssetsLoad={setAssetCount} />}
        {activeTab === 1 && <LiabilitiesTab onLiabilitiesLoad={setLiabilityCount} />}
      </Container>
    </Box>
  );
}


