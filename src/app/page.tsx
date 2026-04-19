import Link from "next/link";
import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { getTenantsForUser } from "@/lib/tenant";

export default async function HomePage() {
  const session = await auth();

  if (!session?.user) {
    return (
      <main className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-br from-indigo-50 to-white px-4">
        <div className="text-center max-w-2xl">
          <div className="mb-8 flex justify-center">
            <div className="h-16 w-16 rounded-2xl bg-indigo-600 flex items-center justify-center">
              <svg className="h-8 w-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
          </div>
          <h1 className="text-5xl font-bold text-gray-900 mb-4">MultiTenant App</h1>
          <p className="text-xl text-gray-500 mb-10">
            A secure, multi-tenant SaaS platform. Sign in with Google, Apple, GitHub, or your email to get started.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/login"
              className="inline-flex items-center justify-center px-8 py-3 rounded-lg bg-indigo-600 text-white font-semibold hover:bg-indigo-700 transition-colors"
            >
              Get started
            </Link>
            <Link
              href="/login"
              className="inline-flex items-center justify-center px-8 py-3 rounded-lg border border-gray-200 text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
            >
              Sign in
            </Link>
          </div>
        </div>

        <div className="mt-20 grid grid-cols-1 sm:grid-cols-3 gap-8 max-w-3xl w-full text-center">
          {[
            { title: "Multi-Tenancy", desc: "Fully isolated workspaces for every team or organisation." },
            { title: "OAuth + Email", desc: "Sign in with Google, Apple, GitHub, or a magic link." },
            { title: "Role-Based Access", desc: "Owners, admins, and members with fine-grained control." },
          ].map((f) => (
            <div key={f.title} className="p-6 rounded-xl border border-gray-100 bg-white shadow-sm">
              <h3 className="font-semibold text-gray-900 mb-2">{f.title}</h3>
              <p className="text-gray-500 text-sm">{f.desc}</p>
            </div>
          ))}
        </div>
      </main>
    );
  }

  const memberships = await getTenantsForUser(session.user.id!);
  if (memberships.length > 0) {
    redirect(`/${memberships[0].tenant.slug}/dashboard`);
  }

  redirect("/onboarding");
}
