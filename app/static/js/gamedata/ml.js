export const WORDS = [
  { answer: "GRADIENT", term: "Gradient", clue: "Vector of partial derivatives that points uphill on the loss surface" },
  { answer: "EPOCH", term: "Epoch", clue: "One full pass of the training set through the model" },
  { answer: "BATCH", term: "Batch", clue: "Group of examples processed together in one optimiser step" },
  { answer: "OVERFITTING", term: "Overfitting", clue: "Memorising training noise so validation error climbs" },
  { answer: "UNDERFITTING", term: "Underfitting", clue: "Model too simple to capture the pattern, even on training data" },
  { answer: "REGULARIZATION", term: "Regularization", clue: "Penalty such as L2 that discourages overly complex models" },
  { answer: "DROPOUT", term: "Dropout", clue: "Randomly zeroing activations during training to fight overfitting" },
  { answer: "SIGMOID", term: "Sigmoid", clue: "S-shaped function mapping a logit to a probability between 0 and 1" },
  { answer: "SOFTMAX", term: "Softmax", clue: "Turns a vector of logits into probabilities that sum to 1" },
  { answer: "RELU", term: "ReLU", clue: "Activation max(0, x), the default in deep networks" },
  { answer: "LOGIT", term: "Logit", clue: "Raw, unnormalised score before sigmoid or softmax" },
  { answer: "BACKPROP", term: "Backpropagation", clue: "Chain rule applied layer by layer to get every weight's gradient" },
  { answer: "CROSSENTROPY", term: "Cross-entropy", clue: "Standard classification loss: negative log of the true class probability" },
  { answer: "LEARNINGRATE", term: "Learning rate", clue: "Step size of gradient descent; too high and the loss diverges" },
  { answer: "PRECISION", term: "Precision", clue: "Of everything predicted positive, the share that really is" },
  { answer: "RECALL", term: "Recall", clue: "Of all real positives, the share the model found" },
  { answer: "LEAKAGE", term: "Data leakage", clue: "Test or future information sneaking into training features" },
  { answer: "BIAS", term: "Bias", clue: "Error from wrong assumptions; high when a model underfits" },
  { answer: "VARIANCE", term: "Variance", clue: "Error from sensitivity to the training sample; high when a model overfits" },
  { answer: "KMEANS", term: "k-means", clue: "Clustering that alternates assigning points and moving centroids" },
  { answer: "PCA", term: "PCA", clue: "Linear projection onto the directions of largest variance" },
  { answer: "EMBEDDING", term: "Embedding", clue: "Dense vector where similar items sit close together" },
  { answer: "COSINE", term: "Cosine similarity", clue: "Angle-based closeness measure used to compare embeddings" },
  { answer: "TOKEN", term: "Token", clue: "Word piece a language model reads and writes" },
  { answer: "TOKENIZER", term: "Tokenizer", clue: "Splits text into vocabulary pieces such as BPE merges" },
  { answer: "ATTENTION", term: "Attention", clue: "Mechanism weighting other tokens by query-key similarity" },
  { answer: "TRANSFORMER", term: "Transformer", clue: "Architecture built from self-attention and feed-forward blocks" },
  { answer: "TEMPERATURE", term: "Temperature", clue: "Sampling knob: lower is more deterministic, higher more random" },
  { answer: "CONTEXTWINDOW", term: "Context window", clue: "Maximum number of tokens a model can attend to at once" },
  { answer: "HALLUCINATION", term: "Hallucination", clue: "Fluent but made-up output from a language model" },
  { answer: "FINETUNING", term: "Fine-tuning", clue: "Further training a pretrained model on task-specific data" },
  { answer: "RAG", term: "RAG", clue: "Retrieve relevant documents, then generate an answer grounded in them" },
  { answer: "AGENT", term: "Agent", clue: "LLM loop that plans, calls tools, observes results and repeats" },
  { answer: "FRONTMATTER", term: "Frontmatter", clue: "YAML block between --- lines holding a skill's name and description" },
];

export const RUSH = [
  { task: "Metric for imbalanced classes", answer: "F1 / PR-AUC", wrong: ["Accuracy", "Mean squared error", "R squared"] },
  { task: "Loss for multi-class classification", answer: "Cross-entropy", wrong: ["Mean squared error", "Mean absolute error", "Hinge loss on prices"] },
  { task: "Loss for predicting house prices", answer: "Mean squared error", wrong: ["Binary cross-entropy", "Accuracy", "Softmax"] },
  { task: "Training loss falls, validation loss rises", answer: "Overfitting: regularise or stop early", wrong: ["Underfitting: add more epochs", "Learning rate too low", "Data is perfectly clean"] },
  { task: "Train and validation error both high", answer: "Underfitting: bigger model or better features", wrong: ["Overfitting: add dropout", "Add more regularisation", "Shuffle the test set"] },
  { task: "Loss explodes to NaN after a few steps", answer: "Lower the learning rate", wrong: ["Train for more epochs", "Remove the bias term", "Increase the learning rate"] },
  { task: "Features on wildly different scales slow training", answer: "Standardise features", wrong: ["Add more layers", "Use accuracy as the loss", "Drop the test set"] },
  { task: "Turn logits into class probabilities", answer: "Softmax", wrong: ["ReLU", "Dropout", "Batch norm"] },
  { task: "Tune hyperparameters without touching the test set", answer: "Cross-validation on training data", wrong: ["Tune on the test set", "Pick the largest model", "Train on all data then score it"] },
  { task: "Reduce 100 features to 2 for a plot", answer: "PCA", wrong: ["Logistic regression", "Softmax", "One-hot encoding"] },
  { task: "Group customers when there are no labels", answer: "k-means clustering", wrong: ["Logistic regression", "Linear regression", "Precision-recall curve"] },
  { task: "Let an LLM answer from your private docs", answer: "Retrieval-augmented generation", wrong: ["Raise the temperature", "Bigger tokenizer", "Train from scratch on one PDF"] },
  { task: "Make LLM output more deterministic", answer: "Lower the temperature", wrong: ["Raise the temperature", "Longer prompt only", "Disable the tokenizer"] },
  { task: "Find semantically similar sentences", answer: "Cosine similarity of embeddings", wrong: ["Exact string match", "Token count", "Character length"] },
  { task: "Tell every coding agent the repo's test command", answer: "AGENTS.md", wrong: ["README badge", "A .gitignore entry", "A commit message"] },
  { task: "Package a reusable agent workflow with scripts", answer: "SKILL.md with frontmatter", wrong: ["One huge AGENTS.md", "A code comment", "An environment variable"] },
  { task: "Apply instructions only to Python files in Cursor", answer: "Rule with globs: **/*.py", wrong: ["alwaysApply: true", "Put it in the README", "A SKILL.md with no description"] },
  { task: "Model must not see future rows in a time series", answer: "Time-based split", wrong: ["Random shuffle split", "Train on everything", "Duplicate recent rows"] },
  { task: "Model is confident but wrong on unseen data", answer: "Collect more varied data and validate", wrong: ["Raise the learning rate", "Remove the validation set", "Report training accuracy"] },
  { task: "Why scale attention scores by sqrt(d)?", answer: "Keep softmax from saturating", wrong: ["Make weights sum to 2", "Speed up tokenization", "Remove the need for keys"] },
];

export const BUGS = [
  {
    symptom: "Test accuracy is excellent offline but drops sharply in production.",
    lang: "python",
    code: `from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)
model.fit(X_train, y_train)
print(model.score(X_test, y_test))`,
    bug: [4],
    why: "Data leakage: the scaler learns mean and variance from the test rows too. Split first, then scaler.fit_transform(X_train) and scaler.transform(X_test) (or use a Pipeline).",
  },
  {
    symptom: "A deep decision tree reports 100% accuracy, yet fails on new customers.",
    lang: "python",
    code: `from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score

model = DecisionTreeClassifier()
model.fit(X, y)
preds = model.predict(X)
print("accuracy", accuracy_score(y, preds))`,
    bug: [5, 6],
    why: "There is no train/test split: the model is scored on the same rows it memorised. Hold out data with train_test_split (or cross-validation) and evaluate on that.",
  },
  {
    symptom: "softmax returns [nan nan] for large logits.",
    lang: "python",
    code: `import numpy as np

def softmax(z):
    e = np.exp(z)
    return e / e.sum()

print(softmax(np.array([1000.0, 1001.0])))`,
    bug: [3],
    why: "np.exp(1000) overflows to inf and inf / inf is nan. Subtract the max first: e = np.exp(z - z.max()). The result is mathematically identical.",
  },
  {
    symptom: "The agent never loads this skill, even when the user asks about PDFs.",
    lang: "markdown",
    code: `---
name: pdf-tools
---

# PDF tools

1. Extract text with scripts/extract.py.
2. Fill forms with scripts/fill.py.`,
    bug: [0, 1, 2],
    why: "The frontmatter has no description, and the description is what the agent matches against. Add one that says what it does and when: \"Extracts text and fills forms in PDFs. Use when the user mentions PDFs or forms.\"",
  },
  {
    symptom: "Churn model scores 0.99 AUC in validation but is useless before customers leave.",
    lang: "python",
    code: `import pandas as pd

df = pd.read_csv("customers.csv")
features = ["tenure", "monthly_spend", "support_calls", "cancellation_date_set"]
X = df[features]
y = df["churned"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
model.fit(X_train, y_train)`,
    bug: [3],
    why: "Target leakage: cancellation_date_set is only filled in once a customer has churned, so it encodes the label. Use only features known at prediction time.",
  },
  {
    symptom: "The fraud model has 99.5% accuracy but catches no fraud at all.",
    lang: "python",
    code: `from sklearn.metrics import accuracy_score

print(y_test.mean())   # 0.005 -> 0.5% fraud
y_pred = model.predict(X_test)
print("accuracy", accuracy_score(y_test, y_pred))
deploy(model)`,
    bug: [4],
    why: "With 0.5% positives, predicting \"not fraud\" every time scores 99.5% accuracy. Judge imbalanced problems with precision, recall, F1 or PR-AUC (and a confusion matrix).",
  },
  {
    symptom: "Loss jumps around and blows up, even with a small learning rate.",
    lang: "python",
    code: `for epoch in range(10):
    for xb, yb in loader:
        pred = model(xb)
        loss = loss_fn(pred, yb)
        loss.backward()
        optimizer.step()`,
    bug: [4],
    why: "PyTorch accumulates gradients across backward() calls. Call optimizer.zero_grad() before loss.backward() in every iteration.",
  },
  {
    symptom: "The coding agent keeps running npm test in a Python repository.",
    lang: "markdown",
    code: `# AGENTS.md

## Project overview
Flask API with a SQLite database.

## Tests
Run the tests before you finish.

## Boundaries
- Never edit files in migrations/.`,
    bug: [6],
    why: "\"Run the tests\" is vague, so the agent guesses. Give the exact command in a code block, for example .venv/bin/python -m pytest -q.",
  },
];

export const META = {
  rushLabel: "AI Rush",
  rushIntro: "Pick the right ML or agent-engineering move for each situation.",
  rushMono: false,
  bugLabel: "ML Bug Hunt",
  bugNoun: "symptom",
};
