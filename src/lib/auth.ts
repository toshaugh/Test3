import NextAuth from "next-auth";
import { PrismaAdapter } from "@auth/prisma-adapter";
import Google from "next-auth/providers/google";
import Apple from "next-auth/providers/apple";
import GitHub from "next-auth/providers/github";
import Nodemailer from "next-auth/providers/nodemailer";
import { prisma } from "@/lib/db";

export const { handlers, signIn, signOut, auth } = NextAuth({
  adapter: PrismaAdapter(prisma),
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
      allowDangerousEmailAccountLinking: true,
    }),
    Apple({
      clientId: process.env.APPLE_ID!,
      clientSecret: process.env.APPLE_SECRET!,
    }),
    GitHub({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
      allowDangerousEmailAccountLinking: true,
    }),
    Nodemailer({
      server: {
        host: process.env.EMAIL_SERVER_HOST,
        port: Number(process.env.EMAIL_SERVER_PORT ?? 587),
        auth: {
          user: process.env.EMAIL_SERVER_USER,
          pass: process.env.EMAIL_SERVER_PASSWORD,
        },
      },
      from: process.env.EMAIL_FROM,
    }),
  ],
  pages: {
    signIn: "/login",
    verifyRequest: "/login?verify=1",
    error: "/login",
  },
  callbacks: {
    async session({ session, user }) {
      if (session.user) {
        session.user.id = user.id;
        const tenantMemberships = await prisma.tenantUser.findMany({
          where: { userId: user.id },
          include: { tenant: true },
        });
        (session.user as typeof session.user & { tenants: unknown[] }).tenants =
          tenantMemberships.map((m) => ({
            id: m.tenant.id,
            name: m.tenant.name,
            slug: m.tenant.slug,
            role: m.role,
          }));
      }
      return session;
    },
  },
  events: {
    async createUser({ user }) {
      // Auto-create a personal tenant when a new user signs up
      if (user.email) {
        const slug = user.email
          .split("@")[0]
          .toLowerCase()
          .replace(/[^a-z0-9]/g, "-")
          .slice(0, 30);
        const uniqueSlug = `${slug}-${Date.now().toString(36)}`;
        const tenant = await prisma.tenant.create({
          data: {
            name: user.name ?? user.email.split("@")[0],
            slug: uniqueSlug,
          },
        });
        await prisma.tenantUser.create({
          data: {
            userId: user.id!,
            tenantId: tenant.id,
            role: "OWNER",
          },
        });
      }
    },
  },
  session: { strategy: "database" },
  trustHost: true,
});
