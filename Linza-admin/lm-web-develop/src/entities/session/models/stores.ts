import { create, useStore } from "zustand";
import { persist } from "zustand/middleware";

type SessionState = {
  accessToken: string;
  portalRoles: string[];
  activeRole: string | null;
  addToken: (accessToken: string) => void;
  setPortalContext: (roles: string[], activeRole: string | null) => void;
  delToken: () => void;
};

const sessionStore = create<SessionState>()(
  persist(
    (set) => ({
      accessToken: "",
      portalRoles: [],
      activeRole: null,
      addToken: (accessToken) => set({ accessToken }),
      setPortalContext: (portalRoles, activeRole) =>
        set({ portalRoles, activeRole }),
      delToken: () =>
        set({ accessToken: "", portalRoles: [], activeRole: null }),
    }),
    {
      name: "session",
    },
  ),
);

export const useAuth = () =>
  useStore(sessionStore, (state) => !!state.accessToken);

export const usePortalRoles = () =>
  useStore(sessionStore, (state) => state.portalRoles);

export const useActiveRole = () =>
  useStore(sessionStore, (state) => state.activeRole);

export const getTokens = () => ({
  accessToken: sessionStore.getState().accessToken,
});

export const getPortalContext = () => ({
  portalRoles: sessionStore.getState().portalRoles,
  activeRole: sessionStore.getState().activeRole,
});

export const addToken = (accessToken: string) =>
  sessionStore.getState().addToken(accessToken);

export const setPortalContext = (roles: string[], activeRole: string | null) =>
  sessionStore.getState().setPortalContext(roles, activeRole);

export const delToken = () => sessionStore.getState().delToken();
