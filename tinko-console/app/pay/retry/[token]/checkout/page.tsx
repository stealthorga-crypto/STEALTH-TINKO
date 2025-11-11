import { RetryTokenCheckoutClient } from './page-client';

// Required for static export with dynamic routes  
export async function generateStaticParams() {
  return [
    { token: 'placeholder-token' }
  ];
}

export default function RetryTokenCheckoutPage({ params }: { params: { token: string } }) {
  return <RetryTokenCheckoutClient />;
}
