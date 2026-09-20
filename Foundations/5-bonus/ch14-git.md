# Chapter 14: Git — the graph beneath the commands

*[← Chapter 13](ch13-data-teams.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

Every engineer uses Git. Far fewer can say what a commit actually *is*. You get by on four memorized commands — `add`, `commit`, `pull`, `push` — right up until the day a merge conflict appears, or you land in "detached HEAD," or you need to undo something you already pushed. Then the memorized commands run out, because you were driving a machine whose model you never learned. This chapter gives you that model. The principle, in the Foundations spirit: **understand the graph of snapshots underneath, and the commands stop being spells.**

---

## The mechanism: history is a graph of snapshots

Here's the one idea that makes the rest fall into place. A **commit is a snapshot** of your entire project at a moment in time, plus a pointer to the commit (or commits) that came before it — its **parent**. Chain those parent pointers together and the whole history of your project is a **directed graph**: each commit points back to where it came from.

> 💡 **Concept notes — commit, branch, HEAD**
> - **Commit:** a full snapshot of the tracked files, stamped with an author, a message, and a link to its parent(s). It's identified by a **hash** (that `a3f9c2…` string) computed from its contents — change anything and you get a *different* commit with a *different* id. Commits are immutable; you never edit one, you make a new one.
> - **Branch:** not a copy of your files — just a **movable pointer to a commit**. `main` is a sticky note that says "the latest commit on this line of work." Making a commit moves the branch pointer forward. This is why branching in Git is cheap: a new branch is one tiny file holding one hash.
> - **HEAD:** a pointer to *where you are right now* — usually "HEAD points to `main`, which points to commit `a3f9`." When HEAD points straight at a commit instead of a branch, that's the scary-sounding but harmless **detached HEAD**: you're looking at a commit with no branch to catch new work.
> Say it in one breath: *a branch is a pointer to a commit, a commit is a snapshot plus a parent, and HEAD is you.*

Once you see history as "pointers into a graph of snapshots," the operations that used to feel magical are just **moving pointers around**. That's the whole trick.

---

## The three places your changes live

Git doesn't have one "saved" state — it has three, and the confusion of the first month comes from not knowing which one you're in.

> 💡 **Concept notes — working directory, staging area, repository**
> - **Working directory:** the actual files on disk you're editing. Changes here are "unstaged" — Git sees them but isn't tracking them for the next commit yet.
> - **Staging area (the index):** a holding pen for exactly what will go into the *next* commit. `git add` moves changes from the working directory into staging. Its whole reason to exist: let you commit a *curated* set of changes — you fixed two unrelated things, but you can stage and commit them separately for a clean history.
> - **Repository (.git):** the permanent, committed graph of snapshots. `git commit` takes what's staged and records it as a new commit.
> The flow is always the same: **edit (working) → `git add` (staging) → `git commit` (repository).** `git status` tells you what's in each place; when you're lost, that's the command to run.

---

## Merge vs rebase: two ways to combine work

You branched off `main`, did three commits, and meanwhile a teammate pushed to `main`. Now history has forked — two lines of commits from a shared parent — and you need them back together. There are two ways, and interviewers love the difference.

> 💡 **Concept notes — merge vs rebase**
> - **Merge** creates a new **merge commit** with *two* parents, tying the branches together. Your branch's commits keep their original ids and history is preserved exactly as it happened — including the fork. Honest but non-linear: the graph shows the branching. `git merge`.
> - **Rebase** *replays* your commits one by one onto the tip of the updated `main`, as if you'd branched from there all along. The result is a clean **linear** history with no merge commit — but because each replayed commit gets a *new* parent, it gets a **new hash**. You've rewritten history.
> The rule that follows directly from "rebase rewrites hashes": **never rebase commits you've already shared/pushed.** Rewriting public history means everyone else's copy now disagrees with yours, and the next `pull` becomes a mess. Rebase your *local, unpushed* work to tidy it; merge when combining *shared* branches. "Rebase local, merge public" is the safe default.

A **merge conflict** isn't Git breaking — it's Git refusing to guess. When both sides changed *the same lines*, Git can't know which you want, so it marks the spot (`<<<<<<<`, `=======`, `>>>>>>>`) and hands it to you. You pick the right result, remove the markers, `git add`, and continue. Conflicts are a *human* decision Git correctly declined to make for you.

---

## Remotes: your graph and theirs

The commit graph on your laptop is complete on its own — Git is **distributed**, so every clone has the full history. A **remote** (conventionally `origin`) is just another copy of that graph, on a server like GitHub, that you sync with.

> 💡 **Concept notes — clone, fetch, pull, push**
> - **`clone`** copies an entire remote repository (all commits, all branches) to your machine.
> - **`fetch`** downloads new commits from the remote but *doesn't* touch your working files — it updates your knowledge of where the remote's branches are (`origin/main`).
> - **`pull`** = `fetch` + `merge` (or `fetch` + `rebase` if configured). It brings remote commits down *and* integrates them into your current branch. The surprise conflicts people hit on `pull` are just the merge step.
> - **`push`** uploads your local commits to the remote. It's rejected if the remote has commits you don't — Git makes you `pull` and integrate first, so you can't silently clobber someone's work. (You *can* force it, and force-pushing a shared branch is exactly the "rewrote public history" footgun — avoid it.)

---

## The "oh no" toolbox: undoing things

Most Git panic is one of a few situations. Knowing the right undo — and which ones are safe — is a real interview and real-life skill.

> 💡 **Concept notes — amend, revert, reset, restore, reflog**
> - **Amend** (`git commit --amend`): fix the *last, unpushed* commit — wrong message or forgot a file. It rewrites that commit, so don't amend something already pushed.
> - **Revert** (`git revert <commit>`): make a *new* commit that undoes an old one. Safe on shared history because it adds rather than rewrites — the way to undo something already public.
> - **Reset** (`git reset`): move the current branch pointer to an earlier commit. `--soft` keeps your changes staged, `--mixed` (default) keeps them unstaged, `--hard` **throws the changes away** — that last one is the destructive one people regret. Use reset to undo *local* history; never on pushed commits others have.
> - **Restore / checkout** (`git restore <file>`): discard uncommitted changes to a file, or switch branches. Discarding is also unrecoverable once done — it's gone from the working directory.
> - **Reflog** (`git reflog`): your safety net. Git records every place HEAD has been, so even a "lost" commit after a bad reset is usually still findable for a while. When you think you destroyed work, check the reflog *before* panicking.

The load-bearing distinction: **revert is additive and safe on shared branches; reset/amend rewrite history and belong to local work only.**

---

## Branching models: how teams organize the graph

The commands are the same everywhere; teams just agree on *conventions* for how branches flow.

> 💡 **Concept notes — feature branches, trunk-based, Gitflow**
> - **Feature branch + pull request:** branch off `main`, do the work, open a **PR** for review, merge back. The near-universal default, and where code review lives.
> - **Trunk-based development:** everyone integrates into `main` frequently (at least daily) behind small changes and feature flags. Favors continuous integration; avoids long-lived branches that drift and conflict.
> - **Gitflow:** a heavier scheme with long-lived `develop`, `release`, and `hotfix` branches. Structured but ceremony-heavy; most fast-moving teams have moved toward trunk-based. Know the name and that it's the "many long-lived branches" model.

---

## In the interview

Git questions are usually a quick fluency check woven into a screen: *"merge vs rebase?"*, *"how would you undo a commit you already pushed?"*, *"what's a merge conflict?"* The junior answer recites a command; the strong answer explains the *graph move* underneath and names the safety tradeoff — "I'd `revert`, not `reset`, because it's already pushed and revert doesn't rewrite shared history." That "and here's why it's safe" clause is the whole signal.

---

## Try it

Answer aloud, as if to an interviewer:

1. What *is* a commit, and what is a branch? Why is creating a branch in Git so cheap?
2. Explain the difference between the working directory, the staging area, and the repository. What does `git add` actually do?
3. Merge vs rebase — what does each do to the history graph, and why must you never rebase commits you've already pushed?
4. You just realized the commit you pushed an hour ago broke production. Do you `reset` or `revert`, and why does it matter that it was already pushed?
5. What is a merge conflict, really — and why can't Git just resolve it for you?
6. `git pull` gave you a conflict you didn't expect. Explain what `pull` did under the hood that produced it.
7. You ran `git reset --hard` and lost an hour of committed work. What's the one command that might get it back?

*Write your answers in [ch14-git-tryit.md](../code/ch14-git-tryit.md).*

---

## The bumper sticker

> *Git isn't a set of spells — it's a graph of immutable snapshots with movable pointers (branches) into it, and every command is just moving a pointer or adding a node. Learn that model and merge, rebase, reset, and "detached HEAD" stop being scary: you can always ask "where's HEAD, and am I rewriting shared history or just my own?"*

That closes the Foundations track. The appendix pulls the whole thing together — a SQL cheat sheet, OS and networking vocabulary, and the full question bank by chapter.

---

<div align="right">

[Appendix →](../foundations-appendix.md)

</div>
