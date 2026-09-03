# Ubiquitous Language

Derived from `ONTOLOGY.md` (order-capture, mode: greenfield, status: settled 16 · deferred 1 · unknown 1) — regenerated, never hand-edited.

## Order capture

| Term | Definition | Aliases to avoid |
|------|-----------|-----------------|
| **Customer** | The billing party that places zero or more orders, identified by the `customer_number` issued by the CRM. | account |
| **Order** | One customer's request, containing one or more order lines, identified by its `order_number`. | pick list |
| **OrderLine** | A single product requested within one order, identified by `(Order, line_no)`. | line, shipment line |
| **Product** | A catalogue item that an order line refers to, identified by its `sku`. | — |
| **Return** | *(deferred — re-enters when returns enter scope)* Insufficient information to define: no reference scheme is settled and no fact type mentions it this release. | — |

## Relationships

- A **Customer** places zero or more **Orders** (mandatory: Order→Customer; unique: Order.order_number)
- An **Order** contains one or more **OrderLines** (mandatory: OrderLine→Order; unique: (Order, line_no))
- An **OrderLine** refers to exactly one **Product** (mandatory: OrderLine→Product)
- An **Order** must not be dispatched before its payment clears — deontic, so this is a validation rule guarding Paid→Shipped, not a structural constraint
- *(unknown)* A **Customer** holds open **Orders** — the frequency is `[unconstrained]`; how many open orders one customer may hold is undecided, so assume no cardinality
- *(deferred)* **Return** has no fact types this release

## Example dialogue

> **Dev:** "When a **Customer** places an **Order**, is the **Order** already payable?"
> **Domain expert:** "It is a Draft until it is submitted. Submitting makes it Placed, and only a Placed order can take payment."

> **Dev:** "Can I dispatch a Placed **Order** if the warehouse has stock?"
> **Domain expert:** "No — dispatch is only legal from Paid. 'Must not dispatch before payment clears' is a rule we enforce, not something the schema makes impossible."

> **Dev:** "The support ticket says 'the customer's account is locked'. Is that a **Customer**?"
> **Domain expert:** "No. **Customer** is the billing party. Login is a separate identity we are not modelling this release — don't call either one 'account'."

> **Dev:** "If someone orders the same **Product** twice, is that one **OrderLine** or two?"
> **Domain expert:** "Two **OrderLines**. Each one refers to exactly one **Product**, and they are told apart by their `line_no` within the **Order**."

## Flagged ambiguities

- "account" was used for both the billing party and the authentication identity — resolved: use **Customer** for the billing party; the authentication identity (`LoginIdentity`) is out of the UoD this release, so do not name it here.
- "order" was used for both the customer's request and the warehouse pick list — resolved: **Order** is the customer's request only.
- "line" was used for both an order line and a shipment line — resolved: **OrderLine** is the order line; the ontology has no shipment line this release.
- *(unknown)* How many open **Orders** one **Customer** may hold is undecided — credit control has not ruled on concurrent open orders. No recommendation; settle it in `/prd-create` before any code assumes a limit.
