"""ds subject content."""

from ._dsl import chain, ex, qa, topic

CATEGORIES = [
    {"id": "foundations", "title": "Foundations & Thinking", "color": "sky", "blurb": "Workflow, data types, EDA, causality traps and ethics."},
    {"id": "statistics", "title": "Statistics", "color": "mint", "blurb": "Describe, estimate and model: spread, intervals, regression."},
    {"id": "probability", "title": "Probability", "color": "lilac", "blurb": "Events, Bayes, expectation, distributions and the CLT."},
    {"id": "experiments", "title": "Testing & Experiments", "color": "rose", "blurb": "Hypothesis tests, power, A/B tests and metric design."},
    {"id": "data-wrangling", "title": "Data Wrangling", "color": "lemon", "blurb": "Cleaning, missing values, quality and feature preparation."},
    {"id": "visualisation", "title": "Visualisation", "color": "peach", "blurb": "Honest charts, picking the right one, and telling the story."},
    {"id": "tooling", "title": "Tooling", "color": "slate", "blurb": "SQL, pandas, NumPy, Jupyter and Spark for real datasets."},
]

TOPICS = []

TOPICS += [
    topic(
        "ds-workflow", "The Data Science Workflow (CRISP-DM)", "foundations", "basic", "WF",
        "From a fuzzy business question to a monitored answer: understand, prepare, model, evaluate, deploy, repeat.",
        "Data science is like cooking for a client. You first ask what they want to eat, then check the pantry, wash and chop, cook, taste against the order, serve, and come back next week to adjust the recipe.",
        "CRISP-DM (Cross-Industry Standard Process for Data Mining) is the most widely used framework for structuring analytics work. It has six phases: business understanding, data understanding, data preparation, modelling, evaluation and deployment. The phases are iterative, not a waterfall: evaluation often sends you back to reframe the question or collect more data. Business understanding turns a vague goal ('reduce churn') into a measurable target, a decision it will inform and a success criterion. Data understanding is where you profile sources, check coverage and spot quality problems early. Preparation (cleaning, joining, feature building) usually consumes most of the time. Evaluation must be against the business criterion, not only a model metric, and deployment includes monitoring for drift and a plan for retraining or retiring the solution. Alternatives such as OSEMN and Microsoft TDSP describe the same loop with different names.",
        ["Scoping an analytics request so everyone agrees on the decision and the metric.", "Planning a churn, forecasting or pricing project with realistic milestones.", "Explaining to stakeholders why 'just build a model' needs data work first.", "Structuring post-launch monitoring and iteration."],
        [
            "Six phases: business, data understanding, preparation, modelling, evaluation, deployment.",
            "Start from the decision the analysis will change, not from the dataset.",
            "Always build a simple baseline before anything sophisticated.",
            "Evaluate against the business success criterion, not just accuracy.",
            "Deployment means monitoring, ownership and a retraining plan.",
        ],
        [
            ex("A tiny end-to-end CRISP-DM loop", "basic", "Synthetic orders go through question, cleaning, comparison and a decision.", "python", """
                import random
                import statistics

                random.seed(7)
                # Business question: does a discount raise average basket value by more than 2?
                orders = []
                for _ in range(300):
                    discounted = random.random() < 0.5
                    value = random.gauss(40 + (3 if discounted else 0), 12)
                    orders.append((discounted, round(value, 2)))
                orders += [(True, None), (False, -5.0)]          # dirty rows found during data understanding
                print("raw rows:", len(orders))

                # Preparation: drop missing and impossible values
                clean = [(d, v) for d, v in orders if v is not None and v > 0]
                print("clean rows:", len(clean))

                # Modelling: compare group means
                disc = [v for d, v in clean if d]
                full = [v for d, v in clean if not d]
                lift = statistics.fmean(disc) - statistics.fmean(full)

                # Evaluation against the business criterion
                print(f"discount {statistics.fmean(disc):.2f} vs full price {statistics.fmean(full):.2f}, lift {lift:+.2f}")
                print("decision:", "roll out" if lift > 2 else "keep testing")
            """),
            ex("Baseline first", "intermediate", "A majority-class baseline sets the bar any churn model must beat.", "python", """
                import random
                from collections import Counter

                random.seed(1)
                customers = [{"tenure": random.randint(1, 60), "tickets": random.randint(0, 6)} for _ in range(500)]
                for c in customers:
                    c["churned"] = random.random() < (0.10 + 0.08 * c["tickets"] - 0.002 * c["tenure"])

                majority = Counter(c["churned"] for c in customers).most_common(1)[0][0]
                base_acc = sum(c["churned"] == majority for c in customers) / len(customers)
                rule_acc = sum(c["churned"] == (c["tickets"] >= 4) for c in customers) / len(customers)
                print(f"baseline (always {majority}): {base_acc:.3f}")
                print(f"rule tickets>=4:          {rule_acc:.3f}")
            """),
        ],
        ["CRISP-DM: business -> data -> prepare -> model -> evaluate -> deploy", "Success criterion: metric + threshold + decision", "Baseline: majority class / last value / mean", "df.info() · df.describe() for data understanding"],
        ["Skipping business understanding produces accurate answers to the wrong question.", "Treating the process as linear hides the need to loop back.", "Declaring success on offline metrics without checking business impact.", "No owner or monitoring after deployment means silent model decay."],
        [
            qa("basic", "What are the phases of CRISP-DM?", "Business understanding, data understanding, data preparation, modelling, evaluation and deployment. They form a loop: findings in later phases frequently send you back to earlier ones, especially from evaluation to business understanding."),
            qa("basic", "Why build a baseline before a complex model?", "A baseline (majority class, historical mean, last value) tells you the minimum performance that requires no skill. If a sophisticated model barely beats it, the extra complexity and maintenance cost are not justified."),
            qa("intermediate", "Which phase usually takes the most time and why?", "Data preparation, often 60-80% of effort. Real data is spread across systems, has missing values, inconsistent keys and definitions, and features must be engineered without leaking future information."),
            qa("intermediate", "How do you turn 'reduce churn' into a workable problem?", "Define churn precisely (e.g., no purchase in 60 days), pick the decision it drives (who gets a retention offer), the metric (retained revenue per offer cost) and the prediction horizon. Then confirm the data exists at prediction time."),
            qa("advanced", "What does deployment involve beyond shipping a model?", "Monitoring input drift and performance, alerting, ownership, documentation, a retraining cadence and a rollback path. It also includes measuring real business impact, ideally through a controlled experiment."),
        ],
        ["eda", "metrics-design", "data-leakage"],
        chain(
            ("Business", "frame question", "Business understanding", "Turn the request into a decision, a measurable target and a success criterion."),
            ("Data", "profile sources", "Data understanding", "Inventory sources, check coverage, types and quality, and form first hypotheses.", "question"),
            ("Prepare", "clean + features", "Data preparation", "Clean, join and build features using only information available at decision time.", "raw data"),
            ("Model", "baseline first", "Modelling", "Start with a baseline, then try models of increasing complexity.", "table"),
            ("Evaluate", "vs business goal", "Evaluation", "Judge results against the business criterion; loop back if they fall short.", "scores"),
            ("Deploy", "monitor + iterate", "Deployment", "Ship, monitor drift and impact, and schedule retraining or retirement.", "approved"),
        ),
    ),
    topic(
        "data-types", "Data Types & Levels of Measurement", "foundations", "basic", "DT",
        "Nominal, ordinal, interval, ratio: the level decides which statistics and charts make sense.",
        "Numbers on football shirts, finishing places in a race, temperatures in Celsius and race times are all numbers, but only the race times let you say one is twice the other.",
        "Stevens' levels of measurement classify variables by which operations are meaningful. Nominal data are labels with no order (country, colour); you can count and take the mode. Ordinal data have an order but unequal gaps (survey ratings, education level); medians and percentiles are valid, means are debatable. Interval data have equal gaps but no true zero (Celsius, calendar year), so differences are meaningful but ratios are not. Ratio data have a true zero (height, revenue, duration), so every arithmetic operation including ratios is valid. Separately, data are qualitative (categorical) or quantitative, and quantitative data are discrete (counts) or continuous (measurements). The level drives the choice of summary, test (e.g., chi-square for nominal, Mann-Whitney for ordinal, t-test for interval/ratio) and chart. Storage type is not measurement level: a zip code stored as an integer is still nominal.",
        ["Choosing the right summary statistic for each column during EDA.", "Picking a statistical test that matches the variable type.", "Deciding how to encode features for a model.", "Catching meaningless operations such as averaging ID numbers."],
        [
            "Nominal: categories only; mode and counts.",
            "Ordinal: ordered; median and percentiles, gaps not equal.",
            "Interval: equal gaps, arbitrary zero; differences but not ratios.",
            "Ratio: true zero; ratios like 'twice as long' are meaningful.",
            "Storage dtype (int, str) does not define the measurement level.",
        ],
        [
            ex("Valid summaries per level", "basic", "Parse a synthetic CSV and summarise each column appropriately.", "python", """
                import csv
                import io
                import statistics

                raw = '''city,satisfaction,temp_c,spend
                Pune,4,31,120.5
                Oslo,2,4,80.0
                Pune,5,29,200.0
                Lima,3,18,95.25
                Oslo,4,6,60.0'''
                rows = list(csv.DictReader(io.StringIO(raw)))

                cities = [r["city"] for r in rows]                       # nominal
                sat = [int(r["satisfaction"]) for r in rows]             # ordinal (1-5)
                temp = [float(r["temp_c"]) for r in rows]                # interval
                spend = [float(r["spend"]) for r in rows]                # ratio

                print("nominal  mode:", statistics.mode(cities))
                print("ordinal  median:", statistics.median(sat))
                print("interval mean diff vs Oslo row:", temp[0] - temp[1])
                print("ratio    max/min spend:", round(max(spend) / min(spend), 2))
            """),
            ex("Why Celsius ratios mislead", "intermediate", "20C is not twice as hot as 10C, but 20K is twice 10K.", "python", """
                c1, c2 = 10.0, 20.0
                k1, k2 = c1 + 273.15, c2 + 273.15
                print("Celsius ratio:", c2 / c1)
                print("Kelvin ratio: ", round(k2 / k1, 3))
                zip_codes = [10001, 94105, 60601]
                print("mean zip code is meaningless:", sum(zip_codes) / len(zip_codes))
            """),
        ],
        ["Nominal: mode, counts · Ordinal: median, IQR", "Interval: mean, sd, differences · Ratio: + ratios, CV", "df['col'].astype('category')", "pd.CategoricalDtype(['low','mid','high'], ordered=True)"],
        ["Averaging Likert scores treats ordinal gaps as equal; state that assumption.", "IDs and zip codes stored as numbers get scaled or averaged by mistake.", "Percent change on interval data (temperature) is not meaningful."],
        [
            qa("basic", "What are the four levels of measurement?", "Nominal (unordered categories), ordinal (ordered categories with unequal gaps), interval (equal gaps, no true zero) and ratio (equal gaps with a true zero). Each level allows all operations of the previous one plus more."),
            qa("basic", "Is a 1-5 satisfaction rating interval or ordinal?", "Strictly ordinal: the gap between 1 and 2 need not equal the gap between 4 and 5. In practice means are often reported for Likert items, but medians, distributions and non-parametric tests are the safer default."),
            qa("intermediate", "What is the difference between interval and ratio data?", "Both have equal intervals, but ratio data have a meaningful zero meaning 'none of the quantity'. So 40 kg is twice 20 kg, while 40C is not twice as hot as 20C."),
            qa("intermediate", "How does measurement level affect test choice?", "Nominal outcomes use counts and chi-square or proportion tests; ordinal outcomes use rank-based tests such as Mann-Whitney or Kruskal-Wallis; interval/ratio outcomes can use t-tests, ANOVA and regression when assumptions hold."),
        ],
        ["descriptive-stats", "encoding-categoricals", "nonparametric-tests"],
        chain(
            ("Nominal", "labels", "Nominal", "Only equality is meaningful: count categories and report the mode."),
            ("Ordinal", "ordered", "Ordinal", "Order is meaningful: medians and percentiles are valid.", "+ order"),
            ("Interval", "equal gaps", "Interval", "Differences are meaningful: means and standard deviations work.", "+ distance"),
            ("Ratio", "true zero", "Ratio", "A true zero allows ratios, percent change and geometric means.", "+ zero"),
        ),
    ),
    topic(
        "eda", "Exploratory Data Analysis (EDA)", "foundations", "basic", "ED",
        "Look before you model: shape, types, missingness, distributions, relationships and surprises.",
        "EDA is the walk-around inspection before buying a used car. You look at the tyres, open the bonnet and check under the seats before you trust the shiny brochure.",
        "Exploratory data analysis, popularised by John Tukey, is the open-ended investigation of a dataset to understand its structure and quality before formal modelling. A typical pass checks the number of rows and columns, data types, the grain (what one row represents), uniqueness of keys and missing values per column. Then univariate analysis summarises each variable with counts, central tendency, spread and a histogram or bar chart. Bivariate and multivariate analysis look at relationships via scatter plots, grouped summaries, correlation matrices and cross-tabs. EDA also surfaces data problems: impossible values, unit mismatches, duplicated records, sudden level shifts over time. Its output is a list of findings, cleaning tasks and hypotheses, not a final answer. Hypotheses suggested by EDA must be confirmed on fresh data, because exploring many patterns guarantees some spurious ones.",
        ["Profiling a new dataset before a modelling project.", "Finding data quality issues before they reach a dashboard.", "Generating hypotheses for experiments or deeper analysis.", "Explaining the data's limitations to stakeholders."],
        [
            "Confirm the grain: what does one row represent?",
            "Profile each column: type, missing %, distinct count, range.",
            "Plot distributions; summary numbers alone hide shapes (Anscombe).",
            "Segment by key dimensions and by time to spot shifts.",
            "Treat EDA findings as hypotheses to confirm, not conclusions.",
        ],
        [
            ex("A stdlib column profiler", "basic", "Count missing values, distinct values and ranges per column.", "python", """
                import csv
                import io

                raw = '''order_id,country,amount,channel
                1,IN,120,web
                2,US,,app
                3,IN,95,web
                3,IN,95,web
                4,DE,-10,store
                5,,300,app'''
                rows = list(csv.DictReader(io.StringIO(raw)))
                print("rows:", len(rows), "columns:", list(rows[0]))
                for col in rows[0]:
                    vals = [r[col] for r in rows]
                    present = [v for v in vals if v != ""]
                    line = f"{col:9} missing={len(vals) - len(present)} distinct={len(set(present))}"
                    try:
                        nums = [float(v) for v in present]
                        line += f" min={min(nums)} max={max(nums)}"
                    except ValueError:
                        pass
                    print(line)
                ids = [r["order_id"] for r in rows]
                print("duplicate ids:", sorted({i for i in ids if ids.count(i) > 1}))
            """),
            ex("Anscombe: same stats, different stories", "intermediate", "Two datasets share mean and correlation but differ in shape.", "python", """
                import statistics as st

                x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
                y1 = [8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68]
                y2 = [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74]
                for name, y in (("set I", y1), ("set II", y2)):
                    print(name, round(st.fmean(y), 2), round(st.variance(y), 2), round(st.correlation(x, y), 3))
                print("set II is a curve, not a line: always plot it")
            """),
            ex("pandas EDA pass", "intermediate", "The usual first commands on a DataFrame.", "python", """
                import pandas as pd

                df = pd.read_csv("orders.csv", parse_dates=["created_at"])
                df.info()
                print(df.describe(include="all").T)
                print(df.isna().mean().sort_values(ascending=False))
                print(df["country"].value_counts(dropna=False).head(10))
                print(df.groupby(df["created_at"].dt.to_period("M"))["amount"].agg(["count", "mean"]))
            """, False),
        ],
        ["df.shape · df.info() · df.describe()", "df.isna().mean()", "df['c'].value_counts(dropna=False)", "df.corr(numeric_only=True)", "df.groupby('k')['v'].agg(['mean','median','count'])"],
        ["Summary statistics without plots can hide nonlinearity and clusters.", "Testing every pattern found during EDA inflates false discoveries.", "Ignoring the time dimension misses pipeline breaks and seasonality."],
        [
            qa("basic", "What do you check first in EDA?", "Shape, grain, data types, key uniqueness and missingness per column. Then distributions of each variable and obvious impossible values, before looking at relationships."),
            qa("basic", "What is Anscombe's quartet?", "Four small datasets with nearly identical means, variances, correlations and regression lines that look completely different when plotted. It shows why you must visualise data instead of trusting summary numbers."),
            qa("intermediate", "How is EDA different from confirmatory analysis?", "EDA is open-ended and generates hypotheses; confirmatory analysis tests a pre-specified hypothesis with controlled error rates. Using the same data for both overstates significance, so confirm EDA findings on new data or a holdout."),
            qa("intermediate", "How do you approach EDA on a dataset with hundreds of columns?", "Automate profiling (missing %, cardinality, constant columns, type), group columns by domain, prioritise those linked to the target or decision, and use correlation or mutual information screens. Then deep-dive on the shortlisted columns visually."),
        ],
        ["ds-workflow", "data-cleaning", "viz-principles"],
        chain(
            ("Shape", "rows, cols, grain", "Structure", "Confirm what a row means and check key uniqueness."),
            ("Profile", "types, missing", "Column profile", "Type, missing %, distinct values and ranges per column.", "columns"),
            ("Univariate", "distributions", "One variable", "Histograms, bar charts and summaries reveal shape and outliers.", "profile"),
            ("Relations", "pairs, segments", "Relationships", "Scatter plots, cross-tabs and grouped stats show how variables move together.", "variables"),
            ("Findings", "hypotheses", "Output", "List cleaning tasks, caveats and hypotheses to confirm later.", "insights"),
        ),
    ),
    topic(
        "correlation-causation", "Correlation vs Causation", "foundations", "intermediate", "CC",
        "Two things moving together does not mean one drives the other: look for confounders, reverse causality and chance.",
        "Ice cream sales and drownings rise together every summer. Ice cream is not dangerous; hot weather sends people both to the ice cream van and to the beach.",
        "Correlation measures how strongly two variables move together; causation means intervening on one changes the other. A correlation can arise from a confounder that drives both variables, from reverse causality (Y causes X), from selection effects in how the data were collected, or simply from chance when many pairs are examined. Randomised controlled experiments break these alternatives because random assignment makes groups comparable on all confounders, measured or not. When experiments are impossible, causal inference methods try to approximate them: adjusting for confounders in regression, matching or propensity scores, difference-in-differences, instrumental variables and regression discontinuity. Each relies on assumptions that must be argued, often using causal diagrams (DAGs). Bradford Hill criteria such as temporality, dose-response and consistency offer a qualitative checklist. Conversely, no correlation does not prove no causation, since effects can cancel or be nonlinear.",
        ["Challenging a claim like 'users of feature X retain better, so push X to everyone'.", "Designing an experiment instead of relying on observational data.", "Choosing control variables for an observational analysis.", "Explaining spurious trends in dashboards to stakeholders."],
        [
            "Confounders, reverse causality, selection and chance all create correlation.",
            "Randomisation is the gold standard for causal claims.",
            "Adjust for confounders, never for mediators or colliders.",
            "Quasi-experiments: diff-in-diff, IV, regression discontinuity, matching.",
            "Zero correlation does not rule out a (nonlinear) causal effect.",
        ],
        [
            ex("A confounder creates correlation", "intermediate", "Temperature drives both ice cream and swimming incidents.", "python", """
                import random
                import statistics as st

                random.seed(3)
                temp = [random.uniform(5, 35) for _ in range(400)]
                ice = [2 * t + random.gauss(0, 8) for t in temp]
                swim = [0.5 * t + random.gauss(0, 3) for t in temp]
                print("corr(ice, swim):", round(st.correlation(ice, swim), 3))

                # Stratify by temperature band: the correlation largely disappears
                for lo in (5, 15, 25):
                    idx = [i for i, t in enumerate(temp) if lo <= t < lo + 10]
                    r = st.correlation([ice[i] for i in idx], [swim[i] for i in idx])
                    print(f"temp {lo}-{lo + 10}: corr = {r:.3f}")
            """),
            ex("Randomisation breaks confounding", "advanced", "Self-selected users look better; randomly assigned users show the true effect.", "python", """
                import random
                import statistics as st

                random.seed(11)
                users = [random.gauss(0, 1) for _ in range(4000)]          # hidden engagement
                TRUE_EFFECT = 0.2

                def outcome(eng, treated):
                    return 1.0 * eng + (TRUE_EFFECT if treated else 0) + random.gauss(0, 1)

                self_sel = [(eng, eng > 0.3) for eng in users]           # engaged users opt in
                rand = [(eng, random.random() < 0.5) for eng in users]
                for name, data in (("self-selected", self_sel), ("randomised", rand)):
                    t = [outcome(e, True) for e, tr in data if tr]
                    c = [outcome(e, False) for e, tr in data if not tr]
                    print(f"{name:14} estimated effect = {st.fmean(t) - st.fmean(c):.3f}")
                print("true effect =", TRUE_EFFECT)
            """),
        ],
        ["Confounder: Z -> X and Z -> Y", "Randomise treatment to estimate causal effect", "DiD = (T_after - T_before) - (C_after - C_before)", "smf.ols('y ~ x + confounder', df).fit()"],
        ["Controlling for a mediator removes part of the real effect.", "Conditioning on a collider (e.g., only hired applicants) creates fake correlations.", "With many variables, some strong correlations appear by pure chance."],
        [
            qa("basic", "Why does correlation not imply causation?", "A correlation can come from a confounder driving both variables, reverse causation, selection effects or chance. Only when those are ruled out, ideally by randomisation, can you claim one variable causes the other."),
            qa("intermediate", "What is a confounder? Give an example.", "A variable that causally affects both the treatment and the outcome. For example, age affects both coffee drinking and heart disease risk, so a raw coffee-heart disease correlation partly reflects age."),
            qa("intermediate", "How can you estimate causal effects without an experiment?", "Use quasi-experimental designs: difference-in-differences with a comparable control group, regression discontinuity around a threshold, instrumental variables, or matching/propensity scores on observed confounders. Each requires untestable assumptions such as parallel trends or no unmeasured confounding."),
            qa("advanced", "What is collider bias?", "A collider is a variable caused by both X and Y. Conditioning on it, for instance analysing only admitted students or only hospitalised patients, induces an association between X and Y even when none exists."),
        ],
        ["simpsons-paradox", "ab-testing", "pearson-spearman"],
        chain(
            ("Observe", "X and Y move", "Correlation", "A strong correlation between X and Y is noticed in data."),
            ("Confounder?", "common cause Z", "Rule out Z", "Is there a variable that drives both? Adjust or stratify.", "r = 0.8"),
            ("Direction?", "Y causes X?", "Reverse causality", "Check timing: the cause must come before the effect.", "candidate"),
            ("Chance?", "many pairs tried", "Multiple looks", "Was this one of hundreds of correlations scanned?", "candidate"),
            ("Experiment", "randomise X", "Confirm", "Randomly assign X and measure Y to establish causation.", "hypothesis"),
        ),
    ),
    topic(
        "simpsons-paradox", "Simpson's Paradox", "foundations", "intermediate", "SP",
        "A trend in every subgroup can reverse when the groups are combined, because group sizes differ.",
        "One surgeon looks worse overall but better in every category, because she takes most of the hard cases. Pooling the cases hides the case mix.",
        "Simpson's paradox occurs when an association that holds within each subgroup reverses or disappears in the aggregated data. It happens because a lurking variable (the grouping) is related to both the treatment and the outcome, and the groups have very different sizes or base rates. Classic examples include the UC Berkeley admissions data, where women appeared to be admitted less overall but were admitted at similar or higher rates within most departments because they applied more to competitive ones, and kidney stone treatments where treatment A won in both small and large stones but lost overall. The paradox is a weighted-average effect: the aggregate rate weights each subgroup by its share, and those shares differ between the compared arms. Which answer is 'right' depends on the causal structure: if the grouping variable is a confounder, use the stratified result; if it is a mediator caused by the treatment, the aggregate may be correct. In product analytics it appears when mix shifts between platforms, regions or new versus returning users.",
        ["Comparing conversion rates across platforms with changing traffic mix.", "Evaluating treatments or vendors that handle different case difficulty.", "Explaining a metric drop that is really a mix shift.", "Checking A/B results by segment when randomisation is imperfect."],
        [
            "Aggregate rates are weighted averages of subgroup rates.",
            "Reversal requires the grouping to relate to both treatment and outcome.",
            "Decide using the causal graph: stratify on confounders, not mediators.",
            "Mix-shift analysis separates rate change from composition change.",
        ],
        [
            ex("Kidney stone reversal", "intermediate", "Treatment A wins in each group but loses overall.", "python", """
                data = {
                    ("A", "small"): (81, 87), ("A", "large"): (192, 263),
                    ("B", "small"): (234, 270), ("B", "large"): (55, 80),
                }
                for size in ("small", "large"):
                    a = data[("A", size)]; b = data[("B", size)]
                    print(f"{size:5}: A {a[0] / a[1]:.1%}  B {b[0] / b[1]:.1%}")
                for t in ("A", "B"):
                    ok = sum(v[0] for k, v in data.items() if k[0] == t)
                    n = sum(v[1] for k, v in data.items() if k[0] == t)
                    print(f"overall {t}: {ok / n:.1%} (n={n})")
            """),
            ex("Mix shift decomposition", "advanced", "Overall conversion fell even though every platform improved.", "python", """
                before = {"desktop": (5000, 0.060), "mobile": (5000, 0.020)}
                after = {"desktop": (2000, 0.065), "mobile": (8000, 0.022)}

                def overall(d):
                    n = sum(v[0] for v in d.values())
                    return sum(v[0] * v[1] for v in d.values()) / n

                print(f"overall before {overall(before):.4f} after {overall(after):.4f}")
                n_b = sum(v[0] for v in before.values()); n_a = sum(v[0] for v in after.values())
                rate_effect = sum(before[k][0] / n_b * (after[k][1] - before[k][1]) for k in before)
                mix_effect = sum((after[k][0] / n_a - before[k][0] / n_b) * after[k][1] for k in before)
                print(f"rate effect {rate_effect:+.4f}, mix effect {mix_effect:+.4f}")
            """),
        ],
        ["overall = sum(share_g * rate_g)", "df.groupby(['treat','segment'])['y'].mean().unstack()", "Mix effect + rate effect = total change", "Stratify on confounders; not on mediators"],
        ["Blindly stratifying on a variable caused by the treatment removes real effects.", "Small subgroups produce noisy rates; show counts alongside percentages.", "Dashboards with only top-line rates hide composition changes."],
        [
            qa("basic", "What is Simpson's paradox?", "A pattern where a relationship holds in every subgroup but reverses or vanishes when the subgroups are combined. It is caused by a lurking variable correlated with both the grouping of interest and the outcome, combined with unequal group sizes."),
            qa("intermediate", "Explain the Berkeley admissions case.", "Overall, men were admitted at a higher rate than women. Within most departments women were admitted at equal or higher rates, but women applied disproportionately to departments with low admission rates, which pulled their aggregate rate down."),
            qa("intermediate", "How do you decide whether to trust the aggregated or stratified result?", "Use the causal structure. If the subgroup variable is a confounder (affects both treatment and outcome, not caused by treatment), the stratified estimate answers the causal question; if it is a mediator caused by the treatment, aggregate effects are appropriate."),
            qa("advanced", "Overall conversion dropped but every country improved. What happened and how do you show it?", "The traffic mix shifted toward lower-converting countries. Decompose the change into a rate effect (holding mix fixed) and a mix effect (holding rates fixed), and present both alongside the segment table."),
        ],
        ["correlation-causation", "survivorship-selection-bias", "dashboards-storytelling"],
        chain(
            ("Segment A", "A beats B", "Within groups", "In each subgroup treatment A has the higher success rate."),
            ("Group sizes", "unequal mix", "Composition", "A was mostly given the hard cases, B the easy ones.", "rates"),
            ("Aggregate", "B beats A", "Pooled", "Pooling weights rates by the unequal mix and the trend reverses.", "weights"),
            ("Causal view", "confounder?", "Decide", "If case difficulty is a confounder, trust the stratified comparison.", "paradox"),
        ),
    ),
    topic(
        "survivorship-selection-bias", "Survivorship & Selection Bias", "foundations", "intermediate", "SB",
        "If only some units make it into your data, your conclusions describe the survivors, not the population.",
        "In WWII, analysts studied bullet holes on returning bombers. Abraham Wald pointed out that planes hit in the engines never came back, so armour belonged where the survivors had no holes.",
        "Selection bias arises when the process that puts observations into your dataset is related to the outcome you study. Survivorship bias is a special case where only units that 'survived' some filter are visible: successful startups, funds that were not closed, customers who did not churn, or bombers that returned. Other forms include self-selection (volunteers or opt-in survey respondents differ from non-respondents), attrition in longitudinal studies, non-response bias, and collider/conditioning bias from filtering on a variable affected by both cause and outcome. Selection bias cannot be fixed by collecting more of the same data; it changes what the sample represents. Remedies include defining the population and sampling frame up front, tracking the full cohort from the start (including failures), weighting by inverse probability of selection, Heckman-style correction, and randomisation. A useful habit is to always ask: what would the missing rows look like, and why are they missing?",
        ["Analysing customer feedback that only engaged users submit.", "Evaluating investment strategies from currently listed funds or stocks.", "Studying which features predict success using only successful companies.", "Interpreting model performance where only approved applicants have labels."],
        [
            "Ask how rows got into the dataset and who is missing.",
            "More data from a biased process does not reduce bias.",
            "Track full cohorts from a fixed start date, including failures.",
            "Inverse probability weighting can correct known selection rates.",
            "Loan or fraud models trained only on approved cases suffer selection bias.",
        ],
        [
            ex("Survivorship inflates fund returns", "intermediate", "Funds that lost money are closed and vanish from the database.", "python", """
                import random
                import statistics as st

                random.seed(5)
                funds = [random.gauss(0.0, 0.10) for _ in range(1000)]   # true mean return 0%
                survivors = [r for r in funds if r > -0.05]               # losers get closed
                print(f"all funds mean return:  {st.fmean(funds):+.3%}")
                print(f"surviving funds mean:   {st.fmean(survivors):+.3%}")
                print(f"funds dropped: {len(funds) - len(survivors)}")
            """),
            ex("Correcting with inverse probability weights", "advanced", "Satisfied users answer surveys more often; weighting fixes it.", "python", """
                import random

                random.seed(8)
                users = [random.random() < 0.6 for _ in range(10000)]      # True = satisfied
                p_respond = {True: 0.30, False: 0.10}
                responses = [s for s in users if random.random() < p_respond[s]]
                naive = sum(responses) / len(responses)
                w = [1 / p_respond[s] for s in responses]
                weighted = sum(wi for wi, s in zip(w, responses) if s) / sum(w)
                print(f"true satisfied share {sum(users) / len(users):.3f}")
                print(f"naive survey share   {naive:.3f}")
                print(f"IPW corrected share  {weighted:.3f}")
            """),
        ],
        ["Weight = 1 / P(selected | x)", "Cohort analysis: fix start date, follow everyone", "Compare respondents vs non-respondents on known fields", "Reject inference for approve/decline models"],
        ["Survey results from opt-in respondents rarely generalise to all users.", "Backtests on today's index constituents ignore delisted companies.", "Filtering to 'active users' before measuring retention is circular."],
        [
            qa("basic", "What is survivorship bias?", "Drawing conclusions only from units that passed some selection filter while ignoring those that did not. Studying only successful companies or only surviving funds makes risky strategies look better than they are."),
            qa("intermediate", "How is selection bias different from sampling error?", "Sampling error is random and shrinks as the sample grows. Selection bias is systematic: the selection mechanism is related to the outcome, so a larger sample just estimates the wrong quantity more precisely."),
            qa("intermediate", "A model is trained only on approved loans. What is the problem?", "Outcomes are observed only for applicants the old policy approved, so the model never learns about the declined population and may misjudge risk there. Remedies include reject inference, small randomised approval of borderline applicants, and careful monitoring."),
            qa("advanced", "How would you correct for non-response bias in a survey?", "Compare respondents with the full population on known attributes, model the response probability, and reweight responses by the inverse of that probability or with post-stratification/raking to known margins. This only corrects bias explained by observed variables."),
        ],
        ["sampling-bias", "simpsons-paradox", "correlation-causation"],
        chain(
            ("Population", "everyone", "Start", "The full population of funds, users or planes you care about."),
            ("Filter", "survive / respond", "Selection", "Some process decides who ends up in your data.", "all units"),
            ("Sample", "visible only", "Biased data", "The remaining rows differ systematically from the dropped ones.", "survivors"),
            ("Correct", "IPW, cohorts", "Remedy", "Follow full cohorts, reweight, or randomise to recover the truth.", "biased est."),
        ),
    ),
    topic(
        "data-leakage", "Data Leakage", "foundations", "advanced", "DL",
        "When information unavailable at prediction time sneaks into training, offline scores lie.",
        "Leakage is a student who saw the exam answers while studying. They score perfectly in practice, then fail the real exam where no answers are lying around.",
        "Data leakage happens when a model or analysis uses information that would not be available at the moment the prediction or decision is made, producing optimistic offline results that collapse in production. Target leakage occurs when a feature is a consequence or proxy of the label, such as 'refund_issued' when predicting fraud or a diagnosis code recorded after the event. Train-test contamination occurs when preprocessing (scaling, imputation, feature selection, target encoding) is fitted on the whole dataset before splitting, letting test statistics influence training. Temporal leakage comes from random splits on time-ordered data, so the model learns from the future. Group leakage happens when the same customer or patient appears in both train and test. Prevention means building features 'as of' the prediction timestamp, splitting before any fitting, using pipelines that fit transforms inside cross-validation folds, splitting by time or group, and treating suspiciously high scores as a bug until proven otherwise.",
        ["Reviewing a churn or fraud model with surprisingly high accuracy.", "Designing time-based train/validation splits for forecasting.", "Building point-in-time correct feature tables.", "Auditing target-encoding and imputation steps in pipelines."],
        [
            "Ask for every feature: would I know this at prediction time?",
            "Split first, then fit scalers, imputers and encoders on train only.",
            "Use time-based splits for temporal data and group splits for repeated entities.",
            "Wrap preprocessing in a Pipeline so CV refits it per fold.",
            "Too-good-to-be-true metrics usually indicate leakage.",
        ],
        [
            ex("Leaky scaling vs proper scaling", "intermediate", "Fitting normalisation on all data leaks test information.", "python", """
                import random
                import statistics as st

                random.seed(2)
                data = [random.gauss(50, 10) for _ in range(80)] + [random.gauss(90, 10) for _ in range(20)]
                train, test = data[:80], data[80:]                     # test comes from a shifted period

                mu_all, sd_all = st.fmean(data), st.stdev(data)        # leaky: uses test rows
                mu_tr, sd_tr = st.fmean(train), st.stdev(train)        # correct: train only
                print(f"leaky   mean={mu_all:.1f} sd={sd_all:.1f}")
                print(f"correct mean={mu_tr:.1f} sd={sd_tr:.1f}")
                z_test = [(x - mu_tr) / sd_tr for x in test]
                print(f"test rows look like {st.fmean(z_test):.1f} sd above train: the shift stays visible")
            """),
            ex("Target leakage from a post-event feature", "intermediate", "A feature recorded after the label makes a perfect, useless model.", "python", """
                import random

                random.seed(4)
                rows = []
                for _ in range(1000):
                    fraud = random.random() < 0.05
                    amount = random.gauss(300 if fraud else 100, 60)
                    chargeback = fraud and random.random() < 0.97        # known only weeks later
                    rows.append((amount, chargeback, fraud))

                acc_leaky = sum((cb == f) for _, cb, f in rows) / len(rows)
                acc_honest = sum(((a > 220) == f) for a, _, f in rows) / len(rows)
                print(f"rule on chargeback flag (leaky): {acc_leaky:.3f}")
                print(f"rule on amount (available now):  {acc_honest:.3f}")
            """),
            ex("Leak-safe pipeline in scikit-learn", "advanced", "Preprocessing is refit inside each time-ordered fold.", "python", """
                from sklearn.pipeline import make_pipeline
                from sklearn.impute import SimpleImputer
                from sklearn.preprocessing import StandardScaler
                from sklearn.linear_model import LogisticRegression
                from sklearn.model_selection import TimeSeriesSplit, cross_val_score

                pipe = make_pipeline(SimpleImputer(strategy="median"), StandardScaler(), LogisticRegression(max_iter=1000))
                scores = cross_val_score(pipe, X_sorted_by_time, y, cv=TimeSeriesSplit(n_splits=5), scoring="roc_auc")
                print(scores.mean())
            """, False),
        ],
        ["train_test_split before fit_transform", "make_pipeline(imputer, scaler, model)", "TimeSeriesSplit · GroupKFold", "Point-in-time join: feature_ts <= prediction_ts"],
        ["Target encoding computed on full data leaks the label; use out-of-fold encoding.", "Duplicate or near-duplicate rows across train and test inflate scores.", "IDs or timestamps can encode the label when data were sorted by outcome.", "Feature selection on all data before CV is a subtle leak."],
        [
            qa("basic", "What is data leakage?", "Using information during training that will not be available when the model makes real predictions. It yields overly optimistic validation scores and a model that underperforms in production."),
            qa("intermediate", "Give examples of target leakage.", "Using 'account_closed_date' to predict churn, 'treatment_given' to predict diagnosis, or 'chargeback' to predict fraud. These features are consequences of the label and are recorded after the moment of prediction."),
            qa("intermediate", "Why must preprocessing be fit only on training data?", "Statistics such as means, standard deviations, imputation values or category encodings computed on all data incorporate test-set information. Fitting them inside a pipeline per fold keeps the evaluation honest."),
            qa("advanced", "How do you build leak-free features for a time-based problem?", "Define a prediction timestamp per row and compute every feature using only events strictly before it (point-in-time joins). Validate with forward-chaining time splits and include a gap if labels mature with delay."),
            qa("advanced", "Your model has 0.99 AUC on a hard problem. What do you do?", "Assume leakage until disproven: inspect feature importances for post-event or ID-like features, check for duplicates and entity overlap across splits, verify the split respects time, and re-run with suspicious features removed."),
        ],
        ["ds-workflow", "feature-engineering", "scaling-normalisation"],
        chain(
            ("Raw events", "timestamps", "Source", "Events with timestamps for each entity."),
            ("Cutoff", "prediction time", "Point in time", "Fix the moment the prediction would be made.", "events"),
            ("Features", "before cutoff", "Build", "Use only information strictly before the cutoff.", "as-of data"),
            ("Split", "time / group", "Validate", "Split by time or entity, then fit transforms on train only.", "features"),
            ("Score", "honest metric", "Evaluate", "Metrics now reflect what production will see.", "folds"),
        ),
    ),
    topic(
        "data-ethics-privacy", "Data Ethics & Privacy (PII, Anonymisation, k-Anonymity)", "foundations", "advanced", "EP",
        "Collect less, protect what you keep, and know that removing names is not anonymisation.",
        "Removing names from medical records is like blurring faces in a photo of a small village: neighbours still recognise people by their house, car and dog.",
        "Personally identifiable information (PII) is any data that can identify a person directly (name, email, national ID) or indirectly when combined (birth date, zip code, gender). Regulations such as GDPR, India's DPDP Act, CCPA and HIPAA require a lawful basis, purpose limitation, data minimisation, retention limits and data subject rights. Pseudonymisation replaces identifiers with tokens, for example a keyed SHA-256 hash with a secret salt, but the data remain personal because re-linking is possible. Anonymisation must make re-identification not reasonably possible; Latanya Sweeney showed 87% of Americans are unique on zip code, birth date and sex. k-anonymity requires every combination of quasi-identifiers to be shared by at least k records, achieved by generalisation (age bands, zip prefixes) and suppression; l-diversity and t-closeness add protection for sensitive attributes. Differential privacy adds calibrated noise to aggregates with a formal privacy budget. Ethics also covers fairness, consent, transparency and avoiding harmful proxies in models.",
        ["Preparing a dataset to share with analysts or vendors.", "Designing logging and analytics events without raw PII.", "Reviewing a model for proxy discrimination.", "Answering a privacy review or data protection impact assessment."],
        [
            "Minimise: collect and keep only what the purpose needs.",
            "Pseudonymised data is still personal data under GDPR.",
            "Use keyed hashing (HMAC-SHA256) with a secret from a vault, never MD5/SHA-1 or unsalted hashes.",
            "k-anonymity: every quasi-identifier combination appears at least k times.",
            "Differential privacy gives a mathematical bound on what aggregates reveal.",
        ],
        [
            ex("Pseudonymise with a keyed SHA-256", "intermediate", "The secret comes from the environment; without it a throwaway random key is used for this run only.", "python", """
                import hashlib
                import hmac
                import os
                import secrets

                # In production load this from a secrets manager; never commit a real value.
                env_salt = os.environ.get("PSEUDONYM_SALT")
                SALT = env_salt.encode() if env_salt else secrets.token_bytes(32)

                def pseudonym(value: str) -> str:
                    normalised = value.strip().lower().encode()
                    return hmac.new(SALT, normalised, hashlib.sha256).hexdigest()[:16]

                emails = ["user1@example.com", "USER1@example.com ", "user2@example.com"]
                for e in emails:
                    print(repr(e), "->", pseudonym(e))
                print("same person, same token:", pseudonym(emails[0]) == pseudonym(emails[1]))
            """),
            ex("Check and achieve k-anonymity", "advanced", "Generalise age and zip code until every group has at least k rows.", "python", """
                from collections import Counter

                rows = [(34, "411045", "F"), (36, "411038", "F"), (35, "411001", "F"),
                        (52, "560034", "M"), (58, "560001", "M"), (51, "560095", "M"),
                        (23, "110017", "F"), (27, "110025", "F"), (29, "110001", "F")]

                def min_group(qis):
                    return min(Counter(qis).values())

                print("raw k =", min_group(rows))
                generalised = [(f"{a // 10 * 10}-{a // 10 * 10 + 9}", z[:3] + "***", g) for a, z, g in rows]
                print("generalised k =", min_group(generalised))
                for key, n in sorted(Counter(generalised).items()):
                    print(key, n)
            """),
            ex("Laplace noise for a private count", "advanced", "Differential privacy adds noise scaled to sensitivity / epsilon.", "python", """
                import math
                import random

                random.seed(0)

                def laplace(scale):
                    u = random.random() - 0.5
                    return -scale * math.copysign(1, u) * math.log(1 - 2 * abs(u))

                true_count = 412
                for eps in (0.1, 1.0, 5.0):
                    noisy = [round(true_count + laplace(1 / eps)) for _ in range(3)]
                    print(f"epsilon={eps}: {noisy}")
            """),
        ],
        ["hmac.new(secret, value, hashlib.sha256).hexdigest()", "k = min(group sizes over quasi-identifiers)", "Generalise: age -> band, zip -> prefix", "DP noise ~ Laplace(sensitivity / epsilon)", "df.drop(columns=pii_cols)"],
        ["Unsalted hashes of emails or phone numbers are trivially reversed by lookup tables.", "Free-text fields and timestamps often leak identity even after dropping ID columns.", "k-anonymity alone fails when everyone in a group shares the same sensitive value.", "Hardcoding the pseudonymisation salt in code exposes every token."],
        [
            qa("basic", "What is PII?", "Information that identifies a person directly (name, email, phone, national ID) or indirectly in combination (birth date, zip code, device ID, precise location). Indirect identifiers are called quasi-identifiers."),
            qa("intermediate", "What is the difference between pseudonymisation and anonymisation?", "Pseudonymisation replaces identifiers with tokens that can be re-linked by whoever holds the key, so it is still personal data. Anonymisation irreversibly prevents re-identification, including by combining with other data, and then the data generally falls outside GDPR."),
            qa("intermediate", "Why is hashing an email not enough?", "The space of emails or phone numbers is small enough to hash every candidate and look them up. Use a keyed hash such as HMAC-SHA256 with a secret kept in a secrets manager, and remember the result is still pseudonymous."),
            qa("advanced", "Explain k-anonymity and its weaknesses.", "A release is k-anonymous if each combination of quasi-identifiers matches at least k records, achieved by generalisation and suppression. It is vulnerable to homogeneity attacks (all k share the same diagnosis) and background knowledge, which l-diversity and t-closeness try to address."),
            qa("advanced", "What does epsilon mean in differential privacy?", "Epsilon bounds how much any single person's data can change the probability of any output; smaller epsilon means stronger privacy and more noise. Each query spends budget, so repeated queries accumulate privacy loss."),
        ],
        ["data-cleaning", "metrics-design", "ds-workflow"],
        chain(
            ("Collect", "minimise", "Minimise", "Only collect fields needed for a stated purpose."),
            ("Classify", "PII / quasi-IDs", "Inventory", "Tag direct identifiers, quasi-identifiers and sensitive attributes.", "raw data"),
            ("Pseudonymise", "HMAC-SHA256", "Tokenise", "Replace direct IDs with keyed hashes; key lives in a vault.", "tagged"),
            ("Generalise", "k-anonymity", "Reduce risk", "Band ages, truncate zips and suppress rare groups until k is met.", "tokens"),
            ("Release", "access + audit", "Share", "Share with access control, retention limits and an audit trail.", "safe set"),
        ),
    ),
]

TOPICS += [
    topic(
        "descriptive-stats", "Descriptive Statistics: Mean, Median, Mode", "statistics", "basic", "MM",
        "Three ways to say 'typical', and why the median is often the honest one.",
        "If a billionaire walks into a small cafe, the average wealth of the customers jumps to millions, but the median customer is exactly as rich as before.",
        "Measures of central tendency summarise where the data sit. The arithmetic mean is the sum divided by the count; it uses every value, is the balance point of the distribution and minimises squared error, but it is pulled strongly by outliers and skew. The median is the middle value of the sorted data (the average of the two middle values for even n); it minimises absolute error and is robust to extreme values, which is why incomes and house prices are reported as medians. The mode is the most frequent value and is the only measure that works for nominal data; distributions can be bimodal or multimodal. Other useful variants are the weighted mean (when observations carry different importance), the trimmed mean (drop a percentage from each tail), the geometric mean (for growth rates and ratios) and the harmonic mean (for averaging rates such as speeds). In a right-skewed distribution the mean usually exceeds the median; in a symmetric one they are close. Always report a measure of spread alongside the centre.",
        ["Reporting typical order value or salary.", "Choosing robust KPIs for skewed metrics like session length.", "Averaging growth rates with a geometric mean.", "Summarising categorical survey answers with the mode."],
        [
            "Mean minimises squared error; median minimises absolute error.",
            "Median and trimmed mean resist outliers; mean does not.",
            "Mode is the only centre for nominal data.",
            "Geometric mean for compound growth; harmonic mean for rates.",
            "Right skew: mean > median; left skew: mean < median (usually).",
        ],
        [
            ex("Mean, median and mode side by side", "basic", "A single large value moves the mean but not the median.", "python", """
                import statistics as st

                incomes = [32, 35, 38, 40, 41, 45, 47, 52]          # thousands, synthetic
                print("mean", st.fmean(incomes), "median", st.median(incomes))
                incomes.append(2000)                                  # one extreme value
                print("mean", round(st.fmean(incomes), 1), "median", st.median(incomes))

                sizes = ["M", "L", "M", "S", "M", "XL", "L"]
                print("mode", st.mode(sizes), "multimode", st.multimode([1, 1, 2, 2, 3]))
            """),
            ex("Weighted, trimmed, geometric and harmonic means", "intermediate", "Pick the mean that matches the question.", "python", """
                import statistics as st

                scores, weights = [80, 90, 70], [0.2, 0.5, 0.3]
                print("weighted mean:", sum(s * w for s, w in zip(scores, weights)))

                data = sorted([3, 4, 4, 5, 5, 5, 6, 6, 7, 60])
                k = int(len(data) * 0.1)
                print("10% trimmed mean:", st.fmean(data[k:len(data) - k]))

                growth = [1.10, 0.80, 1.25]                          # +10%, -20%, +25%
                print("arithmetic avg growth:", round(st.fmean(growth), 4))
                print("geometric avg growth: ", round(st.geometric_mean(growth), 4))
                print("avg speed for equal distances at 60 and 40:", st.harmonic_mean([60, 40]))
            """),
        ],
        ["statistics.fmean(x) · statistics.median(x)", "statistics.mode(x) · statistics.multimode(x)", "statistics.geometric_mean · harmonic_mean", "scipy.stats.trim_mean(x, 0.1)", "df['v'].agg(['mean','median'])"],
        ["Averaging percentages or rates directly ignores their denominators.", "The mean of a bimodal distribution can describe nobody.", "Median of medians is not the overall median."],
        [
            qa("basic", "When would you use the median instead of the mean?", "When the data are skewed or contain outliers, such as incomes, house prices or response times. The median reflects the typical value while the mean is dragged toward the tail."),
            qa("basic", "Which measure of central tendency works for nominal data?", "Only the mode, because nominal categories have no order or numeric distance. Means and medians are undefined for labels like country or colour."),
            qa("intermediate", "Why use a geometric mean for growth rates?", "Growth compounds multiplicatively. The geometric mean of growth factors gives the constant rate that produces the same final value, while the arithmetic mean overstates it, e.g. +50% then -50% averages 0% arithmetically but is a 13.4% loss per period."),
            qa("intermediate", "Mean is much greater than median. What does that tell you?", "The distribution is likely right-skewed, with a long tail of large values or a few outliers. Report the median and percentiles, and investigate the tail."),
        ],
        ["variance-std", "percentiles-iqr", "skew-kurtosis"],
        chain(
            ("Data", "raw values", "Collect", "Gather the numeric or categorical values for one variable."),
            ("Mean", "balance point", "Mean", "Sum divided by count; sensitive to outliers.", "values"),
            ("Median", "middle value", "Median", "Middle of sorted data; robust to extremes.", "sorted"),
            ("Mode", "most frequent", "Mode", "Most common value; works for categories.", "counts"),
            ("Report", "centre + spread", "Summarise", "Pair the chosen centre with a spread measure.", "summary"),
        ),
    ),
    topic(
        "variance-std", "Variance & Standard Deviation", "statistics", "basic", "VS",
        "How far values typically sit from the mean, in squared units (variance) or original units (SD).",
        "Two archers both average the bullseye. One clusters arrows tightly, the other sprays them all over the target. Standard deviation is the number that tells them apart.",
        "Variance is the average squared deviation from the mean; the standard deviation (SD) is its square root and is expressed in the same units as the data. For a sample, divide by n - 1 instead of n (Bessel's correction) because deviations are measured from the sample mean, which makes them slightly too small; this gives an unbiased variance estimate. Squaring emphasises large deviations, so variance and SD are sensitive to outliers; the median absolute deviation (MAD) and IQR are robust alternatives. For roughly normal data about 68%, 95% and 99.7% of values lie within 1, 2 and 3 SDs of the mean (the empirical rule); Chebyshev's inequality guarantees at least 1 - 1/k^2 within k SDs for any distribution. The coefficient of variation (SD / mean) compares variability across scales for ratio data. Do not confuse SD (spread of data) with the standard error (SD / sqrt(n), the uncertainty of the mean). Variances of independent variables add, which underpins portfolio risk and error propagation.",
        ["Quantifying volatility of daily sales or stock returns.", "Setting control limits in process monitoring.", "Standardising features into z-scores.", "Comparing consistency of two suppliers with the coefficient of variation."],
        [
            "Sample variance divides by n - 1; population variance by n.",
            "SD is in original units; variance is in squared units.",
            "Empirical rule: 68-95-99.7 for normal data.",
            "Standard error = SD / sqrt(n) measures uncertainty of the mean.",
            "Var(X + Y) = Var(X) + Var(Y) when independent.",
        ],
        [
            ex("Computing variance by hand and with statistics", "basic", "Sample vs population versions and the z-score.", "python", """
                import math
                import statistics as st

                x = [4, 8, 6, 5, 3, 7, 9, 6]
                mu = st.fmean(x)
                ss = sum((v - mu) ** 2 for v in x)
                print("mean", mu, "sum of squares", ss)
                print("population var", ss / len(x), "==", st.pvariance(x))
                print("sample var    ", round(ss / (len(x) - 1), 4), "==", round(st.variance(x), 4))
                sd = st.stdev(x)
                print("sample sd", round(sd, 4), "standard error", round(sd / math.sqrt(len(x)), 4))
                print("z-scores", [round((v - mu) / sd, 2) for v in x])
            """),
            ex("Checking the empirical rule", "intermediate", "Simulate normal data and count values within 1, 2 and 3 SDs.", "python", """
                import random
                import statistics as st

                random.seed(42)
                data = [random.gauss(100, 15) for _ in range(20000)]
                mu, sd = st.fmean(data), st.stdev(data)
                for k in (1, 2, 3):
                    share = sum(abs(v - mu) <= k * sd for v in data) / len(data)
                    print(f"within {k} SD: {share:.3f}   Chebyshev bound >= {1 - 1 / k ** 2:.3f}")
                print("CV =", round(sd / mu, 3))
            """),
        ],
        ["s^2 = sum((x - mean)^2) / (n - 1)", "statistics.variance(x) · statistics.pstdev(x)", "SE = s / sqrt(n)", "z = (x - mean) / sd", "np.std(x, ddof=1) · df['v'].std()"],
        ["numpy's np.std defaults to ddof=0 (population) while pandas .std() uses ddof=1.", "SD is not meaningful for heavily skewed data without context; show percentiles too.", "Reporting SD when you mean standard error (or vice versa) misleads readers."],
        [
            qa("basic", "What is the difference between variance and standard deviation?", "Variance is the mean squared deviation from the mean, in squared units. Standard deviation is its square root, in the original units, which makes it easier to interpret."),
            qa("intermediate", "Why divide by n - 1 for the sample variance?", "Deviations are measured from the sample mean, which is fitted to the same data and makes the sum of squares systematically too small. Dividing by n - 1 (degrees of freedom) corrects this bias so the estimator is unbiased for the population variance."),
            qa("intermediate", "What is the difference between standard deviation and standard error?", "Standard deviation describes the spread of individual observations. Standard error is the standard deviation of an estimate such as the sample mean, equal to SD / sqrt(n), and shrinks as the sample grows."),
            qa("advanced", "Two independent metrics have SDs of 3 and 4. What is the SD of their sum?", "Variances add for independent variables: 9 + 16 = 25, so the SD is 5. SDs themselves do not add; if the variables are correlated, add 2 * Cov(X, Y) to the variance."),
        ],
        ["descriptive-stats", "percentiles-iqr", "confidence-intervals"],
        chain(
            ("Mean", "centre", "Centre", "Compute the sample mean."),
            ("Deviations", "x - mean", "Deviations", "Subtract the mean from every value.", "mean"),
            ("Square", "sum of squares", "Square and sum", "Square deviations so they do not cancel and sum them.", "deviations"),
            ("Divide", "n - 1", "Variance", "Divide by n - 1 for an unbiased sample variance.", "SS"),
            ("Root", "SD", "Standard deviation", "Take the square root to return to original units.", "variance"),
        ),
    ),
    topic(
        "percentiles-iqr", "Percentiles, IQR & Box Plots", "statistics", "basic", "PQ",
        "Rank-based summaries that describe spread and tails without being fooled by outliers.",
        "Percentiles are like a queue sorted by height: the 90th percentile is the person taller than 90% of the queue, no matter how tall the tallest giant is.",
        "The p-th percentile is the value below which p% of observations fall; quartiles are the 25th (Q1), 50th (median, Q2) and 75th (Q3) percentiles. The interquartile range IQR = Q3 - Q1 covers the middle 50% of the data and is a robust measure of spread. Several interpolation methods exist (numpy offers linear, nearest, midpoint and others; Python's statistics.quantiles offers exclusive and inclusive), so small samples can give slightly different answers across tools. The five-number summary (minimum, Q1, median, Q3, maximum) is drawn as a box plot: the box spans Q1 to Q3 with a line at the median, and whiskers extend to the most extreme points within 1.5 * IQR of the box; points beyond are plotted individually as potential outliers. Box plots are excellent for comparing distributions across groups but hide multimodality, so pair them with histograms, violin or strip plots. In engineering and product work, latency and load are reported as p50, p95 and p99 because averages hide the tail users actually feel.",
        ["Reporting API latency as p50/p95/p99.", "Comparing salary distributions across departments with box plots.", "Flagging outliers with the 1.5 * IQR rule.", "Setting percentile-based thresholds for alerts or bonuses."],
        [
            "IQR = Q3 - Q1 covers the middle half of the data.",
            "Box plot whiskers usually stop at 1.5 * IQR from the box.",
            "Percentile definitions differ slightly between tools.",
            "Tail percentiles (p95, p99) matter more than means for latency.",
            "Box plots hide bimodality; overlay points or use violins.",
        ],
        [
            ex("Quartiles, IQR and fences", "basic", "Compute the five-number summary and outlier fences.", "python", """
                import statistics as st

                latency = [120, 135, 128, 142, 150, 131, 125, 980, 138, 145, 133, 129, 160, 1210, 140]
                q1, q2, q3 = st.quantiles(latency, n=4, method="inclusive")
                iqr = q3 - q1
                lo, hi = q1 - 1.5 * iqr, q3 + 1.5 * iqr
                print("five-number:", min(latency), q1, q2, q3, max(latency))
                print("IQR", iqr, "fences", lo, hi)
                print("outliers:", [x for x in latency if x < lo or x > hi])
            """),
            ex("p50/p95/p99 vs mean", "intermediate", "The mean hides a slow tail that p99 reveals.", "python", """
                import random
                import statistics as st

                random.seed(9)
                ms = [random.lognormvariate(4.6, 0.35) for _ in range(5000)]
                ms += [random.uniform(1500, 3000) for _ in range(60)]        # timeouts
                cuts = st.quantiles(ms, n=100, method="inclusive")
                print(f"mean {st.fmean(ms):.0f} ms")
                print(f"p50 {cuts[49]:.0f}  p95 {cuts[94]:.0f}  p99 {cuts[98]:.0f} ms")
            """),
            ex("Box plot by group with pandas", "basic", "One call compares distributions across categories.", "python", """
                import pandas as pd

                df = pd.read_csv("salaries.csv")
                print(df.groupby("dept")["salary"].describe(percentiles=[.25, .5, .75, .95]))
                df.boxplot(column="salary", by="dept", showfliers=True)
            """, False),
        ],
        ["statistics.quantiles(x, n=4)", "IQR = Q3 - Q1 · fences Q1 - 1.5*IQR, Q3 + 1.5*IQR", "np.percentile(x, [50, 95, 99])", "df['v'].quantile([.25, .5, .75])", "PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY v)"],
        ["Averaging percentiles across servers is wrong; merge raw data or sketches (t-digest).", "Different interpolation methods give different small-sample quartiles.", "A box plot of n=5 looks authoritative but carries little information."],
        [
            qa("basic", "What is the IQR and why is it useful?", "The interquartile range is Q3 minus Q1, the spread of the middle 50% of the data. It is robust to outliers, unlike the range or standard deviation."),
            qa("basic", "How do you read a box plot?", "The box spans Q1 to Q3 with a line at the median; whiskers reach the furthest points within 1.5 IQR; dots beyond are potential outliers. Box position shows centre, box height shows spread, and asymmetry shows skew."),
            qa("intermediate", "Why do engineers report p99 latency instead of mean latency?", "Latency is right-skewed and the slow tail determines user pain and timeouts. With many requests per page, most users hit the p99 at least once, while the mean can look fine even when the tail is terrible."),
            qa("advanced", "Can you average p95 values from 10 servers to get the global p95?", "No. Percentiles are not additive; the global p95 depends on the full combined distribution. Merge raw values or mergeable sketches such as t-digest or HDR histograms."),
        ],
        ["outliers", "descriptive-stats", "choosing-charts"],
        chain(
            ("Sort", "order values", "Sort", "Order the observations from smallest to largest."),
            ("Quartiles", "Q1, Q2, Q3", "Cut points", "Find the 25th, 50th and 75th percentiles.", "sorted"),
            ("IQR", "Q3 - Q1", "Spread", "The IQR measures the middle half of the data.", "quartiles"),
            ("Fences", "1.5 x IQR", "Whiskers", "Whiskers stop at the last point inside the fences.", "IQR"),
            ("Box plot", "draw + flag", "Visualise", "Draw the box, whiskers and flag points beyond the fences.", "summary"),
        ),
    ),
    topic(
        "outliers", "Outliers: Detection & Treatment", "statistics", "intermediate", "OU",
        "Unusual points can be errors, rare truths or the whole story; detect them, then decide with domain knowledge.",
        "An outlier is like a single loud voice in a survey call centre. Sometimes it is a broken microphone, sometimes it is the only customer telling you the product is on fire.",
        "An outlier is an observation far from the bulk of the data. Detection methods include the z-score rule (|z| > 3, which assumes rough normality and is itself distorted by the outliers it seeks), the robust modified z-score based on the median and MAD (|0.6745 * (x - median) / MAD| > 3.5), Tukey's 1.5 * IQR fences, and multivariate methods such as Mahalanobis distance, isolation forest or local outlier factor. Univariate checks miss points that are unusual only in combination, like a 2-metre-tall 5-year-old. Treatment depends on the cause: fix or remove data-entry and sensor errors; keep genuine extreme values but use robust statistics (median, trimmed mean, Huber regression); cap them (winsorising) for modelling stability; transform skewed variables (log); or model them separately, as in fraud detection where the outliers are the target. Document every removal, apply the same rule to train and production data, and never drop points just because they hurt a hypothesis.",
        ["Cleaning sensor or transaction data before analysis.", "Fraud and anomaly detection where outliers are the signal.", "Stabilising regression models with winsorising or robust loss.", "Investigating a spike in a KPI dashboard."],
        [
            "Find the cause before choosing a treatment.",
            "Robust z-score (median, MAD) beats the classic z-score for contaminated data.",
            "Tukey fences: below Q1 - 1.5 IQR or above Q3 + 1.5 IQR.",
            "Multivariate outliers need multivariate methods.",
            "Winsorise, transform or use robust models instead of silently deleting.",
        ],
        [
            ex("Classic vs robust z-score", "intermediate", "Large outliers inflate the SD and hide themselves from the classic rule.", "python", """
                import statistics as st

                x = [10, 11, 9, 10, 12, 11, 10, 9, 11, 10, 95, 102]
                mu, sd = st.fmean(x), st.stdev(x)
                classic = [v for v in x if abs((v - mu) / sd) > 3]
                med = st.median(x)
                mad = st.median([abs(v - med) for v in x])
                robust = [v for v in x if abs(0.6745 * (v - med) / mad) > 3.5]
                print("classic |z|>3 flags:", classic)
                print("robust MAD flags:   ", robust)
            """),
            ex("Winsorising at the 5th and 95th percentiles", "intermediate", "Cap extreme values instead of dropping rows.", "python", """
                import random
                import statistics as st

                random.seed(12)
                spend = [round(random.lognormvariate(3, 0.6), 2) for _ in range(500)] + [5000.0, 7200.0]
                cuts = st.quantiles(spend, n=20, method="inclusive")
                lo, hi = cuts[0], cuts[-1]
                capped = [min(max(v, lo), hi) for v in spend]
                print(f"bounds {lo:.2f} .. {hi:.2f}")
                print(f"mean raw {st.fmean(spend):.2f}  winsorised {st.fmean(capped):.2f}  median {st.median(spend):.2f}")
            """),
            ex("Isolation forest for multivariate anomalies", "advanced", "Scores points that are easy to isolate with random splits.", "python", """
                from sklearn.ensemble import IsolationForest

                iso = IsolationForest(contamination=0.01, random_state=0)
                df["anomaly"] = iso.fit_predict(df[["amount", "hour", "items"]]) == -1
                print(df[df["anomaly"]].head())
            """, False),
        ],
        ["|z| > 3 · modified z = 0.6745 (x - med) / MAD", "x.clip(lower=q05, upper=q95)", "np.log1p(x) for right-skewed values", "IsolationForest(contamination=0.01)", "HuberRegressor() for robust fits"],
        ["Removing outliers repeatedly until none remain destroys real data.", "Outlier rules fitted on all data leak into the test set.", "Heavy-tailed data (income, claims) naturally produces many 'outliers'."],
        [
            qa("basic", "How do you detect outliers in a single variable?", "Common rules are |z| > 3, the robust modified z-score using median and MAD, and Tukey's fences at 1.5 IQR beyond the quartiles. Always look at a plot as well, because rules assume a shape."),
            qa("intermediate", "Should you always remove outliers?", "No. Remove them only if they are errors (typos, sensor faults, test accounts). Genuine extremes carry information; handle them with robust statistics, transformation, capping or a separate model, and document the choice."),
            qa("intermediate", "Why can the z-score method fail to detect outliers?", "The mean and SD are computed including the outliers, which inflates the SD and shrinks every z-score (masking). Robust versions based on median and MAD avoid this."),
            qa("advanced", "What is a multivariate outlier and how do you find it?", "A point that is normal on each variable individually but unusual in combination, such as high spend at 3am from a new device. Mahalanobis distance, isolation forest, local outlier factor or autoencoder reconstruction error can detect them."),
        ],
        ["percentiles-iqr", "data-cleaning", "scaling-normalisation"],
        chain(
            ("Detect", "IQR / MAD / ML", "Detect", "Flag candidates with robust univariate or multivariate methods."),
            ("Investigate", "error or real?", "Root cause", "Check source systems, units and context for each flagged point.", "flags"),
            ("Fix / drop", "if error", "Errors", "Correct or remove genuine data errors with a logged rule.", "errors"),
            ("Robustify", "cap, log, robust", "Real extremes", "Keep real extremes but use robust methods or transforms.", "real"),
        ),
    ),
    topic(
        "skew-kurtosis", "Skewness & Kurtosis", "statistics", "intermediate", "SK",
        "Shape beyond centre and spread: is the distribution lopsided, and how heavy are its tails?",
        "Skewness is a slide in a playground: most kids pile up at the bottom while a few are still way up the long slope. Kurtosis is how many kids are perched at the very top edges compared with a normal playground.",
        "Skewness measures asymmetry. Positive (right) skew means a long right tail, typical of incomes, response times and purchase amounts; negative (left) skew means a long left tail, such as scores on an easy exam. The sample skewness is the average cubed z-score (with small-sample corrections in most libraries); values beyond about +/-1 indicate substantial skew. Kurtosis measures tail heaviness relative to a normal distribution; the normal has kurtosis 3, so libraries often report excess kurtosis (kurtosis minus 3). Positive excess kurtosis (leptokurtic) means more extreme values than a normal, as in financial returns; negative (platykurtic) means lighter tails, like the uniform distribution. Kurtosis is about tails, not 'peakedness', despite the old textbook phrasing. Shape matters because many methods (t-intervals with small n, linear regression residual assumptions, z-score outlier rules) assume near-normality. Log, square-root, Box-Cox or Yeo-Johnson transforms reduce right skew.",
        ["Deciding whether to log-transform a revenue variable.", "Assessing tail risk in returns or insurance claims.", "Checking residual assumptions in regression.", "Choosing between mean-based and rank-based tests."],
        [
            "Skewness is the mean cubed z-score; kurtosis the mean fourth-power z-score.",
            "Right skew: long right tail, mean usually above median.",
            "Normal kurtosis = 3; excess kurtosis = kurtosis - 3.",
            "Kurtosis describes tails and outlier propensity, not peak shape.",
            "Log or Box-Cox transforms tame right skew.",
        ],
        [
            ex("Compute skewness and excess kurtosis", "intermediate", "Compare normal, right-skewed and uniform samples.", "python", """
                import math
                import random
                import statistics as st

                def shape(x):
                    m, s = st.fmean(x), st.pstdev(x)
                    z = [(v - m) / s for v in x]
                    return sum(v ** 3 for v in z) / len(z), sum(v ** 4 for v in z) / len(z) - 3

                random.seed(21)
                samples = {
                    "normal": [random.gauss(0, 1) for _ in range(20000)],
                    "lognormal": [random.lognormvariate(0, 0.8) for _ in range(20000)],
                    "uniform": [random.random() for _ in range(20000)],
                }
                for name, x in samples.items():
                    sk, ku = shape(x)
                    print(f"{name:9} skew={sk:+.2f} excess kurtosis={ku:+.2f}")
                logged = [math.log(v) for v in samples["lognormal"]]
                print("after log: skew=%+.2f" % shape(logged)[0])
            """),
            ex("scipy shape statistics", "basic", "Library versions apply small-sample bias corrections.", "python", """
                from scipy import stats

                print(stats.skew(x, bias=False), stats.kurtosis(x, fisher=True, bias=False))
                transformed, lam = stats.boxcox(x_positive)
                print("Box-Cox lambda", lam)
            """, False),
        ],
        ["skew = mean(z^3) · excess kurtosis = mean(z^4) - 3", "scipy.stats.skew(x) · scipy.stats.kurtosis(x)", "df['v'].skew() · df['v'].kurt()", "np.log1p(x) · stats.boxcox(x)"],
        ["Skewness estimates are themselves noisy for small samples.", "Box-Cox needs strictly positive data; use Yeo-Johnson otherwise.", "A single outlier can dominate the kurtosis estimate."],
        [
            qa("basic", "What does positive skew mean?", "The distribution has a long right tail: most values are small with a few very large ones. The mean is typically pulled above the median, as with incomes or order values."),
            qa("intermediate", "What does kurtosis measure?", "Tail heaviness, i.e. how prone the distribution is to extreme values compared with a normal. Excess kurtosis above 0 means heavier tails than normal; it is not a measure of how pointy the peak is."),
            qa("intermediate", "How do you fix a right-skewed feature?", "Apply a log (or log1p for zeros), square root, Box-Cox (positive data) or Yeo-Johnson transform. Alternatively use rank-based methods or models that do not assume normality, such as tree ensembles."),
            qa("advanced", "Why does kurtosis matter in risk management?", "Heavy tails mean extreme losses are far more likely than a normal model predicts. Value-at-risk based on normal assumptions underestimates tail risk for leptokurtic returns, so analysts use t-distributions, historical simulation or extreme value theory."),
        ],
        ["distributions", "descriptive-stats", "outliers"],
        chain(
            ("Standardise", "z-scores", "Standardise", "Convert values into z-scores using mean and SD."),
            ("Cube", "skewness", "Asymmetry", "Average of z cubed: sign shows the direction of the long tail.", "z"),
            ("Fourth power", "kurtosis", "Tails", "Average of z to the fourth; subtract 3 for excess kurtosis.", "z"),
            ("Act", "transform?", "Decide", "Transform, choose robust methods or model heavy tails explicitly.", "shape"),
        ),
    ),
    topic(
        "sampling-bias", "Sampling Methods & Sampling Bias", "statistics", "basic", "SM",
        "How you pick rows decides what your numbers mean: random, stratified, cluster, systematic, or biased.",
        "Tasting soup works only if you stir first. A spoonful from the top of an unstirred pot tells you about the oil, not the soup.",
        "A sample is a subset of a population used to estimate population quantities. Probability sampling gives every unit a known, non-zero chance of selection: simple random sampling (every subset equally likely), stratified sampling (sample within strata such as region to guarantee coverage and reduce variance), cluster sampling (randomly pick groups like schools, then survey everyone in them, cheaper but higher variance), and systematic sampling (every k-th unit after a random start, which fails if the list has periodicity). Non-probability methods such as convenience, quota, snowball or voluntary response sampling are cheaper but can be badly biased. Sampling bias occurs when the sampling frame or process systematically excludes or over-represents parts of the population, such as phone surveys missing people without landlines (the 1936 Literary Digest poll). Increasing sample size reduces random sampling error but not bias. Survey weighting and post-stratification can partially correct known imbalances. For big data, downsampling must preserve rare classes, often via stratification.",
        ["Designing a customer survey or user research recruitment.", "Downsampling a huge event log for fast analysis.", "Building train/test splits that preserve class balance.", "Auditing whether a dataset represents the target population."],
        [
            "Probability samples allow valid inference; convenience samples do not.",
            "Stratification guarantees coverage and reduces variance.",
            "Cluster sampling is cheaper but less precise per unit.",
            "Bigger samples reduce variance, never bias.",
            "Define the sampling frame and compare it with the population.",
        ],
        [
            ex("Random vs stratified sampling", "basic", "Stratification keeps a small region from being under-sampled.", "python", """
                import random
                import statistics as st
                from collections import Counter

                random.seed(10)
                population = [("north", random.gauss(50, 5)) for _ in range(9000)] + \\
                             [("south", random.gauss(80, 5)) for _ in range(1000)]
                true_mean = st.fmean(v for _, v in population)

                srs_means, strat_means = [], []
                for _ in range(300):
                    srs = random.sample(population, 50)
                    srs_means.append(st.fmean(v for _, v in srs))
                    north = random.sample(population[:9000], 45)
                    south = random.sample(population[9000:], 5)
                    strat_means.append(0.9 * st.fmean(v for _, v in north) + 0.1 * st.fmean(v for _, v in south))
                print(f"true mean {true_mean:.2f}")
                print(f"SRS        mean {st.fmean(srs_means):.2f} sd {st.stdev(srs_means):.3f}")
                print(f"stratified mean {st.fmean(strat_means):.2f} sd {st.stdev(strat_means):.3f}")
                print("one SRS region mix:", Counter(r for r, _ in random.sample(population, 50)))
            """),
            ex("Convenience sample bias does not shrink with n", "intermediate", "Sampling only from an app's power users stays biased at any size.", "python", """
                import random
                import statistics as st

                random.seed(6)
                users = [random.expovariate(1 / 20) for _ in range(50000)]       # minutes per week
                true = st.fmean(users)
                power = [u for u in users if u > 15]                             # who answers in-app surveys
                for n in (100, 1000, 10000):
                    print(f"n={n:5}: random {st.fmean(random.sample(users, n)):.1f}   convenience {st.fmean(random.sample(power, n)):.1f}   true {true:.1f}")
            """),
        ],
        ["random.sample(pop, k) · random.choices(pop, k=k)", "df.sample(frac=0.1, random_state=0)", "df.groupby('stratum').sample(frac=0.1)", "train_test_split(..., stratify=y)", "TABLESAMPLE BERNOULLI (1)"],
        ["Systematic sampling from a periodic list (e.g., every 7th day) aligns with the cycle.", "Opt-in and in-app surveys over-represent engaged users.", "Hash-based user sampling must be stable across days to avoid mixing cohorts."],
        [
            qa("basic", "What is the difference between stratified and cluster sampling?", "Stratified sampling divides the population into strata and samples from every stratum, improving precision. Cluster sampling randomly selects whole groups and includes all their members, reducing cost but usually increasing variance."),
            qa("basic", "What is sampling bias?", "A systematic difference between the sample and the population caused by how units were selected, such as a frame that excludes some groups or voluntary participation. It distorts estimates regardless of sample size."),
            qa("intermediate", "Why did the 1936 Literary Digest poll fail despite 2.4 million responses?", "Its sampling frame (phone books, car registrations, magazine subscribers) over-represented wealthier voters, and only about a quarter responded. Huge size could not fix a biased frame and non-response."),
            qa("intermediate", "When would you use a stratified train/test split?", "When the target is imbalanced or a key subgroup is rare, so that both splits contain representative proportions. Without stratification a small test set may contain very few positives, giving unstable metrics."),
        ],
        ["survivorship-selection-bias", "central-limit-theorem", "confidence-intervals"],
        chain(
            ("Population", "who we care about", "Target", "Define the population the conclusion must describe."),
            ("Frame", "list we can reach", "Sampling frame", "The list or system from which units can actually be drawn.", "definition"),
            ("Method", "SRS / strata", "Design", "Pick random, stratified, cluster or systematic sampling.", "frame"),
            ("Sample", "selected units", "Collect", "Draw units and track non-response.", "design"),
            ("Weight", "fix known gaps", "Adjust", "Weight or post-stratify to known population margins.", "responses"),
        ),
    ),
    topic(
        "confidence-intervals", "Confidence Intervals", "statistics", "intermediate", "CI",
        "A range of plausible values for a parameter, built by a procedure that captures the truth a stated share of the time.",
        "A confidence interval is a ring toss. Each toss either lands around the peg or not; a 95% procedure means that if you threw many rings, about 95 of 100 would circle the peg.",
        "A confidence interval (CI) gives a range for an unknown population parameter such as a mean, proportion or difference. Its general form is estimate +/- critical value * standard error. For a mean with unknown SD, use the t-distribution: x_bar +/- t(n-1, 0.975) * s / sqrt(n); for large samples z = 1.96 gives 95% coverage. For a proportion, the simple Wald interval p +/- 1.96 * sqrt(p(1-p)/n) behaves poorly near 0 or 1 or with small n, so the Wilson interval is preferred. The frequentist interpretation is about the procedure: 95% of intervals built this way contain the true value; a single computed interval either does or does not. Width shrinks with sqrt(n), so quadrupling n halves the width. Higher confidence gives wider intervals. When no formula exists (medians, ratios, complex metrics), bootstrap intervals are used. CIs convey effect size and uncertainty and are more informative than a bare p-value; a 95% CI for a difference that excludes 0 corresponds to p < 0.05 in a two-sided test.",
        ["Reporting a survey estimate with its margin of error.", "Communicating uncertainty in an A/B test lift.", "Deciding the sample size needed for a target precision.", "Comparing segments without over-interpreting small gaps."],
        [
            "CI = estimate +/- critical value x standard error.",
            "Use t critical values when SD is estimated from small samples.",
            "Width scales with 1 / sqrt(n).",
            "Prefer Wilson intervals for proportions.",
            "95% refers to the long-run coverage of the procedure.",
        ],
        [
            ex("t-interval for a mean and Wilson interval for a proportion", "intermediate", "Standard formulas with statistics.NormalDist.", "python", """
                import math
                import statistics as st

                times = [12.1, 9.8, 11.4, 13.0, 10.2, 12.7, 11.9, 10.8, 12.3, 11.1]
                n, m, s = len(times), st.fmean(times), st.stdev(times)
                t975 = 2.262                                     # t critical, df = 9
                half = t975 * s / math.sqrt(n)
                print(f"mean {m:.2f}, 95% CI [{m - half:.2f}, {m + half:.2f}]")

                def wilson(k, n, conf=0.95):
                    z = st.NormalDist().inv_cdf(0.5 + conf / 2)
                    p = k / n
                    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
                    margin = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
                    return centre - margin, centre + margin

                print("conversion 18/200 Wilson CI: [%.4f, %.4f]" % wilson(18, 200))
                print("conversion 0/30   Wilson CI: [%.4f, %.4f]" % wilson(0, 30))
            """),
            ex("What 95% coverage means", "intermediate", "Simulate many intervals and count how many contain the true mean.", "python", """
                import math
                import random
                import statistics as st

                random.seed(1)
                TRUE_MU, hits, trials = 50, 0, 2000
                z = st.NormalDist().inv_cdf(0.975)
                for _ in range(trials):
                    x = [random.gauss(TRUE_MU, 10) for _ in range(40)]
                    half = z * st.stdev(x) / math.sqrt(len(x))
                    hits += st.fmean(x) - half <= TRUE_MU <= st.fmean(x) + half
                print(f"coverage = {hits / trials:.3f}")
            """),
        ],
        ["mean +/- t * s / sqrt(n)", "p +/- z * sqrt(p(1-p)/n) (Wald)", "statistics.NormalDist().inv_cdf(0.975)", "scipy.stats.t.interval(0.95, df, loc, scale)", "statsmodels proportion_confint(k, n, method='wilson')"],
        ["Overlapping CIs do not imply a non-significant difference; compute the CI of the difference.", "The Wald interval for proportions can include negative values or have zero width.", "Saying 'there is a 95% probability the parameter is in this interval' is a Bayesian credible-interval statement."],
        [
            qa("basic", "How do you interpret a 95% confidence interval?", "If we repeated the sampling and interval procedure many times, about 95% of the intervals would contain the true parameter. A specific interval either contains it or not; the 95% describes the method's reliability."),
            qa("intermediate", "What determines the width of a confidence interval?", "The confidence level (critical value), the variability of the data (SD) and the sample size, through the standard error s / sqrt(n). To halve the width you need about four times as much data."),
            qa("intermediate", "Why is the Wilson interval preferred for proportions?", "The Wald interval has poor coverage for small n or proportions near 0 or 1 and can extend beyond [0, 1]. The Wilson score interval keeps close to nominal coverage and stays within bounds."),
            qa("advanced", "Two groups' 95% CIs overlap slightly. Is the difference not significant?", "Not necessarily. The CI of the difference uses sqrt(SE1^2 + SE2^2), which is smaller than SE1 + SE2, so intervals can overlap by up to about a quarter of their width while the difference is still significant at 5%."),
        ],
        ["hypothesis-testing", "bootstrapping", "central-limit-theorem"],
        chain(
            ("Sample", "n observations", "Sample", "Collect a random sample and compute the estimate."),
            ("Std error", "s / sqrt(n)", "Uncertainty", "Estimate how much the statistic varies between samples.", "estimate"),
            ("Critical", "z or t", "Confidence level", "Pick the critical value for the desired confidence.", "SE"),
            ("Interval", "est +/- margin", "Build", "Estimate plus or minus critical value times SE.", "margin"),
        ),
    ),
    topic(
        "bootstrapping", "Bootstrapping", "statistics", "intermediate", "BS",
        "Resample your own data with replacement to see how much a statistic would wobble.",
        "Bootstrapping is like learning about the ocean from one bucket of seawater: you keep scooping cups from the bucket, with replacement, to see how much cup-to-cup variation to expect.",
        "The bootstrap, introduced by Bradley Efron in 1979, estimates the sampling distribution of a statistic by treating the observed sample as a stand-in for the population. You draw B resamples of size n with replacement, compute the statistic on each, and use the spread of those B values as its standard error. The percentile method takes the 2.5th and 97.5th percentiles of the bootstrap distribution as a 95% interval; the BCa (bias-corrected and accelerated) method adjusts for bias and skew and is more accurate. The bootstrap shines for statistics without simple formulas: medians, percentiles, ratios of means, correlations, AUC, or the difference in p90 between two variants. Typical B is 1,000-10,000. It assumes observations are independent and identically distributed, so dependent data need block bootstrap (time series) or cluster bootstrap (users with many sessions). It also struggles with very small samples and statistics depending on extremes, like the maximum. A permutation test is related but answers a different question: it shuffles labels to simulate the null hypothesis.",
        ["Confidence intervals for a median or percentile metric.", "Uncertainty for ratio metrics such as revenue per session.", "Comparing model metrics (AUC, F1) between two models.", "Quick uncertainty estimates where formulas are messy."],
        [
            "Resample n rows with replacement, B times.",
            "Standard error = SD of bootstrap statistics.",
            "Percentile CI: 2.5th and 97.5th bootstrap percentiles; BCa is better for skew.",
            "Resample the independent unit (user, cluster, block), not individual events.",
            "Fix the random seed for reproducible intervals.",
        ],
        [
            ex("Bootstrap CI for a median", "intermediate", "No formula needed: resample and read off percentiles.", "python", """
                import random
                import statistics as st

                random.seed(0)
                sessions = [round(random.lognormvariate(1.5, 0.8), 2) for _ in range(120)]
                B = 2000
                boot = sorted(st.median(random.choices(sessions, k=len(sessions))) for _ in range(B))
                print(f"median {st.median(sessions):.2f}")
                print(f"bootstrap SE {st.stdev(boot):.3f}")
                print(f"95% percentile CI [{boot[int(0.025 * B)]:.2f}, {boot[int(0.975 * B)]:.2f}]")
            """),
            ex("Bootstrap the difference of two groups", "advanced", "CI for the lift in mean revenue per user between variants.", "python", """
                import random
                import statistics as st

                random.seed(3)
                a = [random.expovariate(1 / 10) for _ in range(400)]
                b = [random.expovariate(1 / 11.5) for _ in range(400)]
                diffs = []
                for _ in range(2000):
                    ra = random.choices(a, k=len(a))
                    rb = random.choices(b, k=len(b))
                    diffs.append(st.fmean(rb) - st.fmean(ra))
                diffs.sort()
                print(f"observed lift {st.fmean(b) - st.fmean(a):.2f}")
                print(f"95% CI [{diffs[50]:.2f}, {diffs[1949]:.2f}]")
                print("share of resamples with lift <= 0:", sum(d <= 0 for d in diffs) / len(diffs))
            """),
            ex("scipy.stats.bootstrap with BCa", "advanced", "Library implementation with bias correction.", "python", """
                import numpy as np
                from scipy import stats

                res = stats.bootstrap((data,), np.median, n_resamples=9999, method="BCa", random_state=0)
                print(res.confidence_interval, res.standard_error)
            """, False),
        ],
        ["random.choices(data, k=len(data))", "SE_boot = stdev(boot_stats)", "CI = percentile(boot, [2.5, 97.5])", "scipy.stats.bootstrap((x,), np.median, method='BCa')", "Block bootstrap for time series"],
        ["Resampling events instead of users understates variance when users repeat.", "The bootstrap cannot fix a biased or tiny sample.", "Percentile intervals undercover for skewed statistics; prefer BCa."],
        [
            qa("basic", "What is bootstrapping?", "A resampling technique that draws many samples with replacement from the observed data, recomputes a statistic each time, and uses the resulting distribution to estimate its standard error or confidence interval."),
            qa("intermediate", "When is the bootstrap especially useful?", "When the statistic has no convenient analytic standard error, such as medians, percentiles, ratios, correlations or ML metrics like AUC, or when distributional assumptions behind formulas are doubtful."),
            qa("intermediate", "How does bootstrapping differ from a permutation test?", "The bootstrap resamples with replacement within groups to estimate the variability of an estimate. A permutation test shuffles group labels without replacement to build the null distribution of a test statistic and compute a p-value."),
            qa("advanced", "How would you bootstrap an A/B metric where each user has many sessions?", "Resample users (the randomisation unit), keeping all their sessions together, then recompute the session-level metric. Resampling sessions independently ignores within-user correlation and gives intervals that are too narrow."),
        ],
        ["confidence-intervals", "nonparametric-tests", "ab-testing"],
        chain(
            ("Sample", "n rows", "Observed data", "Start with the single sample you have."),
            ("Resample", "with replacement", "Resample", "Draw n rows with replacement, B times.", "data"),
            ("Statistic", "per resample", "Recompute", "Compute the statistic on each resample.", "B samples"),
            ("Distribution", "B values", "Bootstrap dist.", "The B statistics approximate the sampling distribution.", "B stats"),
            ("Interval", "2.5% - 97.5%", "CI", "Read percentiles (or BCa) for the confidence interval.", "spread"),
        ),
    ),
]

TOPICS += [
    topic(
        "probability-basics", "Probability Basics", "probability", "basic", "PB",
        "Sample spaces, events and the few rules (complement, addition, multiplication) that everything else builds on.",
        "Probability is bookkeeping for uncertainty. Like a budget, all the money (probability 1) must be split across outcomes, and you cannot spend more than you have.",
        "Probability assigns a number between 0 and 1 to events, which are subsets of a sample space of possible outcomes. Kolmogorov's axioms require non-negative probabilities, P(sample space) = 1, and additivity for mutually exclusive events. From these follow the complement rule P(not A) = 1 - P(A), and the general addition rule P(A or B) = P(A) + P(B) - P(A and B), which removes double-counting of the overlap. For independent events, P(A and B) = P(A) * P(B); independence means knowing one event does not change the probability of the other, which is different from being mutually exclusive (exclusive events with positive probability are always dependent). Counting tools help with equally likely outcomes: permutations n!/(n-k)! when order matters and combinations n!/(k!(n-k)!) when it does not. The 'at least one' trick computes 1 - P(none), as in the birthday problem where 23 people give a better than even chance of a shared birthday. Interpretations differ: frequentists treat probability as long-run frequency, Bayesians as degree of belief, but the rules are the same.",
        ["Estimating the chance at least one of several services fails.", "Reasoning about combinations in sampling and lotteries.", "Sanity-checking simulation results.", "Building intuition for p-values and risk."],
        [
            "0 <= P(A) <= 1 and P(all outcomes) = 1.",
            "P(not A) = 1 - P(A); 'at least one' = 1 - P(none).",
            "P(A or B) = P(A) + P(B) - P(A and B).",
            "Independent: P(A and B) = P(A) P(B). Exclusive: P(A and B) = 0.",
            "math.comb(n, k) counts unordered selections.",
        ],
        [
            ex("Birthday problem: formula and simulation", "basic", "Complement rule plus a Monte Carlo check.", "python", """
                import random

                def p_shared(n):
                    p_none = 1.0
                    for i in range(n):
                        p_none *= (365 - i) / 365
                    return 1 - p_none

                for n in (10, 23, 50):
                    print(n, "people:", round(p_shared(n), 3))

                random.seed(0)
                trials = 20000
                hits = sum(len(set(random.randrange(365) for _ in range(23))) < 23 for _ in range(trials))
                print("simulated n=23:", hits / trials)
            """),
            ex("Addition rule, independence and counting", "basic", "Cards, dice and service uptime.", "python", """
                import math
                from fractions import Fraction

                p_heart = Fraction(13, 52); p_king = Fraction(4, 52); p_both = Fraction(1, 52)
                print("P(heart or king) =", p_heart + p_king - p_both)
                print("independent?", p_heart * p_king == p_both)

                uptime = [0.999, 0.995, 0.99]                 # three services in series
                print("all up:", round(math.prod(uptime), 4), "at least one down:", round(1 - math.prod(uptime), 4))
                print("5-card hands:", math.comb(52, 5), "ordered podiums of 10:", math.perm(10, 3))
            """),
        ],
        ["P(A') = 1 - P(A)", "P(A u B) = P(A) + P(B) - P(A n B)", "P(A n B) = P(A) P(B) if independent", "math.comb(n, k) · math.perm(n, k)", "random.seed(0) for reproducible simulation"],
        ["Mutually exclusive is not the same as independent.", "Adding probabilities of overlapping events double-counts.", "The gambler's fallacy: independent trials have no memory."],
        [
            qa("basic", "What is the difference between independent and mutually exclusive events?", "Independent events do not affect each other's probability: P(A and B) = P(A)P(B). Mutually exclusive events cannot both happen: P(A and B) = 0. Two exclusive events with non-zero probabilities are therefore dependent."),
            qa("basic", "How do you compute the probability of at least one success in n independent trials?", "Use the complement: 1 - (1 - p)^n. For example the chance of at least one six in four rolls is 1 - (5/6)^4, about 0.518."),
            qa("intermediate", "Three independent services each have 99.9% availability and a request needs all of them. What is the availability?", "0.999^3, about 99.7%, so downtime roughly triples. Serial dependencies multiply availability, which is why redundancy (parallel paths) is used: 1 - (0.001)^2 for two replicas."),
            qa("intermediate", "What is the birthday paradox and why does it matter in data work?", "With only 23 people the probability that two share a birthday exceeds 50%, because the number of pairs grows quadratically. The same logic explains why hash or ID collisions appear far sooner than intuition suggests."),
        ],
        ["conditional-bayes", "expectation", "distributions"],
        chain(
            ("Sample space", "all outcomes", "Define", "List every possible outcome of the experiment."),
            ("Event", "subset", "Event", "An event is a set of outcomes we care about.", "outcomes"),
            ("Rules", "add, multiply", "Combine", "Use complement, addition and multiplication rules.", "events"),
            ("Check", "simulate", "Verify", "Confirm with a seeded Monte Carlo simulation.", "P(A)"),
        ),
    ),
    topic(
        "conditional-bayes", "Conditional Probability & Bayes' Theorem", "probability", "intermediate", "BY",
        "Update beliefs with evidence: P(A | B) depends heavily on the base rate P(A).",
        "A smoke alarm that beeps for burnt toast is accurate about smoke but not about fires. Whether a beep means 'fire' depends on how rare fires are compared with toast.",
        "Conditional probability P(A | B) is the probability of A given that B occurred: P(A and B) / P(B). Bayes' theorem reverses the conditioning: P(A | B) = P(B | A) P(A) / P(B), where P(A) is the prior, P(B | A) the likelihood and P(A | B) the posterior. The denominator P(B) is computed by the law of total probability: P(B | A) P(A) + P(B | not A) P(not A). The classic medical test example shows base-rate neglect: a test with 99% sensitivity and 95% specificity for a disease with 1% prevalence produces a positive predictive value of only about 17%, because false positives from the large healthy group outnumber true positives. Confusing P(A | B) with P(B | A) is the prosecutor's fallacy. Bayes' rule underpins spam filters (naive Bayes), A/B testing with Bayesian posteriors, diagnostic reasoning and fraud alert triage. Odds form is handy: posterior odds = prior odds * likelihood ratio.",
        ["Interpreting alert precision for fraud or anomaly systems.", "Explaining why a positive screening test is often a false alarm.", "Naive Bayes classifiers for text.", "Updating conversion-rate beliefs as data arrive."],
        [
            "P(A | B) = P(A and B) / P(B).",
            "Bayes: posterior = likelihood x prior / evidence.",
            "Law of total probability builds the evidence term.",
            "Low base rates make even accurate tests produce mostly false positives.",
            "P(A | B) is not P(B | A) (prosecutor's fallacy).",
        ],
        [
            ex("Medical test and base rates", "intermediate", "Positive predictive value at different prevalences.", "python", """
                def ppv(prevalence, sensitivity, specificity):
                    tp = sensitivity * prevalence
                    fp = (1 - specificity) * (1 - prevalence)
                    return tp / (tp + fp)

                for prev in (0.001, 0.01, 0.1, 0.3):
                    print(f"prevalence {prev:>5}: P(disease | positive) = {ppv(prev, 0.99, 0.95):.3f}")

                # natural frequencies for 10,000 people at 1% prevalence
                sick, healthy = 100, 9900
                print("true positives", round(sick * 0.99), "false positives", round(healthy * 0.05))
            """),
            ex("Tiny naive Bayes spam filter", "advanced", "Word likelihoods with Laplace smoothing and log probabilities.", "python", """
                import math
                from collections import Counter

                train = [("win cash prize now", "spam"), ("cheap prize offer", "spam"), ("meeting at noon", "ham"),
                         ("project update attached", "ham"), ("lunch meeting today", "ham"), ("win a free offer", "spam")]
                counts = {"spam": Counter(), "ham": Counter()}
                docs = Counter(label for _, label in train)
                for text, label in train:
                    counts[label].update(text.split())
                vocab = set(w for c in counts.values() for w in c)

                def score(text, label):
                    total = sum(counts[label].values())
                    s = math.log(docs[label] / len(train))
                    for w in text.split():
                        s += math.log((counts[label][w] + 1) / (total + len(vocab)))
                    return s

                for msg in ("free cash offer", "project meeting today"):
                    print(msg, "->", max(("spam", "ham"), key=lambda lab: score(msg, lab)))
            """),
        ],
        ["P(A|B) = P(B|A) P(A) / P(B)", "P(B) = P(B|A)P(A) + P(B|A')P(A')", "posterior odds = prior odds x LR", "PPV = TP / (TP + FP)", "sklearn.naive_bayes.MultinomialNB()"],
        ["Ignoring the base rate (prior) overstates how informative evidence is.", "Naive Bayes assumes features are conditionally independent, which rarely holds exactly.", "Conditioning on the wrong event (P(evidence | guilt) vs P(guilt | evidence))."],
        [
            qa("basic", "State Bayes' theorem.", "P(A | B) = P(B | A) P(A) / P(B). It updates the prior probability of A to a posterior after observing B, weighting by how likely B is when A is true relative to overall."),
            qa("intermediate", "A test is 99% sensitive and 95% specific; prevalence is 1%. What is P(disease | positive)?", "Out of 10,000 people, 100 are sick and 99 test positive, while 9,900 are healthy and about 495 test positive. So P(disease | positive) = 99 / 594, about 16.7%."),
            qa("intermediate", "What is the prosecutor's fallacy?", "Treating P(evidence | innocent) as if it were P(innocent | evidence). A one-in-a-million DNA match probability does not mean a one-in-a-million chance of innocence when millions of people could have matched."),
            qa("advanced", "Why is naive Bayes 'naive' and why does it still work?", "It assumes features are independent given the class, which is usually false. It still classifies well because ranking only needs the class with the highest posterior to be correct, even if the probabilities themselves are poorly calibrated."),
        ],
        ["probability-basics", "bayes-vs-frequentist", "type-errors-power"],
        chain(
            ("Prior", "P(A)", "Prior", "Start with the base rate of the hypothesis."),
            ("Evidence", "observe B", "Observe", "New evidence B arrives, e.g. a positive test.", "belief"),
            ("Likelihood", "P(B | A)", "Likelihood", "How probable is B if A is true, and if not?", "B"),
            ("Normalise", "total prob.", "Evidence term", "P(B) sums over both ways B can happen.", "ratios"),
            ("Posterior", "P(A | B)", "Update", "Posterior = likelihood x prior / evidence.", "updated"),
        ),
    ),
    topic(
        "expectation", "Expected Value & Variance of Random Variables", "probability", "intermediate", "EV",
        "The long-run average outcome, the tool for valuing bets, offers and decisions under uncertainty.",
        "Expected value is the average you would get if you could replay the same gamble thousands of times. A lottery ticket's EV is what each ticket is worth on average, even though nobody ever wins that exact amount.",
        "A random variable maps outcomes to numbers. Its expected value E[X] is the probability-weighted average of its values: sum of x * P(x) for discrete variables or the integral of x * f(x) for continuous ones. Expectation is linear: E[aX + bY + c] = aE[X] + bE[Y] + c, whether or not X and Y are independent, which makes complex expectations easy (e.g., expected number of matches). Variance is Var(X) = E[(X - E[X])^2] = E[X^2] - E[X]^2; Var(aX + b) = a^2 Var(X), and Var(X + Y) = Var(X) + Var(Y) + 2Cov(X, Y). For independent variables E[XY] = E[X]E[Y]. Expected value drives decision analysis: compare actions by expected profit or expected cost, e.g. whether to send a retention offer given churn probability, offer cost and customer value. EV alone ignores risk, so variance, worst-case loss or utility functions matter when outcomes are large relative to resources. The law of large numbers guarantees sample averages converge to E[X] when it exists; heavy-tailed variables such as the Cauchy have no mean.",
        ["Deciding whether a marketing offer is worth sending.", "Pricing insurance or warranties.", "Expected cost of false positives versus false negatives in a classifier threshold.", "Estimating expected revenue from a pipeline of deals."],
        [
            "E[X] = sum x P(x); it may not be a value X can take.",
            "Linearity of expectation needs no independence.",
            "Var(X) = E[X^2] - (E[X])^2.",
            "Var(aX + b) = a^2 Var(X).",
            "Expected value ignores risk; consider variance or utility.",
        ],
        [
            ex("Should we send the retention offer?", "intermediate", "Compare expected profit of acting vs not acting per customer.", "python", """
                customers = [  # (churn probability, annual value), synthetic
                    (0.05, 300), (0.40, 500), (0.70, 200), (0.20, 1200), (0.55, 900),
                ]
                OFFER_COST, SAVE_RATE = 40, 0.30     # offer stops 30% of would-be churners
                total = 0
                for p, value in customers:
                    gain = p * SAVE_RATE * value - OFFER_COST
                    total += max(gain, 0)
                    print(f"p={p:.2f} value={value:5}: expected gain {gain:+7.1f} -> {'send' if gain > 0 else 'skip'}")
                print("expected profit from targeting:", round(total, 1))
            """),
            ex("Linearity, variance and the law of large numbers", "intermediate", "A fair die: exact moments and simulated running mean.", "python", """
                import random
                from fractions import Fraction

                faces = range(1, 7)
                ex1 = sum(Fraction(x, 6) for x in faces)
                ex2 = sum(Fraction(x * x, 6) for x in faces)
                print("E[X] =", ex1, " Var(X) =", ex2 - ex1 ** 2, " E[sum of 10 dice] =", 10 * ex1)

                random.seed(5)
                total = 0
                for n in range(1, 100001):
                    total += random.randint(1, 6)
                    if n in (10, 100, 1000, 100000):
                        print(f"n={n:6}: running mean {total / n:.4f}")
            """),
        ],
        ["E[X] = sum(x * p(x))", "E[aX + bY] = aE[X] + bE[Y]", "Var(X) = E[X^2] - E[X]^2", "Cov(X,Y) = E[XY] - E[X]E[Y]", "np.average(values, weights=probs)"],
        ["Maximising expected value can be ruinous when a rare loss is catastrophic.", "Expected value of a ratio is not the ratio of expected values.", "Heavy-tailed distributions may have undefined or unstable means."],
        [
            qa("basic", "What is expected value?", "The probability-weighted average of all possible values of a random variable, i.e. the long-run average over many repetitions. For a fair die it is 3.5, a value that never actually appears."),
            qa("intermediate", "What does linearity of expectation say and why is it useful?", "E[X + Y] = E[X] + E[Y] for any random variables, even dependent ones. It turns hard problems into sums of simple indicator expectations, e.g. the expected number of people who get their own hat back is 1 for any n."),
            qa("intermediate", "How would you choose a classification threshold using expected value?", "Assign a cost or benefit to each outcome (TP, FP, TN, FN), then pick the threshold that maximises expected profit, which for a calibrated probability p is to act when p * benefit exceeds (1 - p) * cost."),
            qa("advanced", "Is E[X / Y] equal to E[X] / E[Y]?", "Generally no, because division is nonlinear (Jensen's inequality). This matters for ratio metrics such as revenue per session, which need the delta method or bootstrap for correct variance and careful definitions."),
        ],
        ["probability-basics", "distributions", "metrics-design"],
        chain(
            ("Outcomes", "values x", "List", "Enumerate the values the random variable can take."),
            ("Probabilities", "p(x)", "Weigh", "Attach a probability to each value.", "values"),
            ("Expectation", "sum x p(x)", "Average", "Probability-weighted average gives E[X].", "weights"),
            ("Risk", "variance", "Spread", "Variance shows how far outcomes stray from E[X].", "E[X]"),
            ("Decide", "max EV / utility", "Act", "Compare actions by expected value and risk.", "EV, Var"),
        ),
    ),
    topic(
        "distributions", "Probability Distributions: Normal, Binomial, Poisson, Exponential, Uniform", "probability", "intermediate", "DI",
        "A small zoo of shapes that model most real data: bell curves, counts, arrivals, waiting times and flat randomness.",
        "Distributions are templates for the noise in the world. Heights look like a bell, coin-flip tallies like a binomial, calls per minute like a Poisson, and time until the next call like an exponential.",
        "The normal (Gaussian) distribution N(mu, sigma^2) is symmetric and bell-shaped, arises from sums of many small effects (CLT) and models measurement error and many biological traits. The binomial B(n, p) counts successes in n independent yes/no trials with probability p: mean np, variance np(1 - p); conversions out of visitors are binomial. The Poisson(lambda) counts events in a fixed interval when events occur independently at a constant rate: mean and variance both equal lambda, useful for tickets per hour or defects per batch; it approximates the binomial for large n and small p. The exponential(lambda) models waiting time between Poisson events, has mean 1/lambda and is memoryless. The uniform(a, b) gives equal density on an interval, mean (a + b)/2, and is the basis for random number generation. Other important ones include the lognormal (products of effects, e.g. income), Bernoulli, geometric, t, chi-square and F. Discrete distributions have a probability mass function; continuous ones have a density and you compute probabilities over intervals with the CDF. Overdispersion (variance > mean in counts) suggests a negative binomial instead of Poisson.",
        ["Modelling conversions (binomial) and support tickets per hour (Poisson).", "Simulating waiting times for capacity planning (exponential).", "Computing tail probabilities for control charts (normal).", "Generating synthetic data for tests (uniform, normal)."],
        [
            "Normal: symmetric, mean = median = mode, defined by mu and sigma.",
            "Binomial: n trials, p success; mean np, var np(1 - p).",
            "Poisson: counts per interval; mean = variance = lambda.",
            "Exponential: time between Poisson events; memoryless, mean 1/lambda.",
            "Uniform: equal density on [a, b]; mean (a + b)/2, var (b - a)^2/12.",
        ],
        [
            ex("PMFs, PDFs and CDFs with the standard library", "intermediate", "Binomial and Poisson probabilities via math, normal via NormalDist.", "python", """
                import math
                from statistics import NormalDist

                def binom_pmf(k, n, p):
                    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)

                def poisson_pmf(k, lam):
                    return math.exp(-lam) * lam ** k / math.factorial(k)

                print("P(3 conversions of 20 at p=0.1):", round(binom_pmf(3, 20, 0.1), 4))
                print("P(at most 2 tickets | lambda=4):", round(sum(poisson_pmf(k, 4) for k in range(3)), 4))
                iq = NormalDist(100, 15)
                print("P(IQ > 130):", round(1 - iq.cdf(130), 4), " 97.5th pct:", round(iq.inv_cdf(0.975), 1))
                print("P(wait > 5 min | 1 per 3 min):", round(math.exp(-5 / 3), 4))
                print("uniform(0,10) var:", (10 - 0) ** 2 / 12)
            """),
            ex("Simulate and compare moments", "intermediate", "Sample each distribution with random and check mean and variance.", "python", """
                import random
                import statistics as st

                random.seed(7)
                N = 20000

                def poisson(lam):
                    count, t = 0, random.expovariate(lam)
                    while t < 1:
                        count += 1
                        t += random.expovariate(lam)
                    return count

                sims = {
                    "normal(10, 2)": [random.gauss(10, 2) for _ in range(N)],
                    "binomial(20, .3)": [sum(random.random() < 0.3 for _ in range(20)) for _ in range(N)],
                    "poisson(4)": [poisson(4) for _ in range(N)],
                    "exponential(0.5)": [random.expovariate(0.5) for _ in range(N)],
                    "uniform(0, 6)": [random.uniform(0, 6) for _ in range(N)],
                }
                for name, x in sims.items():
                    print(f"{name:17} mean {st.fmean(x):6.3f}  var {st.variance(x):6.3f}")
            """),
            ex("scipy.stats distributions", "basic", "The same distributions with a uniform API.", "python", """
                from scipy import stats

                print(stats.binom.pmf(3, n=20, p=0.1), stats.binom.cdf(3, 20, 0.1))
                print(stats.poisson.sf(6, mu=4))          # P(X > 6)
                print(stats.norm.ppf(0.975), stats.expon.mean(scale=3))
                samples = stats.norm.rvs(loc=0, scale=1, size=1000, random_state=0)
            """, False),
        ],
        ["NormalDist(mu, sigma).cdf(x) / .inv_cdf(q)", "math.comb(n,k) p^k (1-p)^(n-k)", "e^-lam lam^k / k!", "P(T > t) = e^(-lam t)", "stats.binom · stats.poisson · stats.expon · stats.uniform"],
        ["Count data with variance far above the mean is overdispersed; Poisson underestimates uncertainty.", "Real data are rarely exactly normal; check tails before using normal-based thresholds.", "Exponential's rate vs scale parameterisation differs between libraries (random.expovariate takes the rate)."],
        [
            qa("basic", "When would you use a binomial versus a Poisson distribution?", "Binomial counts successes in a fixed number n of independent trials with the same p, such as conversions out of 1,000 visitors. Poisson counts events in a continuous interval with no fixed upper limit, such as calls per hour."),
            qa("intermediate", "What does memorylessness of the exponential distribution mean?", "P(T > s + t | T > s) = P(T > t): having already waited s minutes does not change the distribution of the remaining wait. It is the only continuous distribution with this property."),
            qa("intermediate", "What is the relationship between Poisson and exponential distributions?", "If events arrive as a Poisson process with rate lambda, counts per unit time are Poisson(lambda) and the gaps between events are exponential with mean 1/lambda."),
            qa("advanced", "Your ticket counts have mean 5 and variance 20. What does that suggest?", "Overdispersion relative to a Poisson, often due to heterogeneity between days or clustering of events. A negative binomial model or a Poisson model with covariates and robust errors is more appropriate."),
        ],
        ["central-limit-theorem", "skew-kurtosis", "expectation"],
        chain(
            ("Question", "what is counted?", "Identify", "Is it a measurement, a count of successes, a count of events or a wait?"),
            ("Discrete?", "binomial/Poisson", "Counts", "Fixed trials: binomial. Open-ended interval: Poisson.", "data type"),
            ("Continuous?", "normal/exp/unif", "Measurements", "Symmetric sums: normal; waits: exponential; flat: uniform.", "data type"),
            ("Fit", "estimate params", "Fit", "Estimate parameters, e.g. mean for lambda or p = k / n.", "family"),
            ("Check", "plots, moments", "Validate", "Compare simulated or theoretical moments and Q-Q plots.", "params"),
        ),
    ),
    topic(
        "central-limit-theorem", "Central Limit Theorem", "probability", "intermediate", "CL",
        "Averages of many independent draws look normal, whatever the shape of the original data.",
        "Single dice rolls are flat, but the average of 30 dice clusters into a neat bell. Individual chaos averages out into predictable order.",
        "The central limit theorem (CLT) states that for independent, identically distributed observations with finite mean mu and variance sigma^2, the distribution of the sample mean approaches a normal distribution N(mu, sigma^2 / n) as n grows, regardless of the population's shape. Equivalently, the standardised mean (x_bar - mu) / (sigma / sqrt(n)) approaches the standard normal. This is why z-tests, t-tests and normal-approximation confidence intervals work for means and proportions even when individual data are skewed. The common rule of thumb n >= 30 is only a heuristic: symmetric data converge quickly, while heavily skewed or heavy-tailed data (revenue, latency) may need hundreds or thousands of observations. The CLT requires finite variance; Cauchy-distributed data never converge. It applies to sums as well as means, and variants extend it to non-identical or weakly dependent data, but strongly correlated observations (sessions within users, time series) shrink the effective sample size. The CLT is about the sampling distribution of the mean, not the data themselves: the data do not become normal.",
        ["Justifying normal-based confidence intervals for averages.", "Running z-tests on conversion rates in A/B tests.", "Understanding why noise in aggregated metrics shrinks with sqrt(n).", "Checking whether a sample is large enough for skewed metrics."],
        [
            "Sample mean ~ N(mu, sigma^2 / n) for large n.",
            "Standard error shrinks as 1 / sqrt(n).",
            "Skewed or heavy-tailed data need much larger n than 30.",
            "Requires independence and finite variance.",
            "The data stay skewed; only the mean's distribution becomes normal.",
        ],
        [
            ex("Means of skewed data become normal", "intermediate", "Exponential data have skew 2; their means lose skew as n grows.", "python", """
                import random
                import statistics as st

                random.seed(13)

                def skew(x):
                    m, s = st.fmean(x), st.pstdev(x)
                    return sum(((v - m) / s) ** 3 for v in x) / len(x)

                for n in (1, 5, 30, 200):
                    means = [st.fmean(random.expovariate(1.0) for _ in range(n)) for _ in range(3000)]
                    print(f"n={n:3}: mean {st.fmean(means):.3f}  sd {st.stdev(means):.3f} (theory {1 / n ** 0.5:.3f})  skew {skew(means):+.2f}")
            """),
            ex("Text histogram of dice averages", "basic", "Watch the bell shape appear.", "python", """
                import random
                from collections import Counter

                random.seed(2)
                for n in (1, 2, 10):
                    avgs = Counter(round(sum(random.randint(1, 6) for _ in range(n)) / n) for _ in range(6000))
                    print(f"average of {n} dice")
                    for v in range(1, 7):
                        print(f"  {v} {'#' * (avgs[v] // 100)}")
            """),
        ],
        ["x_bar ~ N(mu, sigma^2 / n)", "z = (x_bar - mu) / (sigma / sqrt(n))", "SE(p_hat) = sqrt(p(1-p)/n)", "Effective n is smaller with correlated data"],
        ["n >= 30 is not a law; check convergence for skewed metrics by simulation or bootstrap.", "Heavy tails (e.g., a few whales in revenue) slow convergence dramatically.", "Non-independent observations break the variance formula."],
        [
            qa("basic", "What does the central limit theorem say?", "The sampling distribution of the mean of n independent, identically distributed variables with finite variance approaches a normal distribution with mean mu and standard deviation sigma / sqrt(n) as n increases, whatever the original distribution."),
            qa("intermediate", "Why is the CLT important for A/B testing?", "Conversion indicators are Bernoulli, but the mean conversion rate over thousands of users is approximately normal, so z-tests and normal confidence intervals for the difference are valid."),
            qa("intermediate", "Is n = 30 always enough?", "No. It works for roughly symmetric data, but highly skewed or heavy-tailed metrics such as revenue per user may need thousands of observations before the mean's distribution is close to normal. Simulation or bootstrap can check this."),
            qa("advanced", "When does the CLT fail?", "When variance is infinite (Cauchy, some Pareto distributions), when observations are strongly dependent, or when n is small relative to the skewness. In these cases use robust statistics, transformations, block methods or exact tests."),
        ],
        ["distributions", "confidence-intervals", "sampling-bias"],
        chain(
            ("Population", "any shape", "Population", "Data may be skewed, flat or lumpy, but with finite variance."),
            ("Samples", "size n, many", "Repeat sampling", "Draw many independent samples of size n.", "draws"),
            ("Means", "one per sample", "Average", "Compute the mean of each sample.", "samples"),
            ("Bell curve", "N(mu, s^2/n)", "Normal limit", "The means form an approximately normal distribution.", "means"),
            ("Inference", "z / t tools", "Use", "Build intervals and tests for the mean.", "normal"),
        ),
    ),
    topic(
        "bayes-vs-frequentist", "Bayesian vs Frequentist Inference", "probability", "advanced", "BF",
        "Fixed parameter and random data, or uncertain parameter updated by data: two lenses on the same evidence.",
        "A frequentist is a referee with a fixed rulebook: given a hypothesis, how surprising is this game? A Bayesian is a detective who starts with a hunch and updates it with every clue.",
        "Frequentist inference treats parameters as fixed unknowns and probability as long-run frequency of data under repeated sampling. Its tools are estimators, p-values, confidence intervals and error rates (alpha, power) that are guaranteed over hypothetical repetitions. Bayesian inference treats parameters as uncertain quantities with a prior distribution and uses Bayes' theorem to produce a posterior given observed data. Results are direct probability statements, such as 'there is a 94% probability variant B beats A', and credible intervals contain the parameter with stated probability. Conjugate pairs make some updates analytic, for example a Beta(a, b) prior for a conversion rate with k successes in n trials gives a Beta(a + k, b + n - k) posterior. Bayesian methods naturally incorporate prior knowledge, handle small samples and hierarchical structure (partial pooling across segments), and allow continuous monitoring of evidence, though optional stopping still affects frequentist error rates. Criticisms are subjectivity of priors and computational cost (MCMC); frequentist critiques include unintuitive p-values. With weak priors and lots of data the two usually agree numerically.",
        ["Reporting A/B results as 'probability to beat control' to stakeholders.", "Estimating rates for small segments with partial pooling.", "Incorporating prior experiments into a new test.", "Choosing between p-value-based and posterior-based decision rules."],
        [
            "Frequentist: parameters fixed, data random; Bayesian: parameters random given data.",
            "Confidence interval vs credible interval interpretations differ.",
            "Beta-binomial conjugacy: Beta(a + k, b + n - k).",
            "Priors matter for small data and wash out with large data.",
            "Hierarchical Bayes shrinks noisy segment estimates toward the group mean.",
        ],
        [
            ex("Beta-binomial A/B posterior", "advanced", "Sample the posteriors to compute P(B > A) and expected lift.", "python", """
                import random
                import statistics as st

                random.seed(4)
                a_conv, a_n = 120, 2400
                b_conv, b_n = 145, 2380
                prior_a, prior_b = 1, 1                               # uniform Beta(1, 1) prior
                draws = 20000
                pa = [random.betavariate(prior_a + a_conv, prior_b + a_n - a_conv) for _ in range(draws)]
                pb = [random.betavariate(prior_a + b_conv, prior_b + b_n - b_conv) for _ in range(draws)]
                lift = sorted(b - a for a, b in zip(pa, pb))
                print(f"P(B > A) = {sum(l > 0 for l in lift) / draws:.3f}")
                print(f"mean lift {st.fmean(lift):.4f}, 95% credible interval [{lift[500]:.4f}, {lift[19499]:.4f}]")
            """),
            ex("Same data, frequentist z-test", "intermediate", "Two-proportion z-test and confidence interval for comparison.", "python", """
                import math
                from statistics import NormalDist

                a_conv, a_n, b_conv, b_n = 120, 2400, 145, 2380
                pa, pb = a_conv / a_n, b_conv / b_n
                pooled = (a_conv + b_conv) / (a_n + b_n)
                se0 = math.sqrt(pooled * (1 - pooled) * (1 / a_n + 1 / b_n))
                z = (pb - pa) / se0
                p_value = 2 * (1 - NormalDist().cdf(abs(z)))
                se = math.sqrt(pa * (1 - pa) / a_n + pb * (1 - pb) / b_n)
                print(f"z = {z:.3f}, two-sided p = {p_value:.4f}")
                print(f"95% CI for lift [{pb - pa - 1.96 * se:.4f}, {pb - pa + 1.96 * se:.4f}]")
            """),
            ex("Hierarchical model in PyMC", "advanced", "Partial pooling of conversion rates across many segments.", "python", """
                import pymc as pm

                with pm.Model():
                    mu = pm.Beta("mu", 2, 20)
                    kappa = pm.HalfNormal("kappa", 100)
                    rate = pm.Beta("rate", mu * kappa, (1 - mu) * kappa, shape=len(segments))
                    pm.Binomial("obs", n=trials, p=rate, observed=conversions)
                    idata = pm.sample(1000, tune=1000, random_seed=0)
            """, False),
        ],
        ["posterior proportional to likelihood x prior", "Beta(a, b) + k/n -> Beta(a+k, b+n-k)", "random.betavariate(a, b)", "Credible interval: percentiles of posterior draws", "pm.sample() · az.summary(idata)"],
        ["A strong, unjustified prior can dominate small datasets.", "Bayesian monitoring does not make peeking free if you then report frequentist error rates.", "Reporting 'P(B > A) = 95%' without the size of the lift hides practical significance."],
        [
            qa("basic", "What is the core difference between Bayesian and frequentist statistics?", "Frequentists treat parameters as fixed and reason about the distribution of data across repeated samples. Bayesians treat parameters as uncertain, encode beliefs as a prior and update to a posterior given the observed data."),
            qa("intermediate", "How does a credible interval differ from a confidence interval?", "A 95% credible interval contains the parameter with 95% posterior probability, given the model and prior. A 95% confidence interval is produced by a procedure that captures the fixed parameter in 95% of repeated samples; it makes no probability statement about this one interval."),
            qa("intermediate", "What is a conjugate prior? Give an example.", "A prior that yields a posterior in the same family. A Beta prior for a binomial proportion is conjugate: Beta(a, b) with k successes in n trials becomes Beta(a + k, b + n - k)."),
            qa("advanced", "When would you prefer a Bayesian approach in industry?", "When data are sparse or hierarchical (many small segments), when prior information from past experiments is reliable, or when decision-makers need direct statements like probability of improvement and expected loss. Frequentist methods remain preferable where regulatory error-rate guarantees are required."),
        ],
        ["conditional-bayes", "hypothesis-testing", "ab-testing"],
        chain(
            ("Prior", "Beta(a, b)", "Belief", "Encode what you believe about the rate before the test."),
            ("Data", "k of n", "Observe", "Collect conversions k out of n users.", "prior"),
            ("Posterior", "Beta(a+k, ..)", "Update", "Combine prior and likelihood into the posterior.", "likelihood"),
            ("Decide", "P(B>A), loss", "Decision", "Act on probability to beat and expected loss.", "posterior"),
        ),
    ),
    topic(
        "pearson-spearman", "Pearson vs Spearman Correlation", "statistics", "intermediate", "PS",
        "Pearson measures straight-line association; Spearman measures any monotonic association using ranks.",
        "Pearson asks 'do these points hug a straight line?'. Spearman asks the more relaxed question 'when one goes up, does the other reliably go up too, at whatever speed?'.",
        "Pearson's correlation coefficient r is the covariance of two variables divided by the product of their standard deviations; it ranges from -1 to 1 and measures the strength of a linear relationship. It is sensitive to outliers and can be near zero for strong nonlinear relationships such as a U-shape. Spearman's rank correlation rho is Pearson's r computed on the ranks of the data, so it captures any monotonic relationship, is robust to outliers and suits ordinal data. Kendall's tau is another rank measure based on concordant and discordant pairs, with better small-sample properties and an intuitive interpretation. r squared in simple regression equals the proportion of variance explained. Significance of a correlation depends on n: with 10,000 points, r = 0.03 is 'significant' but negligible. Correlation coefficients describe association only, not causation, and should always be accompanied by a scatter plot. Restricted range (e.g., only admitted students) attenuates correlations, and aggregating data (ecological correlation) inflates them.",
        ["Screening features for association with a target.", "Measuring agreement between two rankings (e.g., model vs human).", "Checking relationships in ordinal survey data.", "Building a correlation matrix during EDA."],
        [
            "Pearson: linear, uses raw values, outlier-sensitive.",
            "Spearman: monotonic, uses ranks, robust.",
            "r near 0 does not mean no relationship; it might be nonlinear.",
            "Statistical significance is not practical strength.",
            "Always plot before trusting a coefficient.",
        ],
        [
            ex("Linear vs monotonic vs outlier", "intermediate", "statistics.correlation supports method='ranked' (Spearman) in Python 3.12+.", "python", """
                import statistics as st

                x = list(range(1, 21))
                cases = {
                    "linear": [2 * v + 1 for v in x],
                    "exponential": [2 ** (v / 2) for v in x],
                    "u-shape": [(v - 10.5) ** 2 for v in x],
                    "outlier": [v for v in x[:-1]] + [-200],
                }
                for name, y in cases.items():
                    p = st.correlation(x, y)
                    s = st.correlation(x, y, method="ranked")
                    print(f"{name:12} pearson {p:+.3f}  spearman {s:+.3f}")
            """),
            ex("Spearman by hand via ranks", "basic", "Rank both variables, then apply Pearson.", "python", """
                import statistics as st

                def ranks(v):
                    order = sorted(range(len(v)), key=lambda i: v[i])
                    r = [0] * len(v)
                    for rank, i in enumerate(order, start=1):
                        r[i] = rank
                    return r

                hours = [1, 2, 3, 5, 8, 13]
                score = [52, 55, 61, 70, 74, 99]
                print("ranks", ranks(hours), ranks(score))
                print("spearman", st.correlation(ranks(hours), ranks(score)))
                print("pearson ", round(st.correlation(hours, score), 4))
            """),
        ],
        ["statistics.correlation(x, y)", "statistics.correlation(x, y, method='ranked')", "df.corr(method='spearman')", "scipy.stats.pearsonr · spearmanr · kendalltau", "r^2 = share of variance explained (simple OLS)"],
        ["Correlation of aggregated group means is much stronger than of individuals.", "Restricted range shrinks correlation even when the relationship is strong.", "Ties need average ranks; libraries handle this, hand-rolled code may not."],
        [
            qa("basic", "When would you use Spearman instead of Pearson?", "When the relationship is monotonic but not linear, when data are ordinal, or when outliers would distort Pearson. Spearman works on ranks, so only the order of values matters."),
            qa("intermediate", "Can two variables have zero Pearson correlation but be strongly related?", "Yes. A symmetric U-shaped relationship such as y = x^2 on a range centred at zero has Pearson r near zero because increases and decreases cancel. Plotting reveals the dependence."),
            qa("intermediate", "What does r = 0.8 tell you, and what not?", "That there is a strong positive linear association and about 64% of the variance in one variable is linearly explained by the other. It does not say anything about causation, slope size or whether the relationship holds outside the observed range."),
            qa("advanced", "How does Kendall's tau differ from Spearman's rho?", "Tau is based on the proportion of concordant minus discordant pairs, so it has a probabilistic interpretation and better behaviour with small samples and many ties. Its values are usually smaller in magnitude than rho for the same data."),
        ],
        ["correlation-causation", "simple-linear-regression", "eda"],
        chain(
            ("Scatter", "plot first", "Look", "Plot the pair to see shape, clusters and outliers."),
            ("Linear?", "Pearson r", "Pearson", "Use Pearson for straight-line relationships in interval data.", "shape"),
            ("Monotonic?", "Spearman rho", "Spearman", "Use ranks for monotonic, ordinal or outlier-prone data.", "shape"),
            ("Interpret", "size + context", "Meaning", "Judge strength in context; never infer causation.", "coefficient"),
        ),
    ),
    topic(
        "time-series-basics", "Time Series Basics: Trend, Seasonality, Moving Averages", "statistics", "intermediate", "TS",
        "Ordered data have memory: separate trend, seasonal cycles and noise before you compare or forecast.",
        "A time series is like the tide on a beach slowly rising for the season. Waves (noise) and the daily tide (seasonality) ride on top of the slow rise (trend), and you need to tell them apart before predicting tomorrow.",
        "A time series is a sequence of observations indexed by time, where neighbouring values are correlated (autocorrelation). Classical decomposition writes the series as trend + seasonality + residual (additive) or trend * seasonality * residual (multiplicative, when seasonal swings grow with the level). A moving average smooths noise: a simple moving average (SMA) averages the last k points, a centred moving average estimates trend, and an exponentially weighted moving average (EWMA) gives recent points more weight via a smoothing factor alpha. Seasonality is a fixed-period pattern (weekly, yearly); comparing week-over-week or year-over-year, or seasonal differencing, removes it. Many models (ARIMA) assume stationarity, meaning constant mean and variance over time, which differencing or transformations help achieve. Validation must respect time order: train on the past and test on the future, using rolling-origin evaluation. Baselines matter: naive (last value) and seasonal naive (same day last week) forecasts are surprisingly hard to beat. Watch for calendar effects, holidays, missing timestamps and time zone issues.",
        ["Smoothing a noisy daily KPI for a dashboard.", "Forecasting demand or traffic for capacity planning.", "Comparing this week with the same week last year.", "Detecting anomalies relative to a seasonal baseline."],
        [
            "Components: trend, seasonality, residual (additive or multiplicative).",
            "SMA averages a window; EWMA weights recent values more.",
            "Seasonal naive forecast is a strong baseline.",
            "Never shuffle time series for train/test splits.",
            "Differencing removes trend; seasonal differencing removes seasonality.",
        ],
        [
            ex("Moving averages and EWMA", "basic", "Smooth a synthetic daily series with weekly seasonality.", "python", """
                import math
                import random

                random.seed(3)
                days = 28
                series = [100 + 0.8 * d + 15 * math.sin(2 * math.pi * d / 7) + random.gauss(0, 4) for d in range(days)]

                def sma(x, k):
                    return [sum(x[i - k + 1:i + 1]) / k if i >= k - 1 else None for i in range(len(x))]

                def ewma(x, alpha):
                    out, s = [], x[0]
                    for v in x:
                        s = alpha * v + (1 - alpha) * s
                        out.append(s)
                    return out

                ma7, ew = sma(series, 7), ewma(series, 0.3)
                for d in range(0, days, 4):
                    m = "   -  " if ma7[d] is None else f"{ma7[d]:6.1f}"
                    print(f"day {d:2}: raw {series[d]:6.1f}  sma7 {m}  ewma {ew[d]:6.1f}")
            """),
            ex("Seasonal naive beats naive", "intermediate", "Forecast the last two weeks with two baselines and compare MAE.", "python", """
                import math
                import random
                import statistics as st

                random.seed(8)
                y = [200 + 40 * (d % 7 in (5, 6)) + 0.5 * d + random.gauss(0, 5) for d in range(70)]
                train, test = y[:56], y[56:]
                naive = [train[-1]] * len(test)
                seasonal = [train[-7 + (i % 7)] for i in range(len(test))]
                mae = lambda f: st.fmean(abs(a - b) for a, b in zip(test, f))
                print(f"naive MAE {mae(naive):.2f}   seasonal naive MAE {mae(seasonal):.2f}")
            """),
            ex("pandas resample, rolling and decomposition", "intermediate", "Typical time series toolkit.", "python", """
                import pandas as pd
                from statsmodels.tsa.seasonal import seasonal_decompose

                s = df.set_index("date")["orders"].asfreq("D")
                weekly = s.resample("W").sum()
                smooth = s.rolling(7, center=True).mean()
                ewm = s.ewm(alpha=0.3).mean()
                parts = seasonal_decompose(s.interpolate(), model="additive", period=7)
                yoy = s.pct_change(periods=364)
            """, False),
        ],
        ["s.rolling(7).mean() · s.ewm(alpha=0.3).mean()", "s.resample('W').sum()", "s.diff() · s.diff(7)", "seasonal_decompose(s, period=7)", "AVG(v) OVER (ORDER BY d ROWS 6 PRECEDING)"],
        ["Trailing moving averages lag the true signal; centred ones use future data (fine for analysis, not forecasting).", "Random train/test splits leak the future.", "Comparing a holiday week with a normal week produces false alarms."],
        [
            qa("basic", "What are trend and seasonality?", "Trend is the long-term increase or decrease in level; seasonality is a repeating pattern with a fixed period, such as weekday cycles or yearly peaks. Residual is what remains after removing both."),
            qa("basic", "What is the difference between a simple and an exponential moving average?", "A simple moving average weights the last k points equally and drops older ones abruptly. An exponential moving average weights all past points with geometrically decaying weights controlled by alpha, reacting faster to recent changes."),
            qa("intermediate", "How should you validate a forecasting model?", "Use time-ordered splits such as rolling-origin (walk-forward) evaluation: train on data up to t, forecast t+1..t+h, roll forward and repeat. Compare against naive and seasonal-naive baselines with metrics like MAE or MAPE."),
            qa("advanced", "What is stationarity and why does it matter?", "A stationary series has constant mean, variance and autocorrelation structure over time. Models like ARIMA assume it; non-stationary series are made stationary with differencing, log transforms or detrending, and regressions on non-stationary series can produce spurious correlations."),
        ],
        ["eda", "sql-window-functions", "data-leakage"],
        chain(
            ("Series", "ordered values", "Collect", "Regular timestamps; fill or flag gaps."),
            ("Trend", "smooth / MA", "Trend", "Moving averages reveal the slow-moving level.", "series"),
            ("Season", "period 7, 365", "Seasonality", "Average by period position to estimate the seasonal pattern.", "detrended"),
            ("Residual", "what is left", "Noise", "Residuals should look like noise; spikes are anomalies.", "deseasoned"),
            ("Forecast", "vs naive", "Predict", "Forecast and compare with seasonal-naive baselines.", "components"),
        ),
    ),
]

TOPICS += [
    topic(
        "hypothesis-testing", "Hypothesis Testing & p-values", "experiments", "intermediate", "HT",
        "Assume nothing happened, then ask how surprising the data would be; the p-value quantifies that surprise.",
        "A hypothesis test is a courtroom: the defendant (null hypothesis) is presumed innocent, and you convict only if the evidence would be very unlikely were they innocent. Acquittal does not prove innocence.",
        "A hypothesis test compares a null hypothesis H0 (no effect, no difference) with an alternative H1. You choose a significance level alpha (commonly 0.05) before looking at the data, compute a test statistic, and derive the p-value: the probability, assuming H0 is true, of a statistic at least as extreme as the one observed. If p <= alpha you reject H0; otherwise you fail to reject it, which is not the same as proving H0. Tests can be two-sided (any difference) or one-sided (a pre-specified direction). The p-value is not the probability that H0 is true, nor the probability the result is due to chance, and it says nothing about effect size: tiny effects become significant with huge samples, and large effects can be non-significant with small samples. Report effect sizes with confidence intervals alongside p-values. Permutation tests compute p-values by shuffling labels to simulate H0 and make few assumptions. Pre-registration of hypotheses, metrics and sample size guards against p-hacking, where analysts try many analyses until one crosses 0.05.",
        ["Deciding whether an A/B test variant changed conversion.", "Checking if a process change shifted average defect rates.", "Validating that a model's improvement is not noise.", "Testing data quality assumptions (e.g., a stable mean)."],
        [
            "Fix H0, H1, alpha and the test before seeing the data.",
            "p-value = P(data at least this extreme | H0).",
            "Failing to reject H0 is not evidence H0 is true.",
            "Statistical significance is not practical significance.",
            "Permutation tests make minimal assumptions.",
        ],
        [
            ex("Permutation test for a difference in means", "intermediate", "Shuffle group labels to build the null distribution.", "python", """
                import random
                import statistics as st

                random.seed(7)
                control = [random.gauss(10.0, 3) for _ in range(60)]
                variant = [random.gauss(11.2, 3) for _ in range(60)]
                observed = st.fmean(variant) - st.fmean(control)
                pooled = control + variant
                extreme, R = 0, 5000
                for _ in range(R):
                    random.shuffle(pooled)
                    diff = st.fmean(pooled[60:]) - st.fmean(pooled[:60])
                    extreme += abs(diff) >= abs(observed)
                print(f"observed diff {observed:.3f}")
                print(f"two-sided permutation p-value {extreme / R:.4f}")
            """),
            ex("One-sample z-test", "basic", "Is the average delivery time different from the 30-minute promise?", "python", """
                import math
                from statistics import NormalDist, fmean

                times = [31.2, 29.8, 33.1, 30.5, 32.4, 28.9, 31.7, 34.0, 30.2, 32.8] * 4   # 40 synthetic orders
                mu0, sigma = 30.0, 2.0                       # known historical SD
                z = (fmean(times) - mu0) / (sigma / math.sqrt(len(times)))
                p = 2 * (1 - NormalDist().cdf(abs(z)))
                print(f"mean {fmean(times):.2f}, z = {z:.2f}, p = {p:.5f}")
                print("reject H0 at 5%" if p < 0.05 else "fail to reject H0")
            """),
            ex("scipy hypothesis tests", "basic", "One call per common test.", "python", """
                from scipy import stats

                stats.ttest_ind(a, b, equal_var=False)
                stats.permutation_test((a, b), lambda x, y: x.mean() - y.mean(), n_resamples=9999)
                stats.binomtest(k=58, n=100, p=0.5)
            """, False),
        ],
        ["p = P(T >= t_obs | H0)", "reject H0 if p <= alpha", "z = (x_bar - mu0) / (sigma / sqrt(n))", "stats.ttest_ind · stats.permutation_test", "Report effect size + CI with p"],
        ["Peeking and stopping when p < 0.05 inflates false positives.", "p = 0.049 and p = 0.051 are practically the same evidence.", "Choosing a one-sided test after seeing the direction halves the p-value dishonestly."],
        [
            qa("basic", "What is a p-value?", "The probability of observing data at least as extreme as what was observed, assuming the null hypothesis is true. Small p-values indicate the data are surprising under H0."),
            qa("basic", "What is a p-value not?", "It is not the probability that H0 is true, not the probability the result occurred by chance, and not a measure of effect size or importance. It depends on both the effect and the sample size."),
            qa("intermediate", "What does 'fail to reject the null' mean?", "The data were not surprising enough under H0 at the chosen alpha. The test may simply lack power; absence of evidence is not evidence of absence, so report the confidence interval to show which effects remain plausible."),
            qa("intermediate", "When would you use a one-sided test?", "Only when an effect in the other direction is impossible or would lead to the same action as no effect, and the direction is fixed before seeing data. Otherwise use two-sided tests."),
            qa("advanced", "What is p-hacking and how do you prevent it?", "Trying many analyses, subgroups, metrics or stopping points and reporting the one that reaches significance. Prevent it with pre-registered hypotheses and sample sizes, a primary metric, correction for multiple comparisons and transparent reporting of everything tested."),
        ],
        ["type-errors-power", "t-tests", "confidence-intervals"],
        chain(
            ("Hypotheses", "H0 vs H1", "Frame", "State the null (no effect) and the alternative."),
            ("Alpha", "e.g. 0.05", "Error budget", "Fix the false-positive rate before seeing data.", "H0, H1"),
            ("Statistic", "z, t, chi2", "Compute", "Summarise the evidence in a test statistic.", "data"),
            ("p-value", "P(extreme | H0)", "Surprise", "How unusual is the statistic if H0 were true?", "statistic"),
            ("Decide", "+ effect size", "Conclude", "Reject or not, and report the effect with a CI.", "p"),
        ),
    ),
    topic(
        "type-errors-power", "Type I/II Errors & Statistical Power", "experiments", "intermediate", "PW",
        "False alarms, missed effects, and how sample size buys the power to detect what matters.",
        "A smoke detector can scream at toast (Type I, false alarm) or sleep through a fire (Type II, miss). Making it more sensitive reduces misses but increases false alarms, unless you install a better detector, which is like collecting more data.",
        "A Type I error is rejecting a true null hypothesis (a false positive); its probability is alpha, the significance level. A Type II error is failing to reject a false null (a false negative); its probability is beta. Power = 1 - beta is the probability of detecting an effect of a given size when it exists, conventionally targeted at 80% or 90%. Power depends on four linked quantities: alpha, sample size n, effect size (difference relative to variability, e.g. Cohen's d) and noise. For fixed n, lowering alpha raises beta; increasing n or reducing variance (better measurement, variance reduction like CUPED, paired designs) raises power for all effects. Power analysis is done before an experiment to choose n for a minimum detectable effect (MDE) worth acting on. Underpowered studies not only miss real effects but also exaggerate the effects they do find (the winner's curse, or Type M error) and can even get the sign wrong (Type S). Post-hoc power computed from the observed effect adds no information beyond the p-value.",
        ["Choosing an A/B test's sample size and duration.", "Explaining why a 'no difference' result may be inconclusive.", "Trading off false alarms against missed detections in monitoring.", "Planning a clinical or user study."],
        [
            "Type I = false positive (alpha); Type II = false negative (beta).",
            "Power = 1 - beta; target 80% or more.",
            "Power rises with n, effect size and alpha; falls with variance.",
            "Pick the MDE from business value, not from what is convenient.",
            "Underpowered significant results overestimate the effect.",
        ],
        [
            ex("Power by simulation and by formula", "intermediate", "Two-sample z-test power for a mean difference.", "python", """
                import math
                import random
                import statistics as st
                from statistics import NormalDist

                N = NormalDist()
                delta, sigma, alpha = 0.5, 2.0, 0.05
                z_crit = N.inv_cdf(1 - alpha / 2)
                random.seed(0)
                for n in (50, 100, 200, 400):
                    se = sigma * math.sqrt(2 / n)
                    analytic = 1 - N.cdf(z_crit - delta / se)
                    hits = 0
                    for _ in range(400):
                        a = [random.gauss(0, sigma) for _ in range(n)]
                        b = [random.gauss(delta, sigma) for _ in range(n)]
                        hits += abs(st.fmean(b) - st.fmean(a)) / se > z_crit
                    print(f"n={n:3} per group: power formula {analytic:.2f}, simulated {hits / 400:.2f}")
            """),
            ex("Winner's curse in underpowered tests", "advanced", "Significant results from small samples exaggerate the true effect.", "python", """
                import math
                import random
                import statistics as st

                random.seed(9)
                TRUE, sigma, n = 0.2, 1.0, 30
                se = sigma * math.sqrt(2 / n)
                sig_effects = []
                for _ in range(3000):
                    d = st.fmean(random.gauss(TRUE, sigma) for _ in range(n)) - st.fmean(random.gauss(0, sigma) for _ in range(n))
                    if abs(d) / se > 1.96:
                        sig_effects.append(d)
                print(f"power ~ {len(sig_effects) / 3000:.2f}")
                print(f"true effect {TRUE}, mean significant estimate {st.fmean(sig_effects):.2f}")
                print("wrong sign among significant:", sum(d < 0 for d in sig_effects))
            """),
        ],
        ["alpha = P(reject | H0 true) · beta = P(not reject | H1 true)", "power = 1 - beta", "Cohen's d = (mu1 - mu2) / sigma", "statsmodels TTestIndPower().solve_power(effect_size=0.3, power=0.8, alpha=0.05)"],
        ["Post-hoc 'observed power' is a function of the p-value and adds nothing.", "Running until significant without a fixed n destroys the alpha guarantee.", "Power calculations on the wrong variance (e.g., session-level instead of user-level) are too optimistic."],
        [
            qa("basic", "Define Type I and Type II errors.", "A Type I error rejects a true null hypothesis, a false positive with probability alpha. A Type II error fails to reject a false null hypothesis, a false negative with probability beta."),
            qa("basic", "What is statistical power?", "The probability that a test rejects H0 when a specific alternative is true, 1 - beta. It increases with sample size, effect size and alpha, and decreases with variance."),
            qa("intermediate", "How do you increase power without increasing sample size?", "Reduce variance: use paired or within-subject designs, stratification, covariate adjustment such as CUPED, better-targeted populations, less noisy metrics or capping outliers. You can also accept a larger alpha or test a larger MDE."),
            qa("advanced", "Why are significant results from underpowered studies suspicious?", "Only estimates that happen to be large cross the significance threshold, so the published effect is inflated (Type M error) and may even have the wrong sign (Type S). This contributes to the replication crisis."),
        ],
        ["hypothesis-testing", "ab-testing", "multiple-comparisons"],
        chain(
            ("Truth", "H0 or H1", "Reality", "Either there is an effect or there is not."),
            ("Test", "alpha fixed", "Decision", "The test either rejects H0 or does not.", "data"),
            ("Type I", "false positive", "Alpha", "Rejecting a true H0 happens with probability alpha.", "reject"),
            ("Type II", "false negative", "Beta", "Missing a real effect happens with probability beta.", "no reject"),
            ("Power", "1 - beta", "Plan n", "Choose n so power for the MDE reaches 80%+.", "plan"),
        ),
    ),
    topic(
        "t-tests", "t-Tests: One-Sample, Two-Sample (Welch) & Paired", "experiments", "intermediate", "TT",
        "Compare means when the population SD is unknown, using the t-distribution's heavier tails.",
        "A t-test is a z-test that admits it is unsure about the noise level. With few observations it widens its margins, like a cautious judge asking for stronger evidence.",
        "Student's t-test compares means using the t statistic: difference in means divided by its estimated standard error. Because the SD is estimated from the sample, the statistic follows a t-distribution with heavier tails than the normal, converging to it as degrees of freedom grow. A one-sample t-test compares a mean with a fixed value (df = n - 1). The independent two-sample t-test compares two groups; Student's version assumes equal variances, while Welch's t-test does not and uses the Welch-Satterthwaite degrees of freedom, so Welch is the safer default. A paired t-test analyses the differences within matched pairs (before/after on the same user), removing between-subject variability and often greatly increasing power. Assumptions are independent observations and approximately normal means (CLT helps for large n); severe skew with small n, or ordinal data, call for rank-based alternatives. Report the mean difference, its confidence interval and an effect size such as Cohen's d, not only t and p.",
        ["Comparing average order value between two variants.", "Before/after comparison on the same users or machines.", "Checking whether a mean differs from a target value.", "Comparing model error across paired validation folds."],
        [
            "t = difference / estimated standard error.",
            "Welch's t-test is the default for two independent groups.",
            "Paired tests use within-pair differences and df = n - 1.",
            "t-distribution has heavier tails; approaches normal as df grows.",
            "Report mean difference, CI and Cohen's d.",
        ],
        [
            ex("Welch t-test with a stdlib t-distribution", "intermediate", "Computes t, Welch df and a two-sided p-value by numerical integration.", "python", """
                import math
                import statistics as st

                def t_two_sided_p(t, df, steps=2000):
                    c = math.exp(math.lgamma((df + 1) / 2) - math.lgamma(df / 2)) / math.sqrt(df * math.pi)
                    f = lambda x: c * (1 + x * x / df) ** (-(df + 1) / 2)
                    a = abs(t); h = a / steps
                    s = f(0) + f(a) + sum((4 if i % 2 else 2) * f(i * h) for i in range(1, steps))
                    return 1 - 2 * s * h / 3

                a = [23.1, 25.4, 22.8, 26.0, 24.3, 23.9, 25.1, 24.7, 22.5, 26.4]
                b = [26.2, 27.9, 25.8, 28.4, 27.1, 26.6, 29.0, 27.5]
                va, vb, na, nb = st.variance(a), st.variance(b), len(a), len(b)
                se = math.sqrt(va / na + vb / nb)
                t = (st.fmean(b) - st.fmean(a)) / se
                df = (va / na + vb / nb) ** 2 / ((va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1))
                d = (st.fmean(b) - st.fmean(a)) / math.sqrt((va + vb) / 2)
                print(f"t = {t:.3f}, Welch df = {df:.1f}, p = {t_two_sided_p(t, df):.5f}, Cohen's d = {d:.2f}")
            """),
            ex("Paired vs unpaired on the same data", "intermediate", "Pairing removes between-user variation and boosts power.", "python", """
                import math
                import random
                import statistics as st

                random.seed(5)
                base = [random.gauss(100, 20) for _ in range(25)]          # users differ a lot
                before = [b + random.gauss(0, 3) for b in base]
                after = [b + 2.5 + random.gauss(0, 3) for b in base]       # small consistent gain
                diffs = [y - x for x, y in zip(before, after)]
                t_paired = st.fmean(diffs) / (st.stdev(diffs) / math.sqrt(len(diffs)))
                se_unpaired = math.sqrt(st.variance(before) / 25 + st.variance(after) / 25)
                t_unpaired = (st.fmean(after) - st.fmean(before)) / se_unpaired
                print(f"paired t = {t_paired:.2f} (df 24)   unpaired t = {t_unpaired:.2f}")
            """),
            ex("scipy t-tests", "basic", "The three variants.", "python", """
                from scipy import stats

                stats.ttest_1samp(x, popmean=30)
                stats.ttest_ind(a, b, equal_var=False)       # Welch
                stats.ttest_rel(before, after)               # paired
            """, False),
        ],
        ["t = (x_bar1 - x_bar2) / sqrt(s1^2/n1 + s2^2/n2)", "stats.ttest_ind(a, b, equal_var=False)", "stats.ttest_rel(before, after)", "d = diff / pooled_sd", "Welch df = (v1/n1 + v2/n2)^2 / (...)"],
        ["Using an unpaired test on paired data wastes power.", "Student's equal-variance test misbehaves with unequal variances and sizes.", "Small skewed samples violate the normality assumption; consider Mann-Whitney or bootstrap."],
        [
            qa("basic", "When do you use a t-test instead of a z-test?", "When the population standard deviation is unknown and estimated from the sample, which is almost always. For large samples the two give nearly identical results."),
            qa("intermediate", "Why prefer Welch's t-test over Student's?", "Welch does not assume equal variances and stays accurate when variances and sample sizes differ, while losing very little power when they are equal. Many statisticians recommend it as the default."),
            qa("intermediate", "When should you use a paired t-test?", "When each observation in one group is naturally matched to one in the other, such as the same users before and after, or two models evaluated on the same folds. It tests whether the mean of the differences is zero."),
            qa("advanced", "What are the assumptions of the two-sample t-test and how robust is it?", "Independent observations, approximately normal sampling distribution of the means and (for Student's) equal variances. It is robust to moderate non-normality with balanced, reasonably large samples, but not to dependence between observations or extreme skew in small samples."),
        ],
        ["hypothesis-testing", "nonparametric-tests", "anova"],
        chain(
            ("Design", "1, 2 or paired", "Choose", "One-sample, two independent samples or paired?"),
            ("Means", "x_bar, s", "Summarise", "Compute group means and sample SDs.", "data"),
            ("t stat", "diff / SE", "Statistic", "Divide the mean difference by its estimated SE.", "means"),
            ("df", "n - 1 / Welch", "Degrees of freedom", "Pick df for the design to read the t-distribution.", "t"),
            ("Result", "p, CI, d", "Report", "p-value, CI of the difference and effect size.", "p"),
        ),
    ),
    topic(
        "chi-square", "Chi-Square Tests", "experiments", "intermediate", "CS",
        "Compare observed counts with expected counts: goodness of fit and independence of categorical variables.",
        "A chi-square test is a stock-taker comparing the shelf with the inventory sheet. Small mismatches are normal shrinkage; huge ones mean something systematic is going on.",
        "Chi-square tests work on counts of categorical data. The statistic sums (observed - expected)^2 / expected over all cells and follows a chi-square distribution under H0. The goodness-of-fit test checks whether one categorical variable matches a hypothesised distribution, e.g. whether traffic splits 50/50 between A/B arms (sample ratio mismatch check) or whether a die is fair; df = categories - 1. The test of independence uses a contingency table of two categorical variables (e.g., device by converted) and computes expected counts as row total * column total / grand total; df = (rows - 1)(columns - 1). A 2x2 independence test is equivalent to a two-proportion z-test (chi-square = z^2). The approximation requires adequate expected counts, commonly at least 5 in each cell; otherwise use Fisher's exact test or combine categories. The test reports whether an association exists, not its strength; use Cramer's V or differences in proportions for effect size, and standardised residuals to see which cells drive the result.",
        ["Detecting sample ratio mismatch in A/B tests.", "Testing whether conversion depends on device or channel.", "Checking whether category frequencies match expectations.", "Survey analysis of categorical answers by segment."],
        [
            "chi2 = sum (O - E)^2 / E.",
            "Goodness of fit: df = k - 1. Independence: df = (r - 1)(c - 1).",
            "Expected counts should be at least about 5 per cell.",
            "Use Fisher's exact test for small 2x2 tables.",
            "Cramer's V measures strength of association.",
        ],
        [
            ex("Sample ratio mismatch check", "intermediate", "Goodness-of-fit test with a stdlib chi-square survival function.", "python", """
                import math

                def chi2_sf(x, k):
                    s, z = k / 2, x / 2
                    term = total = 1 / s
                    n = 1
                    while term > 1e-12 * total:
                        term *= z / (s + n)
                        total += term
                        n += 1
                    return 1 - total * math.exp(-z + s * math.log(z) - math.lgamma(s))

                observed = [50_812, 49_188]                  # users in A and B, designed 50/50
                expected = [sum(observed) / 2] * 2
                chi2 = sum((o - e) ** 2 / e for o, e in zip(observed, expected))
                print(f"chi2 = {chi2:.2f}, df = 1, p = {chi2_sf(chi2, 1):.2e}")
                print("SRM detected: investigate assignment before reading results" if chi2_sf(chi2, 1) < 0.001 else "split OK")
            """),
            ex("Independence test on a contingency table", "intermediate", "Does conversion depend on device?", "python", """
                import math

                table = {"desktop": (420, 3580), "mobile": (510, 6490), "tablet": (70, 930)}   # (converted, not)
                rows = list(table.values())
                col_tot = [sum(r[j] for r in rows) for j in range(2)]
                grand = sum(col_tot)
                chi2 = 0.0
                for name, r in table.items():
                    rt = sum(r)
                    for j in range(2):
                        e = rt * col_tot[j] / grand
                        chi2 += (r[j] - e) ** 2 / e
                    print(f"{name:8} conversion {r[0] / rt:.3%}")
                df = (len(rows) - 1) * (2 - 1)
                cramers_v = math.sqrt(chi2 / (grand * min(len(rows) - 1, 1)))
                print(f"chi2 = {chi2:.2f}, df = {df}, Cramer's V = {cramers_v:.3f}")
                print("critical value at 5% for df=2 is 5.991 ->", "dependent" if chi2 > 5.991 else "no evidence")
            """),
            ex("scipy chi-square and Fisher", "basic", "Library calls for the same tests.", "python", """
                from scipy import stats

                stats.chisquare(f_obs=[50812, 49188])
                chi2, p, dof, expected = stats.chi2_contingency([[420, 3580], [510, 6490], [70, 930]])
                stats.fisher_exact([[3, 1], [1, 3]])
            """, False),
        ],
        ["chi2 = sum((O - E)^2 / E)", "E_ij = row_i * col_j / N", "stats.chi2_contingency(table)", "stats.fisher_exact(2x2)", "V = sqrt(chi2 / (N * (min(r, c) - 1)))"],
        ["Running chi-square on percentages instead of raw counts gives wrong results.", "Observations must be independent: one user counted in several cells breaks the test.", "Large N makes trivial associations significant; report effect size."],
        [
            qa("basic", "What does a chi-square test of independence test?", "Whether two categorical variables are associated, by comparing observed contingency-table counts with the counts expected if they were independent (row total times column total over grand total)."),
            qa("intermediate", "What is a sample ratio mismatch and how do you detect it?", "When the observed split of users between experiment arms deviates from the designed ratio, indicating broken assignment or logging. A chi-square goodness-of-fit test on arm counts with a strict threshold (e.g., p < 0.001) detects it; results should not be trusted until it is explained."),
            qa("intermediate", "When should you use Fisher's exact test instead?", "When expected cell counts are small (commonly below 5), especially in 2x2 tables, because the chi-square approximation becomes unreliable. Fisher's test computes the exact hypergeometric probability."),
            qa("advanced", "How does a 2x2 chi-square relate to the two-proportion z-test?", "Without continuity correction they are equivalent: the chi-square statistic equals the square of the z statistic and the p-values match. The z-test additionally gives the direction and a CI for the difference."),
        ],
        ["hypothesis-testing", "ab-testing", "data-types"],
        chain(
            ("Counts", "contingency", "Tabulate", "Cross-tabulate raw counts of two categorical variables."),
            ("Expected", "row x col / N", "Expected", "Compute counts expected under independence.", "table"),
            ("Statistic", "sum (O-E)^2/E", "Chi-square", "Sum squared deviations scaled by expected counts.", "E"),
            ("df + p", "(r-1)(c-1)", "p-value", "Compare with the chi-square distribution.", "chi2"),
            ("Effect", "Cramer's V", "Strength", "Report strength and inspect residuals per cell.", "p"),
        ),
    ),
    topic(
        "anova", "ANOVA (Analysis of Variance)", "experiments", "advanced", "AN",
        "Test whether several group means differ by comparing between-group to within-group variability.",
        "ANOVA is like judging whether different coffee beans really taste different. If cups from the same bean vary as much as cups from different beans, the bean probably does not matter.",
        "One-way ANOVA tests H0: all k group means are equal against the alternative that at least one differs. It partitions total variability into the between-group sum of squares (how far group means are from the grand mean) and the within-group sum of squares (spread inside groups). The F statistic is the ratio of the between mean square (SSB / (k - 1)) to the within mean square (SSW / (N - k)); large F means group differences exceed what noise would produce. Running one ANOVA instead of many pairwise t-tests controls the family-wise error rate. A significant F does not tell you which groups differ, so post-hoc tests such as Tukey's HSD or Games-Howell (unequal variances) follow. Assumptions are independence, approximately normal residuals and equal variances (check with Levene's test); Welch's ANOVA relaxes equal variances and Kruskal-Wallis is the rank-based alternative. Two-way ANOVA examines two factors and their interaction. Effect size is eta squared, SSB / SST. ANOVA is a special case of linear regression with categorical predictors.",
        ["Comparing average delivery time across several warehouses.", "Evaluating multiple variants (A/B/C/D tests) on a continuous metric.", "Testing whether price tiers and regions interact on spend.", "Comparing model performance across several configurations."],
        [
            "F = MS_between / MS_within.",
            "df: between k - 1, within N - k.",
            "A significant F needs post-hoc tests to locate differences.",
            "Welch ANOVA for unequal variances; Kruskal-Wallis for ranks.",
            "Eta squared = SSB / SST measures effect size.",
        ],
        [
            ex("One-way ANOVA by hand with a permutation p-value", "advanced", "Compute SSB, SSW, F and eta squared, then a permutation p-value.", "python", """
                import random
                import statistics as st

                random.seed(4)
                groups = {
                    "north": [random.gauss(30, 4) for _ in range(12)],
                    "south": [random.gauss(32, 4) for _ in range(12)],
                    "east": [random.gauss(35, 4) for _ in range(12)],
                }

                def f_stat(gs):
                    allv = [v for g in gs for v in g]
                    grand = st.fmean(allv)
                    ssb = sum(len(g) * (st.fmean(g) - grand) ** 2 for g in gs)
                    ssw = sum((v - st.fmean(g)) ** 2 for g in gs for v in g)
                    k, n = len(gs), len(allv)
                    return (ssb / (k - 1)) / (ssw / (n - k)), ssb / (ssb + ssw)

                F, eta2 = f_stat(list(groups.values()))
                pooled = [v for g in groups.values() for v in g]
                count, R = 0, 2000
                for _ in range(R):
                    random.shuffle(pooled)
                    count += f_stat([pooled[0:12], pooled[12:24], pooled[24:36]])[0] >= F
                for name, g in groups.items():
                    print(f"{name:5} mean {st.fmean(g):.2f}")
                print(f"F = {F:.2f}, eta^2 = {eta2:.3f}, permutation p = {count / R:.4f}")
            """),
            ex("ANOVA and Tukey HSD with scipy/statsmodels", "intermediate", "Omnibus test then post-hoc comparisons.", "python", """
                from scipy import stats
                from statsmodels.stats.multicomp import pairwise_tukeyhsd

                print(stats.f_oneway(north, south, east))
                print(stats.levene(north, south, east))
                print(stats.kruskal(north, south, east))
                print(pairwise_tukeyhsd(df["minutes"], df["warehouse"]))
            """, False),
        ],
        ["SST = SSB + SSW", "F = (SSB/(k-1)) / (SSW/(N-k))", "stats.f_oneway(*groups)", "pairwise_tukeyhsd(y, group)", "smf.ols('y ~ C(group)', df).fit() + anova_lm"],
        ["Running all pairwise t-tests instead of ANOVA inflates false positives.", "Unequal variances with unequal group sizes distort the classic F test.", "A significant interaction in two-way ANOVA makes main effects hard to interpret alone."],
        [
            qa("basic", "Why use ANOVA instead of multiple t-tests?", "Comparing k groups pairwise needs k(k-1)/2 tests, inflating the chance of at least one false positive. ANOVA tests all means in a single omnibus test at the chosen alpha."),
            qa("intermediate", "What does the F statistic represent?", "The ratio of variance between group means to variance within groups, each divided by its degrees of freedom. Under H0 both estimate the same noise variance, so F is near 1; large values suggest real differences."),
            qa("intermediate", "ANOVA is significant. What next?", "Run post-hoc comparisons such as Tukey's HSD (equal variances) or Games-Howell (unequal) to find which pairs differ, report effect sizes like eta squared, and check residual assumptions."),
            qa("advanced", "How does ANOVA relate to linear regression?", "One-way ANOVA is a linear regression of the outcome on dummy-coded group indicators; the overall F test of the regression equals the ANOVA F. This view extends naturally to covariates (ANCOVA) and interactions."),
        ],
        ["t-tests", "multiple-comparisons", "nonparametric-tests"],
        chain(
            ("Groups", "k samples", "Data", "Collect a continuous outcome for k groups."),
            ("Between", "SSB", "Between-group", "Variability of group means around the grand mean.", "means"),
            ("Within", "SSW", "Within-group", "Variability of values around their own group mean.", "residuals"),
            ("F ratio", "MSB / MSW", "Test", "Large F indicates at least one mean differs.", "MS"),
            ("Post-hoc", "Tukey HSD", "Locate", "Find which pairs differ, controlling error rates.", "F, p"),
        ),
    ),
    topic(
        "nonparametric-tests", "Non-Parametric Tests", "experiments", "intermediate", "NP",
        "Rank-based and permutation tests that drop the normality assumption: Mann-Whitney, Wilcoxon, Kruskal-Wallis.",
        "Non-parametric tests are like judging a race by finishing positions instead of exact times. A single runner who stops for lunch cannot distort the result, because only the order matters.",
        "Non-parametric (distribution-free) tests make weaker assumptions about the shape of the data, typically working on ranks or on resampling. The Mann-Whitney U test (Wilcoxon rank-sum) compares two independent groups by ranking all observations together and asking whether one group's ranks are systematically higher; it tests whether P(X > Y) differs from 0.5, which equals a median shift only if the distributions have the same shape. The Wilcoxon signed-rank test is the paired analogue, ranking absolute within-pair differences. Kruskal-Wallis extends Mann-Whitney to three or more groups (a rank-based ANOVA), followed by Dunn's post-hoc test. The sign test is the simplest paired test, using only the direction of differences. Permutation tests compute exact or Monte Carlo p-values for any statistic by shuffling labels. These methods are robust to outliers and suitable for ordinal data, but can be less powerful than parametric tests when parametric assumptions hold, and they answer slightly different questions (stochastic dominance rather than means), which matters when the business cares about totals such as revenue.",
        ["Comparing skewed metrics like time-on-page with small samples.", "Analysing ordinal survey ratings between groups.", "Paired comparisons of model rankings across datasets.", "Robust checks alongside a t-test when outliers exist."],
        [
            "Mann-Whitney: two independent groups, rank-based.",
            "Wilcoxon signed-rank: paired data.",
            "Kruskal-Wallis: three or more groups.",
            "They test distribution shift or P(X > Y), not means.",
            "Robust to outliers; valid for ordinal data.",
        ],
        [
            ex("Mann-Whitney U with normal approximation", "intermediate", "Rank the pooled data and compare rank sums.", "python", """
                import math
                from statistics import NormalDist

                a = [3.1, 4.5, 2.8, 5.0, 3.9, 4.2, 2.5, 60.0]          # one extreme session
                b = [5.8, 6.1, 4.9, 7.2, 6.6, 5.5, 8.0, 6.9]
                pooled = sorted((v, g) for g, vals in (("a", a), ("b", b)) for v in vals)
                ranks = {}
                for r, (v, g) in enumerate(pooled, start=1):
                    ranks.setdefault(g, []).append(r)
                n1, n2 = len(a), len(b)
                u1 = sum(ranks["a"]) - n1 * (n1 + 1) / 2
                mu = n1 * n2 / 2
                sigma = math.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
                z = (u1 - mu) / sigma
                p = 2 * (1 - NormalDist().cdf(abs(z)))
                print(f"U = {u1}, z = {z:.2f}, p = {p:.4f}, P(a > b) estimate = {u1 / (n1 * n2):.2f}")
            """),
            ex("Sign test for paired data", "basic", "Exact binomial p-value from the direction of differences.", "python", """
                import math

                before = [72, 65, 80, 77, 69, 74, 71, 68, 79, 75, 70, 66]
                after = [70, 62, 78, 78, 64, 70, 69, 65, 74, 73, 71, 61]
                diffs = [y - x for x, y in zip(before, after) if y != x]
                k, n = sum(d < 0 for d in diffs), len(diffs)
                tail = sum(math.comb(n, i) for i in range(max(k, n - k), n + 1)) / 2 ** n
                print(f"{k} of {n} decreased, two-sided sign test p = {min(1, 2 * tail):.4f}")
            """),
            ex("scipy non-parametric tests", "basic", "Library calls.", "python", """
                from scipy import stats

                stats.mannwhitneyu(a, b, alternative="two-sided")
                stats.wilcoxon(before, after)
                stats.kruskal(g1, g2, g3)
            """, False),
        ],
        ["stats.mannwhitneyu(a, b)", "stats.wilcoxon(x, y)", "stats.kruskal(*groups)", "U = R1 - n1(n1+1)/2", "AUC = U / (n1 n2)"],
        ["Mann-Whitney is not a test of medians unless shapes are equal.", "Many ties require tie corrections.", "For revenue-type metrics, the business usually cares about the mean, which rank tests ignore."],
        [
            qa("basic", "When would you choose a non-parametric test?", "When data are ordinal, heavily skewed with small samples, or contain outliers that would dominate a mean-based test. They are also a robustness check alongside parametric tests."),
            qa("intermediate", "What does the Mann-Whitney U test actually test?", "Whether a randomly chosen value from one group tends to be larger than one from the other, i.e. P(X > Y) = 0.5 under H0. It is a test of medians only under the extra assumption that both distributions have the same shape."),
            qa("intermediate", "What is the relationship between Mann-Whitney U and ROC AUC?", "U divided by n1 * n2 equals the probability that a random positive scores higher than a random negative, which is exactly the AUC. So AUC is a rescaled Mann-Whitney statistic."),
            qa("advanced", "Are non-parametric tests always safer?", "No. They test a different hypothesis (stochastic dominance rather than means), can lose power when parametric assumptions hold, and still assume independent observations. With large samples, t-tests on means are often valid thanks to the CLT and answer the business question more directly."),
        ],
        ["t-tests", "anova", "bootstrapping"],
        chain(
            ("Pool", "all values", "Combine", "Pool observations from all groups."),
            ("Rank", "1..N", "Rank", "Replace values with ranks; ties get average ranks.", "pooled"),
            ("Rank sums", "per group", "Summarise", "Sum ranks per group.", "ranks"),
            ("Statistic", "U, H, W", "Compare", "Compare rank sums with their null expectation.", "sums"),
            ("p-value", "exact / approx", "Decide", "Exact tables for small n, normal approximation for large.", "stat"),
        ),
    ),
    topic(
        "multiple-comparisons", "Multiple Comparisons", "experiments", "advanced", "MC",
        "Test enough things and something will be significant by chance; control FWER or FDR.",
        "If you buy twenty lottery tickets, winning a small prize is not evidence that you are lucky. Testing twenty metrics is the same: one 'win' at 5% is expected.",
        "Each test at alpha = 0.05 has a 5% chance of a false positive when its null is true, so with m independent tests the chance of at least one false positive is 1 - 0.95^m: about 64% for m = 20. This arises with many metrics, segments, variants, time points or features. The family-wise error rate (FWER) is the probability of any false positive; Bonferroni controls it by testing each hypothesis at alpha / m, and Holm's step-down method controls it with more power. Tukey's HSD controls FWER for all pairwise mean comparisons. The false discovery rate (FDR) is the expected share of false positives among rejected hypotheses; the Benjamini-Hochberg procedure sorts p-values and rejects all up to the largest i with p(i) <= (i / m) * q, offering much more power when many hypotheses are tested, as in genomics or feature screening. Good practice also includes designating a single primary metric, treating secondary and segment analyses as exploratory, pre-registering analyses and replicating surprising findings. The 'garden of forking paths' warns that even unconscious analysis choices create hidden multiplicity.",
        ["Analysing an A/B test with many metrics and segments.", "Screening hundreds of features or genes.", "Running multi-variant (A/B/n) tests.", "Monitoring many dashboards for anomalies."],
        [
            "P(at least one false positive) = 1 - (1 - alpha)^m.",
            "Bonferroni: alpha / m; Holm: step-down, more powerful.",
            "Benjamini-Hochberg controls the false discovery rate.",
            "Pick one primary metric; treat the rest as exploratory.",
            "Replicate surprising subgroup findings.",
        ],
        [
            ex("False positives grow with the number of tests", "intermediate", "Simulate 20 A/A tests per experiment.", "python", """
                import math
                import random
                import statistics as st

                random.seed(0)
                m, sims, any_fp = 20, 300, 0
                for _ in range(sims):
                    hits = 0
                    for _ in range(m):
                        a = [random.gauss(0, 1) for _ in range(50)]
                        b = [random.gauss(0, 1) for _ in range(50)]
                        z = (st.fmean(b) - st.fmean(a)) / math.sqrt(2 / 50)
                        hits += abs(z) > 1.96
                    any_fp += hits > 0
                print(f"theory {1 - 0.95 ** m:.3f}, simulated {any_fp / sims:.3f}")
            """),
            ex("Bonferroni, Holm and Benjamini-Hochberg", "advanced", "Apply three corrections to the same p-values.", "python", """
                p = [0.001, 0.008, 0.012, 0.021, 0.035, 0.041, 0.09, 0.22, 0.48, 0.74]
                m, alpha = len(p), 0.05
                order = sorted(range(m), key=lambda i: p[i])

                bonf = [pv <= alpha / m for pv in p]

                holm = [False] * m
                for rank, i in enumerate(order):
                    if p[i] <= alpha / (m - rank):
                        holm[i] = True
                    else:
                        break

                bh = [False] * m
                cutoff = max((r + 1 for r, i in enumerate(order) if p[i] <= (r + 1) / m * alpha), default=0)
                for r in range(cutoff):
                    bh[order[r]] = True
                print("p          ", p)
                print("Bonferroni ", sum(bonf), "rejections")
                print("Holm       ", sum(holm), "rejections")
                print("BH (FDR 5%)", sum(bh), "rejections")
            """),
            ex("statsmodels multipletests", "basic", "One call for many methods.", "python", """
                from statsmodels.stats.multitest import multipletests

                reject, p_adj, _, _ = multipletests(pvals, alpha=0.05, method="fdr_bh")
                reject_holm = multipletests(pvals, alpha=0.05, method="holm")[0]
            """, False),
        ],
        ["FWER = 1 - (1 - alpha)^m", "Bonferroni: p <= alpha / m", "Holm: p(i) <= alpha / (m - i + 1)", "BH: p(i) <= (i / m) q", "multipletests(p, method='fdr_bh')"],
        ["Bonferroni is very conservative with many correlated tests.", "Slicing results by segment after the fact is multiple testing even if you report only one.", "FDR control allows some false positives by design; know which error matters."],
        [
            qa("basic", "What is the multiple comparisons problem?", "When many hypotheses are tested, the probability of at least one false positive grows quickly, e.g. 64% for 20 independent tests at alpha 0.05. Without correction, 'significant' findings are often noise."),
            qa("intermediate", "What is the difference between FWER and FDR?", "FWER is the probability of making any false discovery; FDR is the expected proportion of false discoveries among all rejections. FWER control (Bonferroni, Holm) is strict; FDR control (Benjamini-Hochberg) is more powerful when many tests are run."),
            qa("intermediate", "How does Benjamini-Hochberg work?", "Sort the m p-values ascending, find the largest rank i where p(i) <= (i / m) q, and reject the hypotheses with the i smallest p-values. This controls the FDR at q under independence or positive dependence."),
            qa("advanced", "An A/B test is flat overall but significant for iOS users in Germany. What do you do?", "Treat it as exploratory: count how many segments were examined, apply a correction, check plausibility and sample size, and then run a confirmatory test targeted at that segment before acting."),
        ],
        ["hypothesis-testing", "anova", "ab-testing"],
        chain(
            ("Many tests", "m hypotheses", "Family", "Metrics, segments or variants form a family of tests."),
            ("Raw p", "each at alpha", "Problem", "Unadjusted, false positives accumulate.", "m tests"),
            ("Choose", "FWER or FDR", "Error type", "Decide which error rate matters for the decision.", "p-values"),
            ("Adjust", "Holm / BH", "Correct", "Apply Holm for FWER or Benjamini-Hochberg for FDR.", "policy"),
            ("Confirm", "replicate", "Follow up", "Re-test surprising findings on fresh data.", "discoveries"),
        ),
    ),
    topic(
        "ab-testing", "A/B Testing: Design & Sample Size", "experiments", "advanced", "AB",
        "Randomise, size the test for a meaningful effect, run it to completion, and check it was not broken.",
        "An A/B test is a fair taste test: blindfold the tasters (randomise), decide in advance how many tasters you need, and do not stop the moment your favourite is ahead.",
        "An online controlled experiment randomly assigns units (usually users) to control and treatment, so differences in outcomes can be attributed to the change. Design starts with a hypothesis, a primary metric (often an overall evaluation criterion), guardrail metrics and the randomisation unit, which should match the analysis unit to avoid underestimating variance. Sample size comes from the baseline rate, the minimum detectable effect (MDE), alpha and power: for proportions, n per group is about (z_{1-alpha/2} + z_{1-beta})^2 * (p1(1-p1) + p2(1-p2)) / (p2 - p1)^2. Duration should cover full weekly cycles and account for novelty and primacy effects. Before reading results, check for sample ratio mismatch and run A/A tests to validate the pipeline. Repeatedly peeking at p-values and stopping early inflates false positives; use a fixed horizon or sequential methods (alpha spending, always-valid p-values). Variance reduction such as CUPED uses pre-experiment data to shrink noise. Interference between units (network effects, marketplaces) violates independence and needs cluster or switchback designs.",
        ["Testing a new checkout flow or recommendation algorithm.", "Pricing and promotion experiments with guardrails.", "Validating that a model improvement moves business metrics.", "Feature rollouts with staged exposure."],
        [
            "Randomise by user; analyse by the same unit.",
            "Size for the MDE that matters to the business.",
            "Run full weeks; do not stop on the first significant peek.",
            "Check SRM and guardrails before celebrating.",
            "CUPED and stratification cut variance and duration.",
        ],
        [
            ex("Sample size for a conversion test", "intermediate", "Users per arm for different minimum detectable effects.", "python", """
                import math
                from statistics import NormalDist

                def n_per_arm(p1, rel_mde, alpha=0.05, power=0.8):
                    p2 = p1 * (1 + rel_mde)
                    z = NormalDist().inv_cdf
                    num = (z(1 - alpha / 2) + z(power)) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2))
                    return math.ceil(num / (p2 - p1) ** 2)

                baseline, daily_users = 0.04, 20_000
                for mde in (0.02, 0.05, 0.10, 0.20):
                    n = n_per_arm(baseline, mde)
                    print(f"relative MDE {mde:4.0%}: {n:>9,} per arm, ~{math.ceil(2 * n / daily_users)} days")
            """),
            ex("Why peeking is dangerous", "advanced", "A/A tests checked daily and stopped at the first p < 0.05.", "python", """
                import math
                import random

                random.seed(1)
                sims, days, per_day, p = 300, 14, 300, 0.1
                fixed_fp = peek_fp = 0
                for _ in range(sims):
                    ca = cb = na = nb = 0
                    stopped = False
                    for _ in range(days):
                        ca += sum(random.random() < p for _ in range(per_day)); na += per_day
                        cb += sum(random.random() < p for _ in range(per_day)); nb += per_day
                        pool = (ca + cb) / (na + nb)
                        z = (cb / nb - ca / na) / math.sqrt(pool * (1 - pool) * (1 / na + 1 / nb))
                        if abs(z) > 1.96 and not stopped:
                            peek_fp += 1; stopped = True
                    fixed_fp += abs(z) > 1.96
                print(f"false positive rate, fixed horizon: {fixed_fp / sims:.3f}")
                print(f"false positive rate, daily peeking: {peek_fp / sims:.3f}")
            """),
            ex("CUPED variance reduction", "advanced", "Adjust the metric with pre-period data.", "python", """
                import random
                import statistics as st

                random.seed(3)
                pre = [random.gauss(50, 15) for _ in range(2000)]
                post = [0.8 * x + random.gauss(10, 6) for x in pre]
                theta = st.covariance(pre, post) / st.variance(pre)
                adjusted = [y - theta * (x - st.fmean(pre)) for x, y in zip(pre, post)]
                print(f"theta {theta:.3f}")
                print(f"variance raw {st.variance(post):.1f} -> CUPED {st.variance(adjusted):.1f}")
                print(f"variance reduction {1 - st.variance(adjusted) / st.variance(post):.1%}")
            """),
        ],
        ["n = (z_a/2 + z_b)^2 (p1q1 + p2q2) / (p2 - p1)^2", "MDE ~ 2.8 * sqrt(2 p(1-p) / n) (alpha .05, power .8)", "SRM: chisquare on arm counts", "CUPED: y - theta (x - mean(x)), theta = cov/var", "hash(user_id + salt) % 100 for assignment"],
        ["Randomising by session but analysing by user (or vice versa) breaks variance estimates.", "Novelty effects make the first days look better than the long run.", "Network effects let treatment leak into control.", "Changing allocation mid-test creates Simpson's-paradox artefacts."],
        [
            qa("basic", "What are the key steps in designing an A/B test?", "Define the hypothesis, primary and guardrail metrics, randomisation unit, MDE, alpha and power; compute the sample size and duration; then implement assignment, run an A/A or SRM check, and analyse only after the planned horizon."),
            qa("intermediate", "How do you compute the sample size for a conversion test?", "Use the baseline rate, the minimum detectable effect, alpha and power: n per arm is about (z_{1-alpha/2} + z_{power})^2 * (p1(1-p1) + p2(1-p2)) / (p2 - p1)^2. Halving the MDE roughly quadruples n."),
            qa("intermediate", "Why is peeking at results a problem?", "Each look is another chance to cross the threshold by luck, so stopping at the first significant look can push the false-positive rate from 5% to 20% or more. Use a fixed horizon or sequential testing designed for repeated looks."),
            qa("advanced", "What is CUPED?", "Controlled-experiment Using Pre-Experiment Data: subtract theta times the centred pre-period covariate from the outcome, where theta = Cov(X, Y) / Var(X). The estimate stays unbiased because the covariate is independent of assignment, while variance drops by about the squared correlation."),
            qa("advanced", "How do you run experiments in a two-sided marketplace?", "User-level randomisation causes interference because treated and control users compete for the same supply. Use cluster randomisation (by city or region), switchback designs (alternate treatment over time windows) or budget-split designs, and accept lower power."),
        ],
        ["type-errors-power", "metrics-design", "chi-square", "multiple-comparisons"],
        chain(
            ("Hypothesis", "metric + MDE", "Design", "State the change, primary metric, guardrails and MDE."),
            ("Size", "n, duration", "Power analysis", "Compute users per arm and full-week duration.", "design"),
            ("Randomise", "hash(user)", "Assign", "Deterministically hash users into arms.", "plan"),
            ("Validate", "SRM, A/A", "Health checks", "Check sample ratio and guardrails before reading lift.", "traffic"),
            ("Analyse", "lift + CI", "Decide", "Report lift, CI and guardrails at the planned horizon.", "clean data"),
        ),
    ),
    topic(
        "metrics-design", "Metrics Design: North Star, Drivers & Guardrails", "experiments", "intermediate", "MD",
        "Choose metrics that capture real customer value, move fast enough to steer by, and protect what you must not break.",
        "A North Star metric is the destination on a ship's compass, driver metrics are the sails you can adjust today, and guardrails are the depth gauge that stops you from running aground while chasing speed.",
        "Good metrics translate strategy into numbers teams can influence. A North Star metric captures the core value customers get (e.g., weekly active listeners, nights booked) and correlates with long-term revenue. Because it moves slowly, teams use input or driver metrics that are more sensitive and directly actionable, such as search success rate or day-7 activation. Guardrail metrics protect the business and users from harm while optimising: latency, crash rate, unsubscribe rate, support tickets, revenue, and experiment trust checks such as sample ratio mismatch. A good metric is clearly defined (numerator, denominator, unit, time window, filters), sensitive to real changes, robust to noise and gaming, and attributable. Ratio metrics need care: per-user means versus per-session ratios answer different questions and need delta-method or bootstrap variance. Goodhart's law warns that a measure that becomes a target stops being a good measure, so pair metrics that pull in opposite directions (speed with quality, volume with satisfaction). Frameworks like HEART (happiness, engagement, adoption, retention, task success) and AARRR (acquisition, activation, retention, referral, revenue) help structure the set.",
        ["Choosing the overall evaluation criterion for experiments.", "Designing a product team's KPI tree.", "Adding guardrails to an ML ranking launch.", "Diagnosing why a metric went up while customers complained."],
        [
            "North Star: long-term customer value, slow-moving.",
            "Drivers: sensitive, actionable inputs to the North Star.",
            "Guardrails: limits that must not regress (latency, errors, churn).",
            "Define numerator, denominator, unit, window and filters precisely.",
            "Goodhart's law: pair metrics to discourage gaming.",
        ],
        [
            ex("Launch decision with a primary metric and guardrails", "intermediate", "A variant wins on the primary metric but must pass every guardrail.", "python", """
                results = {
                    "orders_per_user":  {"control": 1.82, "treat": 1.90, "higher_is_better": True, "kind": "primary"},
                    "p95_latency_ms":   {"control": 420, "treat": 455, "higher_is_better": False, "kind": "guardrail", "max_regress": 0.05},
                    "refund_rate":      {"control": 0.031, "treat": 0.030, "higher_is_better": False, "kind": "guardrail", "max_regress": 0.03},
                    "unsubscribe_rate": {"control": 0.004, "treat": 0.0041, "higher_is_better": False, "kind": "guardrail", "max_regress": 0.05},
                }
                ok = True
                for name, r in results.items():
                    change = (r["treat"] - r["control"]) / r["control"]
                    worse = change < 0 if r["higher_is_better"] else change > 0
                    status = "primary"
                    if r["kind"] == "guardrail":
                        breach = worse and abs(change) > r["max_regress"]
                        ok &= not breach
                        status = "BREACH" if breach else "ok"
                    print(f"{name:17} {change:+.1%}  {status}")
                print("decision:", "ship" if ok else "do not ship; fix guardrail first")
            """),
            ex("Per-user mean vs global ratio", "advanced", "Two definitions of 'conversion per session' disagree when heavy users differ.", "python", """
                users = [  # (sessions, purchases), synthetic
                    (1, 1), (1, 0), (2, 1), (3, 0), (40, 4), (2, 0), (1, 1), (5, 1),
                ]
                global_ratio = sum(p for _, p in users) / sum(s for s, _ in users)
                per_user = sum(p / s for s, p in users) / len(users)
                print(f"global purchases/sessions: {global_ratio:.3f}  (dominated by the heavy user)")
                print(f"mean of per-user ratios:   {per_user:.3f}  (each user counts equally)")
            """),
        ],
        ["Metric spec: name, numerator, denominator, unit, window, filters", "North Star -> driver metrics -> guardrails", "HEART · AARRR frameworks", "Delta method for ratio metric variance", "COUNT(DISTINCT user_id) FILTER (WHERE ...)"],
        ["Vanity metrics (page views, registered users) can rise while value falls.", "Changing a metric definition silently breaks trend comparisons.", "Optimising a proxy (clicks) can hurt the real goal (satisfaction)."],
        [
            qa("basic", "What is a North Star metric?", "A single metric that best captures the core value customers receive and predicts long-term business success, such as nights booked for a travel marketplace. It aligns teams but usually moves too slowly to steer daily work alone."),
            qa("basic", "What are guardrail metrics?", "Metrics that must not degrade beyond a threshold when you optimise the primary metric, such as latency, error rate, unsubscribe rate or revenue. A launch that wins the primary metric but breaches a guardrail is blocked or reworked."),
            qa("intermediate", "What makes a good experiment metric?", "It is aligned with long-term value, sensitive enough to detect changes within a test's duration, has low variance, is hard to game, and is precisely defined with a unit of analysis that matches randomisation."),
            qa("advanced", "Explain Goodhart's law with an example and a mitigation.", "When a measure becomes a target it loses its value as a measure: optimising support tickets closed per hour leads agents to close tickets without solving them. Mitigate by pairing metrics (closure rate with reopen rate and CSAT) and reviewing qualitative signals."),
        ],
        ["ab-testing", "dashboards-storytelling", "ds-workflow"],
        chain(
            ("Strategy", "customer value", "Why", "Start from the value the product delivers."),
            ("North Star", "1 core metric", "Align", "Pick the metric that best captures that value.", "goal"),
            ("Drivers", "actionable inputs", "Steer", "Decompose into sensitive metrics teams can move.", "NSM"),
            ("Guardrails", "do no harm", "Protect", "Add limits for latency, quality, trust and revenue.", "drivers"),
            ("Spec", "exact definition", "Define", "Document numerator, denominator, window and filters.", "metric set"),
        ),
    ),
]

TOPICS += [
    topic(
        "simple-linear-regression", "Simple Linear Regression", "statistics", "intermediate", "LR",
        "Fit the best straight line y = a + b x by least squares, and know what the slope, R squared and residuals tell you.",
        "Regression is drawing the line a stretched rubber band would settle on if every data point pulled on it with a spring. Points far from the line pull hardest, which is why outliers matter so much.",
        "Simple linear regression models a response y as a linear function of one predictor x plus noise: y = b0 + b1 x + e. Ordinary least squares (OLS) chooses b0 and b1 to minimise the sum of squared residuals, giving b1 = Cov(x, y) / Var(x) = r * (s_y / s_x) and b0 = y_bar - b1 x_bar, so the line always passes through the means. The slope is the expected change in y for a one-unit increase in x; the intercept is the predicted y at x = 0, which may be meaningless if x = 0 is outside the data. R squared, the share of variance in y explained by the line, equals r^2 in the one-predictor case. Inference on the slope uses its standard error and a t-test with n - 2 degrees of freedom. The classical assumptions are linearity, independent errors, constant variance (homoscedasticity) and, for small-sample inference, normally distributed errors; residual plots reveal violations such as curvature or funnel shapes. Extrapolating beyond the observed x range is risky, influential points (high leverage plus large residual) can swing the fit, and regression to the mean is a natural consequence of imperfect correlation.",
        ["Estimating how price affects demand in a simple setting.", "Quantifying the relationship between ad spend and sign-ups.", "Building a baseline predictive model.", "Detrending a metric over time."],
        [
            "b1 = Cov(x, y) / Var(x); b0 = y_bar - b1 x_bar.",
            "R^2 = r^2 for one predictor; share of variance explained.",
            "Check residual plots for curvature and changing spread.",
            "Do not extrapolate far outside the data range.",
            "Slope t-test has n - 2 degrees of freedom.",
        ],
        [
            ex("Fit, interpret and check residuals", "intermediate", "statistics.linear_regression plus R squared and the slope's standard error.", "python", """
                import math
                import random
                import statistics as st

                random.seed(4)
                spend = [random.uniform(1, 20) for _ in range(40)]                # ad spend, thousands
                signups = [50 + 12 * s + random.gauss(0, 15) for s in spend]
                fit = st.linear_regression(spend, signups)
                pred = [fit.intercept + fit.slope * s for s in spend]
                resid = [y - p for y, p in zip(signups, pred)]
                ss_res = sum(r * r for r in resid)
                ss_tot = sum((y - st.fmean(signups)) ** 2 for y in signups)
                se_slope = math.sqrt(ss_res / (len(spend) - 2)) / math.sqrt(sum((s - st.fmean(spend)) ** 2 for s in spend))
                print(f"signups = {fit.intercept:.1f} + {fit.slope:.2f} * spend")
                print(f"R^2 = {1 - ss_res / ss_tot:.3f}  (r^2 = {st.correlation(spend, signups) ** 2:.3f})")
                print(f"slope SE = {se_slope:.3f}, t = {fit.slope / se_slope:.1f}")
                print(f"mean residual {st.fmean(resid):.2e}")
            """),
            ex("Regression to the mean", "advanced", "Top performers in period 1 look worse in period 2 without any intervention.", "python", """
                import random
                import statistics as st

                random.seed(10)
                skill = [random.gauss(0, 1) for _ in range(2000)]
                p1 = [s + random.gauss(0, 1) for s in skill]
                p2 = [s + random.gauss(0, 1) for s in skill]
                top = sorted(range(2000), key=lambda i: p1[i])[-100:]
                print(f"top 100 in period 1: mean {st.fmean(p1[i] for i in top):.2f}")
                print(f"same people period 2: mean {st.fmean(p2[i] for i in top):.2f}")
                print(f"slope of p2 on p1: {st.linear_regression(p1, p2).slope:.2f}")
            """),
            ex("statsmodels OLS summary", "basic", "Coefficients, standard errors, CIs and diagnostics in one table.", "python", """
                import statsmodels.formula.api as smf

                model = smf.ols("signups ~ spend", data=df).fit()
                print(model.summary())
                print(model.conf_int())
            """, False),
        ],
        ["statistics.linear_regression(x, y)", "b1 = cov(x, y) / var(x)", "R^2 = 1 - SS_res / SS_tot", "smf.ols('y ~ x', df).fit().summary()", "np.polyfit(x, y, 1)"],
        ["A high R^2 does not mean the model is causal or correct.", "Heteroscedastic residuals make standard errors wrong; use robust (HC) errors.", "One influential point can flip the slope; check leverage and Cook's distance."],
        [
            qa("basic", "How do you interpret the slope in simple linear regression?", "It is the expected change in y for a one-unit increase in x, holding the model's assumptions. For example a slope of 12 means each extra thousand in ad spend is associated with 12 more sign-ups on average."),
            qa("intermediate", "What is R squared and what are its limitations?", "The proportion of variance in y explained by the model. It always increases with more predictors, says nothing about causality or bias, and can be high for a misspecified model or low for a useful one in noisy domains."),
            qa("intermediate", "What assumptions does OLS make?", "A linear relationship, independent errors, constant error variance and (for exact small-sample inference) normally distributed errors. The predictor should be measured without much error; violations are diagnosed with residual plots."),
            qa("advanced", "What is regression to the mean?", "When two measurements are imperfectly correlated, extreme values on the first tend to be closer to the average on the second. It explains why top performers 'decline' and why interventions on extreme groups look effective without a control group."),
        ],
        ["multiple-regression", "pearson-spearman", "logistic-regression"],
        chain(
            ("Scatter", "x vs y", "Look", "Plot y against x to confirm a roughly linear pattern."),
            ("Fit", "least squares", "Estimate", "Choose the line minimising squared residuals.", "points"),
            ("Interpret", "slope, R^2", "Meaning", "Slope is change in y per unit x; R^2 is variance explained.", "b0, b1"),
            ("Diagnose", "residual plots", "Check", "Look for curvature, funnels and influential points.", "residuals"),
        ),
    ),
    topic(
        "multiple-regression", "Multiple Linear Regression", "statistics", "advanced", "MR",
        "Several predictors at once: each coefficient is an effect holding the others fixed, with multicollinearity and confounding to manage.",
        "Multiple regression is like a recipe tasting panel that changes one ingredient while keeping all the others the same, so it can say how much sweetness the sugar alone adds.",
        "Multiple linear regression models y = b0 + b1 x1 + ... + bp xp + e, estimated by OLS via the normal equations b = (X'X)^-1 X'y. Each coefficient is the expected change in y for a one-unit change in that predictor holding the other predictors constant, which is how regression adjusts for measured confounders. Categorical predictors enter as dummy variables relative to a reference level, and interaction terms (x1 * x2) let the effect of one variable depend on another; polynomial terms capture curvature while keeping the model linear in parameters. Adjusted R squared penalises extra predictors, and AIC/BIC or cross-validation guide model selection. Multicollinearity (highly correlated predictors) inflates coefficient standard errors and makes individual coefficients unstable, even though predictions may be fine; the variance inflation factor (VIF) diagnoses it, with values above 5-10 a common warning. Omitted variable bias occurs when a confounder correlated with both a predictor and y is left out. Regularised versions (ridge, lasso) shrink coefficients to handle many or correlated predictors.",
        ["Estimating price elasticity while controlling for seasonality and promotion.", "Explaining salary differences while adjusting for role and tenure.", "Building interpretable forecasting baselines.", "Covariate adjustment in experiments for variance reduction."],
        [
            "Each coefficient is a partial effect holding others fixed.",
            "Dummies encode categories against a reference level.",
            "Interactions model effects that depend on another variable.",
            "VIF > 5-10 signals problematic multicollinearity.",
            "Omitting a confounder biases the remaining coefficients.",
        ],
        [
            ex("OLS via normal equations in pure Python", "advanced", "Two predictors, solved with Gaussian elimination.", "python", """
                import random

                random.seed(6)
                rows = []
                for _ in range(200):
                    price = random.uniform(5, 15)
                    promo = 1 if random.random() < 0.3 else 0
                    demand = 300 - 12 * price + 40 * promo + random.gauss(0, 10)
                    rows.append((1.0, price, promo, demand))

                X = [r[:3] for r in rows]; y = [r[3] for r in rows]
                p = len(X[0])
                XtX = [[sum(x[i] * x[j] for x in X) for j in range(p)] for i in range(p)]
                Xty = [sum(x[i] * yi for x, yi in zip(X, y)) for i in range(p)]
                A = [row[:] + [b] for row, b in zip(XtX, Xty)]
                for c in range(p):
                    piv = max(range(c, p), key=lambda r: abs(A[r][c])); A[c], A[piv] = A[piv], A[c]
                    for r in range(p):
                        if r != c:
                            f = A[r][c] / A[c][c]
                            A[r] = [a - f * b for a, b in zip(A[r], A[c])]
                beta = [A[i][p] / A[i][i] for i in range(p)]
                print("intercept %.2f, price %.2f, promo %.2f" % tuple(beta))
            """),
            ex("Omitted variable bias and multicollinearity", "advanced", "Dropping a correlated confounder biases the slope; VIF measures overlap.", "python", """
                import random
                import statistics as st

                random.seed(2)
                exp_years = [random.uniform(0, 20) for _ in range(500)]
                training = [0.5 * e + random.gauss(0, 2) for e in exp_years]          # correlated with experience
                salary = [30 + 2.0 * e + 1.0 * t + random.gauss(0, 5) for e, t in zip(exp_years, training)]

                naive = st.linear_regression(training, salary).slope
                print(f"salary ~ training only: slope {naive:.2f} (true partial effect 1.0)")
                r2 = st.correlation(training, exp_years) ** 2
                print(f"corr(training, experience)^2 = {r2:.2f}, VIF = {1 / (1 - r2):.2f}")
            """),
            ex("Formulas with dummies and interactions", "intermediate", "statsmodels handles encoding and VIF.", "python", """
                import statsmodels.formula.api as smf
                from statsmodels.stats.outliers_influence import variance_inflation_factor

                m = smf.ols("demand ~ price * promo + C(region) + C(month)", data=df).fit(cov_type="HC3")
                print(m.summary())
                vif = [variance_inflation_factor(m.model.exog, i) for i in range(m.model.exog.shape[1])]
            """, False),
        ],
        ["b = (X'X)^-1 X'y", "smf.ols('y ~ x1 + x2 + C(cat) + x1:x2', df)", "adj R^2 = 1 - (1 - R^2)(n - 1)/(n - p - 1)", "VIF_j = 1 / (1 - R_j^2)", ".fit(cov_type='HC3') for robust SEs"],
        ["Including all dummies plus an intercept causes perfect collinearity (dummy trap).", "Controlling for a mediator or collider biases the effect of interest.", "Coefficients of correlated predictors can flip sign between similar models."],
        [
            qa("basic", "How do you interpret a coefficient in multiple regression?", "As the expected change in y for a one-unit increase in that predictor while all other predictors in the model are held constant. Its meaning therefore depends on which other variables are included."),
            qa("intermediate", "What is multicollinearity and why is it a problem?", "High correlation among predictors. It does not bias predictions much, but it inflates coefficient standard errors and makes individual coefficients unstable and hard to interpret. Detect it with VIF; remedies include dropping or combining variables or using ridge regression."),
            qa("intermediate", "What is omitted variable bias?", "When a variable that affects y and is correlated with an included predictor is left out, the included coefficient absorbs part of its effect. The bias equals the omitted effect times the regression of the omitted variable on the included one."),
            qa("advanced", "Why use adjusted R squared or cross-validation instead of R squared for model selection?", "R squared never decreases when predictors are added, even useless ones. Adjusted R squared penalises extra parameters, and cross-validated error measures out-of-sample performance directly, guarding against overfitting."),
        ],
        ["simple-linear-regression", "logistic-regression", "correlation-causation"],
        chain(
            ("Predictors", "x1..xp", "Choose", "Select predictors using domain knowledge and causal reasoning."),
            ("Encode", "dummies, terms", "Design matrix", "Add dummies, interactions and transformations.", "features"),
            ("Fit", "OLS", "Estimate", "Solve the normal equations for coefficients.", "X"),
            ("Diagnose", "VIF, residuals", "Check", "Check multicollinearity, residuals and influence.", "b"),
            ("Validate", "CV, adj R^2", "Generalise", "Compare models out of sample.", "model"),
        ),
    ),
    topic(
        "logistic-regression", "Logistic Regression Intuition", "statistics", "intermediate", "LG",
        "Model the probability of a yes/no outcome with a linear score squashed through a sigmoid; coefficients are log-odds.",
        "Logistic regression is a dimmer switch rather than an on/off switch. A linear score turns the knob, and the sigmoid makes sure the light level (probability) always stays between fully off and fully on.",
        "Logistic regression models a binary outcome by passing a linear combination z = b0 + b1 x1 + ... through the sigmoid function p = 1 / (1 + e^-z), which maps any real number into (0, 1). Equivalently, the log-odds log(p / (1 - p)) is linear in the predictors, so a coefficient b means a one-unit increase in x multiplies the odds by e^b (the odds ratio). Parameters are estimated by maximum likelihood, minimising log loss (binary cross-entropy), typically with iterative methods such as gradient descent or Newton-Raphson; there is no closed form like OLS. Predictions are probabilities; turning them into decisions requires a threshold chosen from the costs of false positives and negatives, not automatically 0.5. Evaluation uses log loss, ROC AUC, precision/recall and calibration plots. Perfect separation makes coefficients diverge, which regularisation (L2/L1) fixes, and regularisation also handles many predictors. Despite its name it is a classification model, and it remains a strong, interpretable baseline for churn, credit risk and conversion propensity.",
        ["Churn or conversion propensity scoring.", "Credit default risk with interpretable odds ratios.", "Baseline classifier before tree ensembles.", "Estimating adjusted effects on a binary outcome."],
        [
            "p = sigmoid(b0 + b1 x); log-odds are linear in x.",
            "e^b is the odds ratio per unit increase in x.",
            "Fitted by maximum likelihood (log loss), not least squares.",
            "Choose the decision threshold from business costs.",
            "Regularise to handle separation and many features.",
        ],
        [
            ex("Logistic regression by gradient descent", "intermediate", "Fit one feature, read the odds ratio, and score probabilities.", "python", """
                import math
                import random

                random.seed(0)
                data = []
                for _ in range(400):
                    tickets = random.randint(0, 8)
                    p = 1 / (1 + math.exp(-(-3 + 0.6 * tickets)))
                    data.append((tickets, 1 if random.random() < p else 0))

                b0 = b1 = 0.0
                lr = 0.05
                for _ in range(3000):
                    g0 = g1 = 0.0
                    for x, y in data:
                        p = 1 / (1 + math.exp(-(b0 + b1 * x)))
                        g0 += p - y; g1 += (p - y) * x
                    b0 -= lr * g0 / len(data); b1 -= lr * g1 / len(data)
                loss = -sum(y * math.log(1 / (1 + math.exp(-(b0 + b1 * x)))) + (1 - y) * math.log(1 - 1 / (1 + math.exp(-(b0 + b1 * x)))) for x, y in data) / len(data)
                print(f"b0 = {b0:.2f}, b1 = {b1:.2f}, odds ratio per ticket = {math.exp(b1):.2f}, log loss = {loss:.3f}")
                for t in (0, 4, 8):
                    print(f"P(churn | {t} tickets) = {1 / (1 + math.exp(-(b0 + b1 * t))):.3f}")
            """),
            ex("Sigmoid, odds and log-odds", "basic", "How probabilities, odds and logits relate.", "python", """
                import math

                for p in (0.1, 0.25, 0.5, 0.75, 0.9):
                    odds = p / (1 - p)
                    print(f"p={p:.2f}  odds={odds:5.2f}  log-odds={math.log(odds):+.2f}")
                z = 1.2
                print("sigmoid(1.2) =", round(1 / (1 + math.exp(-z)), 4))
            """),
            ex("scikit-learn LogisticRegression", "intermediate", "Regularised fit with scaled features and calibrated evaluation.", "python", """
                from sklearn.pipeline import make_pipeline
                from sklearn.preprocessing import StandardScaler
                from sklearn.linear_model import LogisticRegression
                from sklearn.metrics import roc_auc_score, log_loss

                clf = make_pipeline(StandardScaler(), LogisticRegression(C=1.0, max_iter=1000))
                clf.fit(X_train, y_train)
                proba = clf.predict_proba(X_test)[:, 1]
                print(roc_auc_score(y_test, proba), log_loss(y_test, proba))
            """, False),
        ],
        ["p = 1 / (1 + e^-(b0 + b1 x))", "logit(p) = log(p / (1 - p))", "odds ratio = e^b", "log loss = -mean(y log p + (1-y) log(1-p))", "LogisticRegression(C=1.0, class_weight='balanced')"],
        ["Coefficients are on the log-odds scale; do not read them as probability changes.", "Using 0.5 as the threshold by default ignores costs and class imbalance.", "Unscaled features make regularisation penalise variables unevenly."],
        [
            qa("basic", "Why not use linear regression for a binary outcome?", "A linear model can predict values below 0 or above 1 and assumes constant variance, which does not hold for binary data. Logistic regression keeps predictions in (0, 1) and models the log-odds linearly."),
            qa("intermediate", "How do you interpret a logistic regression coefficient of 0.7?", "A one-unit increase in that predictor multiplies the odds of the outcome by e^0.7, about 2.0, holding other predictors constant. The change in probability depends on the starting probability."),
            qa("intermediate", "How is logistic regression trained?", "By maximum likelihood: choose coefficients that maximise the probability of the observed labels, equivalent to minimising log loss. It has no closed-form solution, so iterative optimisers such as Newton-Raphson, L-BFGS or gradient descent are used."),
            qa("advanced", "What is perfect separation and how do you handle it?", "When a predictor or combination of predictors perfectly separates the classes, the likelihood keeps increasing as coefficients grow, so estimates diverge. Regularisation (L2/L1) or Firth's penalised likelihood gives finite, stable estimates."),
        ],
        ["simple-linear-regression", "multiple-regression", "expectation"],
        chain(
            ("Features", "x1..xp", "Inputs", "Collect predictors for each example."),
            ("Score", "z = b0 + b x", "Linear score", "Combine features linearly into a log-odds score.", "x"),
            ("Sigmoid", "p in (0, 1)", "Squash", "The sigmoid turns the score into a probability.", "z"),
            ("Loss", "log loss", "Fit", "Maximum likelihood adjusts b to reduce log loss.", "p"),
            ("Threshold", "cost-based", "Decide", "Pick a threshold that balances FP and FN costs.", "probs"),
        ),
    ),
    topic(
        "data-cleaning", "Data Cleaning", "data-wrangling", "basic", "DC",
        "Fix types, formats, units and invalid values with reproducible, logged rules before analysis.",
        "Data cleaning is washing vegetables before cooking. It is unglamorous, it takes longer than the cooking, and skipping it ruins the meal however fancy the recipe.",
        "Data cleaning turns raw extracts into a consistent, trustworthy table. Typical steps are parsing types correctly (numbers stored as text, dates in mixed formats, booleans as 'Y'/'yes'/1), standardising strings (trimming whitespace, case, Unicode normalisation, consistent category labels), converting units and currencies, validating ranges and business rules (no negative ages, end date after start date), handling missing values, removing exact and fuzzy duplicates, and fixing structural issues such as merged header rows or wide versus long layout. Cleaning must be scripted and idempotent, not done by hand in a spreadsheet, so it can be rerun when new data arrive and reviewed by others. Keep the raw data immutable and log what each rule changed (rows dropped, values coerced). Validation libraries or schema checks (pandera, Great Expectations, dbt tests) catch regressions automatically. Always fix problems as close to the source as possible and tell upstream owners, otherwise the same bugs return every load.",
        ["Preparing CRM exports or survey data for analysis.", "Building a reliable ETL step before a dashboard.", "Harmonising data from several regional systems.", "Making a modelling dataset reproducible."],
        [
            "Keep raw data immutable; clean in code.",
            "Parse types explicitly; never trust inferred types blindly.",
            "Standardise categories, whitespace, case and units.",
            "Validate business rules and log every change.",
            "Push fixes upstream when possible.",
        ],
        [
            ex("A logged cleaning pipeline with csv and stdlib", "basic", "Parse, normalise, validate and count what changed.", "python", """
                import csv
                import io
                from collections import Counter
                from datetime import datetime

                raw = '''id,signup,country,age,plan
                1,2026-01-05, india ,34,Pro
                2,05/01/2026,INDIA,29,pro
                3,2026-02-11,U.S.,-4,basic
                4,2026-13-01,usa,41,BASIC
                5,2026-03-02,Germany,,Pro'''
                COUNTRY = {"india": "IN", "u.s.": "US", "usa": "US", "germany": "DE"}
                log = Counter()

                def parse_date(s):
                    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            return datetime.strptime(s.strip(), fmt).date()
                        except ValueError:
                            continue
                    log["bad_date"] += 1
                    return None

                clean = []
                for r in csv.DictReader(io.StringIO(raw)):
                    age = int(r["age"]) if r["age"].strip() else None
                    if age is not None and not 0 < age < 120:
                        log["invalid_age"] += 1; age = None
                    clean.append({"id": int(r["id"]), "signup": parse_date(r["signup"]),
                                  "country": COUNTRY.get(r["country"].strip().lower(), "UNKNOWN"),
                                  "age": age, "plan": r["plan"].strip().lower()})
                for row in clean:
                    print(row)
                print("log:", dict(log))
            """),
            ex("pandas cleaning idioms", "intermediate", "Common one-liners for types, strings and validation.", "python", """
                import pandas as pd

                df["signup"] = pd.to_datetime(df["signup"], errors="coerce", dayfirst=True)
                df["amount"] = pd.to_numeric(df["amount"].str.replace(",", ""), errors="coerce")
                df["country"] = df["country"].str.strip().str.upper().replace({"U.S.": "US", "USA": "US"})
                df = df[df["age"].between(0, 120) | df["age"].isna()]
                assert df["order_id"].is_unique
            """, False),
        ],
        ["pd.to_datetime(s, errors='coerce')", "pd.to_numeric(s, errors='coerce')", "s.str.strip().str.lower()", "df['x'].between(lo, hi)", "pandera / Great Expectations / dbt tests"],
        ["Ambiguous dates (05/01) differ between day-first and month-first locales.", "errors='coerce' silently creates NaN; count them after coercion.", "Manual spreadsheet fixes cannot be reproduced or audited."],
        [
            qa("basic", "What are common data cleaning tasks?", "Fixing data types, standardising text and category labels, converting units, validating ranges and business rules, handling missing values and removing duplicates. Each should be scripted and logged."),
            qa("intermediate", "Why should cleaning be scripted rather than done manually?", "Scripts are reproducible, reviewable and rerunnable when new data arrive, and they document every decision. Manual edits are error-prone, invisible to others and lost on the next refresh."),
            qa("intermediate", "How do you handle inconsistent category labels like 'USA', 'U.S.' and 'united states'?", "Normalise case and whitespace, map variants to a canonical code with an explicit dictionary, and route unmapped values to an 'UNKNOWN' bucket that is monitored. For large vocabularies, use fuzzy matching with manual review."),
            qa("advanced", "How would you prevent dirty data from reaching production dashboards?", "Add automated data tests at ingestion and transformation layers (schema, uniqueness, not-null, accepted values, freshness, volume anomalies), fail or quarantine bad loads, alert owners, and track data quality metrics over time."),
        ],
        ["missing-data", "duplicates-quality", "eda"],
        chain(
            ("Raw", "immutable copy", "Land", "Store the raw extract untouched."),
            ("Parse", "types, dates", "Types", "Parse numbers, dates and booleans explicitly.", "raw"),
            ("Standardise", "labels, units", "Normalise", "Trim, case-fold, map categories and convert units.", "typed"),
            ("Validate", "rules, ranges", "Check", "Apply business rules and log violations.", "normalised"),
            ("Publish", "tested table", "Release", "Publish the clean table with data tests.", "validated"),
        ),
    ),
    topic(
        "missing-data", "Missing Data & Imputation", "data-wrangling", "intermediate", "MI",
        "Why values are missing (MCAR, MAR, MNAR) decides whether dropping or imputing is safe.",
        "Missing data is like blank answers on a questionnaire. If a page simply fell off, the blanks are harmless; if people skipped the income question because they earn a lot, ignoring blanks lies to you.",
        "Rubin's framework classifies missingness. Missing completely at random (MCAR) means missingness is unrelated to any data, so dropping rows only loses power. Missing at random (MAR) means missingness depends on observed variables (older users skip a question more often), so methods that condition on those variables can correct bias. Missing not at random (MNAR) means missingness depends on the unobserved value itself (high earners hide income), which no standard method fully fixes without assumptions or extra data. Listwise deletion is simple but biased unless MCAR and wasteful when many columns have gaps. Simple imputation (mean, median, mode, constant) keeps rows but shrinks variance and distorts correlations; adding a missing-indicator column lets models learn from the fact of missingness. Model-based methods include KNN imputation, regression imputation, iterative imputation (MICE), and for time series forward fill or interpolation. Multiple imputation creates several plausible datasets and pools results to reflect imputation uncertainty. Imputers must be fit on training data only to avoid leakage, and the share and pattern of missingness should always be reported.",
        ["Preparing survey or medical data with skipped questions.", "Feature pipelines for ML models that cannot accept NaN.", "Filling gaps in sensor or time series data.", "Assessing whether missingness biases a KPI."],
        [
            "MCAR: unrelated to data. MAR: depends on observed. MNAR: depends on the missing value.",
            "Deletion is unbiased only under MCAR.",
            "Mean imputation shrinks variance and weakens correlations.",
            "Add missing indicators; missingness is often informative.",
            "Fit imputers on training data inside the pipeline.",
        ],
        [
            ex("Deletion and mean imputation under MNAR", "intermediate", "High incomes are hidden more often; both naive methods underestimate.", "python", """
                import random
                import statistics as st

                random.seed(14)
                income = [random.lognormvariate(10.5, 0.5) for _ in range(5000)]
                observed = [x if random.random() > (0.6 if x > 60000 else 0.1) else None for x in income]
                present = [x for x in observed if x is not None]
                print(f"missing share {1 - len(present) / len(observed):.1%}")
                print(f"true mean     {st.fmean(income):,.0f}")
                print(f"complete-case {st.fmean(present):,.0f}")
                imputed = [x if x is not None else st.fmean(present) for x in observed]
                print(f"mean-imputed  {st.fmean(imputed):,.0f}  sd {st.stdev(imputed):,.0f} vs true sd {st.stdev(income):,.0f}")
            """),
            ex("Group-wise imputation plus indicator", "basic", "Impute by segment median under MAR and keep a flag.", "python", """
                import statistics as st
                from collections import defaultdict

                rows = [("mobile", 3.2), ("mobile", None), ("desktop", 8.1), ("desktop", 7.4),
                        ("mobile", 2.9), ("desktop", None), ("mobile", 3.5), ("desktop", 9.0)]
                by_group = defaultdict(list)
                for g, v in rows:
                    if v is not None:
                        by_group[g].append(v)
                medians = {g: st.median(v) for g, v in by_group.items()}
                filled = [(g, v if v is not None else medians[g], v is None) for g, v in rows]
                for row in filled:
                    print(row)
            """),
            ex("scikit-learn imputers", "intermediate", "Simple, KNN and iterative (MICE-like) imputation.", "python", """
                from sklearn.experimental import enable_iterative_imputer  # noqa: F401
                from sklearn.impute import SimpleImputer, KNNImputer, IterativeImputer

                SimpleImputer(strategy="median", add_indicator=True).fit(X_train)
                KNNImputer(n_neighbors=5).fit(X_train)
                IterativeImputer(max_iter=10, random_state=0).fit(X_train)
                df["temp"] = df["temp"].interpolate(method="time")
            """, False),
        ],
        ["df.isna().mean()", "df.dropna(subset=['col'])", "SimpleImputer(strategy='median', add_indicator=True)", "df.groupby('g')['v'].transform(lambda s: s.fillna(s.median()))", "s.ffill() · s.interpolate()"],
        ["Imputing before the train/test split leaks test information.", "Sentinel values like -999 or 0 can masquerade as real data.", "Forward fill across long gaps invents stale values."],
        [
            qa("basic", "What are MCAR, MAR and MNAR?", "MCAR: missingness is unrelated to any variable. MAR: missingness depends only on observed variables. MNAR: missingness depends on the unobserved value itself, such as people with high incomes declining to report income."),
            qa("intermediate", "What is wrong with mean imputation?", "It keeps the mean unchanged but artificially reduces variance, weakens correlations with other variables and ignores uncertainty. It can be acceptable for a few MCAR values in a predictive model, especially with a missing indicator."),
            qa("intermediate", "When is dropping rows with missing values acceptable?", "When data are MCAR and the loss of rows does not hurt power much, or when the missing share is tiny. Under MAR or MNAR, listwise deletion biases estimates."),
            qa("advanced", "What is multiple imputation and why use it?", "It generates several completed datasets by drawing imputations from a predictive distribution, analyses each, and pools the estimates using Rubin's rules. This propagates imputation uncertainty into standard errors, unlike single imputation."),
        ],
        ["data-cleaning", "data-leakage", "feature-engineering"],
        chain(
            ("Measure", "% missing", "Profile", "Quantify missingness per column and per row."),
            ("Mechanism", "MCAR/MAR/MNAR", "Diagnose", "Compare rows with and without values on observed fields.", "pattern"),
            ("Strategy", "drop / impute", "Choose", "Pick deletion, simple, model-based or multiple imputation.", "mechanism"),
            ("Fit", "on train only", "Apply", "Fit imputers in the pipeline on training folds.", "plan"),
            ("Report", "flags + caveats", "Document", "Keep indicators and state assumptions.", "imputed"),
        ),
    ),
    topic(
        "duplicates-quality", "Duplicates & Data Quality", "data-wrangling", "intermediate", "DQ",
        "Measure quality along accuracy, completeness, consistency, timeliness, validity and uniqueness, and hunt duplicates exact and fuzzy.",
        "Duplicate records are like the same guest RSVPing twice under 'Priya S.' and 'priya s'. Count both and you order too much food; merge carelessly and you might combine two different Priyas.",
        "Data quality is fitness for use, commonly assessed on dimensions such as completeness (required values present), validity (values follow formats and rules), accuracy (values reflect reality), consistency (the same fact agrees across systems), timeliness (fresh enough for the decision) and uniqueness (each entity appears once). Duplicates arise from repeated ingestion, retries without idempotency keys, joins on non-unique keys (fan-out), and the same entity entered with variations. Exact duplicates are found by hashing or grouping on all columns; key duplicates by grouping on the business key. Fuzzy duplicates need normalisation (case, whitespace, punctuation, phone and email formats) and similarity measures such as edit distance or token similarity, often with blocking to avoid comparing every pair. Entity resolution then decides which record survives or how fields merge. A classic silent failure is a many-to-many join that multiplies rows and inflates revenue. Quality should be monitored continuously with automated checks on row counts, null rates, uniqueness, referential integrity and freshness, with owners and SLAs.",
        ["De-duplicating customer records from multiple sign-up channels.", "Detecting join fan-out that inflates metrics.", "Building data quality scorecards for critical tables.", "Investigating a sudden jump in a dashboard metric."],
        [
            "Quality dimensions: completeness, validity, accuracy, consistency, timeliness, uniqueness.",
            "Check key uniqueness before and after every join.",
            "Normalise before matching fuzzy duplicates.",
            "Use idempotency keys to prevent duplicate ingestion.",
            "Automate checks and assign owners.",
        ],
        [
            ex("Exact, key and fuzzy duplicates", "intermediate", "Normalise emails and names, then compare with difflib.", "python", """
                import difflib
                from collections import Counter

                rows = [
                    (1, "Priya Sharma", "Priya.S@example.com"), (2, "priya sharma ", "priya.s@example.com"),
                    (3, "Arjun Rao", "arjun@example.com"), (3, "Arjun Rao", "arjun@example.com"),
                    (4, "Meera Iyer", "meera@example.com"), (5, "Meera Iyre", "meera.i@example.com"),
                ]
                exact = [r for r, c in Counter(rows).items() if c > 1]
                ids = Counter(r[0] for r in rows)
                print("exact duplicate rows:", exact)
                print("duplicate keys:", [k for k, c in ids.items() if c > 1])
                emails = Counter(r[2].strip().lower() for r in rows)
                print("same normalised email:", [e for e, c in emails.items() if c > 1])
                names = sorted({r[1].strip().lower() for r in rows})
                for i, a in enumerate(names):
                    for b in names[i + 1:]:
                        score = difflib.SequenceMatcher(None, a, b).ratio()
                        if score > 0.85:
                            print(f"possible match: {a!r} ~ {b!r} ({score:.2f})")
            """),
            ex("Join fan-out inflates revenue", "basic", "A non-unique key on the right side duplicates orders.", "python", """
                orders = [(101, "c1", 50.0), (102, "c2", 80.0), (103, "c1", 20.0)]
                addresses = [("c1", "home"), ("c1", "work"), ("c2", "home")]       # c1 has two addresses
                joined = [(o, c, amt, a) for o, c, amt in orders for c2, a in addresses if c == c2]
                print("true revenue  ", sum(a for _, _, a in orders))
                print("joined revenue", sum(r[2] for r in joined), "rows", len(joined))
            """),
            ex("Quality checks in SQL", "intermediate", "Uniqueness, nulls and freshness checks to schedule.", "sql", """
                SELECT order_id, COUNT(*) AS n FROM orders GROUP BY order_id HAVING COUNT(*) > 1;

                SELECT AVG(CASE WHEN customer_id IS NULL THEN 1.0 ELSE 0 END) AS null_rate FROM orders;

                SELECT MAX(created_at) AS latest, CURRENT_TIMESTAMP - MAX(created_at) AS lag FROM orders;
            """, False),
        ],
        ["df.duplicated(subset=keys).sum()", "df.drop_duplicates(subset=keys, keep='last')", "assert df['id'].is_unique", "pd.merge(..., validate='one_to_one')", "GROUP BY key HAVING COUNT(*) > 1"],
        ["drop_duplicates on all columns misses records differing only in a timestamp.", "Fuzzy matching without review can merge distinct people.", "Row counts that 'look fine' hide offsetting gains and losses; reconcile totals."],
        [
            qa("basic", "What are the main dimensions of data quality?", "Completeness, validity, accuracy, consistency, timeliness and uniqueness. Each needs its own checks, such as null rates, format rules, reconciliation with a source of truth, cross-system comparison, freshness lag and key uniqueness."),
            qa("intermediate", "How do you detect join fan-out?", "Check the uniqueness of join keys on each side before joining, compare row counts and key totals before and after, and use tools like pandas merge(validate='one_to_one' or 'many_to_one') or dbt relationship tests."),
            qa("intermediate", "How would you find fuzzy duplicate customers?", "Normalise names, emails and phones, use blocking (e.g., same postcode or first letters) to limit comparisons, score pairs with string similarity or a trained matcher, and review borderline matches before merging."),
            qa("advanced", "How do you prevent duplicates in an event pipeline?", "Assign idempotency keys or event IDs at the producer, deduplicate on them within a window at ingestion, use upserts/merge statements keyed on the business key, and monitor duplicate rates as a data quality metric."),
        ],
        ["data-cleaning", "missing-data", "sql-window-functions"],
        chain(
            ("Profile", "dimensions", "Assess", "Score completeness, validity, consistency, timeliness, uniqueness."),
            ("Exact", "hash / group", "Exact dups", "Group on all columns or the business key.", "table"),
            ("Fuzzy", "normalise + sim", "Near dups", "Normalise and compare with similarity scores.", "candidates"),
            ("Resolve", "survivorship", "Merge", "Choose surviving records and merge fields.", "matches"),
            ("Monitor", "tests + owners", "Prevent", "Automate checks and alert owners on regressions.", "clean"),
        ),
    ),
    topic(
        "feature-engineering", "Feature Engineering", "data-wrangling", "intermediate", "FE",
        "Turn raw records into informative, leak-free predictors: aggregates, ratios, time features, interactions and text signals.",
        "Feature engineering is a translator turning a customer's messy diary into a short profile a model can read: how often they visit, how much they spend and how long since they last came back.",
        "Feature engineering creates model inputs that expose patterns in a form the algorithm can use. Common families include aggregations over entities and windows (count of orders in the last 30 days, average basket value), recency-frequency-monetary (RFM) features, ratios and differences (spend per visit, change from last month), date and time features (hour, weekday, holiday flag, cyclic sine/cosine encodings), binning of continuous values, interaction terms, text features (length, keyword flags, TF-IDF, embeddings) and geographic features (distance to store). Domain knowledge usually beats blind generation. Features must be computed point-in-time, using only data available before the prediction moment, or they leak. Linear models benefit from transformations (log, polynomial, interactions), while tree models capture nonlinearity themselves but still benefit from good aggregates. Evaluate features with cross-validation, ablation and importance measures, and watch for features that are expensive to compute in production or unstable over time. Feature stores help reuse definitions and keep training and serving consistent.",
        ["Building churn, fraud or demand forecasting models.", "Creating RFM segments for marketing.", "Encoding time and seasonality for forecasting.", "Ensuring training/serving parity with a feature store."],
        [
            "Aggregate behaviour over meaningful windows per entity.",
            "Compute features as of the prediction time to avoid leakage.",
            "Cyclic features (hour, month) use sine and cosine.",
            "Ratios and deltas often carry more signal than raw totals.",
            "Validate with cross-validation and ablation, not intuition alone.",
        ],
        [
            ex("RFM features from an event log", "intermediate", "Recency, frequency and monetary value as of a cutoff date.", "python", """
                from collections import defaultdict
                from datetime import date

                events = [("u1", date(2026, 9, 1), 40.0), ("u1", date(2026, 9, 20), 25.0), ("u2", date(2026, 6, 5), 300.0),
                          ("u3", date(2026, 9, 28), 15.0), ("u3", date(2026, 9, 29), 18.0), ("u3", date(2026, 10, 2), 22.0),
                          ("u1", date(2026, 10, 9), 60.0)]           # after cutoff: must be ignored
                cutoff = date(2026, 10, 1)
                feats = defaultdict(lambda: {"last": None, "freq": 0, "money": 0.0})
                for user, day, amount in events:
                    if day >= cutoff:
                        continue
                    f = feats[user]
                    f["last"] = max(f["last"] or day, day)
                    f["freq"] += 1
                    f["money"] += amount
                for user, f in sorted(feats.items()):
                    recency = (cutoff - f["last"]).days
                    print(f"{user}: recency={recency}d frequency={f['freq']} monetary={f['money']:.0f} avg={f['money'] / f['freq']:.1f}")
            """),
            ex("Cyclic time encoding", "basic", "23:00 and 01:00 are close; sine/cosine keeps them close.", "python", """
                import math

                def enc(hour):
                    a = 2 * math.pi * hour / 24
                    return round(math.sin(a), 3), round(math.cos(a), 3)

                for h in (0, 1, 6, 12, 23):
                    print(h, enc(h))
                d = lambda a, b: math.dist(enc(a), enc(b))
                print("distance 23 vs 1:", round(d(23, 1), 3), " raw diff:", 22)
            """),
            ex("Window aggregates in pandas", "intermediate", "Rolling per-user features computed strictly from the past.", "python", """
                import pandas as pd

                ev = ev.sort_values(["user_id", "ts"])
                g = ev.groupby("user_id")
                ev["orders_prev_30d"] = g.rolling("30D", on="ts", closed="left")["order_id"].count().values
                ev["days_since_prev"] = g["ts"].diff().dt.days
                ev["amount_vs_user_avg"] = ev["amount"] / g["amount"].transform(lambda s: s.shift().expanding().mean())
            """, False),
        ],
        ["RFM: recency, frequency, monetary", "sin(2 pi h / 24), cos(2 pi h / 24)", "df.groupby('id')['v'].transform('mean')", "g.rolling('30D', closed='left')", "np.log1p(x) · pd.cut(x, bins)"],
        ["Aggregates that include the current or future rows leak the label.", "Thousands of auto-generated features overfit small datasets.", "Features unavailable or slow at serving time cannot be used in production."],
        [
            qa("basic", "What is feature engineering?", "Creating new input variables from raw data to make patterns easier for a model to learn, such as aggregates, ratios, time-based features and encodings. It often improves performance more than changing algorithms."),
            qa("intermediate", "Why encode hour of day with sine and cosine?", "Hour is cyclic: 23 and 0 are adjacent but numerically far apart. Mapping to points on a circle with sine and cosine preserves the closeness so models see the cycle correctly."),
            qa("intermediate", "How do you avoid leakage when building aggregate features?", "Define a prediction timestamp per row and compute aggregates using only events strictly before it (closed='left' windows, point-in-time joins). Validate with time-based splits."),
            qa("advanced", "How do you decide whether a new feature is worth keeping?", "Compare cross-validated performance with and without it (ablation), check stability across time folds, consider permutation importance, and weigh the cost and latency of computing it in production against the gain."),
        ],
        ["encoding-categoricals", "scaling-normalisation", "data-leakage"],
        chain(
            ("Raw events", "logs, tables", "Source", "Transactions, sessions, profiles and text."),
            ("Cutoff", "as-of time", "Point in time", "Fix the prediction time for every row.", "events"),
            ("Aggregate", "windows, RFM", "Aggregate", "Counts, sums and averages over past windows.", "history"),
            ("Transform", "ratios, cyclic", "Transform", "Ratios, deltas, logs and cyclic encodings.", "aggregates"),
            ("Evaluate", "CV, ablation", "Select", "Keep features that help out of sample.", "features"),
        ),
    ),
    topic(
        "encoding-categoricals", "Encoding Categorical Variables", "data-wrangling", "intermediate", "EC",
        "One-hot, ordinal, target, frequency and hashing encodings, chosen by cardinality, order and model type.",
        "Encoding is like assigning seats at a dinner. You can give each guest their own chair (one-hot), seat them by age order (ordinal), or group them by how much they usually tip (target encoding), but you should not pretend table number 7 is worth more than table 3.",
        "Most models need numeric inputs, so categorical variables must be encoded. One-hot encoding creates a binary column per category and is the safe default for nominal variables with modest cardinality; drop one column (or use regularisation) in linear models to avoid the dummy-variable trap. Ordinal encoding maps ordered categories to integers that preserve order (low < medium < high); applying arbitrary integers to nominal categories imposes a fake order, which linear models misread, although tree models often cope. High-cardinality variables (zip codes, product IDs) explode one-hot dimensions, so alternatives include frequency or count encoding, grouping rare categories into 'other', feature hashing into a fixed number of buckets, learned embeddings, and target (mean) encoding. Target encoding replaces each category with the smoothed mean of the target and is powerful but leaks the label unless computed out-of-fold and blended with the global mean for rare categories. Encoders must be fit on training data, and unseen categories at prediction time need a defined handling (ignore, 'other' bucket). Gradient boosting libraries like CatBoost and LightGBM have native categorical support.",
        ["Preparing country, device and plan columns for a model.", "Handling thousands of product or merchant IDs.", "Encoding ordered survey answers.", "Making pipelines robust to new categories in production."],
        [
            "One-hot for nominal, low-cardinality variables.",
            "Ordinal encoding only when categories truly have order.",
            "Target encoding needs out-of-fold computation and smoothing.",
            "Hashing or grouping rare levels tames high cardinality.",
            "Define behaviour for unseen categories.",
        ],
        [
            ex("One-hot, ordinal and frequency encoding", "basic", "Three encodings of small synthetic columns.", "python", """
                from collections import Counter

                devices = ["ios", "android", "web", "ios", "web", "ios"]
                levels = ["low", "high", "medium", "low", "high", "medium"]

                cats = sorted(set(devices))
                print("one-hot columns", cats)
                for d in devices:
                    print(d, [int(d == c) for c in cats])
                order = {"low": 0, "medium": 1, "high": 2}
                print("ordinal", [order[l] for l in levels])
                freq = Counter(devices)
                print("frequency", [round(freq[d] / len(devices), 2) for d in devices])
            """),
            ex("Out-of-fold smoothed target encoding", "advanced", "Each row's encoding uses only other folds, blended with the global mean.", "python", """
                import random
                from collections import defaultdict

                random.seed(3)
                cities = ["A"] * 40 + ["B"] * 40 + ["C"] * 4
                rate = {"A": 0.1, "B": 0.4, "C": 0.9}
                rows = [(c, int(random.random() < rate[c])) for c in cities]
                random.shuffle(rows)
                K, M = 5, 10                                          # folds, smoothing strength
                folds = [i % K for i in range(len(rows))]
                encoded = []
                for i, (city, _) in enumerate(rows):
                    other = [(c, y) for j, (c, y) in enumerate(rows) if folds[j] != folds[i]]
                    prior = sum(y for _, y in other) / len(other)
                    ys = [y for c, y in other if c == city]
                    encoded.append((city, (sum(ys) + M * prior) / (len(ys) + M)))
                summary = defaultdict(list)
                for c, e in encoded:
                    summary[c].append(e)
                for c in sorted(summary):
                    print(c, "n =", cities.count(c), "mean encoding", round(sum(summary[c]) / len(summary[c]), 3))
            """),
            ex("scikit-learn encoders", "intermediate", "ColumnTransformer with safe handling of unknown categories.", "python", """
                from sklearn.compose import ColumnTransformer
                from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, TargetEncoder

                pre = ColumnTransformer([
                    ("onehot", OneHotEncoder(handle_unknown="infrequent_if_exist", min_frequency=20), ["device", "country"]),
                    ("ordinal", OrdinalEncoder(categories=[["low", "medium", "high"]]), ["tier"]),
                    ("target", TargetEncoder(smooth="auto", cv=5), ["merchant_id"]),
                ])
            """, False),
        ],
        ["pd.get_dummies(df, columns=['c'], drop_first=True)", "OneHotEncoder(handle_unknown='ignore')", "OrdinalEncoder(categories=[[...]])", "TargetEncoder(cv=5) · smoothed mean", "FeatureHasher(n_features=2**18)"],
        ["Label-encoding nominal categories as 0, 1, 2 implies a false order for linear models.", "Target encoding on the full dataset leaks the label.", "One-hot on IDs with thousands of levels creates sparse, overfit models."],
        [
            qa("basic", "When would you use one-hot versus ordinal encoding?", "One-hot for nominal categories without order, such as country or device. Ordinal encoding for categories with a natural order, such as education level or small/medium/large, mapped to integers preserving that order."),
            qa("intermediate", "What is the dummy variable trap?", "With an intercept and one-hot columns for every category, the columns sum to one and are perfectly collinear with the intercept, making OLS coefficients unidentifiable. Drop one reference category or use regularisation."),
            qa("intermediate", "How do you handle a categorical feature with 50,000 levels?", "Options include grouping rare levels, frequency encoding, smoothed out-of-fold target encoding, feature hashing, learned embeddings, or models with native categorical support such as CatBoost. Choice depends on the model and data size."),
            qa("advanced", "Why does target encoding need smoothing and out-of-fold computation?", "Using the row's own target in its encoding leaks the label and overfits, especially for rare categories whose mean is extreme by chance. Out-of-fold means remove self-information, and smoothing shrinks rare categories toward the global mean."),
        ],
        ["feature-engineering", "data-types", "scaling-normalisation"],
        chain(
            ("Category", "nominal/ordinal", "Inspect", "Determine order and cardinality."),
            ("Low card.", "one-hot", "Small sets", "One-hot nominal; ordinal map for ordered levels.", "type"),
            ("High card.", "hash / target", "Many levels", "Group rare levels, hash, embed or target-encode.", "levels"),
            ("Fit", "train folds", "No leakage", "Fit encoders on training data, out-of-fold for targets.", "encoder"),
            ("Unseen", "fallback bucket", "Production", "Map new categories to a defined fallback.", "model"),
        ),
    ),
    topic(
        "scaling-normalisation", "Scaling & Normalisation", "data-wrangling", "basic", "SN",
        "Put features on comparable scales: standardisation, min-max, robust scaling and log transforms, fitted on training data only.",
        "Scaling is converting all prices to the same currency before comparing them. Without it, a feature measured in rupees shouts over one measured in lakhs simply because its numbers are bigger.",
        "Many algorithms are sensitive to the scale of features. Distance-based methods (k-nearest neighbours, k-means, SVM with RBF kernels), gradient-descent-trained models (logistic regression, neural networks) and regularised linear models (ridge, lasso) all behave better when features are on similar scales, while tree-based models are largely scale-invariant. Standardisation (z-score) subtracts the mean and divides by the standard deviation, giving mean 0 and SD 1. Min-max normalisation maps values to [0, 1] and is sensitive to outliers because a single extreme value compresses everyone else. Robust scaling subtracts the median and divides by the IQR, resisting outliers. Non-linear transforms such as log, square root, Box-Cox, Yeo-Johnson or quantile transformation change the distribution's shape, not just its scale, and help with heavy right skew. 'Normalisation' is also used for scaling each row to unit length (L2 norm), common in text vectors. Every scaler must be fit on training data and applied unchanged to validation, test and production data, ideally inside a pipeline.",
        ["Preparing features for k-means customer segmentation.", "Training regularised regression or neural networks.", "Comparing metrics on different units in a composite score.", "Normalising text vectors for cosine similarity."],
        [
            "Z-score: (x - mean) / sd.",
            "Min-max: (x - min) / (max - min), outlier-sensitive.",
            "Robust: (x - median) / IQR.",
            "Tree models rarely need scaling; distance and gradient models do.",
            "Fit scalers on train only, reuse everywhere else.",
        ],
        [
            ex("Three scalers on data with an outlier", "basic", "See how min-max is compressed by one extreme value.", "python", """
                import statistics as st

                x = [12, 15, 14, 10, 13, 16, 11, 95]
                mu, sd = st.fmean(x), st.stdev(x)
                lo, hi = min(x), max(x)
                q1, med, q3 = st.quantiles(x, n=4, method="inclusive")
                print("z-score:", [round((v - mu) / sd, 2) for v in x])
                print("min-max:", [round((v - lo) / (hi - lo), 2) for v in x])
                print("robust: ", [round((v - med) / (q3 - q1), 2) for v in x])
            """),
            ex("Why k-NN needs scaling", "intermediate", "Income in rupees dominates distance until features are standardised.", "python", """
                import math
                import statistics as st

                people = {"A": (25, 800000), "B": (60, 804000), "C": (27, 1200000)}    # (age, income)
                query = (26, 805000)

                def nearest(points, q):
                    return min(points, key=lambda k: math.dist(points[k], q))

                print("raw nearest:", nearest(people, query))
                ages = [v[0] for v in people.values()] + [query[0]]
                incs = [v[1] for v in people.values()] + [query[1]]
                z = lambda v, s: (v - st.fmean(s)) / st.stdev(s)
                scaled = {k: (z(a, ages), z(i, incs)) for k, (a, i) in people.items()}
                print("scaled nearest:", nearest(scaled, (z(query[0], ages), z(query[1], incs))))
            """),
            ex("Scalers in a scikit-learn pipeline", "intermediate", "Fit on train, transform test with the same parameters.", "python", """
                from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, PowerTransformer
                from sklearn.pipeline import make_pipeline
                from sklearn.neighbors import KNeighborsClassifier

                pipe = make_pipeline(RobustScaler(), KNeighborsClassifier(n_neighbors=15))
                pipe.fit(X_train, y_train)
                print(pipe.score(X_test, y_test))
                PowerTransformer(method="yeo-johnson").fit_transform(X_train)
            """, False),
        ],
        ["StandardScaler: (x - mean) / sd", "MinMaxScaler: (x - min) / (max - min)", "RobustScaler: (x - median) / IQR", "np.log1p(x) · PowerTransformer()", "Normalizer(norm='l2') for row vectors"],
        ["Fitting the scaler on all data before splitting leaks test statistics.", "Min-max scaled production data can fall outside [0, 1] when new extremes arrive.", "Scaling binary or one-hot features is usually unnecessary and can hurt interpretability."],
        [
            qa("basic", "What is the difference between standardisation and normalisation?", "Standardisation rescales to mean 0 and SD 1 using the z-score. Min-max normalisation rescales to a fixed range such as [0, 1]. The term normalisation is also used for scaling each sample vector to unit norm."),
            qa("intermediate", "Which models need feature scaling?", "Distance-based models (k-NN, k-means, SVM), models trained with gradient descent (logistic regression, neural networks) and regularised linear models, whose penalties depend on coefficient scale. Tree-based models are largely unaffected."),
            qa("intermediate", "When would you use a robust scaler?", "When features contain outliers that would distort the mean and SD or the min and max. Centring on the median and dividing by the IQR keeps the bulk of the data on a sensible scale."),
            qa("advanced", "Why must the scaler be fit only on training data?", "Its parameters (mean, SD, min, max) are learned from data; fitting on the full dataset lets validation or test information influence training, which is leakage and produces optimistic estimates. In production the same fitted parameters must be applied."),
        ],
        ["feature-engineering", "outliers", "numpy-vectorisation"],
        chain(
            ("Inspect", "units, skew", "Look", "Check ranges, units, skew and outliers per feature."),
            ("Transform", "log / power", "Shape", "Reduce heavy skew with log or power transforms.", "features"),
            ("Scale", "z / minmax / IQR", "Scale", "Choose standard, min-max or robust scaling.", "shaped"),
            ("Fit train", "learn params", "Fit", "Learn scaling parameters on training data only.", "scaler"),
            ("Apply", "test + prod", "Reuse", "Apply identical parameters to test and production.", "params"),
        ),
    ),
]

TOPICS += [
    topic(
        "viz-principles", "Data Visualisation Principles", "visualisation", "basic", "VP",
        "Encode data with position and length first, cut clutter, keep scales honest, and label so the chart reads itself.",
        "A good chart is a well-designed road sign: readable at a glance, no decoration competing for attention, and never pointing you the wrong way.",
        "Effective visualisation relies on how people perceive visual encodings. Cleveland and McGill's research ranks accuracy roughly as position on a common scale, then position on non-aligned scales, length, angle and slope, area, volume, and colour saturation or hue, which is why bar and dot charts beat pie charts and bubble charts for precise comparison. Tufte's data-ink ratio encourages removing chart junk: heavy gridlines, 3D effects, shadows and redundant legends. Honesty matters: bar charts must start at zero because length encodes value, while line charts may use a truncated axis when change matters more than absolute level, as long as it is clearly labelled; dual y-axes and inconsistent scales across small multiples often mislead. Colour should be purposeful: sequential palettes for ordered values, diverging palettes around a meaningful midpoint, categorical palettes for groups, colour-blind safe choices, and a highlight colour for the one series that matters. Direct labelling beats legends, titles should state the takeaway, and annotations explain anomalies. Small multiples compare many groups better than one overloaded chart.",
        ["Designing charts for a report or a stakeholder deck.", "Reviewing a dashboard for misleading scales.", "Choosing accessible colour palettes.", "Turning an exploratory plot into a publication-quality figure."],
        [
            "Position and length are decoded most accurately; area and colour least.",
            "Bar charts start at zero; label truncated line axes.",
            "Maximise data-ink: remove 3D, shadows and heavy gridlines.",
            "Use colour purposefully and colour-blind safe palettes.",
            "Title with the insight; label lines directly.",
        ],
        [
            ex("A text bar chart that respects zero", "basic", "Bar length proportional to value, sorted and directly labelled.", "python", """
                sales = {"North": 182, "South": 240, "East": 96, "West": 205, "Central": 150}
                width = 40
                top = max(sales.values())
                print("Q3 sales by region (units): South leads")
                for region, v in sorted(sales.items(), key=lambda kv: kv[1], reverse=True):
                    bar = "#" * round(v / top * width)
                    print(f"{region:8} {bar} {v}")
            """),
            ex("How a truncated axis exaggerates", "intermediate", "The same two values drawn from zero and from a truncated baseline.", "python", """
                a, b = 50.2, 51.0
                for base in (0, 50):
                    scale = 40 / (max(a, b) - base)
                    print(f"axis starts at {base}:")
                    print("  A", "#" * round((a - base) * scale), a)
                    print("  B", "#" * round((b - base) * scale), b)
                print(f"real difference: {(b - a) / a:.1%}")
            """),
            ex("Clean matplotlib defaults", "intermediate", "Remove clutter, highlight one series and annotate.", "python", """
                import matplotlib.pyplot as plt

                fig, ax = plt.subplots(figsize=(7, 4))
                for name, s in series.items():
                    ax.plot(s.index, s.values, color="#d62728" if name == "Ours" else "#bbbbbb", lw=2 if name == "Ours" else 1)
                    ax.text(s.index[-1], s.values[-1], f" {name}", va="center")
                ax.spines[["top", "right"]].set_visible(False)
                ax.set_title("Our retention overtook competitors in March")
                ax.annotate("pricing change", xy=(change_date, value), xytext=(10, 20), textcoords="offset points", arrowprops={"arrowstyle": "->"})
            """, False),
        ],
        ["Encoding ranking: position > length > angle > area > colour", "ax.spines[['top','right']].set_visible(False)", "Sequential / diverging / categorical palettes", "plt.subplots(nrows, ncols, sharey=True) for small multiples", "Title = takeaway, not 'Chart of X'"],
        ["Pie charts with many slices make comparison nearly impossible.", "Dual y-axes let the designer manufacture any correlation.", "Rainbow colour maps distort perceived differences and fail for colour-blind readers."],
        [
            qa("basic", "Why should bar charts start at zero?", "Bars encode value by length, so a truncated baseline makes small differences look huge. Line charts encode change by position and slope, so a non-zero baseline can be acceptable when clearly labelled."),
            qa("intermediate", "What is the data-ink ratio?", "Tufte's ratio of ink used to show data to total ink in the graphic. Maximising it means removing non-informative elements such as 3D effects, backgrounds, heavy gridlines and redundant labels."),
            qa("intermediate", "Why are pie charts often discouraged?", "People judge angles and areas less accurately than lengths or positions, so comparing similar slices or many categories is hard. A sorted bar chart communicates the same information more precisely; pies are acceptable for two or three parts of a whole."),
            qa("advanced", "How do you choose a colour palette?", "Use sequential palettes for ordered magnitudes, diverging palettes when values deviate from a meaningful centre, and qualitative palettes for unordered categories. Check colour-blind safety, keep the number of colours small and use a single accent colour to highlight the key series."),
        ],
        ["choosing-charts", "dashboards-storytelling", "eda"],
        chain(
            ("Message", "one takeaway", "Purpose", "Decide what the reader should learn."),
            ("Encoding", "position first", "Encode", "Map the key comparison to position or length.", "message"),
            ("Declutter", "data-ink", "Simplify", "Remove junk, mute context, keep the data.", "draft"),
            ("Honesty", "scales, zero", "Check", "Zero baselines for bars; consistent scales.", "clean"),
            ("Label", "title + notes", "Annotate", "Insight title, direct labels and annotations.", "honest"),
        ),
    ),
    topic(
        "choosing-charts", "Choosing the Right Chart", "visualisation", "basic", "CH",
        "Start from the question (comparison, trend, distribution, relationship, composition), then pick the chart.",
        "Choosing a chart is like choosing a tool from a toolbox. A hammer and a screwdriver both join things, but using the wrong one for the job makes a mess.",
        "Chart choice follows the analytical question and the data types involved. Comparisons across categories use bar charts (horizontal for long labels), dot plots, or grouped bars for a second dimension. Trends over time use line charts, area charts for cumulative totals, and sparklines in tables. Distributions of one variable use histograms, density plots, box plots, violin plots or ECDFs; ECDFs show percentiles directly and avoid bin-width choices. Relationships between two numeric variables use scatter plots, with transparency or hexbin plots for many points and trend lines for guidance; a third variable can be shown with colour or size. Composition (parts of a whole) uses stacked bars, 100% stacked bars, treemaps or, with few categories, a pie or donut. Rankings use sorted bars or slope charts for change between two points. Geographic data use choropleths (rates, not counts) or symbol maps. Correlation matrices use heatmaps. For many groups, small multiples with shared axes beat a single crowded chart. Tables remain best when readers need precise individual values.",
        ["Picking visuals for a monthly business review.", "Exploring distributions and relationships during EDA.", "Showing before/after change across segments.", "Choosing map types for regional KPIs."],
        [
            "Comparison: bars or dots. Trend: lines.",
            "Distribution: histogram, box, violin, ECDF.",
            "Relationship: scatter (alpha or hexbin for many points).",
            "Composition: stacked bars; pie only for 2-3 parts.",
            "Many groups: small multiples with shared axes.",
        ],
        [
            ex("A rule-based chart chooser", "basic", "Map question type and data shape to sensible chart options.", "python", """
                def choose_chart(question, n_categories=0, over_time=False, n_points=0):
                    if question == "trend" or over_time:
                        return "line chart" if n_categories <= 5 else "small multiples of line charts"
                    if question == "comparison":
                        return "sorted bar chart" if n_categories <= 15 else "dot plot or top-N bar chart"
                    if question == "distribution":
                        return "histogram + box plot" if n_points < 10000 else "ECDF or density plot"
                    if question == "relationship":
                        return "scatter plot" if n_points < 5000 else "hexbin or scatter with alpha"
                    if question == "composition":
                        return "pie/donut" if n_categories <= 3 else "100% stacked bar"
                    return "table"

                cases = [("trend", 3, True, 0), ("comparison", 30, False, 0), ("distribution", 0, False, 50000),
                         ("relationship", 0, False, 200), ("composition", 6, False, 0)]
                for c in cases:
                    print(c, "->", choose_chart(*c))
            """),
            ex("Histogram vs ECDF in text", "intermediate", "Bins hide detail; the ECDF shows percentiles directly.", "python", """
                import random
                from collections import Counter

                random.seed(5)
                x = sorted(round(random.gauss(30, 8)) for _ in range(500))
                bins = Counter(v // 10 * 10 for v in x)
                for b in sorted(bins):
                    print(f"{b:3}-{b + 9:<3} {'#' * (bins[b] // 5)}")
                for q in (0.1, 0.5, 0.9):
                    print(f"ECDF: {q:.0%} of values <= {x[int(q * len(x)) - 1]}")
            """),
            ex("seaborn chart families", "basic", "One call per question type.", "python", """
                import seaborn as sns

                sns.barplot(data=df, x="revenue", y="region", estimator="sum", errorbar=None)
                sns.lineplot(data=daily, x="date", y="orders", hue="channel")
                sns.histplot(df["basket"], bins=40); sns.ecdfplot(df["basket"])
                sns.scatterplot(data=df, x="sessions", y="spend", alpha=0.3)
                sns.relplot(data=daily, x="date", y="orders", col="country", col_wrap=4, kind="line")
            """, False),
        ],
        ["Comparison -> bar/dot · Trend -> line", "Distribution -> hist/box/violin/ECDF", "Relationship -> scatter/hexbin", "Composition -> stacked bar", "sns.relplot(..., col='group') for small multiples"],
        ["Line charts across unordered categories imply a false continuity.", "Choropleths of raw counts mostly show where people live; map rates.", "Stacked areas make every layer except the bottom hard to read."],
        [
            qa("basic", "Which chart would you use to show a trend over time?", "A line chart with time on the x-axis, because position and slope make change easy to see. For a few periods or discrete comparisons, bars are acceptable; for many series, use small multiples."),
            qa("basic", "How do you visualise the distribution of one numeric variable?", "Use a histogram or density plot for shape, a box or violin plot to compare groups, and an ECDF to read percentiles directly without choosing bins."),
            qa("intermediate", "How do you plot a relationship with a million points?", "Overplotting hides density, so use transparency, hexbin or 2D density plots, or sample the data, and optionally add a smoothed trend line. Facet by a key category if relationships differ by group."),
            qa("advanced", "When is a table better than a chart?", "When the audience needs to look up precise individual values, compare a few exact numbers, or when there are many dimensions with no single pattern to highlight. Tables can still use conditional formatting and sparklines to add visual cues."),
        ],
        ["viz-principles", "percentiles-iqr", "dashboards-storytelling"],
        chain(
            ("Question", "what to show?", "Intent", "Comparison, trend, distribution, relationship or composition?"),
            ("Data types", "cat / num / time", "Inputs", "Which variables are categorical, numeric or temporal?", "intent"),
            ("Candidates", "2-3 charts", "Options", "List chart types that fit the intent and data.", "types"),
            ("Pick", "clearest one", "Choose", "Prefer the one with the most accurate encoding.", "options"),
        ),
    ),
    topic(
        "dashboards-storytelling", "Dashboards & Data Storytelling", "visualisation", "intermediate", "DB",
        "Dashboards monitor; stories persuade. Both need context: targets, comparisons and a clear 'so what'.",
        "A dashboard is a car's instrument panel: a few gauges you glance at to know if anything needs attention. A data story is the mechanic explaining why the engine light is on and what to fix.",
        "Dashboards serve ongoing monitoring and should be designed for a specific audience and decision cadence. Put the most important KPIs top-left, show each with context (target, previous period, same period last year, trend sparkline), and allow drill-down from summary to detail rather than cramming everything onto one screen. Consistent definitions, refresh timestamps, data quality notes and owners build trust; too many charts or vanity metrics lead to dashboards nobody opens. Data storytelling is about explanation and persuasion for a one-off decision. A common structure is situation, complication, resolution (or the Pyramid principle: lead with the answer, then support it). Each slide or section has an action title stating the insight, one chart supporting it, and annotations guiding the eye. Know the audience: executives want the decision and its impact, analysts want methods and caveats. Quantify uncertainty honestly, show what was ruled out, and end with a concrete recommendation and next steps. Narrative without data is anecdote; data without narrative is noise.",
        ["Building a weekly business review dashboard.", "Presenting an analysis to leadership for a decision.", "Designing self-serve KPI views for product teams.", "Explaining an A/B test result to non-technical stakeholders."],
        [
            "Design for a specific audience, question and cadence.",
            "Every KPI needs context: target, prior period, trend.",
            "Lead with the answer; support with evidence.",
            "One chart, one message, one action title.",
            "Show freshness, definitions and caveats to earn trust.",
        ],
        [
            ex("KPI tiles with context", "basic", "Compute week-over-week change and target status for a text dashboard.", "python", """
                kpis = {
                    "Active users": {"now": 48200, "prev": 46900, "target": 50000, "higher_better": True},
                    "Conversion": {"now": 0.034, "prev": 0.036, "target": 0.035, "higher_better": True},
                    "p95 latency ms": {"now": 410, "prev": 380, "target": 400, "higher_better": False},
                }
                print(f"{'KPI':16}{'value':>10}{'WoW':>9}  status")
                for name, k in kpis.items():
                    wow = (k["now"] - k["prev"]) / k["prev"]
                    on_track = k["now"] >= k["target"] if k["higher_better"] else k["now"] <= k["target"]
                    value = f"{k['now']:.1%}" if k["now"] < 1 else f"{k['now']:,}"
                    print(f"{name:16}{value:>10}{wow:>+9.1%}  {'on track' if on_track else 'needs attention'}")
                print("data as of 2026-10-17 06:00 UTC (synthetic)")
            """),
            ex("Situation, complication, resolution", "intermediate", "Generate a structured narrative from analysis results.", "python", """
                result = {"metric": "checkout conversion", "before": 0.041, "after": 0.036,
                          "driver": "Android app v5.2", "driver_share": 0.78, "fix_eta_days": 3}
                drop = (result["after"] - result["before"]) / result["before"]
                print("Situation:   ", f"{result['metric']} averaged {result['before']:.1%} last quarter.")
                print("Complication:", f"it fell {abs(drop):.0%} this week; {result['driver_share']:.0%} of the drop comes from {result['driver']}.")
                print("Resolution:  ", f"roll back the release; the fix ships in {result['fix_eta_days']} days. Monitor daily until recovered.")
            """),
        ],
        ["KPI tile: value, delta vs prior, vs target, sparkline", "Action title = insight sentence", "Situation -> Complication -> Resolution", "Overview first, zoom and filter, details on demand", "Show 'data as of' timestamp"],
        ["Dashboards with 30 charts answer no question well.", "Changing metric definitions without notes destroys trust.", "Presenting every analysis step buries the conclusion."],
        [
            qa("basic", "What makes a good dashboard?", "It targets a defined audience and decision, shows a few key metrics with context (targets, comparisons, trends), supports drill-down, uses consistent definitions and displays data freshness. It should make it obvious what needs attention."),
            qa("intermediate", "How do you structure a data story for executives?", "Lead with the answer and recommendation, quantify the impact, support with two or three key charts with action titles, state risks and confidence, and close with clear next steps. Keep method details in an appendix."),
            qa("intermediate", "What is the difference between a dashboard and a report?", "A dashboard is an ongoing monitoring tool refreshed regularly for repeated questions. A report or story is a one-off analysis answering a specific question with narrative, interpretation and a recommendation."),
            qa("advanced", "Nobody uses a dashboard you built. How do you diagnose and fix it?", "Check usage logs and interview intended users about the decisions they make, then remove metrics that do not inform those decisions, add context and alerts for what changed, fix trust issues (freshness, definitions) and embed it in an existing meeting cadence."),
        ],
        ["viz-principles", "metrics-design", "choosing-charts"],
        chain(
            ("Audience", "who decides?", "Know them", "Identify the audience, decisions and cadence."),
            ("Answer", "lead with it", "Headline", "State the conclusion and recommended action first.", "needs"),
            ("Evidence", "2-3 charts", "Support", "Show the few charts that justify the answer.", "claim"),
            ("Context", "targets, trends", "Frame", "Add comparisons, uncertainty and caveats.", "charts"),
            ("Action", "next steps", "Close", "End with owners, dates and what to monitor.", "story"),
        ),
    ),
    topic(
        "sql-window-functions", "SQL for Analysis: Window Functions", "tooling", "intermediate", "SQ",
        "Rank, running totals, moving averages and period-over-period comparisons without collapsing rows.",
        "A window function is like each runner in a race glancing at the runners around them: everyone keeps their own place in the list, but can see the leader's time, their rank and the gap to the person ahead.",
        "Window functions compute values across a set of rows related to the current row while keeping every row, unlike GROUP BY which collapses groups. The syntax is FUNCTION() OVER (PARTITION BY ... ORDER BY ... frame). PARTITION BY restarts the calculation per group, ORDER BY defines sequence, and the frame clause (ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) defines which rows are included, for example a 7-day moving average. Ranking functions are ROW_NUMBER (unique sequence, used for de-duplication and 'latest record per key'), RANK (gaps after ties) and DENSE_RANK (no gaps); NTILE(n) buckets rows into quantiles. LAG and LEAD access previous or next rows, ideal for period-over-period change, time between events and sessionisation. Aggregates such as SUM, AVG and COUNT become running or partitioned totals, and FIRST_VALUE / LAST_VALUE fetch boundary values (mind the default frame). Window functions cannot be used directly in WHERE, so filter them in a subquery, CTE or with QUALIFY where supported. Combined with CTEs they express cohort retention, funnels and top-N-per-group queries concisely.",
        ["Top N products per category.", "Running revenue totals and 7-day moving averages.", "Month-over-month growth with LAG.", "De-duplicating to the latest record per customer."],
        [
            "OVER (PARTITION BY ... ORDER BY ...) keeps all rows.",
            "ROW_NUMBER for dedup; RANK/DENSE_RANK for ties.",
            "LAG/LEAD compare with previous or next rows.",
            "ROWS BETWEEN n PRECEDING AND CURRENT ROW for moving windows.",
            "Filter window results in an outer query or QUALIFY.",
        ],
        [
            ex("Window functions in in-memory SQLite", "intermediate", "Run real SQL from Python's stdlib sqlite3 with synthetic rows.", "python", """
                import sqlite3

                con = sqlite3.connect(":memory:")
                con.execute("CREATE TABLE sales (day TEXT, region TEXT, revenue REAL)")
                rows = [("2026-10-0%d" % d, r, v) for d, r, v in [
                    (1, "N", 100), (2, "N", 120), (3, "N", 90), (4, "N", 150),
                    (1, "S", 80), (2, "S", 60), (3, "S", 110), (4, "S", 130)]]
                con.executemany("INSERT INTO sales VALUES (?, ?, ?)", rows)
                query = '''
                SELECT day, region, revenue,
                       SUM(revenue) OVER (PARTITION BY region ORDER BY day) AS running_total,
                       ROUND(AVG(revenue) OVER (PARTITION BY region ORDER BY day ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 1) AS ma3,
                       revenue - LAG(revenue) OVER (PARTITION BY region ORDER BY day) AS change,
                       RANK() OVER (PARTITION BY day ORDER BY revenue DESC) AS rank_in_day
                FROM sales ORDER BY region, day
                '''
                for row in con.execute(query):
                    print(row)
            """),
            ex("Latest record per key with ROW_NUMBER", "intermediate", "Classic de-duplication pattern.", "python", """
                import sqlite3

                con = sqlite3.connect(":memory:")
                con.execute("CREATE TABLE profile (user_id INT, updated_at TEXT, plan TEXT)")
                con.executemany("INSERT INTO profile VALUES (?, ?, ?)", [
                    (1, "2026-09-01", "free"), (1, "2026-10-02", "pro"), (2, "2026-08-15", "pro"),
                    (2, "2026-08-15", "pro"), (3, "2026-10-10", "free")])
                query = '''
                WITH ranked AS (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY updated_at DESC) AS rn
                    FROM profile
                )
                SELECT user_id, updated_at, plan FROM ranked WHERE rn = 1
                '''
                print(con.execute(query).fetchall())
            """),
            ex("Cohort retention with windows", "advanced", "First month per user, then share active in later months.", "sql", """
                WITH activity AS (
                    SELECT user_id, DATE_TRUNC('month', event_at) AS month FROM events GROUP BY 1, 2
                ), cohorts AS (
                    SELECT user_id, month, MIN(month) OVER (PARTITION BY user_id) AS cohort FROM activity
                )
                SELECT cohort,
                       DATE_DIFF('month', cohort, month) AS months_since,
                       COUNT(DISTINCT user_id) * 1.0
                         / FIRST_VALUE(COUNT(DISTINCT user_id)) OVER (PARTITION BY cohort ORDER BY DATE_DIFF('month', cohort, month)) AS retention
                FROM cohorts
                GROUP BY cohort, months_since
                ORDER BY cohort, months_since;
            """, False),
        ],
        ["ROW_NUMBER() OVER (PARTITION BY k ORDER BY ts DESC)", "SUM(v) OVER (ORDER BY d ROWS UNBOUNDED PRECEDING)", "AVG(v) OVER (ORDER BY d ROWS 6 PRECEDING)", "v - LAG(v) OVER (PARTITION BY k ORDER BY d)", "NTILE(4) OVER (ORDER BY v)"],
        ["LAST_VALUE with the default frame returns the current row; specify ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING.", "ROWS vs RANGE frames differ when ORDER BY values tie or dates have gaps.", "Missing days make 'ROWS 6 PRECEDING' span more than 7 calendar days; join to a date spine."],
        [
            qa("basic", "What is the difference between GROUP BY and a window function?", "GROUP BY collapses rows into one per group. A window function computes an aggregate or ranking across related rows but returns a value for every input row, so you can show each row alongside its group total or rank."),
            qa("intermediate", "What is the difference between ROW_NUMBER, RANK and DENSE_RANK?", "ROW_NUMBER assigns unique sequential numbers even for ties. RANK gives ties the same rank and skips the following numbers (1, 1, 3). DENSE_RANK gives ties the same rank without gaps (1, 1, 2)."),
            qa("intermediate", "How do you get the top 3 products per category?", "Compute ROW_NUMBER() (or DENSE_RANK if ties should be included) OVER (PARTITION BY category ORDER BY sales DESC) in a CTE, then filter rn <= 3 in the outer query, or use QUALIFY where supported."),
            qa("advanced", "How would you compute a 7-day moving average correctly when some days have no sales?", "Join the data to a complete date spine so missing days appear with zero (or null, depending on the metric), then use AVG(...) OVER (ORDER BY day ROWS BETWEEN 6 PRECEDING AND CURRENT ROW). Alternatively use a RANGE frame with an interval where the engine supports it."),
        ],
        ["pandas-essentials", "time-series-basics", "duplicates-quality"],
        chain(
            ("Rows", "table", "Input", "Start with row-level data."),
            ("Partition", "PARTITION BY", "Group", "Split rows into independent windows.", "rows"),
            ("Order", "ORDER BY", "Sequence", "Order rows within each partition.", "groups"),
            ("Frame", "ROWS BETWEEN", "Window", "Choose which neighbouring rows are included.", "ordered"),
            ("Compute", "rank, lag, sum", "Result", "Every row gets its windowed value.", "frame"),
        ),
    ),
    topic(
        "pandas-essentials", "pandas Essentials", "tooling", "basic", "PD",
        "DataFrames for selection, filtering, groupby-aggregate, merge, reshape and time series, the analyst's daily toolkit.",
        "pandas is a spreadsheet you drive with code: every click (filter, pivot, lookup) becomes a line you can rerun, review and scale to millions of rows.",
        "pandas provides the DataFrame, a table of labelled columns that can hold different types, and the Series, a single labelled column. Core operations are reading data (read_csv, read_parquet, read_sql), inspecting (head, info, describe, value_counts), selecting with loc (labels) and iloc (positions), boolean filtering and query, creating columns with vectorised expressions or assign, and handling missing values (isna, fillna, dropna). The split-apply-combine pattern uses groupby with agg, transform (returns same-shaped output for group-wise features) or apply. Joins use merge with explicit how and validate arguments; concat stacks frames. Reshaping uses pivot_table and melt to move between wide and long formats. Time series features include datetime parsing, the dt accessor, resample, rolling and shift. Performance comes from vectorised operations; row-wise apply and iterrows are slow. Use categorical dtype for repeated strings and Parquet for storage. Since pandas 2.x, copy-on-write semantics and the Arrow backend change some behaviour, and chained assignment such as df[df.a > 0]['b'] = 1 does not modify df; use df.loc[mask, 'b'] = 1.",
        ["Cleaning and joining CSV or database extracts.", "Group-wise KPIs and pivot tables.", "Feature creation for models.", "Quick time series resampling and rolling statistics."],
        [
            "loc is label-based, iloc is position-based.",
            "groupby + agg/transform is split-apply-combine.",
            "merge(how=..., validate=...) prevents silent fan-out.",
            "Vectorise; avoid iterrows and row-wise apply.",
            "Use df.loc[mask, col] = value, not chained assignment.",
        ],
        [
            ex("groupby, merge and pivot in pure Python", "basic", "The same operations pandas performs, using csv and collections.", "python", """
                import csv
                import io
                from collections import defaultdict

                orders = list(csv.DictReader(io.StringIO('''order_id,customer,month,amount
                1,c1,2026-09,120
                2,c2,2026-09,80
                3,c1,2026-10,60
                4,c3,2026-10,200
                5,c2,2026-10,40''')))
                customers = {"c1": "IN", "c2": "US", "c3": "IN"}

                # merge (many-to-one lookup)
                for o in orders:
                    o["country"] = customers[o["customer"]]
                # groupby + agg
                totals = defaultdict(float)
                for o in orders:
                    totals[o["country"]] += float(o["amount"])
                print("revenue by country:", dict(totals))
                # pivot: country x month
                pivot = defaultdict(lambda: defaultdict(float))
                for o in orders:
                    pivot[o["country"]][o["month"]] += float(o["amount"])
                months = sorted({o["month"] for o in orders})
                print("country", *months)
                for c in sorted(pivot):
                    print(c, *[pivot[c][m] for m in months])
            """),
            ex("Core pandas operations", "basic", "The idioms used every day.", "python", """
                import pandas as pd

                df = pd.read_csv("orders.csv", parse_dates=["created_at"], dtype={"country": "category"})
                big = df.loc[df["amount"] > 100, ["order_id", "customer_id", "amount"]]
                df = df.assign(month=df["created_at"].dt.to_period("M"), log_amt=lambda d: np.log1p(d["amount"]))
                kpi = df.groupby(["country", "month"], observed=True).agg(orders=("order_id", "nunique"), revenue=("amount", "sum"))
                df["share_of_customer"] = df["amount"] / df.groupby("customer_id")["amount"].transform("sum")
                full = df.merge(customers, on="customer_id", how="left", validate="many_to_one")
                wide = kpi.reset_index().pivot_table(index="country", columns="month", values="revenue", fill_value=0)
                long = wide.reset_index().melt(id_vars="country", var_name="month", value_name="revenue")
            """, False),
            ex("Time series and window operations", "intermediate", "Resample, rolling and shift.", "python", """
                daily = df.set_index("created_at")["amount"].resample("D").sum()
                out = pd.DataFrame({
                    "revenue": daily,
                    "ma7": daily.rolling(7).mean(),
                    "wow": daily.pct_change(7),
                    "prev_day": daily.shift(1),
                })
            """, False),
        ],
        ["df.loc[mask, cols] · df.iloc[0:5]", "df.groupby(k).agg(name=('col', 'sum'))", "df.groupby(k)['v'].transform('mean')", "df.merge(o, on=k, how='left', validate='m:1')", "df.pivot_table(...) · df.melt(...)"],
        ["Chained assignment may modify a copy and be silently lost.", "groupby drops NaN keys by default; pass dropna=False when they matter.", "Reading IDs as numbers strips leading zeros; set dtype=str."],
        [
            qa("basic", "What is the difference between loc and iloc?", "loc selects by labels (index labels and column names, inclusive slices); iloc selects by integer position (exclusive end like Python slices). Mixing them up is a common bug after filtering changes the index."),
            qa("intermediate", "What is the difference between groupby agg, transform and apply?", "agg reduces each group to summary values; transform returns an output the same shape as the input, aligned to original rows, useful for group-wise features; apply runs an arbitrary function per group and is flexible but slower."),
            qa("intermediate", "How do you avoid row duplication when merging?", "Check key uniqueness first and use merge(..., validate='one_to_one' or 'many_to_one'), which raises an error if the assumption is violated. Compare row counts before and after."),
            qa("advanced", "How do you speed up slow pandas code?", "Replace loops and row-wise apply with vectorised operations, use categorical dtypes, filter and select columns early, read Parquet with column pruning, avoid repeated concatenation in loops, and for larger-than-memory data move to Polars, DuckDB or Spark."),
        ],
        ["numpy-vectorisation", "sql-window-functions", "jupyter-workflow"],
        chain(
            ("Read", "csv, parquet", "Load", "Read data with explicit dtypes and dates."),
            ("Inspect", "info, describe", "Profile", "Check types, missing values and ranges.", "DataFrame"),
            ("Transform", "loc, assign", "Clean", "Filter, create columns and fix types.", "profile"),
            ("Aggregate", "groupby, merge", "Summarise", "Group, join and reshape for the question.", "clean df"),
            ("Output", "pivot, plot", "Deliver", "Export tables, charts or features.", "results"),
        ),
    ),
    topic(
        "numpy-vectorisation", "NumPy & Vectorisation", "tooling", "intermediate", "NV",
        "Operate on whole arrays at once in compiled code: broadcasting, ufuncs and boolean masks instead of Python loops.",
        "Vectorisation is like a printing press versus a calligrapher. The calligrapher writes each letter by hand (a Python loop); the press stamps the whole page in one motion.",
        "NumPy's ndarray stores elements of a single dtype in a contiguous block of memory, which lets operations run in optimised C loops instead of the Python interpreter. Vectorised expressions such as a * 2 + b apply element-wise across entire arrays via universal functions (ufuncs) and are often 10-100x faster than equivalent Python loops. Broadcasting extends operations to arrays of different shapes by virtually stretching dimensions of size one, so you can subtract a per-column mean of shape (n_cols,) from an (n_rows, n_cols) matrix without copying. Boolean masks (a[a > 0]) and np.where replace if-statements; fancy indexing selects by integer arrays. Reductions (sum, mean, std, argmax) accept an axis argument: axis=0 collapses rows to give per-column results. Slicing returns views that share memory, whereas fancy indexing returns copies, so in-place edits can surprise you. The Generator API (np.random.default_rng(seed)) is the modern, reproducible way to draw random numbers. Mind dtypes: integer overflow wraps silently, float32 loses precision, and np.std defaults to ddof=0.",
        ["Fast numerical feature computation.", "Monte Carlo simulation with millions of draws.", "Distance and similarity matrices.", "Underpinning pandas, scikit-learn and SciPy operations."],
        [
            "Arrays are homogeneous and contiguous, enabling C-speed loops.",
            "Broadcasting aligns shapes from the trailing dimension.",
            "Boolean masks and np.where replace element-wise ifs.",
            "axis=0 reduces over rows (per column); axis=1 over columns.",
            "Slices are views; fancy indexing makes copies.",
        ],
        [
            ex("Loop vs built-in vs comprehension timing", "basic", "Even in pure Python, pushing work into C (sum, map) beats explicit loops; NumPy goes further.", "python", """
                import time

                data = list(range(300_000))

                t = time.perf_counter()
                total = 0
                for v in data:
                    total += v * v
                loop = time.perf_counter() - t

                t = time.perf_counter()
                total2 = sum(v * v for v in data)
                gen = time.perf_counter() - t

                t = time.perf_counter()
                total3 = sum(map(int.__mul__, data, data))
                mapped = time.perf_counter() - t
                print(total == total2 == total3)
                print(f"loop {loop * 1000:.1f} ms, generator {gen * 1000:.1f} ms, map {mapped * 1000:.1f} ms")
            """),
            ex("Broadcasting rules, simulated", "intermediate", "Check whether two shapes broadcast and what the result shape is.", "python", """
                def broadcast(a, b):
                    out = []
                    for x, y in zip(reversed((1,) * (len(b) - len(a)) + a), reversed((1,) * (len(a) - len(b)) + b)):
                        if x != y and 1 not in (x, y):
                            return None
                        out.append(max(x, y))
                    return tuple(reversed(out))

                for a, b in [((1000, 3), (3,)), ((1000, 3), (1000, 1)), ((4, 1, 5), (3, 1)), ((1000, 3), (1000,))]:
                    print(a, "+", b, "->", broadcast(a, b) or "error: shapes do not broadcast")
            """),
            ex("Vectorised NumPy patterns", "intermediate", "Standardise columns, mask, where and a Monte Carlo estimate.", "python", """
                import numpy as np

                rng = np.random.default_rng(0)
                X = rng.normal(50, 10, size=(100_000, 3))
                Z = (X - X.mean(axis=0)) / X.std(axis=0, ddof=1)        # broadcasting over rows
                clipped = np.where(Z > 3, 3, Z)
                share_extreme = (np.abs(Z) > 3).mean()
                pts = rng.random((1_000_000, 2))
                pi_est = 4 * (np.square(pts).sum(axis=1) <= 1).mean()
                D = np.sqrt(((X[:5, None, :] - X[None, :5, :]) ** 2).sum(-1))   # 5x5 distance matrix
            """, False),
        ],
        ["np.array(x, dtype=np.float64)", "X.mean(axis=0) · X.std(axis=0, ddof=1)", "np.where(cond, a, b) · a[a > 0]", "rng = np.random.default_rng(seed)", "X[:, None, :] - X[None, :, :] (pairwise)"],
        ["Integer arrays overflow silently (int32 * int32).", "Modifying a slice modifies the original array.", "np.std uses ddof=0 by default, unlike pandas and statistics.stdev."],
        [
            qa("basic", "Why is NumPy faster than Python lists for numeric work?", "Arrays store homogeneous data contiguously, and operations run in compiled C loops without per-element interpreter overhead or type checks. Python lists store pointers to separate objects and loop in the interpreter."),
            qa("intermediate", "Explain broadcasting.", "When operating on arrays of different shapes, NumPy compares dimensions from the right; dimensions are compatible if equal or one of them is 1, and size-1 dimensions are virtually stretched. For example (1000, 3) minus (3,) subtracts a row vector from every row without copying."),
            qa("intermediate", "What does axis=0 mean in X.sum(axis=0)?", "It reduces along axis 0 (the rows), producing one value per column. axis=1 reduces along columns, producing one value per row."),
            qa("advanced", "What is the difference between a view and a copy in NumPy?", "Basic slicing returns a view that shares memory with the original, so writes propagate back. Fancy (integer array) or boolean indexing returns a new copy. Use .copy() explicitly when you need independence, and np.shares_memory to check."),
        ],
        ["pandas-essentials", "scaling-normalisation", "spark-overview"],
        chain(
            ("Python loop", "per element", "Slow path", "Each element goes through the interpreter."),
            ("ndarray", "contiguous dtype", "Layout", "Homogeneous memory enables compiled loops.", "list"),
            ("Ufunc", "element-wise C", "Vectorise", "Operations apply to whole arrays at C speed.", "array"),
            ("Broadcast", "align shapes", "Shapes", "Size-1 dims stretch to match without copying.", "arrays"),
            ("Reduce", "axis=0/1", "Summarise", "sum, mean, std along chosen axes.", "result"),
        ),
    ),
    topic(
        "jupyter-workflow", "Jupyter Notebook Workflow", "tooling", "basic", "JW",
        "Explore interactively, but keep notebooks reproducible: run top to bottom, pin environments, move reusable code into modules.",
        "A notebook is a lab bench: wonderful for experiments, but if you leave half-finished set-ups everywhere and never write down the order you did things, nobody, including future you, can repeat the result.",
        "Jupyter notebooks combine code, output, charts and narrative markdown in cells, which makes them ideal for exploration, teaching and sharing analyses. The flexibility is also the danger: cells can be run out of order, leaving hidden state where the visible code no longer produces the displayed results. Good practice is to restart the kernel and run all cells before sharing, set random seeds, put imports and parameters at the top, avoid hardcoded absolute paths, and keep notebooks short and focused. Reusable logic belongs in importable Python modules with tests; the %autoreload extension reloads them while you work. Pin dependencies with a requirements or lock file and record versions. For version control, notebooks' JSON is noisy, so strip outputs (nbstripout) or pair them with plain scripts using Jupytext, and review diffs with nbdime. Never store credentials in notebooks: read them from environment variables or a secrets manager, because outputs and history get committed and shared. Parameterised execution (papermill) turns notebooks into repeatable reports, and tools like nbconvert export to HTML or scripts.",
        ["Exploratory analysis and quick prototyping.", "Sharing an analysis with narrative and charts.", "Teaching and documenting methods.", "Scheduled parameterised reports with papermill."],
        [
            "Restart and run all before sharing.",
            "Imports, parameters and seeds at the top.",
            "Move reusable code into tested modules.",
            "Strip outputs or pair with scripts for clean diffs.",
            "Secrets come from the environment, never from cells.",
        ],
        [
            ex("A reproducible analysis cell pattern", "basic", "Parameters, seed, pure functions and assertions make a cell safe to rerun.", "python", """
                import os
                import random
                import statistics as st
                import sys

                PARAMS = {"seed": 42, "n": 1000, "segment": "trial"}
                random.seed(PARAMS["seed"])
                API_TOKEN = os.environ.get("ANALYTICS_API_TOKEN")      # never paste credentials into a notebook

                def simulate(n):
                    return [random.expovariate(1 / 12) for _ in range(n)]

                def summarise(x):
                    return {"n": len(x), "mean": round(st.fmean(x), 2), "median": round(st.median(x), 2)}

                result = summarise(simulate(PARAMS["n"]))
                assert result["n"] == PARAMS["n"], "unexpected row count"
                print("python", sys.version.split()[0], "| params", PARAMS)
                print(result)
                print("token configured:", API_TOKEN is not None)
            """),
            ex("Hidden state demonstration", "intermediate", "Running cells out of order changes results; a function avoids it.", "python", """
                # Simulates three notebook cells run as 1, 2, 2 instead of 1, 2.
                cell_state = {}

                def cell_1():
                    cell_state["prices"] = [100, 200, 300]

                def cell_2():
                    cell_state["prices"] = [p * 1.1 for p in cell_state["prices"]]   # mutates shared state

                cell_1(); cell_2(); cell_2()
                print("after accidental re-run:", [round(p, 2) for p in cell_state["prices"]])

                def with_tax(prices):
                    return [p * 1.1 for p in prices]                              # pure: safe to re-run
                base = [100, 200, 300]
                print("pure function, run twice:", with_tax(base), with_tax(base))
            """),
            ex("Notebook tooling commands", "basic", "Magics and CLI tools for a clean workflow.", "python", """
                %load_ext autoreload
                %autoreload 2
                from mypkg.features import build_features

                # terminal:
                # pip freeze > requirements.txt
                # nbstripout --install
                # jupytext --set-formats ipynb,py:percent analysis.ipynb
                # papermill report.ipynb out.ipynb -p segment trial
            """, False),
        ],
        ["Kernel -> Restart & Run All", "%load_ext autoreload · %autoreload 2", "%timeit expr · %%time", "nbstripout --install · jupytext --sync", "papermill in.ipynb out.ipynb -p key value"],
        ["Out-of-order execution produces results the visible code cannot reproduce.", "Committed outputs can leak data samples or secrets.", "Giant notebooks mixing ETL, modelling and reporting are untestable."],
        [
            qa("basic", "What is the hidden state problem in notebooks?", "Variables persist in the kernel regardless of cell order, so deleting or editing cells, or running them out of order, can leave results that the current code does not reproduce. Restart and run all to verify."),
            qa("intermediate", "How do you make a notebook reproducible?", "Pin the environment, set random seeds, keep parameters at the top, use relative paths or config, avoid manual steps, and confirm it runs top to bottom after a kernel restart. Move shared logic into tested modules."),
            qa("intermediate", "How do you version-control notebooks effectively?", "Strip outputs before committing (nbstripout), pair notebooks with plain-text scripts using Jupytext for readable diffs, and use nbdime for notebook-aware diffs and merges."),
            qa("advanced", "When should analysis move out of notebooks into a pipeline?", "When it runs on a schedule, feeds production systems or dashboards, or is reused by others. Then refactor into modules with tests, orchestrate with a scheduler, and keep notebooks for exploration and reporting."),
        ],
        ["pandas-essentials", "ds-workflow", "data-ethics-privacy"],
        chain(
            ("Setup", "env + params", "Start", "Pinned environment, imports, parameters and seeds."),
            ("Explore", "cells + notes", "Explore", "Iterate in small cells with markdown explanations.", "kernel"),
            ("Refactor", "into modules", "Harden", "Move reusable code into tested modules.", "findings"),
            ("Verify", "restart + run all", "Reproduce", "Run top to bottom on a fresh kernel.", "code"),
            ("Share", "strip / export", "Publish", "Strip outputs or export HTML; no secrets.", "notebook"),
        ),
    ),
    topic(
        "spark-overview", "Big Data Tools: Apache Spark Overview", "tooling", "advanced", "BD",
        "Distributed, lazy DataFrame processing across a cluster when data no longer fit on one machine.",
        "Spark is a head chef with many line cooks. The chef plans the whole menu first (lazy plan), splits the ingredients across stations (partitions), and only cooks when the order is actually placed (action).",
        "Apache Spark is a distributed processing engine for large-scale data. A driver program builds a plan and executors on worker nodes process partitions of the data in parallel. The DataFrame API (and Spark SQL) is the main interface; it resembles pandas and SQL, but operations are lazy: transformations such as select, filter, withColumn and join only build a logical plan, which the Catalyst optimiser rewrites (predicate pushdown, column pruning) before an action such as count, collect or write triggers execution. Narrow transformations (filter, map) work within partitions, while wide transformations (groupBy, join, distinct) require a shuffle that moves data across the network and is usually the main cost. Performance levers include reading columnar formats like Parquet or Delta with partition pruning, broadcasting small tables in joins, handling skewed keys (salting, adaptive query execution), caching reused DataFrames, and right-sizing partitions. Python UDFs are slow compared with built-in functions; pandas UDFs (vectorised via Arrow) are a middle ground. Spark also offers Structured Streaming and MLlib. For data up to tens of gigabytes, DuckDB or Polars on one machine are often simpler and faster.",
        ["Aggregating billions of event rows into daily features.", "ETL on a data lake with Parquet or Delta tables.", "Distributed joins of large customer and transaction tables.", "Streaming aggregations with Structured Streaming."],
        [
            "Transformations are lazy; actions trigger execution.",
            "Shuffles (groupBy, join) are the expensive step.",
            "Broadcast small tables; salt or use AQE for skewed keys.",
            "Prefer built-in functions over Python UDFs.",
            "Use Parquet/Delta with partition pruning.",
        ],
        [
            ex("Map-shuffle-reduce in pure Python", "intermediate", "Simulate partitions, a map step, a hash shuffle and a reduce like a groupBy count.", "python", """
                from collections import Counter, defaultdict

                events = [("u%d" % (i % 7), ["view", "click", "buy"][i % 3]) for i in range(60)]
                N_PART = 3
                partitions = [events[i::N_PART] for i in range(N_PART)]          # data spread over executors

                # map + partial aggregation inside each partition (narrow)
                partials = [Counter(action for _, action in p) for p in partitions]
                print("partial counts:", [dict(c) for c in partials])

                # shuffle: route each key to a reducer by hash (wide)
                reducers = defaultdict(Counter)
                for c in partials:
                    for key, n in c.items():
                        reducers[sum(map(ord, key)) % N_PART][key] += n
                for r in sorted(reducers):
                    print(f"reducer {r}:", dict(reducers[r]))
            """),
            ex("Lazy plan vs action", "basic", "Transformations are recorded; nothing runs until an action.", "python", """
                class LazyFrame:
                    def __init__(self, rows, plan=()):
                        self.rows, self.plan = rows, plan

                    def filter(self, fn, label):
                        return LazyFrame(self.rows, self.plan + (("filter", fn, label),))

                    def select(self, fn, label):
                        return LazyFrame(self.rows, self.plan + (("map", fn, label),))

                    def explain(self):
                        return " -> ".join(label for _, _, label in self.plan)

                    def collect(self):
                        out = self.rows
                        for kind, fn, _ in self.plan:
                            out = [r for r in out if fn(r)] if kind == "filter" else [fn(r) for r in out]
                        return out

                df = LazyFrame(list(range(20))).filter(lambda x: x % 2 == 0, "even").select(lambda x: x * 10, "times10")
                print("plan:", df.explain())
                print("collect():", df.collect())
            """),
            ex("PySpark DataFrame pipeline", "advanced", "Typical aggregation with a broadcast join and partitioned output.", "python", """
                from pyspark.sql import SparkSession, functions as F

                spark = SparkSession.builder.appName("daily-features").getOrCreate()
                events = spark.read.parquet("s3://lake/events/").where(F.col("dt") >= "2026-10-01")
                users = spark.read.parquet("s3://lake/users/")
                daily = (events.join(F.broadcast(users), "user_id")
                         .groupBy("dt", "country")
                         .agg(F.countDistinct("user_id").alias("dau"), F.sum("amount").alias("revenue")))
                daily.explain()
                daily.write.mode("overwrite").partitionBy("dt").parquet("s3://lake/daily_kpis/")
            """, False),
        ],
        ["spark.read.parquet(path).where(...)", "df.groupBy('k').agg(F.sum('v'))", "df.join(F.broadcast(small), 'k')", "df.explain() · df.cache()", "spark.conf.set('spark.sql.adaptive.enabled', 'true')"],
        ["collect() on a huge DataFrame pulls everything to the driver and crashes it.", "Skewed join keys leave one task running for hours.", "Row-wise Python UDFs serialise data and are far slower than built-ins."],
        [
            qa("basic", "What is lazy evaluation in Spark?", "Transformations only build a logical plan; nothing is computed until an action such as count, collect or write runs. This lets the Catalyst optimiser rewrite the whole plan, pushing filters down and pruning columns."),
            qa("intermediate", "What is a shuffle and why is it expensive?", "A shuffle redistributes data across partitions by key for wide operations like groupBy, join or distinct. It involves disk writes, network transfer and serialisation, so minimising and optimising shuffles is the main performance lever."),
            qa("intermediate", "When would you use a broadcast join?", "When one side of a join is small enough to fit in each executor's memory. Spark sends a copy to every executor so the large table does not need to be shuffled."),
            qa("advanced", "How do you handle data skew in a Spark join?", "Enable adaptive query execution's skew join handling, salt the hot keys by adding a random suffix and replicating the other side, broadcast the smaller side if possible, or process the hot keys separately."),
            qa("advanced", "When is Spark the wrong tool?", "When data fit comfortably on one machine (up to tens of GB), where pandas, Polars or DuckDB are simpler, cheaper and often faster. Cluster overhead, shuffles and operational complexity only pay off at larger scale."),
        ],
        ["pandas-essentials", "sql-window-functions", "numpy-vectorisation"],
        chain(
            ("Driver", "builds plan", "Plan", "Transformations build a lazy logical plan."),
            ("Optimise", "Catalyst", "Optimise", "Pushdown, pruning and join strategy selection.", "plan"),
            ("Partitions", "executors", "Parallel", "Executors process partitions independently.", "physical"),
            ("Shuffle", "by key", "Exchange", "Wide operations move data across the network.", "partials"),
            ("Action", "write / count", "Execute", "An action triggers the job and writes results.", "aggregates"),
        ),
    ),
]

SCENARIOS = [
    {"level": "intermediate", "topic": "ab-testing",
     "q": "Your A/B test shows +4% conversion with p = 0.03, but the arms received 50.8% and 49.2% of 100,000 users when the design was 50/50. What do you do?",
     "a": "Treat it as a sample ratio mismatch: a chi-square test on 50,800 vs 49,200 gives p far below 0.001, so assignment or logging is broken and the lift cannot be trusted. Investigate bot filtering, redirects, crashes in one arm or late-triggered exposure, fix it, and rerun the test rather than reporting the result."},
    {"level": "advanced", "topic": "data-leakage",
     "q": "A churn model scores 0.97 AUC offline but performs barely better than random after launch. How do you investigate?",
     "a": "Suspect leakage first: inspect top features for post-churn signals (cancellation tickets, account closed flags), check that features are computed as of the prediction date, verify the split is by time and by customer, and look for duplicates across splits. Retrain with point-in-time features and a forward-chaining validation to get an honest estimate."},
    {"level": "intermediate", "topic": "simpsons-paradox",
     "q": "Overall checkout conversion dropped from 4.0% to 3.6% month over month, yet every country's conversion went up. Leadership wants to know what broke.",
     "a": "Nothing may have broken: a marketing campaign likely shifted traffic toward low-converting countries or channels. Decompose the change into a mix effect and a rate effect, show the segment table with traffic shares, and recommend tracking a mix-adjusted conversion metric alongside the raw one."},
    {"level": "intermediate", "topic": "missing-data",
     "q": "In a salary survey 35% of respondents left income blank, mostly senior staff. A colleague fills blanks with the mean. Is that OK?",
     "a": "No. Missingness depends on seniority (MAR at best, possibly MNAR since high earners hide income), so the mean of respondents is biased low and mean imputation further shrinks variance. Impute conditionally on observed predictors such as level and tenure with multiple imputation, report sensitivity analyses, and state the assumption."},
    {"level": "advanced", "topic": "multiple-comparisons",
     "q": "An experiment is flat overall, but an analyst finds a significant lift (p = 0.02) for Android users aged 25-34 in two cities after slicing 40 segments. Should you launch to that segment?",
     "a": "Not yet. With 40 segments about two false positives are expected at alpha 0.05; after Holm or Benjamini-Hochberg correction this result is unlikely to survive. Treat it as a hypothesis, check whether the effect is plausible and consistent, and run a pre-registered confirmatory test on that segment."},
    {"level": "basic", "topic": "descriptive-stats",
     "q": "A product manager reports 'average session length is 14 minutes' to show strong engagement, but most users say sessions are short. Who is right?",
     "a": "Probably both: session length is heavily right-skewed, so a few very long sessions pull the mean up while the median may be 3-4 minutes. Report the median and p75/p90, show a histogram, and investigate whether the long sessions are idle tabs or bots."},
    {"level": "advanced", "topic": "data-ethics-privacy",
     "q": "Marketing wants to share a customer table with an agency, 'anonymised' by dropping names and emails but keeping birth date, zip code, gender and purchase history. Is this safe?",
     "a": "No. Birth date, zip code and gender are quasi-identifiers that uniquely identify most people, and purchase histories are highly distinctive. Minimise columns to what the agency needs, pseudonymise IDs with a keyed SHA-256 (HMAC) whose secret stays in your vault, generalise quasi-identifiers until k-anonymity holds, consider aggregates or differential privacy, and put a data processing agreement in place."},
    {"level": "intermediate", "topic": "type-errors-power",
     "q": "A two-week test of a new onboarding flow shows +1.5% activation with p = 0.31, and the team concludes 'it has no effect'. How do you respond?",
     "a": "A non-significant result is not proof of no effect. Compute the confidence interval and the test's power for the minimum effect the business cares about; if the interval still includes meaningful lifts, the test was underpowered. Either extend it to the sample size required for that MDE or apply variance reduction such as CUPED."},
]
