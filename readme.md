## Resume-Analyzer & Job-Finder

A resume-analyzer & job-finder , where user uploads the resume and the model analyze the resume and shows the better suiting job role and finds the skill-gap for the job , the user can select the job role according to it wil make the score based on the resume. The user can find the top 10 suitable jobs extracted using API from internet, and the user can also update his resume using the llm model find the jobs on updated resume also.....

## Phase 1 : Progress

Extracted personal information from the resume.

## Completed till now
- Extracted all the personal information 
- finded the skillgap

## Next phase 
- Selecting the role
- Finding jobs
- Resume update

## The project is under Development
Complete till novembergit commit -m "refactor(app): restructure into guided multi-step wizard

- Split single-page UI into 3 steps: upload/analyze, role selection,
  skill gap detail — tracked via st.session_state
- Step 2 now offers both top-3 recommended roles AND a manual dropdown
  to explore any role, using the new skills_gap functions
- Add 'Start over' / 'Back' navigation between steps
- Extraction still only re-runs on a genuinely new file (hash-cached),
  never on navigation between wizard steps"