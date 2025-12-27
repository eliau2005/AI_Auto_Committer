# Product Roadmap

1. [ ] GUI Skeleton & Project Selection — Create the main window with path input, browse button, log window, and placeholder buttons. Implement folder selection logic. `S`
2. [ ] Git Repository Validation — Implement logic to check if the selected folder is a valid git repository (check for .git). Update UI status validation. `XS`
3. [ ] Change Analysis Logic — Implement backend logic to run `git status` and `git diff` to extract changes. Display raw output in the terminal window. `S`
4. [ ] Configuration Management — Create a system to load `API_KEY` and `MODEL_NAME` from a `config.json` or `.env` file. `XS`
5. [ ] AI Integration Service — Implement the service to send diffs to the OpenAI/Claude API using the specified system prompt and handle responses. `S`
6. [ ] Smart Diff Handling — Add logic to truncate large diffs (>4000 chars) or send file lists to avoid token limits before sending to AI. `XS`
7. [ ] Message Preview & Editing — Connect the AI response to the Message Preview text box, allowing user edits. `XS`
8. [ ] Commit Execution — Implement the "Generate & Commit" button logic to run `git add .` and `git commit -m "..."` using the final message. `XS`
9. [ ] Error Handling & Polish — Implement comprehensive error handling for no repo, no changes, API errors, and git locks. Add final UI polish (Dark mode checks). `S`

> Notes
> - Order items by technical dependencies and product architecture
> - Each item should represent an end-to-end (frontend + backend) functional and testable feature
