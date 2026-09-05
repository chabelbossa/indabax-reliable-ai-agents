# IndabaX Benin 2026 Workshop Submission Package

## Workshop

- **Title:** Building Reliable AI Agents
- **Subtitle:** Tool Calling, Orchestration and Evaluation in Practice
- **Speaker:** BOSSA Chabel
- **Format:** 50-minute hands-on lab
- **Immersive case:** KoraCare cold-chain incident response (fully synthetic)

## Delivery status

Final French-first and English materials are built locally. The URLs below are
the intended publication targets; they do not identify this final revision until
the local changes have been published. No submission email has been sent.

## Publication targets

- Repository: https://github.com/chabelbossa/indabax-reliable-ai-agents
- French participant notebook (primary): https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-fr.ipynb
- French solution notebook: https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-solution-fr.ipynb
- English participant notebook: https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-en.ipynb
- English solution notebook: https://colab.research.google.com/github/chabelbossa/indabax-reliable-ai-agents/blob/main/notebooks/workshop-solution-en.ipynb
- English speaker deck (PowerPoint): https://github.com/chabelbossa/indabax-reliable-ai-agents/raw/main/slides/indabax-reliable-ai-agents-en.pptx
- English speaker deck (PDF): https://github.com/chabelbossa/indabax-reliable-ai-agents/raw/main/slides/indabax-reliable-ai-agents-en.pdf
- French speaker deck (PowerPoint): https://github.com/chabelbossa/indabax-reliable-ai-agents/raw/main/slides/indabax-reliable-ai-agents-fr.pptx
- French speaker deck (PDF): https://github.com/chabelbossa/indabax-reliable-ai-agents/raw/main/slides/indabax-reliable-ai-agents-fr.pdf

## Verification snapshot

- 37 automated tests pass, including notebook-runtime regression tests and
  delivery-contract checks for bilingual notebooks, TODOs and speaker notes.
- 10 of 10 deterministic evaluations pass (three operational and seven adverse cases).
- All four notebooks execute in fresh local kernels in explicit mock mode.
- The French-first and English participant notebooks contain the same ten guided TODOs and four checkpoints.
- Both solution notebooks complete the five-tool incident workflow, record simulated operator approval, render the incident dashboard and eval matrix, and pass the `10 / 10` evaluation gate.
- Both solution notebooks unlock a portable JSON evidence dossier; participant notebooks keep it locked until the mission and all evaluations pass.
- Both decks contain 20 slides adapted from the official template, with speaker notes.
  The mission, tool-call example, loop diagram, failure case, evaluation comparison
  and dossier excerpt are explained on the slides themselves. All 40 final PDF pages
  were rendered and visually checked after the editorial revision.
- Gemini is the normal live path; the key is requested securely and is never embedded in notebook output.
- Mock mode remains an explicit no-key fallback and the deterministic evaluation path.

## Live-provider verification

A genuine Gemini smoke test executed the saved French solution's runtime:
five tools succeeded, the incident was escalated, and all six acceptance checks
passed (run `RUN-F96BE6CC`, model `gemini-3.7-flash`). This proves one live run,
not simultaneous classroom quota capacity. Quota and network failures stop
cleanly; switching to mock remains explicit.

See `VALIDATION.md` for the precise verification scope and remaining rehearsal
and publication checks. KoraCare, its data, and operator decisions are simulated;
the lab performs no physical action and is not a medical protocol.
