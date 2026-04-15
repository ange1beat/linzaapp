import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Persona from "./index";

describe("Persona", () => {
  it("Small variant", () => {
    const tree = render(
      <Persona
        text="test text"
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Charles_Darwin_by_Julia_Margaret_Cameron%2C_c._1868.jpg/193px-Charles_Darwin_by_Julia_Margaret_Cameron%2C_c._1868.jpg"
        size="s"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Disable variant", () => {
    const tree = render(
      <Persona
        text="test text"
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Charles_Darwin_by_Julia_Margaret_Cameron%2C_c._1868.jpg/193px-Charles_Darwin_by_Julia_Margaret_Cameron%2C_c._1868.jpg"
        disabled={true}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
  it("Big variant", () => {
    const tree = render(
      <Persona
        text="test text"
        image="https://upload.wikimedia.org/wikipedia/commons/thumb/3/33/Charles_Darwin_by_Julia_Margaret_Cameron%2C_c._1868.jpg/193px-Charles_Darwin_by_Julia_Margaret_Cameron%2C_c._1868.jpg"
        size="n"
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
