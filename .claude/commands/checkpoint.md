# Checkpoint Command

Create a git checkpoint with code commit, push to GitHub, and documentation updates.

## Instructions

You are creating a project checkpoint. Follow these steps:

1. **Review Changes**:
   - Run `git status` to see all changes
   - Run `git diff` to see detailed changes
   - Summarize what was accomplished in this session

2. **Update Documentation**:
   - Read `PROJECT_CONTEXT.md` and update if needed:
     - Update "Last Updated" date to today
     - Update system metrics if they changed
     - Add any new bug fixes or features to the appropriate sections
     - Update "Current System State" with latest information
   - Read `TODO.md` and update if needed:
     - Mark completed tasks as [x]
     - Add any new tasks discovered during this session
     - Move completed items to the "Completed" section

3. **Create Git Commit**:
   - Add all relevant changes: `git add .`
   - Create a concise commit message that describes:
     - What was built or fixed
     - Why it was needed
     - Any important technical details
   - Include the standard footer:
     ```
     🤖 Generated with [Claude Code](https://claude.com/claude-code)

     Co-Authored-By: Claude <noreply@anthropic.com>
     ```

4. **Push to GitHub**:
   - Push changes to remote: `git push`
   - Confirm push succeeded

5. **Summary**:
   - Provide a brief summary of what was checkpointed
   - Confirm all documentation is up to date
   - State that the checkpoint is complete

## Notes

- Only commit files that are part of the project (exclude temporary files in /tmp/)
- Make sure PROJECT_CONTEXT.md accurately reflects current system state
- Ensure TODO.md tracks all pending and completed tasks
- Use clear, descriptive commit messages
