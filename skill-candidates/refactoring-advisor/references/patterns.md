# Refactoring Advisor — Patterns

---

## Characterization Tests

**When**: Inheriting code without tests. Write before touching a single line.

```python
# Step 1: Call the code, observe output
def test_calculate_discount_characterization():
    result = calculate_discount(100, "SUMMER")
    assert result == 15  # Whatever it actually returned

# Step 2: Add edge cases until you trust the net
    assert calculate_discount(100, "WINTER") == 10
    assert calculate_discount(100, "INVALID") == 0
    assert calculate_discount(-50, "SUMMER") == 0  # found an edge case!

# These tests capture WHAT the code does, not what it SHOULD do.
# Bugs are preserved intentionally — fix them separately after refactoring.
```

---

## Safe Refactoring Cycle

**When**: Any refactoring, any size. No exceptions.

```
1. Tests pass? ✓ — commit checkpoint
2. Make ONE small change
3. Run tests
4. Fail → undo immediately (do not debug, do not push through)
5. Pass → commit ("Extract validate_order from process_order")
6. Repeat
```

Each commit is independently revertable. If a step feels too big to undo easily, it's too big.

---

## Strangler Fig

**When**: Replacing a legacy module or system — never big-bang.

```python
class OrderProcessor:
    def process(self, order):
        # Phase 1: 100% legacy
        return self.legacy.process(order)

    # Phase 2: route low-risk traffic to new system
    def use_new_processor(self, order):
        return order.total < 100 and random.random() < 0.01

    # Phase 3: expand coverage, Phase 4: flip to 100%, Phase 5: delete legacy
```

Each phase is independently deployable and reversible. Old system runs throughout.

---

## Parallel Change (Expand and Contract)

**When**: Changing an interface without breaking callers.

```python
# Phase 1: Expand — add new signature alongside old
class UserService:
    def get_user(self, user_id: int) -> User: ...       # old, still works
    def get_user_by_uuid(self, uuid: str) -> User: ...  # new

# Phase 2: Migrate callers one by one
# Phase 3: Contract — remove old when no callers remain
```

Never break callers. Migration can be gradual. Rollback is trivial at any phase.

---

## Extract Till You Drop

**When**: Long method doing too much.

```python
# Before: 50-line method handling everything
# After: composed method, each extraction independently testable

def process_payment(order, card):
    validate_card(card)
    check_for_fraud(order, card)
    fees = calculate_processing_fees(order)
    charge_result = charge_card(card, order.total + fees)
    record_payment(order, charge_result)

# Stop when: function does one thing, you can't name an extraction well,
# or extraction would make understanding harder.
```

---

## Mikado Method

**When**: Refactoring that keeps revealing more changes needed.

```
Goal: Rename User.name → User.fullName

Try the change → 200 files break → revert

Draw the graph:
  [Rename User.name] (GOAL)
    ├── [Update UserSerializer] (broke)
    ├── [Update UserForm] (broke)
    └── [Update 15 templates] (broke)

Pick a leaf → try it → commit if it works → mark done
Work leaves to root. Each leaf is a small, committed PR.
```

Keeps scope visible. Work on independent branches in parallel.

---

## Seam Identification

**When**: Untestable legacy code with hardcoded dependencies.

```python
# A "seam" is where you can change behavior without editing the code there.

# Object Seam (inject dependency):
class ReportGenerator:
    def __init__(self, database=None):
        self.database = database or Database()  # mockable in tests

# Preprocessing Seam (override in test subclass):
class ReportGenerator:
    def get_database(self): return Database()  # override in TestableReportGenerator

# Look for seam candidates: imports, new X(), global calls, static methods.
```

---

## Code Smell Taxonomy

Smells are symptoms, not diagnoses. Refactor when a smell causes actual pain.

| Smell | Symptom | When It Matters |
|---|---|---|
| Long Method (50+ lines) | Hard to understand, test | Actively changing it |
| God Class | Attracts every change | Blocks team velocity |
| Feature Envy | Method uses another class's data more than its own | Causes coupling bugs |
| Data Clump | Same 3+ fields appear together everywhere | Needs to change together |
| Primitive Obsession | `userId: string` instead of branded type | Type confusion causes bugs |
| Refused Bequest | Subclass throws NotImplemented | Inheritance is wrong |
| Shotgun Surgery | One change → edits in many files | Causes missed changes |

**Don't refactor just because something smells. Refactor when the smell is costing you.**
