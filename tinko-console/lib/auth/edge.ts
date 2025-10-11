// lib/auth/edge.ts
// Minimal, duplication-free helpers for reading auth/customer cookies in Edge middleware.

export function getCookie(headers: Headers, name: string): string | undefined {
  const raw = headers.get("cookie");
  if (!raw) return undefined;
  // Manual parse (Edge-safe)
  const pairs = raw.split(";").map((s) => s.trim());
  for (const p of pairs) {
    const i = p.indexOf("=");
    if (i === -1) continue;
    const k = p.slice(0, i);
    const v = p.slice(i + 1);
    if (k === name) return decodeURIComponent(v);
  }
  return undefined;
}

export function isAuthenticated(headers: Headers): boolean {
  // "1" means authenticated
  return getCookie(headers, "tinko_auth") === "1";
}

export function isCustomer(headers: Headers): boolean {
  // "1" means customer; "0" or undefined means not a customer
  return getCookie(headers, "tinko_customer") === "1";
}
