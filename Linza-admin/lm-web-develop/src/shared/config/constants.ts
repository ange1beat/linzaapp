export const PAGE_SIZE = 10;
export const PAGE_SIZE_OPTIONS = [5, 10, 20];
export const AVATAR_MAX_SIZE = 300;
export const USER_ROLES = {
  User: "User",
  Supervisor: "Supervisor",
};

export const PORTAL_ROLES = {
  Administrator: "administrator",
  Operator: "operator",
  Lawyer: "lawyer",
  ChiefEditor: "chief_editor",
} as const;

export type PortalRole = (typeof PORTAL_ROLES)[keyof typeof PORTAL_ROLES];
