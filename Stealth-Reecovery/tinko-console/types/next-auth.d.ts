declare module "next-auth" {
  interface Session {
    orgId: string;
    role: "owner" | "admin" | "operator" | "viewer";
    user: {
      id: string;
      name?: string | null;
      email?: string | null;
      image?: string | null;
    };
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    orgId: string;
    role: "owner" | "admin" | "operator" | "viewer";
  }
}
