/**
 * Violation example: silent inference is a runtime error.
 *
 * This example demonstrates the load-bearing rule. An LLM that "thinks"
 * something happened cannot resolve a claim — only deterministic verification
 * can. Attempting to do so throws.
 *
 * Run with: npx ts-node examples/violation.ts
 */

import { ExplicitCommitmentDebt } from '../src/ecd.ts';

const ecd = new ExplicitCommitmentDebt();

// 1. Human articulates an explicit claim.
const claimId = ecd.addClaim(
  'Deploy the new version of the service to production',
  'management-agent@example.com',
  1.0
);

console.log('After adding the claim:', ecd.getDebt());
// → { totalDebt: 1, unresolvedCount: 1 }

// 2. The management agent tries to resolve via LLM inference instead of a
//    deterministic check. The verification status is UNABLE_TO_CHECK because
//    the LLM cannot actually probe the deployment state — it can only guess.
const llmGuess = {
  status: 'UNABLE_TO_CHECK' as const,
  evidence: 'LLM consensus from three models suggests deployment likely succeeded',
};

// 3. The runtime check fires. The claim is NOT resolved.
try {
  ecd.resolveClaim(claimId, llmGuess);
  console.error('FAIL: should have thrown');
  process.exit(1);
} catch (err) {
  console.log('Runtime check fired (expected):');
  console.log('  ' + (err as Error).message);
}

// 4. ECD is unchanged. The claim is still UNRESOLVED. The "no silent
//    inference" rule held.
console.log('After violation attempt:', ecd.getDebt());
// → { totalDebt: 1, unresolvedCount: 1 }
