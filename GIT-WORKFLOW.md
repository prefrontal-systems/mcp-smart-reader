# Git Workflow Quick Reference

## Three Commands, That's It

### Starting New Work
```bash
git start feature/describe-your-work
```
Does: checkout main → pull → create branch

### Finishing Work (Success!)
```bash
git finish
```
Does: checkout main → pull → merge → push → delete local branch → delete remote branch

### Abandoning Work (Didn't Work Out)
```bash
git abandon
```
Does: checkout main → force delete local branch → delete remote branch

## Examples

```bash
# Add PDF support
git start feature/pdf-support
# ... code code code ...
git add . && git commit -m "Add PDF support"
git finish

# Try something experimental
git start experiment/llm-summarization
# ... nope, doesn't work ...
git abandon

# Quick refactor
git start refactor/clean-up-summarizer
# ... clean up code ...
git add . && git commit -m "Refactor summarizer"
git finish
```

## Branch Naming

- `feature/` - New functionality
- `fix/` - Bug fixes
- `refactor/` - Code improvements
- `docs/` - Documentation
- `experiment/` - Might not work

## What If I Forgot?

Check what branch you're on:
```bash
git branch --show-current
```

If you're on a feature branch and already merged manually:
```bash
# Just delete it
git checkout main
git branch -d feature/old-branch
git push origin --delete feature/old-branch
```

## The Rule

**Never keep a branch after merging**. Feature branches are temporary scratch spaces.
