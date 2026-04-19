"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { signOut } from "next-auth/react";
import Image from "next/image";
import type { Tenant, TenantSettings } from "@prisma/client";
import type { Session } from "next-auth";

type NavUser = Session["user"];

interface TenantNavProps {
  tenant: Tenant & { settings: TenantSettings | null };
  user: NavUser;
  role: string;
}

export function TenantNav({ tenant, user, role }: TenantNavProps) {
  const pathname = usePathname();

  const links = [
    { href: `/${tenant.slug}/dashboard`, label: "Dashboard" },
    ...(role !== "MEMBER"
      ? [{ href: `/${tenant.slug}/settings`, label: "Settings" }]
      : []),
  ];

  return (
    <nav className="bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex h-16 items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="flex items-center gap-2 font-bold text-gray-900">
              <div
                className="h-7 w-7 rounded-lg flex items-center justify-center text-white text-xs font-bold"
                style={{ backgroundColor: tenant.settings?.primaryColor ?? "#6366f1" }}
              >
                {tenant.name.charAt(0).toUpperCase()}
              </div>
              <span>{tenant.name}</span>
            </Link>

            <div className="hidden sm:flex items-center gap-1">
              {links.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
                    pathname === link.href
                      ? "bg-indigo-50 text-indigo-700"
                      : "text-gray-600 hover:text-gray-900 hover:bg-gray-50"
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className="hidden sm:block text-xs text-gray-500 capitalize">
              {role.toLowerCase()}
            </span>
            {user?.image && (
              <Image
                src={user.image}
                alt={user.name ?? ""}
                width={32}
                height={32}
                className="rounded-full"
              />
            )}
            {!user?.image && (
              <div className="h-8 w-8 rounded-full bg-indigo-100 flex items-center justify-center text-indigo-700 text-sm font-semibold">
                {(user?.name ?? user?.email ?? "?").charAt(0).toUpperCase()}
              </div>
            )}
            <button
              onClick={() => signOut({ callbackUrl: "/" })}
              className="text-sm text-gray-500 hover:text-gray-900 transition-colors"
            >
              Sign out
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
}
