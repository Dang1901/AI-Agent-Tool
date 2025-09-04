import React from 'react';
import { MatrixDataTable } from '@components/MatrixDataTable';
import { featureColumns, type FeatureRow } from '../ListPermissionUser/tableConfig';
import type { ColumnDef } from '@components/MatrixDataTable';

type Props = {
  data: FeatureRow[];
  onChange: (newData: FeatureRow[]) => void;
};

export default function PermissionUserForm({ data, onChange }: Props) {
  const handleToggle = (index: number, field: 'read' | 'write') => {
    const newData = [...data];
    newData[index] = { ...newData[index], [field]: !newData[index][field] };
    onChange(newData);
  };

  const editableColumns: ColumnDef<FeatureRow>[] = featureColumns.map((col) => {
    if (col.key === 'read' || col.key === 'write') {
      return {
        ...col,
        render: (_val, row, idx) => {
          const key = col.key as 'read' | 'write';
          return (
            <span
              style={{ cursor: 'pointer' }}
              onClick={() => handleToggle(idx, key)}
            >
              {row[key] ? '✓' : '✗'}
            </span>
          );
        },
      };
    }
    return col;
  });

  return (
    <MatrixDataTable
      columns={editableColumns}
      data={data}
      rowKey={(row) => row.feature}
    />
  );
}
