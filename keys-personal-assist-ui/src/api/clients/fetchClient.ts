import { getAuthBase } from '../config';

/**
 * Shared refresh promise to prevent concurrent duplicate refresh requests.
 */
let refreshPromise: Promise<{ access_token: string; refresh_token: string } | null> | null = null;

async function performRefresh(): Promise<{ access_token: string; refresh_token: string } | null> {
  const refreshToken = localStorage.getItem('refresh_token');
  if (!refreshToken) {
    return null;
  }
  try {
    const authBase = getAuthBase();
    const response = await fetch(`${authBase}/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });
    if (response.ok) {
      const data = await response.json();
      return data;
    }
  } catch (err) {
    console.error("Failed to perform token refresh:", err);
  }
  return null;
}

/**
 * Authorized fetch wrapper
 * Automatically appends the access token from localStorage, attempts silent refresh on 401, and redirects on failure.
 */
export async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  let token = localStorage.getItem('access_token');
  
  // Prepare headers
  const headers = new Headers(options.headers || {});
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  let response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    const isRefreshRequest = url.includes('/refresh');
    
    if (!isRefreshRequest) {
      if (!refreshPromise) {
        refreshPromise = performRefresh().then((data) => {
          refreshPromise = null;
          return data;
        });
      }
      
      const refreshResult = await refreshPromise;
      if (refreshResult) {
        const { access_token, refresh_token: new_refresh_token } = refreshResult;
        
        // Save new tokens
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('refresh_token', new_refresh_token);
        
        // Dispatch event to sync AuthContext state
        window.dispatchEvent(new CustomEvent('auth-refresh', { detail: { access_token } }));
        
        // Retry original request with the new access token
        const retryHeaders = new Headers(options.headers || {});
        retryHeaders.set('Authorization', `Bearer ${access_token}`);
        
        response = await fetch(url, {
          ...options,
          headers: retryHeaders,
        });
      } else {
        // Refresh failed (or no refresh token was present)
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        
        // Dispatch logout event to sync AuthContext state
        window.dispatchEvent(new Event('auth-logout'));
        
        // Redirect to login page unless we are already on it (handling both BrowserRouter and HashRouter paths)
        if (window.location.pathname !== '/login' && window.location.hash !== '#/login') {
          if (window.location.hash.startsWith('#/')) {
            window.location.hash = '#/login';
          } else {
            window.location.href = '/login';
          }
        }
      }
    }
  }

  return response;
}
