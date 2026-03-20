import { NextRequest, NextResponse } from "next/server";
import { connectDB } from "@/lib/mongoose";
import User from "@/models/User";
import { signToken } from "@/lib/auth";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { name, email, password, role } = body;

    if (!name || !email || !password) {
      return NextResponse.json({ error: "All fields are required." }, { status: 400 });
    }
    if (password.length < 6) {
      return NextResponse.json({ error: "Password must be at least 6 characters." }, { status: 400 });
    }

    await connectDB();

    const existing = await User.findOne({ email: email.toLowerCase() });
    if (existing) {
      return NextResponse.json({ error: "Email already registered." }, { status: 409 });
    }

    const user = new User({
      name,
      email: email.toLowerCase(),
      password,
      role: role === "admin" ? "admin" : "user",
    });

    await user.save();

    const token = await signToken({
      userId: (user._id as { toString(): string }).toString(),
      email: user.email,
      role: user.role as "user" | "admin",
      name: user.name,
    });

    const response = NextResponse.json(
      { message: "Account created successfully.", role: user.role },
      { status: 201 }
    );

    response.cookies.set("auth_token", token, {
      httpOnly: false,
      secure: process.env.NODE_ENV === "production",
      sameSite: "lax",
      maxAge: 60 * 60 * 24 * 7,
      path: "/",
    });

    return response;
  } catch (err: unknown) {
    const message = err instanceof Error ? err.message : String(err);
    const stack = err instanceof Error ? err.stack : "";
    console.error("[SIGNUP ERROR]", message, stack);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
