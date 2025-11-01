# Deploying to Vercel (tinko.in)

## 1) Push to GitHub

- Repo: https://github.com/stealthorga-crypto/Stealth-Reecovery (branch: main)

## 2) Create Vercel Project

- Import the repo.
- Framework preset: Next.js (defaults OK).

## 3) Set Environment Variables (Project → Settings → Environment Variables → Production)

- NEXT_PUBLIC_API_URL = https://api.tinko.in
- NEXTAUTH_URL = https://www.tinko.in
- NEXTAUTH_SECRET = fWYfKw-SC4IuVYB-w-5jddzavI3IxGyV7vBBu0nzawM2eIoaVXjDXD0WG1NGkYPs

Re-deploy after saving envs.

## 4) Add Domains (Project → Settings → Domains)

- Add: www.tinko.in (primary)
- Add: tinko.in (apex)
  Vercel will show DNS instructions:
- On Cloudflare, create:
  - CNAME www -> cname.vercel-dns.com
  - Apex (tinko.in) -> follow Vercel’s A/ALIAS instructions (or set CNAME flattening if supported).

Wait for DNS to propagate; Vercel will issue TLS automatically.

## 5) Verify routes

- https://www.tinko.in/ (homepage)
- https://www.tinko.in/auth/signin (auth page)
- https://www.tinko.in/dashboard (logged out → redirects to /auth/signin)
- Sign in → lands on /dashboard

## 6) Backend requirements

- https://api.tinko.in must be publicly reachable.
- CORS on the backend must allow:
  - https://www.tinko.in
  - https://tinko.in (if apex used)

## 7) Optional

- `vercel.json` already redirects apex → www (preserves path & query).
- To force HTTPS-only on backend, enable HSTS on the API host.
