import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/providers/query-client-provider";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "Tinko Recovery",
  description: "B2B payment-failure recovery platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>
          <Providers>{children}</Providers>
        </AuthProvider>
      </body>
    </html>
  );
}

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  viewportFit: "cover",
};
