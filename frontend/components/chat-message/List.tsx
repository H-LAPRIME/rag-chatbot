import React from "react";

interface ListItem {
  text: string;
}

interface ListLayout {
  items: ListItem[];
}

interface ListComponentProps {
  list_layout: ListLayout;
}

const ListComponent: React.FC<ListComponentProps> = ({ list_layout }) => {
  return (
    <ul className="list-disc pl-6 mb-4">
      {list_layout.items.map((item, i) => (
        <li key={i} className="text-black py-1">{item.text}</li>
      ))}
    </ul>
  );
};

export default ListComponent;