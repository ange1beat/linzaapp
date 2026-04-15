import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Text from "./index";

describe("Text", () => {
  it("Body-1 variant text", () => {
    const tree = render(<Text variant="body-1">Text with variant body-1</Text>);
    expect(tree).toMatchSnapshot();
  });
  it("Body-2 variant text", () => {
    const tree = render(<Text variant="body-2">Text with variant body-2</Text>);
    expect(tree).toMatchSnapshot();
  });

  it("Body-3 variant text", () => {
    const tree = render(<Text variant="body-3">Text with variant body-3</Text>);
    expect(tree).toMatchSnapshot();
  });

  it("Body-short variant text", () => {
    const tree = render(
      <Text variant="body-short">Text with variant body-short</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Caption-1 variant text", () => {
    const tree = render(
      <Text variant="caption-1">Text with variant caption-1</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Caption-2 variant text", () => {
    const tree = render(
      <Text variant="caption-1">Text with variant caption-2</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Header-1 variant text", () => {
    const tree = render(
      <Text variant="header-1">Text with variant header-1</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Header-2 variant text", () => {
    const tree = render(
      <Text variant="header-2">Text with variant header-2</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Subheader-1 variant text", () => {
    const tree = render(
      <Text variant="subheader-1">Text with variant subheader-1</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("SubHeader-2 variant text", () => {
    const tree = render(
      <Text variant="subheader-2">Text with variant subheader-2</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("SubHeader-3 variant text", () => {
    const tree = render(
      <Text variant="subheader-3">Text with variant subheader-3</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Display-1 variant text", () => {
    const tree = render(
      <Text variant="display-1">Text with variant display-1</Text>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Display-2 variant text", () => {
    const tree = render(
      <Text variant="display-2">Text with variant display-2</Text>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Display-3 variant text", () => {
    const tree = render(
      <Text variant="display-3">Text with variant display-3</Text>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Display-4 variant text", () => {
    const tree = render(
      <Text variant="display-4">Text with variant display-4</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Code-1 variant text", () => {
    const tree = render(<Text variant="code-1">Text with variant code-1</Text>);
    expect(tree).toMatchSnapshot();
  });
  it("Code-2 variant text", () => {
    const tree = render(<Text variant="code-2">Text with variant code-2</Text>);
    expect(tree).toMatchSnapshot();
  });
  it("Code-3 variant text", () => {
    const tree = render(<Text variant="code-3">Text with variant code-3</Text>);
    expect(tree).toMatchSnapshot();
  });

  it("Code-Inline-1 variant text", () => {
    const tree = render(
      <Text variant="code-inline-1">Text with variant code-inline-1</Text>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Code-Inline-2 variant text", () => {
    const tree = render(
      <Text variant="code-inline-2">Text with variant code-inline-2</Text>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Code-Inline-3 variant text", () => {
    const tree = render(
      <Text variant="code-inline-3">Text with variant code-inline-3</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Modal-name variant text", () => {
    const tree = render(
      <Text variant="modal-name">Text with variant modal-name</Text>,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Modal-email variant text", () => {
    const tree = render(
      <Text variant="modal-email">Text with variant modal-email</Text>,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Another variant text with classname", () => {
    const tree = render(
      <Text variant="header-1" className="test-class">
        Text with variant header-1 and test-class
      </Text>,
    );
    expect(tree).toMatchSnapshot();
  });
});
