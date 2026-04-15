import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import UserModalEntity from "./index";

describe("UserModalEntity", () => {
  it("View default", () => {
    const tree = render(
      <UserModalEntity
        isLoad={false}
        email="test@mail.ru"
        avatar="https://fastly.picsum.photos/id/237/200/300.jpg?hmac=TmmQSbShHz9CdQm0NkEjx1Dyh_Y984R9LpNrpvH2D_U"
        firstName="Test"
        lastName="User"
        onOpenProfile={() => {}}
        onLogout={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Without avatar", () => {
    const tree = render(
      <UserModalEntity
        isLoad={false}
        email="test@mail.ru"
        firstName="Test"
        lastName="User"
        onOpenProfile={() => {}}
        onLogout={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Overflow", () => {
    const tree = render(
      <UserModalEntity
        isLoad={false}
        email={"wjdajwdhawhdawjhduawhduawhduawhduawhud@nauk.ru"}
        firstName={"ohmygodwhythisfirstnameissobig"}
        lastName={"mylastnamesobigiwasprettyanswered"}
        onOpenProfile={() => {}}
        avatar={
          "https://fastly.picsum.photos/id/790/200/300.jpg?hmac=FVbUQYv_h5C4v5_RAIja_q1c5UShyHhRu6C7DvjZM8U"
        }
        onLogout={() => {}}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
