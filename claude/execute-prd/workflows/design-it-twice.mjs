export const meta = {
  name: 'design-it-twice',
  description: 'Three parallel design explorations under different constraints, judged and synthesized',
  phases: [{ title: 'Explore' }, { title: 'Judge' }],
}

const DESIGN_SCHEMA = {
  type: 'object', required: ['constraint', 'interface', 'usageExample', 'hides', 'tradeoffs'],
  properties: {
    constraint: { type: 'string' }, interface: { type: 'string' },
    usageExample: { type: 'string' }, hides: { type: 'string' }, tradeoffs: { type: 'string' },
  },
}
const JUDGE_SCHEMA = {
  type: 'object', required: ['recommendation', 'rationale'],
  properties: { recommendation: { type: 'string' }, rationale: { type: 'string' } },
}

const CONSTRAINTS = [
  ['minimal-surface', 'Minimize surface area: 1–3 methods/endpoints max, hide everything else.'],
  ['max-flexibility', 'Maximize flexibility: support the most use cases, extensible.'],
  ['common-case', 'Optimize the common case: make the 80% path trivial; accept edge-case trade-offs.'],
]

phase('Explore')
const options = (await parallel(CONSTRAINTS.map(([key, constraint]) => () =>
  agent(
    `Design decision: ${args.decision}\nContext: ${args.contextSummary}\n` +
    `Repo audit: read ${args.repoAuditPath} for existing patterns.\n` +
    `Design under this constraint ONLY: ${constraint}\n` +
    `Return the interface signature, a usage example, what it hides, and trade-offs.`,
    { schema: DESIGN_SCHEMA, label: `design:${key}`, phase: 'Explore' })
))).filter(Boolean)
if (options.length < 2) throw new Error('Design exploration produced fewer than 2 options')

phase('Judge')
const judge = await agent(
  `Judge these ${options.length} designs for: ${args.decision}\n` +
  options.map((o, i) => `--- Option ${i + 1} (${o.constraint})\n${o.interface}\n${o.usageExample}\nHides: ${o.hides}\nTrade-offs: ${o.tradeoffs}`).join('\n') +
  `\nCriteria: interface simplicity; depth (small surface hiding complex internals); ` +
  `implementation efficiency; ease of correct use vs ease of misuse. ` +
  `Recommend one shape (synthesis allowed) with rationale.`,
  { schema: JUDGE_SCHEMA, label: 'judge', effort: 'high' })

return { options, recommendation: judge.recommendation, rationale: judge.rationale }
