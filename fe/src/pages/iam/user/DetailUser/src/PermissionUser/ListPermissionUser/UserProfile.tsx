import { MatrixDataTable } from "@components/MatrixDataTable";
import { featureColumns,  featureData,  type FeatureRow } from "./tableConfig";

export default function UserProfile() {
  return (
    <MatrixDataTable<FeatureRow>
      columns={featureColumns}
      data={featureData}
      rowKey={(row) => row.feature}
    />
  );
}
