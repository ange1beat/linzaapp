import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import AuthResult from "./index";

describe("AuthResult", () => {
  it("Success window", () => {
    const tree = render(
      <AuthResult
        title="Successfully"
        header={<h1>Header!</h1>}
        isSuccess
        message="message"
        link="/login"
        linkText="Go to login page"
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Unsuccess window", () => {
    const tree = render(
      <AuthResult
        title="Invitation expired"
        header={<h1>Header!</h1>}
        isSuccess={false}
        message="message"
        link="/login"
        linkText="Go to login page"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
