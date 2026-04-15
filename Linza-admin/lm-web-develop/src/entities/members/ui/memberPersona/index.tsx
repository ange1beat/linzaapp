import { defaultAva } from "@/entities/members";
import { useGetMemberQuery } from "@/entities/members/api/queries";
import { getFullName } from "@/shared/lib";
import { Persona, Skeleton } from "@/shared/ui";

function MemberPersona({ memberId }: { memberId: string }) {
  const memberQuery = useGetMemberQuery(memberId);
  const fullName = getFullName(memberQuery.selectedMember);
  return (
    <Skeleton isLoad={memberQuery.isPending} height={18}>
      <Persona
        size="xxs"
        image={memberQuery.selectedMember.avatarUrl}
        defaultImage={defaultAva}
        text={fullName}
      />
    </Skeleton>
  );
}

export default MemberPersona;
