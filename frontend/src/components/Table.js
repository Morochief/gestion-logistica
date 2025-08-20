import React from "react";

function Table({ columns, data, onEdit, onDelete }) {
  return (
    <div className="overflow-x-auto">
      <table className="table-auto w-full border-collapse">
        <thead>
          <tr className="bg-gray-100">
            {columns.map((col) => (
              <th key={col.field} className="px-4 py-2 border-b text-left text-sm font-semibold text-gray-700">
                {col.label}
              </th>
            ))}
            {(onEdit || onDelete) && (
              <th className="px-4 py-2 border-b text-left text-sm font-semibold text-gray-700">
                Acciones
              </th>
            )}
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={row.id} className="hover:bg-gray-50 transition">
              {columns.map((col) => (
                <td key={col.field} className="px-4 py-2 border-b text-sm text-gray-800">
                  {(() => {
                    try {
                      if (col.render) return col.render(row[col.field], row);
                      const val = row[col.field];
                      if (typeof val === "object" && val !== null) {
                        console.warn("Campo objeto no renderizable en tabla:", val, "en fila:", row);
                        return <span className="text-orange-500">[obj]</span>;
                      }
                      return val;
                    } catch (e) {
                      console.error("Error renderizando celda:", e, "col:", col, "row:", row);
                      return <span className="text-red-500">error</span>;
                    }
                  })()}
                </td>
              ))}
              {(onEdit || onDelete) && (
                <td className="px-4 py-2 border-b text-sm whitespace-nowrap">
                  {onEdit && (
                    <button
                      onClick={() => onEdit(row)}
                      className="bg-indigo-50 text-indigo-700 hover:bg-indigo-100 border border-indigo-200 px-3 py-1 rounded mr-1 transition"
                    >
                      Editar
                    </button>
                  )}
                  {onDelete && (
                    <button
                      onClick={() => onDelete(row.id)}
                      className="bg-red-50 text-red-700 hover:bg-red-100 border border-red-200 px-3 py-1 rounded transition"
                    >
                      Eliminar
                    </button>
                  )}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default Table;
