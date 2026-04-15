import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Filter from "./index";

const groups = [
  {
    label: "Status",
    name: "status",
    options: [
      { value: "works", label: "Works" },
      { value: "stopped", label: "Stopped" },
    ],
  },
  {
    label: "Type source",
    name: "type-source",
    options: [
      { value: "telegram", label: "Telegram" },
      { value: "web", label: "Web" },
      { value: "vk", label: "VK" },
      { value: "ok", label: "OK" },
    ],
  },
];

describe("Filter", () => {
  it("Default view", () => {
    const tree = render(
      <Filter
        value={{ name: ["works", "vk"] }}
        groups={groups}
        onChange={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
