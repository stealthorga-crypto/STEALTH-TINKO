const en = {
  nav: {
    dashboard: "Dashboard",
    rules: "Rules",
    templates: "Templates",
    settings: "Settings",
    developer: "Developer",
    help: "Help",
  },
  help: {
    title: "Help & Guides",
    onboarding: {
      title: "Onboarding",
      stripe: "Verify your Stripe setup via Developer > Stripe Ping, then set a Retry Policy in Settings.",
    },
    retryPolicy: {
      title: "Retry Policy",
      desc: "Configure channels and schedule under Settings > Retry Policy. Keep one active policy per organization.",
    },
    troubleshooting: {
      title: "Troubleshooting",
      items: [
        "Notifications not sending? Verify SMTP and Redis are reachable.",
        "Checkout not redirecting? Check STRIPE_SECRET_KEY and network console.",
        "Webhooks failing? Ensure STRIPE_WEBHOOK_SECRET matches and the endpoint is accessible.",
      ],
    },
    links: {
      docs: "Documentation",
      support: "Contact Support",
    },
  },
};

export default en;
