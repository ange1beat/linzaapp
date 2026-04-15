import React, { useCallback } from "react";

import { Select } from "@gravity-ui/uikit";

import { PORTAL_ROLES } from "@/shared/config";

import {
  addToken,
  setPortalContext,
  useActiveRole,
  usePortalRoles,
} from "@/entities/session";

import { switchPortalRole } from "../api/requests";

const ROLE_LABELS: Record<string, string> = {
  [PORTAL_ROLES.Administrator]: "Администратор",
  [PORTAL_ROLES.Operator]: "Оператор",
  [PORTAL_ROLES.Lawyer]: "Юрист",
  [PORTAL_ROLES.ChiefEditor]: "Главный редактор",
};

export function PortalRoleSwitcher() {
  const portalRoles = usePortalRoles();
  const activeRole = useActiveRole();

  const handleChange = useCallback(
    async (value: string[]) => {
      const newRole = value[0];
      if (!newRole || newRole === activeRole) return;

      try {
        const { access_token } = await switchPortalRole(newRole);
        addToken(access_token);
        setPortalContext(portalRoles, newRole);
      } catch {
        // Silently fail — token stays the same
      }
    },
    [activeRole, portalRoles],
  );

  if (portalRoles.length <= 1) return null;

  const options = portalRoles.map((role) => ({
    value: role,
    content: ROLE_LABELS[role] || role,
  }));

  return (
    <Select
      value={activeRole ? [activeRole] : []}
      options={options}
      onUpdate={handleChange}
      size="s"
      width="max"
    />
  );
}
