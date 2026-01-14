import React from "react";

interface TextLayout {
  content: string;
}

interface TextComponentProps {
  text_layout: TextLayout;
}

 const TextComponent: React.FC<TextComponentProps> = ({ text_layout }) => {
  return (
    <p className="text-black bg-muted/50 p-3 rounded-lg mb-4">{text_layout.content}</p>
  );
};

export  default TextComponent;
