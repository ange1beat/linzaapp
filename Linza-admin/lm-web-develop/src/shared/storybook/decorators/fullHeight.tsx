import { StoryFn } from "@storybook/react";

function fullHeight(Story: StoryFn) {
  return (
    <div style={{ height: "100vh" }}>
      <Story />
    </div>
  );
}

export default fullHeight;
