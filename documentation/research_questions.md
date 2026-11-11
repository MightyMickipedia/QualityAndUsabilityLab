# Research questions

Draft by Ivan, 10.11.2026. To be discussed with the team and finalised with Neha on 11.11.

**RQ1 (error sensitivity):** For each of the 11 error types, how often do LLM judges prefer the original summary over the version with one injected error, and does that rate grow with the error's severity (low, medium, high)?

**RQ2 (faithfulness vs coverage):** When one version of a summary contains a factual error and the other version is missing a sentence, which one do LLM judges prefer?

**RQ3 (prompt design):** Do LLM judges prefer the original summary over the injected version more often with the detailed prompt than with the simple prompt?

## How we'd measure them

- The judge gets the article and two summaries and answers "A" or "B" (both judge prompts are in `documentation/intro_kickoff.pdf`: "Prompt 1: simple" and "Prompt 2: detailed and defined").
- **RQ1:** pairs of (original, injected version). The metric is the share of pairs where the judge picks the original, per error type and per severity. A judge that sees no difference lands at 50%.
- **RQ2:** both versions come from the same perfect summary. One gets a faithfulness error injected, the other gets a sentence deleted. The metric is the share of pairs where the judge picks each version.
- **RQ3:** the same pairs as in RQ1, judged once with the simple prompt and once with the detailed prompt, which defines coverage and faithfulness.

## How they relate to the kickoff slides

RQ1 is the kickoff's "Error Sensitivity". RQ2 is the faithfulness-against-coverage conflict from its "Reliability and Consistency" question. RQ3 takes the prompt comparison from "Mitigating Evaluation Failures".
