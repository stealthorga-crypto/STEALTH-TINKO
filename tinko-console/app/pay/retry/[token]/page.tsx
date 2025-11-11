import { RetryTokenPageClient } from "./page-client";

// Generate static params for build time
export async function generateStaticParams() {
  return [
    { token: 'placeholder-token' }
  ];
}

export default function RetryTokenPage({ params }: { params: { token: string } }) {
  return <RetryTokenPageClient />;
}
