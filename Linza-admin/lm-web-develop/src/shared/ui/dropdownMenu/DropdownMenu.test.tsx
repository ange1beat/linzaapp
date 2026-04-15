import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Dropdown from "./index";

describe("Dropdown", () => {
  it("View default", () => {
    const tree = render(
      <Dropdown
        items={[
          {
            text: <div>123</div>,
            theme: "normal",
          },
          {
            text: <div>123</div>,
            theme: "danger",
          },
          {
            text: <div>123</div>,
            theme: "danger",
            disabled: true,
          },
        ]}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Double nesting", () => {
    const tree = render(
      <Dropdown
        items={[
          {
            text: <div>123</div>,
            theme: "normal",
          },
          {
            text: <div>123</div>,
            theme: "danger",
            items: [
              {
                text: <div>123</div>,
                theme: "normal",
                action: () => {},
              },
              {
                text: <div>123</div>,
                theme: "normal",
                action: () => {},
              },
            ],
          },
          {
            text: <div>123</div>,
            theme: "danger",
            disabled: true,
          },
        ]}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Triple nesting", () => {
    const tree = render(
      <Dropdown
        items={[
          {
            text: <div>123</div>,
            theme: "normal",
          },
          {
            text: <div>123</div>,
            theme: "danger",
            items: [
              {
                text: <div>Some</div>,
                action: () => {},
                items: [
                  {
                    action: () => {},
                    text: <div>Important</div>,
                  },
                  {
                    text: <div>Favorite</div>,
                    action: () => {},
                  },
                ],
              },
            ],
          },
          {
            text: <div>123</div>,
            theme: "danger",
            disabled: true,
          },
        ]}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
