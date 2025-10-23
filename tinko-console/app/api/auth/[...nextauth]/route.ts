import NextAuth from "next-auth";
import { authOptions } from "@/lib/auth/auth";

// Work around TS typing friction across versions
const handler = (NextAuth as unknown as (opts: any) => any)(authOptions);

export { handler as GET, handler as POST };
