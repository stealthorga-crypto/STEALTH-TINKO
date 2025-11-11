import { CheckoutRedirectPageClient } from "./page-client";

// Generate static params for build time
export async function generateStaticParams() {
  return [
    { ref: 'placeholder-ref' }
  ];
}

export default function CheckoutRedirectPage({ params }: { params: { ref: string } }) {
  return <CheckoutRedirectPageClient />;
}
