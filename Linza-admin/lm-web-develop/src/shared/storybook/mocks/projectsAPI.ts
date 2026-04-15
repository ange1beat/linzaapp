import env from "../../config/env";

export const listProjects = {
  url: `${env.API_URL}/projects`,
  method: "GET",
  status: 200,
  response: {
    projects: [
      {
        id: "1",
        name: "Projects 1",
        createdBy: "1",
        createdAt: "2023-12-29T11:52:47.059Z",
        avatarUrl: "",
      },
      {
        id: "2",
        name: "Projects 2",
        createdBy: "2",
        createdAt: "2023-12-29T11:52:47.059Z",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "3",
        name: "Projects 3",
        createdBy: "3",
        createdAt: "2023-12-29T11:52:47.059Z",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "4",
        name: "Projects 4",
        createdBy: "2",
        createdAt: "2023-12-29T11:52:47.059Z",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "5",
        name: "Projects 5",
        createdBy: "2",
        createdAt: "2023-12-29T11:52:47.059Z",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
    ],
    total: 5,
  },
  delay: 1000,
};

export const addProject = {
  url: `${env.API_URL}/projects`,
  method: "POST",
  status: 201,
  response: {
    id: "1",
    name: "Your project name",
    createdBy: "Bogdan",
    createdAt: "2023-12-22T13:13:39.006Z",
    avatarUrl: "/my-mock-url",
  },
};

export const updateProjectAvatar = {
  url: `${env.API_URL}/projects/:projectId/avatar`,
  method: "PUT",
  status: 204,
  response: undefined,
};

export const project = {
  url: `${env.API_URL}/projects/:projectId`,
  method: "GET",
  status: 200,
  response: {
    id: "1",
    name: "Project 1",
    tenantId: "1",
    createdBy: "Bogdan",
    createdAt: "2024-01-12T08:10:03.770Z",
    avatarUrl: "https://placekitten.com/g/200/200",
  },
};

export const updateProjectName = {
  url: `${env.API_URL}/projects/:projectId/name`,
  method: "PUT",
  status: 200,
  response: undefined,
};

export const favProjects = {
  url: `${env.API_URL}/projects/favorites`,
  method: "GET",
  status: 200,
  response: {
    favorites: [
      {
        id: "2",
        name: "Projects 2",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "3",
        name: "Projects 3",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "5",
        name: "Projects 5",
        avatarUrl: "https://placekitten.com/g/200/200",
      },
    ],
  },
  delay: 1000,
};

export const addMemberToProject = {
  url: `${env.API_URL}/projects/:projectId/members/`,
  method: "POST",
  status: 204,
  response: {},
};

export const deleteMemberFromProject = {
  url: `${env.API_URL}/projects/:projectId/members/:userId`,
  method: "DELETE",
  status: 204,
  response: {},
};

export const addProjectToFav = {
  url: `${env.API_URL}/projects/favorites/:projectId`,
  method: "PUT",
  status: 200,
  response: {},
};

export const deleteProjectFromFav = {
  url: `${env.API_URL}/projects/favorites/:projectId`,
  method: "DELETE",
  status: 204,
  response: {},
};

export const getAllFolders = {
  url: `${env.API_URL}/projects/:projectId/folders`,
  method: "GET",
  status: 200,
  response: {
    folders: [
      {
        id: "1",
        name: "Folder 01.01.2024 42423 adwadaw daw daw dad awdawdawdaad",
      },
      {
        id: "2",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "3",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "4",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "5",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "6",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "7",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "8",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "9",
        name: "Folder 01.01.2024 42423",
      },
      {
        id: "10",
        name: "Folder 01.01.2024 42423",
      },
    ],
    total: 10,
  },
};

export const deleteFolder = {
  url: `${env.API_URL}/projects/:projectId/folders/:folderId`,
  method: "DELETE",
  status: 204,
  response: {},
};

export const deleteProjectReports = {
  url: `${env.API_URL}/projects/:projectId/reports`,
  method: "DELETE",
  status: 204,
  response: {},
};
