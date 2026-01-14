"use client";

import { useEffect, useState } from "react";
import type { ResponseType } from "./@type-resp";
import TextComponent from "./Text";
import ListComponent from "./List";
import CardsComponent from "./Card";
import TableComponent from "./Table";

export default function Parent({ reply }: { reply: string }) {
  const [response, setResponse] = useState<ResponseType | null>(null);

  useEffect(() => {
    if (reply.trim().startsWith("{") || reply.trim().startsWith("[")) {
      try {
        const parsedResponse: ResponseType = JSON.parse(reply);
        setResponse(parsedResponse);
      } catch (error) {
        console.error("Failed to parse response:", error);
      }
    } else {
      setResponse(null);
    }
  }, [reply]);

  return (
    <div className="w-full h-full p-2 flex flex-col space-y-4">
      {response ? (
        <>
          {/* Intro message */}
          {response.intro_message && (
            <p className="mb-2 text-primary font-semibold">{response.intro_message}</p>
          )}

          {/* Structured components */}
          {response.content.structured.map((block, i) => (
            <div key={i} className="flex flex-col space-y-2">
              {/* Block message */}
              {block.message && <p className="font-medium">{block.message}</p>}

              {/* Components in this block */}
              {block.components.map((comp, j) => {
                switch (comp.component_type) {
                  case "table":
                    return comp.table_layout ? (
                      <TableComponent key={j} table_layout={comp.table_layout} />
                    ) : null;

                  case "cards":
                    return comp.cards_layout ? (
                      <CardsComponent key={j} cards_layout={comp.cards_layout} />
                    ) : null;

                  case "list":
                    return comp.list_layout ? (
                      <ListComponent key={j} list_layout={comp.list_layout} />
                    ) : null;

                  case "text":
                    return comp.text_layout ? (
                      <TextComponent key={j} text_layout={comp.text_layout} />
                    ) : null;

                  default:
                    return null;
                }
              })}
            </div>
          ))}

          {/* Raw text fallback */}
          {response.content.rawtext && (
            <p className="mt-4 text-black">{response.content.rawtext}</p>
          )}
        </>
      ) : (
        <p>{reply}</p>
      )}
    </div>
  );
}
