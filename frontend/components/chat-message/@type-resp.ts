export type ResponseType = {
  intro_message: string;
  content: {
    structured: {
      message: string;
      components: (
        | {
            component_type: "table";
            table_layout: {
              columns: { key: string; label: string }[];
              rows: Record<string, string | number | null>[];
            };
            cards_layout?: never;
            list_layout?: never;
            text_layout?: never;
          }
        | {
            component_type: "cards";
            cards_layout: {
              cards: {
                title: string;
                subtitle?: string;
                meta: {
                  label: "head" | "body" | "image" | "footer";
                  value: string;
                }[];
              }[];
            };
            table_layout?: never;
            list_layout?: never;
            text_layout?: never;
          }
        | {
            component_type: "list";
            list_layout: {
              items: { text: string }[];
            };
            table_layout?: never;
            cards_layout?: never;
            text_layout?: never;
          }
        | {
            component_type: "text";
            text_layout: {
              content: string;
            };
            table_layout?: never;
            cards_layout?: never;
            list_layout?: never;
          }
      )[];
    }[];
    rawtext: string;
  };
};
