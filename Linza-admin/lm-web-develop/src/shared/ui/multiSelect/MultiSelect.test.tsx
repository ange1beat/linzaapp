import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import { getOptions, options } from "./mocks";

import MultiSelect from "./index";

describe("MultiSelect", () => {
  it("Default view", () => {
    const tree = render(
      <MultiSelect
        noOptionsMessage={"not"}
        loadOptions={getOptions}
        values={[]}
        onChange={() => null}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Default view", () => {
    const tree = render(
      <MultiSelect
        noOptionsMessage={"not"}
        values={options.slice(0, 5)}
        loadOptions={getOptions}
        onChange={() => null}
      />,
    );
    expect(tree).toMatchSnapshot();
  });

  it("Disabled", () => {
    const tree = render(
      <MultiSelect
        noOptionsMessage={"not"}
        isDisabled={true}
        values={options.slice(0, 5)}
        loadOptions={getOptions}
        onChange={() => null}
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
