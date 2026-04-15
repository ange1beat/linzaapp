import { StoryObj } from "@storybook/react";

import { getOptions, options } from "./mocks";

import MultiSelect from "./index";

export const Default: StoryObj<typeof MultiSelect> = {
  args: {
    loadOptions: getOptions,
    placeholder: "Filter by templates",
    noOptionsMessage: "NOT",
    isClearable: true,
    isLoading: false,
  },
  argTypes: {
    onChange: { action: "onChange" },
  },
};

export const Multiline: StoryObj<typeof MultiSelect> = {
  args: {
    loadOptions: getOptions,
    values: options.slice(7),
    placeholder: "Filter by templates",
    noOptionsMessage: "NOT",
    isClearable: true,
    isLoading: false,
  },
};

export const Scroll: StoryObj<typeof MultiSelect> = {
  args: {
    loadOptions: getOptions,
    values: options.slice(5),
    placeholder: "Filter by templates",
    noOptionsMessage: "NOT",
    isClearable: true,
    isLoading: false,
  },
  decorators: [
    (Story) => (
      <div style={{ height: "50px" }}>
        <Story />
      </div>
    ),
  ],
};

export const Disabled: StoryObj<typeof MultiSelect> = {
  args: {
    loadOptions: getOptions,
    values: options.slice(0, 4),
    placeholder: "Filter by templates",
    noOptionsMessage: "NOT",
    isClearable: true,
    isLoading: false,
    isDisabled: true,
  },
};

export default {
  title: "Shared/MultiSelect",
  component: MultiSelect,
};
