import { notFound, redirect } from "next/navigation";
import { requireTenantAccess } from "@/lib/tenant";
import { TenantNav } from "@/components/layout/TenantNav";
import { auth } from "@/lib/auth";

export default async function TenantLayout({
  children,
  params,
}: {
  children: React.ReactNode;
  params: { tenant: string };
}) {
  const session = await auth();
  if (!session?.user) redirect(`/login?callbackUrl=/${params.tenant}/dashboard`);

  const membership = await requireTenantAccess(params.tenant);
  if (!membership) notFound();

  return (
    <div className="min-h-screen bg-gray-50">
      <TenantNav
        tenant={membership.tenant}
        user={session.user}
        role={membership.role}
      />
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
