/**
 * Authorized fetch wrapper
 * Automatically appends the access token from localStorage and redirects to /login on 401 responses.
 */
export async function fetchWithAuth(url: string, options: RequestInit = {}): Promise<Response> {
  const token = localStorage.getItem('access_token');
  
  // Prepare headers
  const headers = new Headers(options.headers || {});
  if (token && !headers.has('Authorization')) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Session expired or invalid token
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    
    // Redirect to login page unless we are already on it
    if (window.location.pathname !== '/login') {
      window.location.href = '/login';
    }
  }

  return response;
}
