import { useMemo, useState } from "react";

type MockOrganization = {
  id: string;
  name: string;
};

type MockUser = {
  id: string;
  name: string;
  email: string;
  image?: string;
};

type SessionStatus = "authenticated" | "unauthenticated" | "loading";

type MockSession = {
  user: MockUser;
  organizations: MockOrganization[];
  activeOrganizationId: string;
};

const mockSession: MockSession = {
  user: {
    id: "user_mock_1",
    name: "Jordan Merchant",
    email: "jordan@tinko.dev",
    image: "https://avatars.dicebear.com/api/initials/jordan.svg",
  },
  organizations: [
    { id: "org_tinko", name: "Tinko Retail" },
    { id: "org_demo", name: "Demo Retailers" },
  ],
  activeOrganizationId: "org_tinko",
};

export const useSession = () => {
  const [activeOrgId, setActiveOrgId] = useState(mockSession.activeOrganizationId);

  const data = useMemo(
    () => ({
      ...mockSession,
      activeOrganizationId: activeOrgId,
    }),
    [activeOrgId],
  );

  return {
    data,
    status: "authenticated" as SessionStatus,
    update: setActiveOrgId,
  };
};
