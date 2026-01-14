import React from "react";
import { Avatar, AvatarImage, AvatarFallback } from "../ui/avatar";

interface CardMeta {
  label: "head" | "body" | "image" | "footer";
  value: string;
}

interface Card {
  title: string;
  subtitle?: string;
  meta: CardMeta[];
}

interface CardsLayout {
  cards: Card[];
}

interface CardsComponentProps {
  cards_layout: CardsLayout;
}

const CardsComponent: React.FC<CardsComponentProps> = ({ cards_layout }) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-4">
      {cards_layout.cards.map((card, i) => (
        <div key={i} className="bg-white border border-gray-300 rounded-lg shadow-md p-4 hover:shadow-lg transition">
          {card.meta.map((m, j) => {
            if (m.label === "head") return <h3 key={j} className="text-primary font-bold text-lg">{m.value}</h3>;
            if (m.label === "body") return <p key={j} className="text-black mt-2">{m.value}</p>;
            if (m.label === "image")
              return (
                <Avatar key={j} className="my-2 w-24 h-24 rounded-full">
                  <AvatarImage src={m.value} alt={card.title} />
                  <AvatarFallback>?</AvatarFallback>
                </Avatar>
              ); if (m.label === "footer") return <small key={j} className="text-gray-500 mt-2 block">{m.value}</small>;
            return null;
          })}
          {card.subtitle && <h4 className="text-gray-700 mt-1">{card.subtitle}</h4>}
        </div>
      ))}
    </div>
  );
};


export default CardsComponent;