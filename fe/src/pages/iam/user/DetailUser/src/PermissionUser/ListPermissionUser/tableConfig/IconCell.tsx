import { CheckIcon, Cross1Icon } from "@radix-ui/react-icons";
import { IconButton, Tooltip } from "@radix-ui/themes";

export const IconCell = ({ val, label }: { val: boolean; label: string }) => (
  <Tooltip content={`${label}: ${val ? "✓" : "✗"}`}>
    <IconButton variant="ghost" color={val ? "green" : "red"}>
      {val ? <CheckIcon /> : <Cross1Icon />}
    </IconButton>
  </Tooltip>
);
