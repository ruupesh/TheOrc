const TOKEN_STORAGE_KEY = "theorchestrator_access_token";

let token: string | null = null;

export function getToken(): string | null {
  if (token) return token;

  if (typeof window === "undefined") {
    return null;
  }

  token = window.localStorage.getItem(TOKEN_STORAGE_KEY);
  return token;
}

export function setToken(newToken: string): void {
  token = newToken;
  if (typeof window !== "undefined") {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
  }
}

export function clearToken(): void {
  token = null;
  if (typeof window !== "undefined") {
    window.localStorage.removeItem(TOKEN_STORAGE_KEY);
  }
}
