export const WORDS = [
  { answer: "MEAN", term: "Mean", clue: "Sum divided by count; easily pulled around by outliers" },
  { answer: "MEDIAN", term: "Median", clue: "Middle value of the sorted data; resistant to outliers" },
  { answer: "MODE", term: "Mode", clue: "Most frequent value in a dataset" },
  { answer: "VARIANCE", term: "Variance", clue: "Average squared distance from the mean" },
  { answer: "STDDEV", term: "Standard deviation", clue: "Square root of the variance, in the data's own units" },
  { answer: "QUARTILE", term: "Quartile", clue: "Cut point splitting sorted data into four equal parts" },
  { answer: "PERCENTILE", term: "Percentile", clue: "Value below which a given share of observations fall" },
  { answer: "IQR", term: "IQR", clue: "Q3 minus Q1: the spread of the middle half of the data" },
  { answer: "OUTLIER", term: "Outlier", clue: "Point far from the rest, e.g. beyond 1.5 IQR outside the box" },
  { answer: "SKEW", term: "Skew", clue: "Asymmetry where one tail of a distribution is longer" },
  { answer: "HISTOGRAM", term: "Histogram", clue: "Bar chart of counts per bin of a numeric variable" },
  { answer: "BOXPLOT", term: "Box plot", clue: "Chart of median, quartiles, whiskers and outliers" },
  { answer: "CORRELATION", term: "Correlation", clue: "Strength of association between two variables, from -1 to +1" },
  { answer: "PEARSON", term: "Pearson r", clue: "Correlation coefficient measuring straight-line association" },
  { answer: "SPEARMAN", term: "Spearman rho", clue: "Rank-based correlation that captures any monotonic trend" },
  { answer: "REGRESSION", term: "Regression", clue: "Modelling a target as a function of one or more predictors" },
  { answer: "RESIDUAL", term: "Residual", clue: "Observed value minus the model's predicted value" },
  { answer: "HYPOTHESIS", term: "Null hypothesis", clue: "Default claim, such as 'no difference', that a test tries to reject" },
  { answer: "PVALUE", term: "p-value", clue: "Chance of data at least this extreme if the null hypothesis were true" },
  { answer: "ALPHA", term: "Alpha", clue: "Significance threshold chosen before the test, commonly 0.05" },
  { answer: "POWER", term: "Statistical power", clue: "Probability that a test detects an effect that really exists" },
  { answer: "CONFIDENCE", term: "Confidence interval", clue: "Range of plausible values for a parameter, e.g. at the 95% level" },
  { answer: "SAMPLE", term: "Sample", clue: "The subset of a population that you actually measure" },
  { answer: "POPULATION", term: "Population", clue: "The whole group you want to draw conclusions about" },
  { answer: "BIAS", term: "Bias", clue: "Systematic error that pushes estimates consistently one way" },
  { answer: "BOOTSTRAP", term: "Bootstrap", clue: "Resampling the data with replacement to estimate uncertainty" },
  { answer: "NORMAL", term: "Normal distribution", clue: "Bell-shaped distribution fully described by mean and std dev" },
  { answer: "ZSCORE", term: "z-score", clue: "How many standard deviations a value sits from the mean" },
  { answer: "CONFOUNDER", term: "Confounder", clue: "Hidden variable that influences both the supposed cause and effect" },
  { answer: "SIMPSON", term: "Simpson's paradox", clue: "A trend that reverses when separate groups are combined" },
  { answer: "IMPUTATION", term: "Imputation", clue: "Filling in missing values with estimates such as the median" },
  { answer: "LEAKAGE", term: "Data leakage", clue: "Test-set or future information sneaking into model training" },
  { answer: "TIDY", term: "Tidy data", clue: "One variable per column, one observation per row" },
  { answer: "GROUPBY", term: "Group by", clue: "Split-apply-combine: aggregate the rows that share a key" },
];

export const RUSH = [
  { task: "Resistant to outliers: mean or median?", answer: "Median", wrong: ["Mean", "Standard deviation", "Range"] },
  { task: "Right-skewed data with a long high tail: mean vs median?", answer: "Mean is above the median", wrong: ["Mean is below the median", "They are always equal", "They cannot be compared"] },
  { task: "Spread measure in the same units as the data", answer: "Standard deviation", wrong: ["Variance", "Correlation", "p-value"] },
  { task: "The 1.5 IQR rule flags points that are...", answer: "More than 1.5 IQR beyond Q1 or Q3", wrong: ["More than 1.5 from the mean", "Above the median", "In the top 1.5%"] },
  { task: "r = -0.9 means...", answer: "Strong negative linear relationship", wrong: ["Weak relationship", "x causes 90% of y", "No relationship"] },
  { task: "Curved but always increasing relationship: best correlation", answer: "Spearman rho", wrong: ["Pearson r", "Covariance", "Difference of means"] },
  { task: "p = 0.03 with alpha = 0.05", answer: "Reject the null hypothesis", wrong: ["The alternative is proven", "The effect is large", "3% chance the null is true"] },
  { task: "What does a p-value measure?", answer: "How surprising the data is if the null is true", wrong: ["Probability the null is true", "Size of the effect", "Chance the result replicates"] },
  { task: "95% CI for B minus A is -0.4 to +1.2 pp", answer: "Not significant at the 5% level", wrong: ["B is definitely better", "A is definitely better", "The test is invalid"] },
  { task: "You want to detect a smaller effect. Sample size must...", answer: "Increase", wrong: ["Decrease", "Stay the same", "Halve"] },
  { task: "Checking daily and stopping at the first p < 0.05", answer: "Inflates false positives", wrong: ["Safely saves time", "Reduces bias", "Has no effect"] },
  { task: "Central limit theorem: means of large samples are roughly...", answer: "Normally distributed", wrong: ["Uniformly distributed", "Shaped like the population", "Always skewed"] },
  { task: "Standard error of the mean shrinks with sample size as...", answer: "1 / sqrt(n)", wrong: ["1 / n", "n", "log(n)"] },
  { task: "Sample standard deviation divides the squared deviations by...", answer: "n - 1", wrong: ["n", "n + 1", "sqrt(n)"] },
  { task: "Fit the scaler or imputer on...", answer: "The training split only", wrong: ["The full dataset", "The test split only", "Train plus test"] },
  { task: "Ice cream sales correlate with drownings. Most likely?", answer: "A confounder: hot weather", wrong: ["Ice cream causes drowning", "Drowning drives sales", "Pure coincidence every year"] },
  { task: "A trend reverses when groups are pooled", answer: "Simpson's paradox", wrong: ["Regression to the mean", "Central limit theorem", "Overfitting"] },
  { task: "Fill missing values in a skewed numeric column", answer: "Median imputation", wrong: ["Mean imputation", "Fill with zero", "Fill with the maximum"] },
  { task: "Simple linear fit has R squared = 0.64, so r is...", answer: "0.8 or -0.8", wrong: ["0.64", "0.32", "0.41"] },
  { task: "A type I error is...", answer: "A false positive", wrong: ["A false negative", "A rounding error", "A missing value"] },
];

export const BUGS = [
  {
    symptom: "Test accuracy looks excellent offline but drops in production.",
    lang: "python",
    code: `from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))`,
    bug: [4],
    why: "The scaler learns its mean and std from every row, including the test rows, so test information leaks into training. Split first, fit the scaler on X_train only, then transform X_test with it (or use a Pipeline).",
  },
  {
    symptom: "Both variants show a conversion rate about half of what the dashboard reports.",
    lang: "python",
    code: `visitors = {"A": 5000, "B": 4800}
signups = {"A": 250, "B": 264}
total = sum(visitors.values())

for v in ("A", "B"):
    rate = signups[v] / total
    print(v, f"{rate:.2%}")`,
    bug: [5],
    why: "Each variant's signups are divided by the visitors of both variants combined. The denominator must be that variant's own visitors: signups[v] / visitors[v].",
  },
  {
    symptom: "Click-through rate always prints 0.00%.",
    lang: "python",
    code: `clicks = 37
views = 1200
ctr = clicks // views
print(f"CTR: {ctr:.2%}")`,
    bug: [2],
    why: "// is floor division, so 37 // 1200 is 0. Use true division: clicks / views.",
  },
  {
    symptom: "The estimated spread of the whole batch is consistently a little too small.",
    lang: "python",
    code: `import statistics

sample = [12.1, 11.8, 12.6, 12.0, 11.7]   # 5 bolts from a batch of 10,000
spread = statistics.pstdev(sample)
print(f"estimated batch std dev: {spread:.3f}")`,
    bug: [3],
    why: "pstdev divides by n and treats the five bolts as the entire population. To estimate the batch from a sample use statistics.stdev, which divides by n - 1.",
  },
  {
    symptom: "Average order value is inflated by a tiny store with a few big orders.",
    lang: "python",
    code: `stores = [("North", 120, 3600.0), ("South", 15, 900.0), ("East", 80, 2000.0)]
# (name, orders, revenue)
avgs = [revenue / orders for _, orders, revenue in stores]
overall = sum(avgs) / len(avgs)
print(f"average order value: {overall:.2f}")`,
    bug: [3],
    why: "Averaging the per-store averages gives the 15-order store as much weight as the 120-order store. Divide total revenue by total orders instead.",
  },
  {
    symptom: "The average rating drops every time a customer skips the question.",
    lang: "python",
    code: `ratings = ["5", "4", "", "3", "", "5"]
nums = [int(r) if r else 0 for r in ratings]
print(sum(nums) / len(nums))`,
    bug: [1],
    why: "Blank answers become 0, a real (terrible) rating. Missing is not zero: drop them with [int(r) for r in ratings if r] and report how many were missing.",
  },
  {
    symptom: "The sales forecast scored well in testing but fails on next month's data.",
    lang: "python",
    code: `import random

rows.sort(key=lambda r: r["date"])
random.shuffle(rows)
cut = int(len(rows) * 0.8)
train, test = rows[:cut], rows[cut:]
model.fit(features(train), target(train))`,
    bug: [3],
    why: "Shuffling a time series lets the model train on days after the ones it is tested on. Keep the sorted order and split by time so the test set is strictly in the future.",
  },
  {
    symptom: "The hand-written median returns 9 for [7, 1, 9, 3, 5].",
    lang: "python",
    code: `def median(xs):
    mid = len(xs) // 2
    if len(xs) % 2:
        return xs[mid]
    return (xs[mid - 1] + xs[mid]) / 2

print(median([7, 1, 9, 3, 5]))`,
    bug: [3, 4],
    why: "The median is the middle of the sorted values, but the function indexes the list in its original order. Sort first: xs = sorted(xs).",
  },
];

export const META = {
  rushLabel: "Stats Rush",
  rushIntro: "Pick the statistically sound answer.",
  rushMono: false,
  bugLabel: "Analysis Bug Hunt",
  bugNoun: "symptom",
};
