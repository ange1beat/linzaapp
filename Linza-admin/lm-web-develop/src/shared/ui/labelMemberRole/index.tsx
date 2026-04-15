import Label from "../label";

export default function LabelMemberRole(props: { role: string }) {
  const roleToTheme: { [key: string]: string } = {
    User: "normal",
    Supervisor: "info",
  };
  return (
    <Label theme={roleToTheme[props.role] as "normal" | "info"}>
      {props.role}
    </Label>
  );
}
