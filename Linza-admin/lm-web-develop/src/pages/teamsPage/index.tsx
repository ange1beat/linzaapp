import React, { useState } from "react";

import {
  Button,
  Card,
  Dialog,
  Table,
  Text,
  TextInput,
  withTableActions,
} from "@gravity-ui/uikit";
import { useNavigate } from "react-router-dom";

import {
  useCreateTeamMutation,
  useDeleteTeamMutation,
  useTeamsQuery,
} from "@/entities/team";
import type { ITeam } from "@/entities/team";
import { ROUTES } from "@/shared/config";

const ActionsTable = withTableActions(Table);

export default function TeamsPage() {
  const navigate = useNavigate();
  const { data: teams = [], isLoading } = useTeamsQuery();
  const createMutation = useCreateTeamMutation();
  const deleteMutation = useDeleteTeamMutation();

  const [showDialog, setShowDialog] = useState(false);
  const [newName, setNewName] = useState("");

  const columns = [
    { id: "name", name: "Название" },
    { id: "member_count", name: "Участников" },
    {
      id: "created_at",
      name: "Создана",
      template: (item: ITeam) =>
        item.created_at
          ? new Date(item.created_at).toLocaleDateString("ru")
          : "—",
    },
  ];

  const handleCreate = async () => {
    if (!newName.trim()) return;
    await createMutation.mutateAsync(newName.trim());
    setNewName("");
    setShowDialog(false);
  };

  const getRowActions = (item: ITeam) => [
    {
      text: "Открыть",
      handler: () => navigate(ROUTES.teamDetail(String(item.id))),
    },
    {
      text: "Удалить",
      handler: () => deleteMutation.mutate(item.id),
      theme: "danger" as const,
    },
  ];

  return (
    <div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 16,
        }}
      >
        <Text variant="header-1">Команды</Text>
        <Button view="action" onClick={() => setShowDialog(true)}>
          Создать команду
        </Button>
      </div>

      <Card>
        <ActionsTable
          data={teams}
          columns={columns}
          getRowActions={getRowActions}
          emptyMessage="Нет команд"
        />
      </Card>

      <Dialog
        open={showDialog}
        onClose={() => setShowDialog(false)}
        hasCloseButton
      >
        <Dialog.Header caption="Новая команда" />
        <Dialog.Body>
          <TextInput
            value={newName}
            onUpdate={setNewName}
            placeholder="Название команды"
            autoFocus
          />
        </Dialog.Body>
        <Dialog.Footer
          onClickButtonApply={handleCreate}
          textButtonApply="Создать"
          onClickButtonCancel={() => setShowDialog(false)}
          textButtonCancel="Отмена"
          loading={createMutation.isPending}
        />
      </Dialog>
    </div>
  );
}
