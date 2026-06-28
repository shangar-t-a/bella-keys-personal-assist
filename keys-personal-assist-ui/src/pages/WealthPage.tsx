import { useState } from 'react';
import { Box, Container, Typography, Tab, Tabs } from '@mui/material';
import AssetsTab from '@/components/wealth/AssetsTab';
import LiabilitiesTab from '@/components/wealth/LiabilitiesTab';
import NetWorthTab from '@/components/wealth/NetWorthTab';
import AllocationTab from '@/components/wealth/AllocationTab';

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
    if (activeTab === 2) {
      return 'Portfolio net value analysis';
    }
    if (activeTab === 3) {
      return 'Portfolio distribution details';
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
          >
            <Tab label="Assets" id="wealth-tab-assets" value={0} />
            <Tab label="Liabilities" id="wealth-tab-liabilities" value={1} />
            <Tab label="Net Worth" id="wealth-tab-networth" value={2} />
            <Tab label="Allocation" id="wealth-tab-allocation" value={3} />
          </Tabs>
        </Box>

        {/* Tab Contents */}
        {activeTab === 0 && <AssetsTab onAssetsLoad={setAssetCount} />}
        {activeTab === 1 && <LiabilitiesTab onLiabilitiesLoad={setLiabilityCount} />}
        {activeTab === 2 && <NetWorthTab />}
        {activeTab === 3 && <AllocationTab />}
      </Container>
    </Box>
  );
}


