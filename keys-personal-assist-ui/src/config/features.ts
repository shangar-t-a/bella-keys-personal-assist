// Feature flags for optional services
export interface FeatureFlags {
  bellaChatEnabled: boolean;
  expenseManagerEnabled: boolean;
  bellaChatObservabilityEnabled: boolean; // Sub-option for chat service
}

// Default feature flags - all services enabled
const defaultFlags: FeatureFlags = {
  bellaChatEnabled: true,
  expenseManagerEnabled: true,
  bellaChatObservabilityEnabled: false, // Phoenix, Arize, etc.
};

// Parse feature flags from environment variables
export function getFeatureFlags(): FeatureFlags {
  return {
    bellaChatEnabled: parseEnvFlag('VITE_BELLA_CHAT_ENABLED', defaultFlags.bellaChatEnabled),
    expenseManagerEnabled: parseEnvFlag('VITE_EXPENSE_MANAGER_ENABLED', defaultFlags.expenseManagerEnabled),
    bellaChatObservabilityEnabled: parseEnvFlag('VITE_BELLA_CHAT_OBSERVABILITY_ENABLED', defaultFlags.bellaChatObservabilityEnabled),
  };
}

// Helper to parse boolean environment variables
function parseEnvFlag(key: string, defaultValue: boolean): boolean {
  const value = import.meta.env[key];
  if (value === undefined) return defaultValue;
  return value === 'true' || value === '1';
}

// Check if a service is enabled
export function isServiceEnabled(service: keyof FeatureFlags): boolean {
  const flags = getFeatureFlags();
  return flags[service];
}

// Get available services for UI
export function getAvailableServices() {
  const flags = getFeatureFlags();
  return {
    bellaChat: flags.bellaChatEnabled,
    expenseManager: flags.expenseManagerEnabled,
    bellaChatObservability: flags.bellaChatEnabled && flags.bellaChatObservabilityEnabled,
  };
}
