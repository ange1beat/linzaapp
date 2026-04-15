import env from "../../config/env";

export const memberList = {
  url: `${env.API_URL}/users/search?pageSize=10&pageNumber=1`,
  method: "POST",
  status: 200,
  response: {
    users: [
      {
        id: "c414b363-d206-458d-ab4a-8f0c48a63fb9",
        firstName: "Mab",
        lastName: "Nunson",
        email: "mnunson0@themeforest.net",
        phoneNumber: "+62 (574) 597-5326",
        telegramUsername: "11-4081331",
        roles: ["User"],
        avatarUrl: null,
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "bbc36d5d-3006-4998-be6c-d6fcc52e4dde",
        firstName: "Yorke",
        lastName: "Kingh",
        email: "ykingh1@google.co.jp",
        phoneNumber: "+86 (848) 163-5039",
        telegramUsername: "83-1470691",
        roles: ["Supervisor"],
        avatarUrl:
          "https://robohash.org/eanumquamreprehenderit.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "3abc7962-d66f-4748-9358-42cdfc74e1db",
        firstName: "Ann-marie",
        lastName: "Hanwright",
        email: "ahanwright2@senate.gov",
        phoneNumber: "+46 (819) 717-1892",
        telegramUsername: "25-6385339",
        roles: ["User"],
        avatarUrl:
          "https://robohash.org/eumaccusamusminima.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "8798f09a-263d-4f72-87cd-f3b26431db29",
        firstName: "Beale",
        lastName: "Oseman",
        email: "boseman3@quantcast.com",
        phoneNumber: "+52 (920) 537-5288",
        telegramUsername: "07-9563073",
        roles: ["Supervisor"],
        avatarUrl:
          "https://robohash.org/natusdistinctioet.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "1864dea5-731f-4045-831e-de5537619b5b",
        firstName: "Gradey",
        lastName: "Kenzie",
        email: "gkenzie4@pen.io",
        phoneNumber: "+62 (368) 250-7848",
        telegramUsername: "52-3684732",
        roles: ["Supervisor"],
        avatarUrl:
          "https://robohash.org/officiisutanimi.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "1cc14fcb-5f7e-4801-a4ee-6c68b304b2a8",
        firstName: "Cyndie",
        lastName: "Stubbins",
        email: "cstubbins5@marriott.com",
        phoneNumber: "+62 (739) 868-3852",
        telegramUsername: "67-6860017",
        roles: ["Supervisor"],
        avatarUrl:
          "https://robohash.org/enimrepellatminima.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "610b7185-5ef7-4935-8c47-e5c6968c21d8",
        firstName: "Robinson",
        lastName: "Crookes",
        email: "rcrookes6@is.gd",
        phoneNumber: "+7 (860) 686-8305",
        telegramUsername: "20-9360243",
        roles: ["Supervisor"],
        avatarUrl:
          "https://robohash.org/ipsamtemporanesciunt.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "c36e23be-0a31-4155-a563-e5a0093c3c9d",
        firstName: "Mareah",
        lastName: "Yushkov",
        email: "myushkov7@infoseek.co.jp",
        phoneNumber: "+62 (197) 985-3260",
        telegramUsername: "34-7818526",
        roles: ["Supervisor"],
        avatarUrl:
          "https://robohash.org/etassumendaerror.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "dc7a4c73-2fa0-49e5-b03d-02f07ef2d875",
        firstName: "Creight",
        lastName: "End",
        email: "cend8@oracle.com",
        phoneNumber: "+86 (872) 533-6016",
        telegramUsername: "70-4526624",
        roles: ["User"],
        avatarUrl: "https://robohash.org/aeaquequi.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
      {
        id: "8aeeb12f-6898-4151-95d0-249d1fa0743f",
        firstName: "Ruthann",
        lastName: "Farady",
        email: "rfarady9@parallels.com",
        phoneNumber: "+86 (824) 903-3564",
        telegramUsername: "44-9456271",
        roles: ["User"],
        avatarUrl:
          "https://robohash.org/voluptasaccusantiumdeserunt.png?size=50x50&set=set1",
        lastLogin: "2024-02-09T22:13:04.269979+00:00",
      },
    ],
    total: 10,
  },
  delay: 1000,
};

export const selectedMember = {
  url: `${env.API_URL}/users/1`,
  method: "GET",
  status: 200,
  response: {
    id: "1",
    firstName: "John",
    lastName: "Week",
    email: "john_week@mail.ru",
    phoneNumber: "88005553535",
    telegramUsername: "john_suka_week",
    roles: ["User"],
    avatarUrl: "https://placekitten.com/g/200/200",
  },
  delay: 1000,
};

export const updateMemberPassword = {
  url: `${env.API_URL}/users/:memberId/password`,
  method: "PUT",
  status: 200,
  response: undefined,
  delay: 1000,
};

export const getProjectsOfMember = {
  url: `${env.API_URL}/membership/1`,
  method: "GET",
  status: 200,
  response: {
    userId: "1",
    projectIds: ["1", "2"],
  },
};

export const modifyMembershipProjects = {
  url: `${env.API_URL}/membership/1`,
  method: "PATCH",
  status: 204,
  response: {},
};
