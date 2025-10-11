import { withAuth } from "next-auth/middleware";

export default withAuth({
  pages: { signIn: "/auth/signin" },
});

export const config = {
  // protect console & root route (root is a page, but public content renders there)
  matcher: ["/", "/(console)(.*)"],
};
