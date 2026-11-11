# Research questions

Agreed with Neha on 11.11.2026.

**RQ1 (error sensitivity):** For each of the 11 error types, how often do LLM judges prefer the original summary over the version with one injected error, and does that rate grow with the error's severity (low, medium, high)?

**RQ2 (faithfulness vs coverage):** When one version of a summary contains a factual error and the other version is missing a sentence, which one do LLM judges prefer?

**RQ3 (prompt design):** Do LLM judges prefer the original summary over the injected version more often with the detailed prompt than with the simple prompt?

## How we'd measure them

- We give the judge the article and two summaries. It answers "A" or "B". We use the two judge prompts from the kickoff slides (`documentation/intro_kickoff.pdf`): the simple one and the detailed one.
- **RQ1:** the judge compares the original summary with the version that has an error. We count how often it picks the original, for each error type and each severity.
- **RQ2:** we take one perfect summary and make two versions of it. One has a factual error, the other is missing a sentence. We count how often the judge picks each of them.
- **RQ3:** we take the pairs from RQ1 and run them twice, once with the simple prompt and once with the detailed prompt. The detailed prompt explains what coverage and faithfulness mean.

## How they relate to the kickoff slides

RQ1 is the kickoff's "Error Sensitivity". RQ2 is the faithfulness-against-coverage conflict from its "Reliability and Consistency" question. RQ3 takes the prompt comparison from "Mitigating Evaluation Failures".
