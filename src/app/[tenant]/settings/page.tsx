import { requireTenantAccess } from "@/lib/tenant";
import { notFound, redirect } from "next/navigation";

export const metadata = { title: "Settings" };

export default async function SettingsPage({
  params,
}: {
  params: { tenant: string };
}) {
  const membership = await requireTenantAccess(params.tenant);
  if (!membership) notFound();

  if (membership.role === "MEMBER") redirect(`/${params.tenant}/dashboard`);

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-8">Workspace settings</h1>

      <div className="bg-white rounded-xl border border-gray-200 divide-y divide-gray-100">
        <div className="p-6">
          <h2 className="font-semibold text-gray-900 mb-1">General</h2>
          <p className="text-sm text-gray-500 mb-4">Basic workspace information.</p>
          <dl className="text-sm space-y-3">
            <div className="flex justify-between">
              <dt className="text-gray-500">Name</dt>
              <dd className="font-medium text-gray-900">{membership.tenant.name}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Slug</dt>
              <dd className="font-mono text-gray-900">{membership.tenant.slug}</dd>
            </div>
            <div className="flex justify-between">
              <dt className="text-gray-500">Plan</dt>
              <dd className="capitalize font-medium text-gray-900">
                {membership.tenant.plan.toLowerCase()}
              </dd>
            </div>
          </dl>
        </div>

        <div className="p-6">
          <h2 className="font-semibold text-gray-900 mb-1">Danger zone</h2>
          <p className="text-sm text-gray-500 mb-4">
            These actions are irreversible. Please be certain.
          </p>
          <button
            disabled
            className="px-4 py-2 rounded-lg border border-red-200 text-red-600 text-sm font-medium opacity-50 cursor-not-allowed"
          >
            Delete workspace
          </button>
        </div>
      </div>
    </div>
  );
}
