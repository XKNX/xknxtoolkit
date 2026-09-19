export interface IrComObject {
  Id: string;
  Name: string;
  Text: string;
  Number: number;
  DatapointType: string[];
  CommunicationFlag: string;
  ReadFlag: string;
  WriteFlag: string;
  TransmitFlag: string;
  UpdateFlag: string;
  ReadOnInitFlag: string;
}

export interface IrComObjectRef {
  Id: string;
  RefId: string;
  Name: string | null;
  Text: string | null;
  FunctionText: string | null;
  DatapointType: string[];
  CommunicationFlag: string | null;
  ReadFlag: string | null;
  WriteFlag: string | null;
  TransmitFlag: string | null;
  UpdateFlag: string | null;
  ReadOnInitFlag: string | null;
}

export interface ComRowFlags {
  C: boolean;
  R: boolean;
  W: boolean;
  T: boolean;
  U: boolean;
  I: boolean;
}

export interface ComRow {
  key: string;
  number: number | undefined;
  name: string;
  dpts: string[];
  flags: ComRowFlags;
}

export function flagEnabled(refFlag: string | null, tmplFlag: string): boolean {
  return (refFlag ?? tmplFlag) === "Enabled";
}

function flagsFromTemplate(co: IrComObject): ComRowFlags {
  return {
    C: co.CommunicationFlag === "Enabled",
    R: co.ReadFlag === "Enabled",
    W: co.WriteFlag === "Enabled",
    T: co.TransmitFlag === "Enabled",
    U: co.UpdateFlag === "Enabled",
    I: co.ReadOnInitFlag === "Enabled",
  };
}

function rowFromTemplate(co: IrComObject): ComRow {
  return {
    key: co.Id,
    number: co.Number,
    name: co.Name,
    dpts: co.DatapointType,
    flags: flagsFromTemplate(co),
  };
}

function rowFromRef(ref: IrComObjectRef, tmpl: IrComObject | undefined): ComRow {
  return {
    key: ref.Id,
    number: tmpl?.Number,
    name: ref.Text ?? ref.FunctionText ?? ref.Name ?? tmpl?.Name ?? "—",
    dpts: ref.DatapointType.length > 0 ? ref.DatapointType : (tmpl?.DatapointType ?? []),
    flags: {
      C: flagEnabled(ref.CommunicationFlag, tmpl?.CommunicationFlag ?? "Disabled"),
      R: flagEnabled(ref.ReadFlag, tmpl?.ReadFlag ?? "Disabled"),
      W: flagEnabled(ref.WriteFlag, tmpl?.WriteFlag ?? "Disabled"),
      T: flagEnabled(ref.TransmitFlag, tmpl?.TransmitFlag ?? "Disabled"),
      U: flagEnabled(ref.UpdateFlag, tmpl?.UpdateFlag ?? "Disabled"),
      I: flagEnabled(ref.ReadOnInitFlag, tmpl?.ReadOnInitFlag ?? "Disabled"),
    },
  };
}

export function resolveComRows(refs: IrComObjectRef[], templates: IrComObject[]): ComRow[] {
  if (refs.length === 0) return templates.map(rowFromTemplate);
  const tmplById = new Map(templates.map((co) => [co.Id, co]));
  return refs.map((ref) => rowFromRef(ref, tmplById.get(ref.RefId)));
}
