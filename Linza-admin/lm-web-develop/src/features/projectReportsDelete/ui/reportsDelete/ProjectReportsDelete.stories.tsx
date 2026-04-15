import { Meta, StoryObj } from "@storybook/react";

import { deleteProjectReports } from "@/shared/storybook/mocks";

import ProjectReportsDelete from "./index";

const meta: Meta<typeof ProjectReportsDelete> = {
  component: ProjectReportsDelete,
  title: "Features/Project/ReportsDelete",
  args: {
    projectId: "1",
  },
  parameters: {
    mockData: [deleteProjectReports],
  },
};

export default meta;

type Story = StoryObj<typeof ProjectReportsDelete>;

export const Default: Story = {
  args: {
    reports: [
      {
        id: "1",
        name: "Test report 1",
      },
      {
        id: "2",
        name: "Test report 2",
      },
      {
        id: "3",
        name: "Test report 3",
      },
    ],
    isOpen: true,
    onClose: () => {},
  },
};

export const Many: Story = {
  args: {
    reports: [
      {
        id: "1",
        name: "Test report 1",
      },
      {
        id: "2",
        name: "Test report 2",
      },
      {
        id: "3",
        name: "Test report 3",
      },
      {
        id: "4",
        name: "Test report 4",
      },
      {
        id: "5",
        name: "Test report 5",
      },
      {
        id: "6",
        name: "Test report 6",
      },
      {
        id: "7",
        name: "Test report 7",
      },
    ],
    isOpen: true,
    onClose: () => {},
  },
};
