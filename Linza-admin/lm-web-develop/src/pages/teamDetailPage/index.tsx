import React from "react";

import { Card, Table, Text } from "@gravity-ui/uikit";
import { useParams } from "react-router-dom";

import {
  useRemoveTeamMemberMutation,
  useTeamMembersQuery,
  useTeamQuery,
} from "@/entities/team";
import type { ITeamMember } from "@/entities/team";

export default function TeamDetailPage() {
  const { teamId } = useParams<{ teamId: string }>();
  const id = Number(teamId);

  const { data: team, isLoading: teamLoading } = useTeamQuery(id);
  const { data: members = [], isLoading: membersLoading } =
    useTeamMembersQuery(id);
  const removeMutation = useRemoveTeamMemberMutation(id);

  const columns = [
    {
      id: "name",
      name: "Имя",
      template: (item: ITeamMember) =>
        `${item.first_name} ${item.last_name}`,
    },
    { id: "email", name: "Email" },
    { id: "role", name: "Роль" },
  ];

  if (teamLoading) return <Text>Загрузка...</Text>;
  if (!team) return <Text>Команда не найдена</Text>;

  return (
    <div>
      <Text variant="header-1" style={{ marginBottom: 16 }}>
        {team.name}
      </Text>
      <Text variant="body-1" color="secondary" style={{ marginBottom: 16 }}>
        Участников: {team.member_count}
      </Text>

      <Card>
        <Table
          data={members}
          columns={columns}
          emptyMessage="Нет участников"
        />
      </Card>
    </div>
  );
}
