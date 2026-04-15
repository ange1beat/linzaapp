import React from "react";

import { Outlet } from "react-router-dom";
import { createBrowserRouter } from "react-router-dom";

import {
  BaseLayout,
  DashboardPage,
  LoginPage,
  MemberDetailPage,
  MembersPage,
  MenuLayout,
  ProjectDashboardPage,
  ProjectDetailsPage,
  ProjectsPage,
  RegistrationErrorPage,
  RegistrationPage,
  RegistrationSuccessPage,
  ResetPasswordPage,
  ResetPasswordSuccessPage,
  StoragePage,
  TeamDetailPageComponent,
  TeamsPage,
  UserChangeEmailPage,
  UserChangeNamePage,
  UserChangePasswordPage,
  UserChangePhonePage,
  UserChangeTelegramPage,
  UserProfilePage,
} from "@/pages/index";
import ProjectFolder from "@/pages/projectFolder";
import ProjectFolders from "@/pages/projectFolders";
import { ROUTES } from "@/shared/config";

import AuthProvider from "./authProvider";
import GuestProvider from "./guestProvider";

const publicRoutes = createBrowserRouter([
  {
    path: "/",
    element: (
      <BaseLayout>
        <Outlet />
      </BaseLayout>
    ),
    children: [
      {
        element: <GuestProvider />,
        children: [
          {
            path: ROUTES.login,
            element: <LoginPage />,
          },
          {
            path: ROUTES.forgotPassword,
            element: <ResetPasswordPage />,
          },
          {
            path: ROUTES.registration,
            element: <RegistrationPage />,
          },
          {
            path: ROUTES.resetPasswordSuccess,
            element: <ResetPasswordSuccessPage />,
          },
          {
            path: ROUTES.registrationSuccess,
            element: <RegistrationSuccessPage />,
          },
          {
            path: ROUTES.registrationError,
            element: <RegistrationErrorPage />,
          },
        ],
      },
      {
        element: (
          <AuthProvider>
            <Outlet />
          </AuthProvider>
        ),
        children: [
          {
            path: ROUTES.profilePassword,
            element: <UserChangePasswordPage />,
          },
          {
            element: (
              <MenuLayout>
                <Outlet />
              </MenuLayout>
            ),
            children: [
              {
                path: ROUTES.profile,
                element: <UserProfilePage />,
              },
              {
                path: ROUTES.profileTelegram,
                element: <UserChangeTelegramPage />,
              },
              {
                path: ROUTES.profileName,
                element: <UserChangeNamePage />,
              },
              {
                path: ROUTES.profilePhone,
                element: <UserChangePhonePage />,
              },
              {
                path: ROUTES.profilePassword,
                element: <UserChangePasswordPage />,
              },
              {
                path: ROUTES.profileEmail,
                element: <UserChangeEmailPage />,
              },
              {
                path: ROUTES.dashboard,
                element: <DashboardPage />,
              },
              {
                path: ROUTES.members,
                element: <MembersPage />,
              },
              {
                path: ROUTES.memberDetail(":memberId"),
                element: <MemberDetailPage />,
              },
              {
                path: ROUTES.projects,
                element: <ProjectsPage />,
              },
              {
                path: ROUTES.project(":projectId"),
                element: <ProjectDashboardPage />,
              },
              {
                path: ROUTES.projectSettings(":projectId"),
                element: <ProjectDetailsPage />,
              },
              {
                path: ROUTES.folders(":projectId"),
                element: <ProjectFolders />,
              },
              {
                path: ROUTES.folder(":projectId", ":folderId"),
                element: <ProjectFolder />,
              },
              {
                path: ROUTES.teams,
                element: <TeamsPage />,
              },
              {
                path: ROUTES.teamDetail(":teamId"),
                element: <TeamDetailPageComponent />,
              },
              {
                path: ROUTES.storage,
                element: <StoragePage />,
              },
            ],
          },
        ],
      },
    ],
  },
]);

export default publicRoutes;
