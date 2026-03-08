// In-memory JWT token storage — secure default (no XSS via localStorage)
// Token is lost on page refresh; user must re-login.

let token: string | null = null;

export function getToken(): string | null {
  return token;
}

export function setToken(newToken: string): void {
  token = newToken;
}

export function clearToken(): void {
  token = null;
}
