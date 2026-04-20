export type DynamicFieldType = "text" | "textarea" | "select" | "multiselect";

export type DynamicField = {
  id: string;
  label: string;
  type: DynamicFieldType;
  placeholder?: string;
  required?: boolean;
  options?: string[];
};

export type DynamicSchema = {
  schemaVersion: string;
  requestClass: string;
  fields: DynamicField[];
};
