import React from 'react';
import { Box, Typography, Chip, Collapse } from '@mui/material';
import { AccountTree as TreeIcon, SmartToy as SubAgentIcon, CheckCircle as SuccessIcon, Error as ErrorIcon } from '@mui/icons-material';
import type { ThinkingStep } from '@/types/chat';

interface TaskExecutionTreeProps {
  steps: ThinkingStep[];
}

export const TaskExecutionTree: React.FC<TaskExecutionTreeProps> = ({ steps }) => {
  if (!steps || steps.length === 0) return null;

  return (
    <Box
      sx={{
        my: 1.5,
        p: 1.5,
        borderRadius: 2,
        bgcolor: (theme) => (theme.palette.mode === 'light' ? '#f0f4f8' : '#1e293b'),
        border: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
        <TreeIcon fontSize="small" color="primary" />
        <Typography variant="caption" sx={{ fontWeight: 700, textTransform: 'uppercase', letterSpacing: 0.5 }}>
          Deep Agent Execution Steps
        </Typography>
      </Box>

      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
        {steps.map((step, idx) => {
          const isSubAgent = step.isSubAgent || step.kind.startsWith('subagent');
          const isCall = step.kind.endsWith('call');
          const isResult = step.kind.endsWith('result');

          return (
            <Collapse key={step.id || idx} in={true}>
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1,
                  pl: isSubAgent ? 2 : 0,
                  borderLeft: isSubAgent ? '2px solid' : 'none',
                  borderColor: 'primary.main',
                }}
              >
                {isSubAgent && <SubAgentIcon fontSize="small" color="secondary" sx={{ mt: 0.3 }} />}
                <Box sx={{ flex: 1 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" sx={{ fontWeight: isSubAgent ? 600 : 400 }}>
                      {step.label}
                    </Typography>
                    {isSubAgent && <Chip size="small" label="Sub-Agent" color="secondary" variant="outlined" sx={{ height: 18, fontSize: '0.65rem' }} />}
                    {step.isError && <ErrorIcon fontSize="small" color="error" />}
                    {!step.isError && isResult && <SuccessIcon fontSize="small" color="success" />}
                  </Box>
                  {step.detail && isCall && (
                    <Typography variant="caption" sx={{ color: 'text.secondary', display: 'block', fontFamily: 'monospace' }}>
                      {step.detail}
                    </Typography>
                  )}
                </Box>
              </Box>
            </Collapse>
          );
        })}
      </Box>
    </Box>
  );
};
