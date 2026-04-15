import { vi } from "vitest";

global.ResizeObserver = class MockedResizeObserver {
  observe = vi.fn();

  unobserve = vi.fn();

  disconnect = vi.fn();
};

export {};
