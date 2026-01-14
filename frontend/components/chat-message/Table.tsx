import React from "react";

type TableColumn = { key: string; label: string };
type TableRow = Record<string, string | number | null>;

interface TableLayout {
  columns: TableColumn[];
  rows: TableRow[];
}

interface TableComponentProps {
  table_layout: TableLayout;
}

const TableComponent: React.FC<TableComponentProps> = ({ table_layout }) => {
  return (
    <div className="overflow-x-auto border border-gray-300 rounded-lg shadow-sm mb-4">
      <table className="w-full border-collapse">
        <thead className="bg-primary text-white">
          <tr>
            {table_layout.columns.map((col) => (
              <th key={col.key} className="px-4 py-2 text-left">{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody className="bg-muted/50 text-black">
          {table_layout.rows.map((row, i) => (
            <tr key={i} className="border-b border-gray-200 hover:bg-gray-100">
              {table_layout.columns.map((col) => (
                <td key={col.key} className="px-4 py-2">{row[col.key]}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};


export default TableComponent;