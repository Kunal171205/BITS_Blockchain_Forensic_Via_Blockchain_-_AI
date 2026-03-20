import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const secret = new TextEncoder().encode(process.env.JWT_SECRET!);

interface JWTPayload {
  userId: string;
  email: string;
  role: "user" | "admin";
  name: string;
}

async function getPayload(token: string): Promise<JWTPayload | null> {
  try {
    const { payload } = await jwtVerify(token, secret);
    return payload as unknown as JWTPayload;
  } catch {
    return null;
  }
}

export async function middleware(req: NextRequest) {
  const token = req.cookies.get("auth_token")?.value;
  const { pathname } = req.nextUrl;

  const payload = token ? await getPayload(token) : null;

  if (pathname.startsWith("/admin") || pathname.startsWith("/dashboard")) {
    console.log("[MIDDLEWARE] Requesting:", pathname, "Payload role:", payload?.role);
  }

  // Protect /dashboard — must be logged in
  if (pathname.startsWith("/dashboard")) {
    if (!payload) {
      return NextResponse.redirect(new URL("/login", req.url));
    }
  }

  // Protect /admin — must be logged in AND be an admin
  if (pathname.startsWith("/admin")) {
    if (!payload) {
      return NextResponse.redirect(new URL("/login", req.url));
    }
    if (payload.role !== "admin") {
      return NextResponse.redirect(new URL("/dashboard", req.url));
    }
  }

  // If already logged in, redirect away from auth pages
  if ((pathname === "/login" || pathname === "/signup") && payload) {
    const dest = payload.role === "admin" ? "/admin" : "/dashboard";
    return NextResponse.redirect(new URL(dest, req.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/dashboard/:path*", "/admin/:path*", "/login", "/signup"],
};
