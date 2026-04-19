import { auth } from "@/lib/auth";
import { redirect } from "next/navigation";
import { OnboardingForm } from "@/components/onboarding/OnboardingForm";

export const metadata = { title: "Create your workspace — MultiTenant App" };

export default async function OnboardingPage() {
  const session = await auth();
  if (!session?.user) redirect("/login");

  return (
    <main className="min-h-screen flex items-center justify-center bg-gradient-to-br from-indigo-50 to-white px-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Create your workspace</h1>
          <p className="text-gray-500 mt-1 text-sm">
            A workspace is a shared space for your team.
          </p>
        </div>
        <OnboardingForm userName={session.user.name ?? session.user.email ?? ""} />
      </div>
    </main>
  );
}
