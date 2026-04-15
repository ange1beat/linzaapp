import { vi } from "vitest";

vi.mock("@tanstack/react-query", () => ({
  useMutation: () => ({
    isPending: false,
    isError: false,
    mutateAsync: vi.fn(() => new Promise(() => {})),
  }),
  useQuery: () => ({
    isPending: false,
    isError: false,
    data: null,
  }),
  QueryClient: vi.fn(),
}));

export {};
