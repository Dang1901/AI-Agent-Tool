import type { ColumnDef } from "@components/MatrixDataTable";
import type { FeatureRow } from "./type";
import { IconCell } from "./IconCell";

export const featureColumns: ColumnDef<FeatureRow>[] = [
  { key: "name", title: "Feature", width: "40%" },
  {
    key: "read",
    title: "READ",
    align: "center",
    render: (val) => <IconCell val={!!val} label="Read" />,  // dùng !! để ép kiểu boolean
  },
  {
    key: "write",
    title: "WRITE",
    align: "center",
    render: (val) => <IconCell val={!!val} label="Write" />,
  },
];
