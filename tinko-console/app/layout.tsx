import type { Metadata, Viewport } from "next";
import "./globals.css";
import { Providers } from "@/components/providers/query-client-provider";

export const metadata: Metadata = {
  title: "Tinko Recovery",
  description: "B2B payment-failure recovery platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
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
