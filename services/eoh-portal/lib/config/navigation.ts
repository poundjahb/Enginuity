export type NavItem = {
  label: string;
  href: string;
};

export const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard", href: "/dashboard" },
  { label: "Threads", href: "/threads" },
  { label: "Gatekeeper", href: "/gatekeeper" },
  { label: "Vault", href: "/vault" },
  { label: "Knowledge", href: "/knowledge" },
  { label: "Admin", href: "/admin" },
];
