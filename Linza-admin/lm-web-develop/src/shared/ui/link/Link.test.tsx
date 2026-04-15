import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Link from "./index";

describe("Link", () => {
  it("href work", () => {
    const tree = render(
      <Link href="http://www.facebook.com" target="_self">
        Facebook
      </Link>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("target work", () => {
    const tree = render(
      <Link href="/" target="_blank">
        Facebook
      </Link>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("className work", () => {
    const tree = render(
      <Link href="/" className="default" target="_parent">
        Main
      </Link>,
    );
    expect(tree).toMatchSnapshot();
  });
});
