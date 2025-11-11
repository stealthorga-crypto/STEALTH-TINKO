import { RetryTokenCheckoutClient } from './page-client';

// Required for static export with dynamic routes  
export async function generateStaticParams() {
  // Return empty array to generate at request time
  return [];
}

export default function RetryTokenCheckoutPage({ params }: { params: { token: string } }) {
  return <RetryTokenCheckoutClient params={params} />;
}
