import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { createTenant, slugify } from "@/lib/tenant";

export async function POST(req: NextRequest) {
  const session = await auth();
  if (!session?.user?.id) {
    return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  }

  const body = await req.json();
  const name = String(body.name ?? "").trim();
  if (!name || name.length < 2) {
    return NextResponse.json({ error: "Name must be at least 2 characters" }, { status: 400 });
  }

  const slug = slugify(name);
  if (!slug) {
    return NextResponse.json({ error: "Invalid workspace name" }, { status: 400 });
  }

  try {
    const tenant = await createTenant(name, slug, session.user.id);
    return NextResponse.json({ tenant }, { status: 201 });
  } catch (err) {
    const message = err instanceof Error ? err.message : "Failed to create workspace";
    return NextResponse.json({ error: message }, { status: 409 });
  }
}
