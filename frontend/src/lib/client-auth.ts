/**
 * Safe client-side JWT parsing.
 * Since we don't have jwt-decode, we use atob with base64url support.
 */
export interface JWTPayload {
  userId: string;
  email: string;
  role: "user" | "admin";
  name: string;
}

export function parseToken(token: string): JWTPayload | null {
  try {
    const base64Url = token.split(".")[1];
    if (!base64Url) return null;
    
    // Convert base64url to base64
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    
    // Decode with padding support
    const padLen = (4 - (base64.length % 4)) % 4;
    const paddedBase64 = base64 + "=".repeat(padLen);
    
    const jsonPayload = decodeURIComponent(
      atob(paddedBase64)
        .split("")
        .map((c) => "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2))
        .join("")
    );

    return JSON.parse(jsonPayload);
  } catch (err) {
    console.error("[parseToken Error]", err);
    return null;
  }
}

export function getAuthData(): JWTPayload | null {
  if (typeof document === "undefined") return null;
  
  const cookies = document.cookie.split(";");
  const tokenCookie = cookies.find((c) => c.trim().startsWith("auth_token="));
  if (!tokenCookie) return null;
  
  const token = tokenCookie.split("=")[1];
  return parseToken(token);
}
