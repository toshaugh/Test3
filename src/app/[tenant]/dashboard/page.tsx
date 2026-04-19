import { requireTenantAccess } from "@/lib/tenant";
import { prisma } from "@/lib/db";
import { notFound } from "next/navigation";

export async function generateMetadata({ params }: { params: { tenant: string } }) {
  return { title: `Dashboard — ${params.tenant}` };
}

export default async function DashboardPage({
  params,
}: {
  params: { tenant: string };
}) {
  const membership = await requireTenantAccess(params.tenant);
  if (!membership) notFound();

  const [memberCount, inviteCount] = await Promise.all([
    prisma.tenantUser.count({ where: { tenantId: membership.tenant.id } }),
    prisma.tenantInvite.count({ where: { tenantId: membership.tenant.id } }),
  ]);

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">{membership.tenant.name}</h1>
        <p className="text-gray-500 text-sm mt-1">
          Workspace dashboard · <span className="capitalize">{membership.tenant.plan.toLowerCase()}</span> plan
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <StatCard label="Team members" value={memberCount} />
        <StatCard label="Pending invites" value={inviteCount} />
        <StatCard label="Your role" value={membership.role} />
      </div>

      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h2 className="font-semibold text-gray-900 mb-4">Workspace info</h2>
        <dl className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
          <div>
            <dt className="text-gray-500">Workspace ID</dt>
            <dd className="font-mono text-gray-800 mt-1">{membership.tenant.id}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Slug</dt>
            <dd className="font-mono text-gray-800 mt-1">{membership.tenant.slug}</dd>
          </div>
          <div>
            <dt className="text-gray-500">Created</dt>
            <dd className="text-gray-800 mt-1">
              {new Intl.DateTimeFormat("en-US", { dateStyle: "medium" }).format(
                new Date(membership.tenant.createdAt)
              )}
            </dd>
          </div>
          <div>
            <dt className="text-gray-500">Custom domain</dt>
            <dd className="text-gray-800 mt-1">{membership.tenant.domain ?? "—"}</dd>
          </div>
        </dl>
      </div>
    </div>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
    </div>
  );
}
