import React from "react";

import {
  BellDot,
  Boxes3,
  ChartMixed,
  Database,
  Persons,
  PersonWorker,
} from "@gravity-ui/icons";
import { useMatch } from "react-router";

import { MenuProjectItem, useFavProjectsQuery } from "@/entities/projects";
import { useActiveRole } from "@/entities/session";
import { PORTAL_ROLES, ROUTES } from "@/shared/config";

import { UserModalWindow } from "../../features/user";
import Menu from "../../shared/ui/menu";

function MenuWidget({ className }: { className?: string }) {
  const { projects } = useFavProjectsQuery();
  const activeRole = useActiveRole();

  const isAdmin = activeRole === PORTAL_ROLES.Administrator;

  return (
    <Menu
      className={className}
      mainItems={
        <>
          <Menu.MenuItem isSelected={!!useMatch(ROUTES.profile)}>
            <UserModalWindow isSelected={!!useMatch(ROUTES.profile)} />
          </Menu.MenuItem>
          <Menu.MenuItemButton isSelected={false}>
            <BellDot />
          </Menu.MenuItemButton>
          <Menu.MenuItemLink link={ROUTES.dashboard}>
            <ChartMixed />
          </Menu.MenuItemLink>
          <Menu.MenuItemLink link={ROUTES.members}>
            <Persons />
          </Menu.MenuItemLink>
          <Menu.MenuItemLink link={ROUTES.projects} end={true}>
            <Boxes3 />
          </Menu.MenuItemLink>
          {isAdmin && (
            <Menu.MenuItemLink link={ROUTES.teams}>
              <PersonWorker />
            </Menu.MenuItemLink>
          )}
          {isAdmin && (
            <Menu.MenuItemLink link={ROUTES.storage}>
              <Database />
            </Menu.MenuItemLink>
          )}
        </>
      }
      secondaryItems={
        <>
          {projects.map((project) => (
            <Menu.MenuItemLink
              key={project.id}
              link={ROUTES.project(project.id)}
            >
              <MenuProjectItem avatarUrl={project.avatarUrl} />
            </Menu.MenuItemLink>
          ))}
        </>
      }
    />
  );
}

export default MenuWidget;
