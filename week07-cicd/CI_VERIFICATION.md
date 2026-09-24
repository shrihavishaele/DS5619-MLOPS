# CI verification

Fill this in after you push and watch the workflow run on GitHub (Actions
tab of your repo). This is how we confirm your CI actually ran green in a
real GitHub Actions runner, not just locally.

## Workflow run

Paste the URL of a successful run of all three jobs (Actions tab -> click
the run -> copy the URL):

```
https://github.com/shrihavishaele/DS5619-MLOPS/actions/runs/36048548426
```

## Job summary

For each job, note pass/fail and how long it took:

- `lint`: pass (9s)
- `unit-test`: pass (7s)
- `integration-test`: pass (14s)

## What broke on the way there (optional but useful)

If any job failed before you got it working, briefly note what the failure
was and what fixed it. (Not required, but if `integration-test` gave you
trouble, this is worth 2 sentences for your own future reference — Week 9's
lab also builds on debugging CI-style failures.)

The workflow couldn't find `ci.yml` initially because it was placed inside the `week07-cicd` subfolder instead of the repository root. Moving the `.github` folder to the root of the repo fixed the issue!
