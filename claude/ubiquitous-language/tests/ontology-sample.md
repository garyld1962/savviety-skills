# Ontology: order-capture
mode: greenfield
extends: none
scope: Customer, Order, OrderLine, Product
uod: Representable: orders placed by one customer against catalogue products, and the state of those orders through to delivery. Not representable this release: returns, partial shipments, multi-currency pricing, customer merges.
seeded-from-code: n/a (greenfield)
thesis: Capture an order against the catalogue and track it to delivery.
status: settled 16 · deferred 1 · unknown 1 · mandatory core: complete

## Entity Types

| Entity | Reference scheme | Homonym resolution | Status | Source |
|---|---|---|---|---|
| **Customer** | `customer_number`, issued by the CRM | "account" means the billing party here; the authentication identity is `LoginIdentity`, out of the UoD this release | settled | interview |
| **Order** | `order_number` | "order" is the customer's request, never the warehouse pick list | settled | interview |
| **OrderLine** | `(Order, line_no)` | "line" means an order line, never a shipment line | settled | interview |
| **Product** | `sku` | none | settled | interview |
| **Return** | [deferred] | none | deferred | interview |

## Fact Types

| # | Verbalized fact type | Constraints | Modality | Status | Source |
|---|---|---|---|---|---|
| F1 | A **Customer** places zero or more **Orders** | mandatory: Order→Customer; unique: Order.order_number | alethic | settled | interview |
| F2 | An **Order** contains one or more **OrderLines** | mandatory: OrderLine→Order; unique: (Order, line_no) | alethic | settled | interview |
| F3 | An **OrderLine** refers to exactly one **Product** | mandatory: OrderLine→Product | alethic | settled | interview |
| F4 | An **Order** must not be dispatched before its payment clears | guard on Paid→Shipped | deontic | settled | interview |
| F5 | A **Customer** holds open **Orders** | [unconstrained] — frequency not decided | alethic | unknown | interview |

## Lifecycles

### Order — Total: yes

| From | Event | To | Guard | Status |
|---|---|---|---|---|
| Draft | submit | Placed | every OrderLine refers to a Product | settled |
| Placed | payment clears | Paid | — | settled |
| Placed | cancel | Cancelled | — | settled |
| Paid | dispatch | Shipped | payment cleared (F4) | settled |
| Shipped | delivery confirmed | Delivered | — | settled |

Terminal: Delivered, Cancelled

## Temporality

| Fact / attribute | Instant or interval | Correction vs supersession distinguishable | Status |
|---|---|---|---|
| Product.price | instant (point-in-time); historisation out of scope this release | no | settled |
| Order.placed_at | instant | n/a | settled |
| OrderLine.quantity | instant; last write wins | no | settled |

## Deferred (with re-entry condition)

| Item | Category | Re-entry condition |
|---|---|---|
| Return entity, its reference scheme and its fact types | Entity types | When returns enter scope |

## Unknown

| Item | Category | Why unknown |
|---|---|---|
| Frequency constraint on F5 — how many open Orders one Customer may hold | Constraints | Credit control has not decided whether concurrent open orders are allowed |

## Extension Log

| Date | Change | Class | Result |
|---|---|---|---|
| 2026-09-02 | Initial greenfield ontology | addition | appended |
