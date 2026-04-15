import React from "react";

import { Meta, StoryObj } from "@storybook/react";

import Accordion from "./index";

const meta: Meta<typeof Accordion> = {
  component: Accordion,
  title: "shared/Accordion",
};

export default meta;

type Story = StoryObj<typeof Accordion>;

export const Default: Story = {
  args: {
    children: [
      <Accordion.Head key={0}>Hello</Accordion.Head>,
      <Accordion.Body key={1}>
        Folder long name to check how is it will be display in my component
        <input placeholder="some content" />
        <button>Button!</button>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipisicing elit. A, aliquid
          commodi eos fugiat ipsam minima molestias nam omnis quam recusandae
          repellat, vero! Dicta dolorum illum nulla quae qui quisquam rem! Animi
          deleniti eligendi id natus ut? Asperiores cumque debitis distinctio
          esse est eveniet ex inventore maxime neque nesciunt nostrum omnis,
          perferendis perspiciatis quia, quidem saepe sapiente sint, sit
          temporibus voluptatum? Aliquam ea eos ex iste nemo nihil odio odit
          sunt? Culpa eaque earum error eum fuga hic provident quam quisquam
          sed. Consequatur fuga iste laudantium molestiae odio quisquam, ullam
          veniam.
        </p>
      </Accordion.Body>,
    ],
  },
};
