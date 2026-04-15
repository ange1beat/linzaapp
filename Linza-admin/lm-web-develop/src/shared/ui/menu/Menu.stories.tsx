import {
  BellDot,
  Box,
  ChartMixed,
  Circle,
  Persons,
  Plus,
} from "@gravity-ui/icons";
import { StoryObj } from "@storybook/react";

import Menu from "./index";

export const Default: StoryObj<typeof Menu> = {
  args: {
    mainItems: (
      <>
        <Menu.MenuItemButton isSelected={false}>
          <Circle />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <BellDot />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <ChartMixed />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={true}>
          <Persons />
        </Menu.MenuItemButton>
      </>
    ),
    secondaryItems: (
      <>
        <Menu.MenuItemButton isSelected={false}>
          <Plus />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <Box />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <Box />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <Box />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <Box />
        </Menu.MenuItemButton>
        <Menu.MenuItemButton isSelected={false}>
          <Box />
        </Menu.MenuItemButton>
      </>
    ),
  },
};

export default {
  title: "Shared/Menu",
  component: Menu,
};
