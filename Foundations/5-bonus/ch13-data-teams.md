# Chapter 13: Working with the data teams

*[← Chapter 12](../4-putting-it-together/ch12-ritual.md) · [Contents](../foundations-README.md)*

- [ ] **Mark as read**

This one's a bonus, and it's not a pop-quiz chapter — nobody is going to ask you to define a star schema in a rapid-fire round. It's here because the moment you join a real team, you discover that a whole class of problems that *look* like yours actually belong to someone else. The dashboard the product manager wants, the six-hour nightly job that keeps falling over, the "can you just pull these numbers" request, the model someone prototyped in a notebook and now wants in production — each of these has a person whose actual job it is. Knowing who they are, what they own, and the vocabulary they speak is what lets you hand the problem to the right place instead of half-solving it yourself at 11pm. The principle for this chapter: **feel where your job ends and theirs begins before reinventing their work.**

---

## The data org is one pipeline, sliced into jobs

Here's the mental model that makes all the titles click. Data moves through a pipeline — from raw events nobody can read, to clean tables, to metrics, to insight, to models that predict — and each role owns one stretch of that pipe.

> 💡 **Concept notes — the data pipeline and who owns each stretch**
> - **Raw → stored:** events, logs, and app-database rows get pulled into a central place (a *warehouse* or *lake*). The **Data Engineer** owns this plumbing.
> - **Stored → clean:** raw tables get reshaped into trustworthy, well-named models other people can query without footguns. The **Analytics Engineer** owns this transform layer.
> - **Clean → answer:** someone writes the queries and dashboards that turn those tables into "here's what's happening." The **Data Analyst** owns this.
> - **Clean → prediction:** someone uses the data to run experiments and train models that estimate or forecast. The **Data Scientist** owns this.
> - **Prediction → production:** a prototype model becomes a reliable service that serves predictions at scale. The **ML Engineer** owns this.
> The same raw click that the Data Engineer lands in the warehouse is the one the Analyst counts in a funnel and the Scientist trains a churn model on. One pipe, different stretches.

You, the software engineer, usually sit *upstream* of all of it — you build the app that emits the events — and sometimes *downstream*, consuming a model or a metric through an API. The friction happens at those two seams, which is exactly where knowing the next person's job pays off.

---

## The five roles, briefly

**Data Engineer (DE).** Builds and runs the pipelines that move data from your app into the warehouse and keep it fresh. Thinks in batch jobs, streams, schedules, and "why did last night's load fail." Lives in SQL, Python, a workflow orchestrator (Airflow and friends), and a distributed compute engine (Spark / Databricks) when the data is too big for one machine. When your service starts emitting a new event and "the numbers" need it, this is who makes that event show up downstream.

**Analytics Engineer (AE).** The relatively new role that sits between the DE and the Analyst. Takes the raw, awkward tables the DE landed and turns them into clean, documented, version-controlled models that everyone else builds on — mostly through SQL managed by a tool like dbt. If a Data Engineer is plumbing and an Analyst is asking questions, the Analytics Engineer is the one making sure the tables are trustworthy enough that the question gets a correct answer. Very SQL-heavy, very software-engineering-flavored (tests, version control, code review on SQL).

**Data Analyst (DA).** Answers business questions with data. "Did the new checkout flow lift conversion?" "Which regions are churning?" Lives in SQL and a BI tool (Tableau, Looker, Power BI), builds dashboards, and translates a vague ask into a precise query. Strong on business context and communication; lighter on engineering. When a PM wants a chart, this is the person — not you hand-rolling a one-off query against prod.

**Data Scientist (DS).** Uses statistics and modeling to *estimate things you can't directly measure* — will this user churn, what's this transaction's fraud risk, how much will demand rise. Designs and reads experiments (A/B tests), engineers features, trains models, and quantifies uncertainty. Lives in Python (pandas, notebooks), statistics, and ML. Overlaps with the AI/ML track in this collection — that track is the deeper dive on what a DS actually does day to day.

**ML Engineer (MLE).** Takes a model that works in a notebook and makes it a real, reliable system: serving it behind an API, retraining it, monitoring it for drift, keeping latency sane. The most software-engineering-like of the five — it's basically backend/infra engineering with a model in the middle (often called *MLOps*). If you're a strong SWE drifting toward data, this is the most natural bridge. Also covered more deeply in the AI/ML track.

---

## At a glance

| Role | Owns | Lives in | Pull them in when… |
|---|---|---|---|
| **Data Engineer** | Pipelines, warehouse plumbing, data freshness | SQL, Python, Airflow, Spark/Databricks | A new event needs to flow downstream, or a data job is slow/failing |
| **Analytics Engineer** | The clean, trusted table layer | SQL, dbt, version control | The numbers disagree, or tables are a mess nobody trusts |
| **Data Analyst** | Business answers, dashboards | SQL, Tableau/Looker | Someone wants a chart, a metric, or "what happened here?" |
| **Data Scientist** | Experiments, models, forecasts | Python, stats, ML | You need a prediction, an A/B test read, or a probability |
| **ML Engineer** | Models running in production | Python, serving infra, MLOps | A prototype model needs to be a reliable service |

---

## Knowing when to call them — and when not to

The trap isn't ignorance, it's *misplaced competence*. You're a capable engineer, so when a data problem lands you're tempted to just do it. Sometimes that's right; often it quietly creates a worse version of something a specialist would have done cleanly.

> 💡 **Concept notes — the do-it-yourself vs hand-it-off line**
> - **A one-off number for yourself?** Write the SQL, move on. Don't file a ticket for a count you'll use once.
> - **A number other people will *trust and repeat*?** That belongs in the modeled, tested table layer — loop in the Analytics Engineer or Analyst so the definition is one everyone shares. (Three teams quietly computing "active user" three different ways is the classic data-org bug.)
> - **A recurring dashboard or a stakeholder-facing metric?** Analyst. They'll do it better and own it going forward; your one-off query rots the moment the schema changes.
> - **A pipeline that has to run reliably on a schedule?** Data Engineer. Cron-on-a-box plus a Python script is exactly the thing they exist to replace.
> - **"Can the app predict / recommend / score X?"** Data Scientist to find out if it's feasible and build the model; ML Engineer to run it in production. Don't hard-code heuristics that are secretly a bad model.
> The tell is *ownership over time*: if the thing needs to keep working, keep being correct, and keep being trusted after you've moved on, hand it to the person whose job is to own it.

The flip side matters too: when you *are* the upstream app engineer, small choices make their lives much easier. A clean, well-named event schema; not silently changing the meaning of a column; telling the DE *before* you rename a field — these cost you minutes and save them days of forensic debugging.

---

## A small map of the tools you'll hear

You don't need to *use* these — just to recognize what someone means when they drop the name, so the conversation doesn't stall. This is a map, not a manual.

- **SQL** — the lingua franca of all five roles; everything starts here. (Chapters 1–4 of this track are your foundation.)
- **dbt** — turns SQL transformations into version-controlled, tested "models"; the Analytics Engineer's main tool.
- **Airflow** (and similar) — schedules and orchestrates pipelines as DAGs of tasks; "the nightly job" usually runs here.
- **Spark / Databricks** — distributed compute for data too big for one machine; Databricks is a hosted platform built around Spark.
- **Snowflake / BigQuery / Redshift** — cloud data warehouses; the central place the clean tables live.
- **Tableau / Looker / Power BI** — BI tools that turn queries into dashboards business users click through.

Notice none of these change the *mechanism* lessons of this track — an index is still an index, a JOIN still a JOIN. These are where those fundamentals get used at scale, by people whose whole job is one stretch of the pipe.

---

## Try it

1. A PM messages you: "Can you get me a dashboard of weekly signups by region?" Who should own this, and what's the risk if you just build it yourself?
2. Your service is about to start emitting a new `subscription_upgraded` event. Who do you tell, and *before* what?
3. Someone says "active users dropped 10%" but two dashboards show different numbers. Which role's stretch of the pipeline is the likely culprit, and why?
4. A teammate prototypes a churn-prediction model in a notebook and it works. Name the two roles involved in getting it live, and what each does.
5. Name one thing *you*, as the upstream app engineer, can do this week to make a Data Engineer's life easier.
6. For your own current or target team, write down who plays each of the five roles (some may be one person, or missing entirely — that's a signal too).

*Write your answers in [ch13-data-teams-tryit.md](../code/ch13-data-teams-tryit.md).*

---

## The bumper sticker

> *A whole class of problems that look like yours belong to someone else — the pipeline to the Data Engineer, the trusted tables to the Analytics Engineer, the dashboard to the Analyst, the prediction to the Data Scientist, the production model to the ML Engineer. Feel where your job ends and theirs begins, and you'll hand the work to the right place instead of half-rebuilding it yourself.*

That's the Foundations track, bonus included. The appendix is your cheat-sheet kit — SQL reference, OS and networking vocabularies, and a question bank by chapter — the things to skim the morning of the interview.

---

<div align="right">

[Chapter 14 →](ch14-git.md)

</div>
