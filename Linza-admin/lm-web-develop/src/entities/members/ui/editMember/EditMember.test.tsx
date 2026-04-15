import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import EditMember from "./index";

describe("Edit Member", () => {
  it("Test with data", () => {
    const tree = render(
      <EditMember
        isOpen
        className="new-class"
        data={{
          id: "1",
          firstName: "First Name",
          lastName: "Last Name",
          email: "Email",
          phoneNumber: "88005553535",
          telegramUsername: "Telegram",
          avatarUrl: "AvatarUrl",
        }}
        errors={{
          firstName: "First Name",
          lastName: "Last Name",
          email: "Email",
          phoneNumber: "88005553535",
          telegramUsername: "Telegram",
        }}
        onSubmit={() => {}}
        isLoad={false}
        onCancel={() => {}}
        onChange={() => {}}
        isDisabled={false}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
