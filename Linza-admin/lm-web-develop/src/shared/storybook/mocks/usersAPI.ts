import env from "../../config/env";

export const getLoggedUser = {
  url: `${env.API_URL}/users/me`,
  method: "GET",
  status: 200,
  delay: 1000,
  response: {
    id: "1",
    firstName: "John",
    lastName: "Smith",
    email: "john@smith.com",
    phoneNumber: "88005553535",
    telegramUsername: "smith_john",
    avatarUrl: "https://placekitten.com/g/200/200",
  },
};

export const changeLoggedUserPassword = {
  url: `${env.API_URL}/users/me/password`,
  method: "POST",
  status: 200,
  response: {},
  delay: 1000,
};

export const getUserInvitation = {
  url: `${env.API_URL}/users/invitations/123412341`,
  method: "GET",
  status: 200,
  response: {},
  delay: 1000,
};

export const getMembersInfo = {
  url: `${env.API_URL}/users/search`,
  method: "POST",
  status: 200,
  response: {
    users: [
      {
        id: "1",
        firstName: "Albert",
        lastName: "Enstein",
        email: "albert_enstein@mail.ru",
        phoneNumber: "89043782298",
        telegramUsername: "@albert_forever",
        roles: ["User"],
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "2",
        firstName: "Dmitry",
        lastName: "Larin",
        email: "dmitry_larin@mail.ru",
        phoneNumber: "88005553535",
        telegramUsername: "@dima_lima",
        roles: ["User"],
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "3",
        firstName: "Vitali",
        lastName: "Klichko",
        email: "zavtrashnii_den@mail.ru",
        phoneNumber: "89999999999",
        telegramUsername: "@aaaa_iiiii_oooo",
        roles: ["User"],
        avatarUrl: "https://placekitten.com/g/200/200",
      },
      {
        id: "4",
        firstName: "Hto",
        lastName: "Ya",
        email: "hto_ya@mail.ru",
        phoneNumber: "89005003525",
        telegramUsername: "@vladimir_zel",
        roles: ["User"],
        avatarUrl: "https://placekitten.com/g/200/200",
      },
    ],
    total: 4,
  },
  delay: 1000,
};

export const updateUserName = {
  url: `${env.API_URL}/users/me/name`,
  method: "PUT",
  status: 200,
  response: {},
};

export const sendReportsOnEmail = {
  url: `${env.API_URL}/users/me/reports/email`,
  method: "POST",
  status: "204",
  response: {},
};

export const sendReportsOnTelegram = {
  url: `${env.API_URL}/users/me/reports/telegram`,
  method: "POST",
  status: "204",
  response: {},
};
