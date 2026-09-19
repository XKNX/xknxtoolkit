import { test } from "node:test";
import assert from "node:assert/strict";
import {
  flagEnabled,
  resolveComRows,
  type ComRow,
  type IrComObject,
  type IrComObjectRef,
} from "../src/lib/comObjects.ts";

function tmpl(opts: Partial<IrComObject>): IrComObject {
  return {
    Id: opts.Id ?? "T-1",
    Name: opts.Name ?? "Objekt",
    Text: opts.Text ?? "",
    Number: opts.Number ?? 1,
    DatapointType: opts.DatapointType ?? [],
    CommunicationFlag: opts.CommunicationFlag ?? "Disabled",
    ReadFlag: opts.ReadFlag ?? "Disabled",
    WriteFlag: opts.WriteFlag ?? "Disabled",
    TransmitFlag: opts.TransmitFlag ?? "Disabled",
    UpdateFlag: opts.UpdateFlag ?? "Disabled",
    ReadOnInitFlag: opts.ReadOnInitFlag ?? "Disabled",
  };
}

function ref(opts: Partial<IrComObjectRef>): IrComObjectRef {
  return {
    Id: opts.Id ?? "T-1_R-1",
    RefId: opts.RefId ?? "T-1",
    Name: opts.Name ?? null,
    Text: opts.Text ?? null,
    FunctionText: opts.FunctionText ?? null,
    DatapointType: opts.DatapointType ?? [],
    CommunicationFlag: opts.CommunicationFlag ?? null,
    ReadFlag: opts.ReadFlag ?? null,
    WriteFlag: opts.WriteFlag ?? null,
    TransmitFlag: opts.TransmitFlag ?? null,
    UpdateFlag: opts.UpdateFlag ?? null,
    ReadOnInitFlag: opts.ReadOnInitFlag ?? null,
  };
}

test("flagEnabled: non-null ref flag overrides the template flag", () => {
  assert.equal(flagEnabled("Enabled", "Disabled"), true);
  assert.equal(flagEnabled("Disabled", "Enabled"), false);
});

test("flagEnabled: null ref flag inherits the template flag (never Enabled by default)", () => {
  assert.equal(flagEnabled(null, "Enabled"), true);
  assert.equal(flagEnabled(null, "Disabled"), false);
});

test("resolveComRows: when refs are absent, renders the template table as-is (backward compat)", () => {
  const templates = [
    tmpl({
      Id: "T-1",
      Name: "Objekt",
      Number: 7,
      DatapointType: ["DPST-1-1"],
      ReadFlag: "Enabled",
    }),
    tmpl({ Id: "T-2", Name: "Foo", Number: 9, CommunicationFlag: "Enabled" }),
  ];
  const rows = resolveComRows([], templates);
  assert.equal(rows.length, 2);
  assert.deepStrictEqual(rows[0], {
    key: "T-1",
    number: 7,
    name: "Objekt",
    dpts: ["DPST-1-1"],
    flags: { C: false, R: true, W: false, T: false, U: false, I: false },
  } satisfies ComRow);
  assert.deepStrictEqual(rows[1], {
    key: "T-2",
    number: 9,
    name: "Foo",
    dpts: [],
    flags: { C: true, R: false, W: false, T: false, U: false, I: false },
  } satisfies ComRow);
});

test("resolveComRows: template-only branch preserves the old Name source (not ref.Text chain)", () => {
  const rows = resolveComRows([], [tmpl({ Name: "N", Text: "ignored-by-template-branch" })]);
  assert.equal(rows[0].name, "N");
});

test("resolveComRows: refs-only (no template) renders ref values; null flags -> Disabled; number undefined", () => {
  const rows = resolveComRows(
    [
      ref({
        Id: "R-1",
        Text: "Solo",
        DatapointType: ["DPST-3-7"],
        CommunicationFlag: "Enabled",
        ReadFlag: "Enabled",
      }),
    ],
    [],
  );
  assert.deepStrictEqual(rows[0], {
    key: "R-1",
    number: undefined,
    name: "Solo",
    dpts: ["DPST-3-7"],
    flags: { C: true, R: true, W: false, T: false, U: false, I: false },
  } satisfies ComRow);
});

test("resolveComRows: ref DPT wins over template DPT", () => {
  const rows = resolveComRows(
    [ref({ Id: "R-1", RefId: "T-1", DatapointType: ["DPST-1-2"] })],
    [tmpl({ Id: "T-1", DatapointType: ["DPST-1-1"] })],
  );
  assert.deepStrictEqual(rows[0].dpts, ["DPST-1-2"]);
});

test("resolveComRows: empty ref DPT inherits the template DPT (fixture that puts DPT on template)", () => {
  const rows = resolveComRows(
    [ref({ Id: "R-1", RefId: "T-1", DatapointType: [] })],
    [tmpl({ Id: "T-1", DatapointType: ["DPST-5-1"] })],
  );
  assert.deepStrictEqual(rows[0].dpts, ["DPST-5-1"]);
});

test("resolveComRows: null ref flag inherits the template flag (module-style override)", () => {
  const rows = resolveComRows(
    [ref({ Id: "R-1", RefId: "T-1", ReadFlag: null, CommunicationFlag: null, TransmitFlag: null })],
    [
      tmpl({
        Id: "T-1",
        ReadFlag: "Enabled",
        CommunicationFlag: "Enabled",
        TransmitFlag: "Disabled",
      }),
    ],
  );
  assert.equal(rows[0].flags.R, true);
  assert.equal(rows[0].flags.C, true);
  assert.equal(rows[0].flags.T, false);
});

test("resolveComRows: non-null ref flag overrides a conflicting template flag", () => {
  const rows = resolveComRows(
    [ref({ Id: "R-1", RefId: "T-1", ReadFlag: "Disabled", WriteFlag: "Enabled" })],
    [tmpl({ Id: "T-1", ReadFlag: "Enabled", WriteFlag: "Disabled" })],
  );
  assert.equal(rows[0].flags.R, false);
  assert.equal(rows[0].flags.W, true);
});

test("resolveComRows: name fallback chain Text -> FunctionText -> Name -> template.Name -> dash", () => {
  const t = (overrides: Partial<IrComObject>) => tmpl({ Id: "T-1", Name: "TplName", ...overrides });
  const cases: Array<{ ref: IrComObjectRef; templates: IrComObject[]; want: string }> = [
    { ref: ref({ Id: "R", RefId: "T-1", Text: "A" }), templates: [t({})], want: "A" },
    {
      ref: ref({ Id: "R", RefId: "T-1", Text: null, FunctionText: "B" }),
      templates: [t({})],
      want: "B",
    },
    {
      ref: ref({ Id: "R", RefId: "T-1", Text: null, FunctionText: null, Name: "C" }),
      templates: [t({})],
      want: "C",
    },
    {
      ref: ref({ Id: "R", RefId: "T-1", Text: null, FunctionText: null, Name: null }),
      templates: [t({})],
      want: "TplName",
    },
    {
      ref: ref({ Id: "R", RefId: "MISSING", Text: null, FunctionText: null, Name: null }),
      templates: [t({})],
      want: "—",
    },
  ];
  for (const c of cases) {
    const [row] = resolveComRows([c.ref], c.templates);
    assert.equal(row.name, c.want);
  }
});

test("resolveComRows: empty ref text fields fall back to template.Name even when template Text is set", () => {
  const rows = resolveComRows(
    [ref({ Id: "R", RefId: "T-1" })],
    [tmpl({ Id: "T-1", Name: "TplName", Text: "TplText" })],
  );
  assert.equal(rows[0].name, "TplName");
});

test("resolveComRows: Number always comes from the joined template (undefined when unresolved)", () => {
  const rows = resolveComRows(
    [ref({ Id: "R", RefId: "T-1" }), ref({ Id: "R2", RefId: "NOPE" })],
    [tmpl({ Id: "T-1", Number: 134 })],
  );
  assert.equal(rows[0].number, 134);
  assert.equal(rows[1].number, undefined);
});

test("resolveComRows: multiple refs to one template each render as their own row (no collapse)", () => {
  const rows = resolveComRows(
    [
      ref({ Id: "R-1", RefId: "T-1", Text: "first" }),
      ref({ Id: "R-2", RefId: "T-1", Text: "second" }),
    ],
    [tmpl({ Id: "T-1", Number: 50 })],
  );
  assert.equal(rows.length, 2);
  assert.equal(rows[0].key, "R-1");
  assert.equal(rows[1].key, "R-2");
  assert.equal(rows[0].number, 50);
  assert.equal(rows[1].number, 50);
  assert.equal(rows[0].name, "first");
  assert.equal(rows[1].name, "second");
});

test("resolveComRows: bug-report fixture row O-134_R-1 resolves to the expected output", () => {
  const templates: IrComObject[] = [
    tmpl({
      Id: "M-0008_A-7072-21-5CC3-O000A_O-134",
      Name: "Objekt",
      Text: "",
      Number: 134,
      DatapointType: [],
      CommunicationFlag: "Enabled",
      ReadFlag: "Disabled",
      WriteFlag: "Disabled",
      TransmitFlag: "Disabled",
      UpdateFlag: "Disabled",
      ReadOnInitFlag: "Disabled",
    }),
  ];
  const refs: IrComObjectRef[] = [
    ref({
      Id: "M-0008_A-7072-21-5CC3-O000A_O-134_R-1",
      RefId: "M-0008_A-7072-21-5CC3-O000A_O-134",
      Name: null,
      Text: "Logic - Output",
      FunctionText: "Result output 2 (1-bit)",
      DatapointType: ["DPST-1-2"],
      CommunicationFlag: "Enabled",
      ReadFlag: "Enabled",
      WriteFlag: "Disabled",
      TransmitFlag: "Enabled",
      UpdateFlag: "Enabled",
      ReadOnInitFlag: "Disabled",
    }),
  ];
  const rows = resolveComRows(refs, templates);
  assert.equal(rows.length, 1);
  assert.deepStrictEqual(rows[0], {
    key: "M-0008_A-7072-21-5CC3-O000A_O-134_R-1",
    number: 134,
    name: "Logic - Output",
    dpts: ["DPST-1-2"],
    flags: { C: true, R: true, W: false, T: true, U: true, I: false },
  } satisfies ComRow);
});

test("resolveComRows: empty refs and empty templates yields no rows", () => {
  assert.deepStrictEqual(resolveComRows([], []), []);
});
