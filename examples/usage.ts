/**
 * Five-line usage example for Explicit Commitment Debt.
 *
 * Run with: npx ts-node examples/usage.ts
 */

import { ExplicitCommitmentDebt } from '../src/ecd.ts';

const ecd = new ExplicitCommitmentDebt();

// 1. Human articulates an explicit claim.
const claimId = ecd.addClaim(
  'Write quarterly report to /data/q1-2026.csv',
  'andy@example.com',
  1.0
);

console.log('After adding the claim:', ecd.getDebt());
// → { totalDebt: 1, unresolvedCount: 1 }

// 2. Deterministic verification fires (in production, this comes from a
//    filesystem check, an HTTP probe, or an explicit human override).
const verification = {
  status: 'CONFIRMED' as const,
  evidence: 'file exists at /data/q1-2026.csv (4.2 KB, modified 2026-04-09T18:00:00Z)',
};

// 3. The claim is resolved. ECD decreases by the claim weight.
const result = ecd.resolveClaim(claimId, verification);
console.log('After resolution:', result);
// → { claimId: 'claim-...', status: 'CONFIRMED', newDebt: 0 }

console.log('Final state:', ecd.getDebt());
// → { totalDebt: 0, unresolvedCount: 0 }

// 4. The full audit trace is append-only.
console.log('Trace:', ecd.getTrace());
