import React from "react";
import {
  Table as RadixTable,
} from "@radix-ui/themes";

export type ColumnDef<T> = {
  key: keyof T | string;
  title: string;
  width?: number | string;
  align?: "left" | "center" | "right";
  render?: (value: T[keyof T], row: T, rowIndex: number) => React.ReactNode;
};

type Props<T> = {
  columns: ColumnDef<T>[];
  data: T[];
  rowKey: (row: T) => string;
};

export function MatrixDataTable<T>({ columns, data, rowKey }: Props<T>) {
  return (
    <RadixTable.Root variant="surface" size="2">
      <RadixTable.Header>
        <RadixTable.Row>
          {columns.map((col) => (
            <RadixTable.ColumnHeaderCell
              key={col.key.toString()}
              style={{
                width: col.width ?? undefined,
                textAlign: col.align ?? "left",
              }}
            >
              {col.title}
            </RadixTable.ColumnHeaderCell>
          ))}
        </RadixTable.Row>
      </RadixTable.Header>

      <RadixTable.Body>
        {data.map((row, rowIndex) => (
          <RadixTable.Row key={rowKey(row)}>
            {columns.map((col) => {
              const raw = row[col.key as keyof T];
              const content = col.render ? col.render(raw, row, rowIndex) : raw;
              return (
                <RadixTable.Cell
                  key={col.key.toString()}
                  style={{ textAlign: col.align ?? "left" }}
                >
                  {content as React.ReactNode}
                </RadixTable.Cell>
              );
            })}
          </RadixTable.Row>
        ))}

      </RadixTable.Body>
    </RadixTable.Root>
  );
}
