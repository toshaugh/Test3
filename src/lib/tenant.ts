import { prisma } from "@/lib/db";
import { auth } from "@/lib/auth";

export async function getTenantBySlug(slug: string) {
  return prisma.tenant.findUnique({
    where: { slug },
    include: { settings: true },
  });
}

export async function getTenantByDomain(domain: string) {
  return prisma.tenant.findUnique({
    where: { domain },
    include: { settings: true },
  });
}

export async function requireTenantAccess(tenantSlug: string) {
  const session = await auth();
  if (!session?.user?.id) return null;

  const membership = await prisma.tenantUser.findFirst({
    where: {
      userId: session.user.id,
      tenant: { slug: tenantSlug },
    },
    include: { tenant: { include: { settings: true } } },
  });

  return membership ?? null;
}

export async function createTenant(
  name: string,
  slug: string,
  ownerId: string
) {
  const existing = await prisma.tenant.findUnique({ where: { slug } });
  if (existing) throw new Error("Tenant slug already taken");

  const tenant = await prisma.tenant.create({
    data: {
      name,
      slug,
      settings: { create: {} },
      users: {
        create: { userId: ownerId, role: "OWNER" },
      },
    },
    include: { settings: true },
  });

  return tenant;
}

export async function getTenantsForUser(userId: string) {
  return prisma.tenantUser.findMany({
    where: { userId },
    include: { tenant: true },
    orderBy: { createdAt: "asc" },
  });
}

export function slugify(text: string): string {
  return text
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/[\s_-]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .slice(0, 48);
}
