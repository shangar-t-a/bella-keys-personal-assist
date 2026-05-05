// Service health checking utilities
export interface ServiceHealth {
  name: string;
  url: string;
  isHealthy: boolean;
  lastChecked: Date;
  error?: string;
}

const serviceUrls = {
  expenseManager: 'http://localhost:8000/health',
  bellaChat: 'http://localhost:5000/health',
};

// Check if a service is healthy
export async function checkServiceHealth(serviceName: keyof typeof serviceUrls): Promise<ServiceHealth> {
  const url = serviceUrls[serviceName];
  const health: ServiceHealth = {
    name: serviceName,
    url,
    isHealthy: false,
    lastChecked: new Date(),
  };

  try {
    const response = await fetch(url, { 
      method: 'GET',
      signal: AbortSignal.timeout(5000) // 5 second timeout
    });
    
    health.isHealthy = response.ok;
    if (!response.ok) {
      health.error = `HTTP ${response.status}: ${response.statusText}`;
    }
  } catch (error) {
    health.error = error instanceof Error ? error.message : 'Unknown error';
    health.isHealthy = false;
  }

  return health;
}

// Check all services health
export async function checkAllServicesHealth(): Promise<Record<string, ServiceHealth>> {
  const results: Record<string, ServiceHealth> = {};
  
  for (const [serviceName, url] of Object.entries(serviceUrls)) {
    try {
      results[serviceName] = await checkServiceHealth(serviceName as keyof typeof serviceUrls);
    } catch (error) {
      results[serviceName] = {
        name: serviceName,
        url,
        isHealthy: false,
        lastChecked: new Date(),
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  return results;
}

// Get service health with caching
const healthCache = new Map<string, { health: ServiceHealth; timestamp: number }>();
const CACHE_DURATION = 30000; // 30 seconds

export async function getServiceHealth(serviceName: keyof typeof serviceUrls): Promise<ServiceHealth> {
  const cacheKey = serviceName;
  const cached = healthCache.get(cacheKey);
  const now = Date.now();

  // Return cached result if still valid
  if (cached && (now - cached.timestamp) < CACHE_DURATION) {
    return cached.health;
  }

  // Check health and cache result
  const health = await checkServiceHealth(serviceName);
  healthCache.set(cacheKey, { health, timestamp: now });

  return health;
}
