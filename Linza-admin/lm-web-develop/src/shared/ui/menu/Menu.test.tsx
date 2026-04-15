import {
  BellDot,
  Box,
  ChartMixed,
  Circle,
  Persons,
  Plus,
} from "@gravity-ui/icons";
import { describe, it, expect } from "vitest";

import { render } from "@/shared/tests";

import Menu from "./index";

describe("Menu", () => {
  it("View default", () => {
    const tree = render(
      <Menu
        mainItems={
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
        }
        secondaryItems={
          <>
            <Menu.MenuItemButton isSelected={false}>
              <Plus />
            </Menu.MenuItemButton>
            <Menu.MenuItemLink link="project/1">
              <Box />
            </Menu.MenuItemLink>
            <Menu.MenuItemLink link="porject/2">
              <Box />
            </Menu.MenuItemLink>
            <Menu.MenuItemLink link="porject/3">
              <Box />
            </Menu.MenuItemLink>
            <Menu.MenuItemLink link="porject/4">
              <Box />
            </Menu.MenuItemLink>
            <Menu.MenuItemLink link="porject/5">
              <Box />
            </Menu.MenuItemLink>
          </>
        }
      />,
    );
    expect(tree).toMatchSnapshot();
  });
});
