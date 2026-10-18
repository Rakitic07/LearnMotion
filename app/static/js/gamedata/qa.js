export const WORDS = [
  { answer: "ASSERTION", term: "Assertion", clue: "Check that fails the test when an expectation does not hold" },
  { answer: "FIXTURE", term: "Fixture", clue: "Known setup state (objects, data) that a test runs against" },
  { answer: "SETUP", term: "setUp", clue: "unittest hook that runs before every test method" },
  { answer: "TEARDOWN", term: "tearDown", clue: "Hook that cleans up after each test, even after a failure" },
  { answer: "MOCK", term: "Mock", clue: "Test double you program and then verify how it was called" },
  { answer: "STUB", term: "Stub", clue: "Test double that returns canned answers and verifies nothing" },
  { answer: "SPY", term: "Spy", clue: "Wraps a real object and records how it was called" },
  { answer: "FAKE", term: "Fake", clue: "Working but simplified implementation, like an in-memory database" },
  { answer: "DUMMY", term: "Dummy", clue: "Placeholder object passed only to fill a parameter list" },
  { answer: "PATCH", term: "mock.patch", clue: "Temporarily replaces a name where the code under test looks it up" },
  { answer: "COVERAGE", term: "Code coverage", clue: "Share of the code that the test suite executes" },
  { answer: "BRANCH", term: "Branch coverage", clue: "Coverage that needs every decision seen both true and false" },
  { answer: "MUTANT", term: "Mutant", clue: "Copy of the code with one small deliberate change" },
  { answer: "MUTATION", term: "Mutation testing", clue: "Rates a suite by how many injected faults it detects" },
  { answer: "BOUNDARY", term: "Boundary value analysis", clue: "Testing exactly at and just around the edges of input ranges" },
  { answer: "PARTITION", term: "Equivalence partitioning", clue: "Splitting inputs into classes expected to behave the same" },
  { answer: "REGRESSION", term: "Regression", clue: "Something that used to work breaks again after a change" },
  { answer: "SMOKE", term: "Smoke test", clue: "Quick shallow check that the build basically works" },
  { answer: "SANITY", term: "Sanity test", clue: "Narrow check that one specific fix or feature works" },
  { answer: "INTEGRATION", term: "Integration test", clue: "Checks that several components work together" },
  { answer: "UNIT", term: "Unit test", clue: "Fast test of one small piece of code in isolation" },
  { answer: "ENDTOEND", term: "End-to-end test", clue: "Exercises the whole system through its real interface" },
  { answer: "ACCEPTANCE", term: "Acceptance test", clue: "Confirms the software meets the business requirements" },
  { answer: "FLAKY", term: "Flaky test", clue: "Test that passes or fails without any code change" },
  { answer: "ORACLE", term: "Test oracle", clue: "Source of truth that decides what the expected result is" },
  { answer: "TDD", term: "TDD", clue: "Write a failing test first, then just enough code to pass it" },
  { answer: "BDD", term: "BDD", clue: "Given-When-Then style that describes behaviour in plain language" },
  { answer: "PYTEST", term: "pytest", clue: "Popular Python test runner with plain assert and fixtures" },
  { answer: "SUBTEST", term: "subTest", clue: "unittest context manager that reports each failing case separately" },
  { answer: "EDGECASE", term: "Edge case", clue: "Input at an extreme of what is allowed" },
  { answer: "PYRAMID", term: "Test pyramid", clue: "Many unit tests, fewer integration tests, few end-to-end tests" },
  { answer: "SEED", term: "Random seed", clue: "Fixed starting value that makes random numbers repeatable" },
  { answer: "BLACKBOX", term: "Black-box testing", clue: "Designing tests from the spec without looking at the code" },
  { answer: "FUZZING", term: "Fuzzing", clue: "Feeding random or malformed input to find crashes" },
];

export const RUSH = [
  { task: "Replace a dependency with one you program, then assert how it was called", answer: "Mock", wrong: ["Stub", "Dummy", "Fixture"] },
  { task: "Wrap the real object so it still works but records every call", answer: "Spy", wrong: ["Stub", "Dummy", "Fake"] },
  { task: "Return a canned answer and check nothing", answer: "Stub", wrong: ["Mock", "Spy", "Oracle"] },
  { task: "Use an in-memory database instead of the real one", answer: "Fake", wrong: ["Stub", "Dummy", "Spy"] },
  { task: "Test at 0, 1, the maximum and the maximum + 1", answer: "Boundary value analysis", wrong: ["Equivalence partitioning", "Smoke testing", "Fuzzing"] },
  { task: "Pick one representative input from each class of similar inputs", answer: "Equivalence partitioning", wrong: ["Boundary value analysis", "Mutation testing", "Regression testing"] },
  { task: "After a deploy, check that the app starts and the home page loads", answer: "Smoke test", wrong: ["Regression test", "Load test", "Unit test"] },
  { task: "Re-run existing tests to make sure old features still work after a change", answer: "Regression testing", wrong: ["Exploratory testing", "Smoke testing", "Fuzzing"] },
  { task: "Measure how many injected bugs your suite catches", answer: "Mutation score", wrong: ["Line coverage", "Branch coverage", "Pass rate"] },
  { task: "Every if must be seen both true and false", answer: "Branch coverage", wrong: ["Line coverage", "Function coverage", "Mutation score"] },
  { task: "Write a failing test, make it pass, then refactor", answer: "TDD: red, green, refactor", wrong: ["BDD", "Waterfall", "Exploratory testing"] },
  { task: "A test passes on retry without any code change", answer: "Flaky test", wrong: ["Smoke test", "Golden test", "Pending test"] },
  { task: "Make a test that uses random numbers repeatable", answer: "Fix the random seed", wrong: ["Retry until green", "Raise the timeout", "Mark it skipped"] },
  { task: "Test a function that reads the current date", answer: "Inject or patch the clock", wrong: ["Run the suite at midnight", "Sleep until the right day", "Compare with datetime.now()"] },
  { task: "Run one test body over many inputs in unittest", answer: "with self.subTest(...)", wrong: ["self.loop(...)", "@unittest.repeat", "self.assertMany(...)"] },
  { task: "Check that a call raises ValueError", answer: "with self.assertRaises(ValueError):", wrong: ["self.assertTrue(ValueError)", "try: ... except: pass", "self.assertEqual(f(), ValueError)"] },
  { task: "shop.py does 'from rates import get_rate'. What do you patch?", answer: "shop.get_rate", wrong: ["rates.get_rate", "get_rate", "builtins.get_rate"] },
  { task: "Expensive setup shared once by all tests in a class", answer: "setUpClass", wrong: ["setUp", "__init__", "tearDown"] },
  { task: "Verify a mock was called exactly once with given arguments", answer: "assert_called_once_with(...)", wrong: ["mock.called == 1", "assert_called()", "was_called_with(...)"] },
  { task: "Design tests from the spec without seeing the code", answer: "Black-box testing", wrong: ["White-box testing", "Static analysis", "Code review"] },
];

export const BUGS = [
  {
    symptom: "The suite is green, yet a 10% discount turns 100 into 110.",
    lang: "python",
    code: `import unittest

def apply_discount(price, pct):
    return price * (1 + pct / 100)

class DiscountTest(unittest.TestCase):
    def test_ten_percent(self):
        result = apply_discount(100, 10)
        result == 90`,
    bug: [8],
    why: "result == 90 is a bare comparison: its value is thrown away and nothing is asserted, so the test can never fail. Use self.assertEqual(result, 90).",
  },
  {
    symptom: "test_starts_empty passes on its own but fails when the whole class runs.",
    lang: "python",
    code: `import unittest

class CartTest(unittest.TestCase):
    items = []

    def test_add(self):
        self.items.append("apple")
        self.assertEqual(len(self.items), 1)

    def test_starts_empty(self):
        self.assertEqual(self.items, [])`,
    bug: [3],
    why: "items is a class attribute, so every test shares one list and test_add (which runs first, alphabetically) leaks into test_starts_empty. Create the list in setUp so each test is isolated and order does not matter.",
  },
  {
    symptom: "Customers who are exactly 18 are rejected, but the age tests are green.",
    lang: "python",
    code: `import unittest

def is_adult(age):
    return age > 18

class AgeTest(unittest.TestCase):
    def test_adult(self):
        self.assertTrue(is_adult(19))

    def test_minor(self):
        self.assertFalse(is_adult(17))`,
    bug: [3, 7],
    why: "The tests skip the boundary. 19 and 17 behave the same under > and >=, so the off-by-one in age > 18 survives. Test exactly 18 (and 17) and fix the comparison to >=.",
  },
  {
    symptom: "The test calls the real rates API and fails when the build machine is offline.",
    lang: "python",
    code: `# shop.py
from rates import get_rate

def to_eur(usd):
    return round(usd * get_rate("EUR"), 2)

# test_shop.py
import unittest
from unittest.mock import patch
import shop

class ShopTest(unittest.TestCase):
    @patch("rates.get_rate", return_value=0.5)
    def test_to_eur(self, fake_rate):
        self.assertEqual(shop.to_eur(10), 5.0)`,
    bug: [12],
    why: "shop imported get_rate by name, so shop.get_rate still points at the real function. Patch where the name is looked up: patch(\"shop.get_rate\").",
  },
  {
    symptom: "Every January the build turns red without any code change.",
    lang: "python",
    code: `import unittest
from datetime import date

def greeting():
    return "Happy New Year" if date.today().month == 1 else "Hello"

class GreetingTest(unittest.TestCase):
    def test_greeting(self):
        self.assertEqual(greeting(), "Hello")`,
    bug: [8],
    why: "The assertion depends on the real calendar. Pass today in as a parameter (or patch the clock) and test both January and another month explicitly.",
  },
  {
    symptom: "The order total is 25, but the test that expects 30 still passes.",
    lang: "python",
    code: `import unittest

def order_total(prices):
    return sum(prices[1:])

class TotalTest(unittest.TestCase):
    def test_total(self):
        total = order_total([5, 10, 15])
        self.assertTrue(total, 30)`,
    bug: [8],
    why: "assertTrue(x, msg) only checks that x is truthy; 30 is treated as the failure message. Use assertEqual(total, 30), which also exposes the slicing bug.",
  },
  {
    symptom: "withdraw(-5) silently succeeds, yet test_rejects_negative is green.",
    lang: "python",
    code: `import unittest

class AccountTest(unittest.TestCase):
    def test_rejects_negative(self):
        account = Account(10)
        try:
            account.withdraw(-5)
        except ValueError:
            pass`,
    bug: [5, 7, 8],
    why: "If no exception is raised the try block just finishes and the test passes. Use with self.assertRaises(ValueError): so a missing exception is a failure.",
  },
  {
    symptom: "CI fails roughly once in 52 runs; pressing re-run makes it green.",
    lang: "python",
    code: `import random
import unittest

def shuffled_deck():
    deck = list(range(52))
    random.shuffle(deck)
    return deck

class DeckTest(unittest.TestCase):
    def test_is_shuffled(self):
        self.assertNotEqual(shuffled_deck()[0], 0)`,
    bug: [10],
    why: "The assertion relies on unseeded randomness: card 0 lands on top 1 time in 52. Seed the generator (or inject it) and assert a property that always holds, such as sorted(deck) == list(range(52)).",
  },
];

export const META = {
  rushLabel: "QA Rush",
  rushIntro: "Pick the testing technique, test double or unittest call that fits.",
  rushMono: false,
  bugLabel: "Test Bug Hunt",
  bugNoun: "symptom",
};
