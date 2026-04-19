# Multi-Tenant OAuth App

A production-ready multi-tenant SaaS starter built with **Next.js 14**, **NextAuth v5**, **Prisma**, and **Tailwind CSS**. Deploy to **Railway** in minutes.

## Features

- **Multi-tenancy** — path-based tenant isolation (`/:tenant/dashboard`)
- **OAuth providers** — Google, Apple, GitHub, Email (magic link)
- **Role-based access** — Owner / Admin / Member per workspace
- **Database** — PostgreSQL via Prisma ORM
- **Railway-ready** — `railway.toml` with health check, migrations on boot

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/toshaugh/Test3.git
cd Test3
npm install
```

### 2. Configure environment

```bash
cp .env.example .env
# Fill in all values in .env
```

### 3. Set up the database

```bash
npm run db:push        # Push schema (dev)
# or
npm run db:migrate     # Run migrations (prod)
```

### 4. Run locally

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Deploy to Railway

1. Create a new project on [Railway](https://railway.app).
2. Add a **PostgreSQL** plugin — `DATABASE_URL` is injected automatically.
3. Set all environment variables from `.env.example` in the Railway dashboard.
4. Push this repo — Railway picks up `railway.toml` and builds automatically.

> **Apple Sign In** requires a paid Apple Developer account and a real domain with HTTPS.

## Project Structure

```
src/
├── app/
│   ├── [tenant]/         # Tenant-scoped pages (dashboard, settings)
│   ├── api/
│   │   ├── auth/         # NextAuth route handler
│   │   ├── health/       # Railway health check
│   │   └── tenants/      # Workspace creation API
│   ├── login/            # Sign-in page
│   ├── onboarding/       # New-user workspace creation
│   └── page.tsx          # Marketing home / redirect
├── components/
│   ├── auth/             # LoginForm (OAuth + email)
│   ├── layout/           # TenantNav
│   └── onboarding/       # OnboardingForm
├── lib/
│   ├── auth.ts           # NextAuth config
│   ├── db.ts             # Prisma singleton
│   └── tenant.ts         # Tenant helpers
└── middleware.ts          # Auth gate for all routes
prisma/
└── schema.prisma          # DB schema (User, Tenant, TenantUser, …)
```

## OAuth Setup

### Google
1. [Create OAuth credentials](https://console.cloud.google.com/apis/credentials)
2. Add `http://localhost:3000/api/auth/callback/google` as an authorised redirect URI

### GitHub
1. [Register a new OAuth app](https://github.com/settings/applications/new)
2. Set callback URL to `http://localhost:3000/api/auth/callback/github`

### Apple
1. Create a Services ID in the [Apple Developer portal](https://developer.apple.com)
2. Generate a client secret JWT — see the [Auth.js Apple guide](https://authjs.dev/reference/core/providers/apple)

### Email (magic links)
Any SMTP provider works. For local dev, use [Mailhog](https://github.com/mailhog/MailHog) or [Resend](https://resend.com).
