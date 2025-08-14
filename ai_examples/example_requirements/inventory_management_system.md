# Business Logic Description

* **Catalog & Discovery**

    * Manage products with embedded **variants** (per-SKU stock/price) and embedded **recent reviews** (denormalized rating summary).
    * Support **text search** (title/description/brand) and **faceted browse** (category, price, rating, attributes).
* **Ordering (single-item for demo)**

    * Create an order for a specific **SKU** and **qty**.
    * A **state machine** orchestrates the lifecycle: reserve stock, take payment, fulfill, ship, deliver; with compensations that **release stock** on failure/cancel/timeout.
* **Reviews**

    * Users can post reviews; newest N reviews are embedded in the product; rating summary kept on the product for fast filtering and sort.
* **Auditing & Events**

    * Every state transition is recorded on the order timeline.
    * Outbox ensures idempotent emission of integration events (payment, shipping).

---

# Entities & Data Model

## Product

```jsonc
{
  "_id": "ObjectId",
  "slug": "string",                       // unique
  "title": "string",
  "brand": "string",
  "categories": ["string"],
  "description": "string",
  "price": 129.99,                        // list/base price
  "currency": "USD",
  "attributes": {                         // flexible filter bag
    "gender": "unisex",
    "colorways": ["black","teal"],
    "drop_mm": 8,
    "waterproof": false
  },
  "variants": [                           // embedded inventory per SKU
    {
      "sku": "string",
      "options": { "color": "black", "sizeEU": 42 },
      "stock": 18,                        // integer >= 0
      "price": 124.99                     // optional per-variant price
    }
  ],
  "rating": { "average": 4.5, "count": 238 },
  "reviews": [                            // keep latest N (e.g., 20)
    {
      "reviewId": "ObjectId",
      "userId": "ObjectId",
      "stars": 5,
      "title": "string",
      "body": "string",
      "createdAt": "ISODate",
      "status": "published"               // pending|published|flagged
    }
  ],
  "popularityScore": 0.87,
  "isActive": true,
  "createdAt": "ISODate",
  "updatedAt": "ISODate"
}
```

**Indexes**

* `{ slug: 1 } (unique)`
* `{ "variants.sku": 1 }`
* `{ isActive: 1, categories: 1, price: 1 }`
* `{ isActive: 1, "rating.average": -1 }`
* Text search: `{ title: "text", description: "text", brand: "text" }`

## Order

```jsonc
{
  "_id": "ObjectId",
  "userId": "ObjectId",
  "items": [
    {
      "sku": "string",
      "qty": 1,
      "priceAtPurchase": 124.99,
      "productSnapshot": { "title": "string", "slug": "string" }
    }
  ],
  "state": "NEW",                         // state machine controlled
  "payment": {
    "provider": "stripe",                 // or "mock" for demo
    "intentId": "string|null",
    "status": "none|authorized|captured|failed"
  },
  "shipping": {
    "addressId": "ObjectId|null",
    "carrier": "string|null",
    "tracking": "string|null"
  },
  "timeline": [                           // append-only audit log
    { "at": "ISODate", "state": "NEW", "by": "system|user|webhook" }
  ],
  "outbox": [                             // integration events
    { "type": "OrderStateChanged", "state": "PAID", "at": "ISODate", "attempts": 0, "delivered": false }
  ],
  "createdAt": "ISODate",
  "updatedAt": "ISODate"
}
```

**Indexes**

* `{ userId: 1, createdAt: -1 }`
* `{ state: 1, createdAt: -1 }`
* `{ "outbox.delivered": 1 }`

## User (minimal for demo)

```jsonc
{
  "_id": "ObjectId",
  "email": "string",
  "name": "string",
  "createdAt": "ISODate",
  "blocked": false
}
```

## (Optional) Long-tail Reviews Collection

```jsonc
{
  "_id": "ObjectId",
  "productId": "ObjectId",
  "userId": "ObjectId",
  "stars": 5,
  "title": "string",
  "body": "string",
  "createdAt": "ISODate",
  "status": "published"
}
```

**Indexes**: `{ productId: 1, createdAt: -1 }`, `{ userId: 1 }`

---

# State Machine

## Name

`order-lifecycle`

## States

* **NEW** (initial)
* **RESERVING\_STOCK**
* **PAYMENT\_PENDING**
* **PAID**
* **FULFILLING**
* **SHIPPED**
* **DELIVERED** (final)
* **OUT\_OF\_STOCK** (final)
* **PAYMENT\_FAILED** (final; includes compensation)
* **CANCELLED** (final; includes compensation)
* **EXPIRED** (final; includes compensation)

## Events

* `PLACE`, `RESERVE_OK`, `RESERVE_FAIL`
* `PAYMENT_OK`, `PAYMENT_FAIL`, `TIMEOUT`, `CANCEL`
* `FULFILLMENT_OK`, `LABEL_OK`, `DELIVERY_CONFIRMED`

## Guards (key ones)

* Product `isActive = true`
* Atomic stock decrement success on the product variant
* Payment authorization/capture success

## Actions

* **reserveStock**:
  `products.updateOne({ "variants.sku": sku, "variants.stock": { $gte: qty }, isActive: true }, { $inc: { "variants.$.stock": -qty } })`
* **releaseStock** (compensation):
  `products.updateOne({ "variants.sku": sku }, { $inc: { "variants.$.stock": +qty } })`
* **authorizePayment / capturePayment** (idempotent with provider key)
* **enqueueFulfillment / createLabel**
* **appendTimeline, emitOutboxEvent**

## Transitions (summary)

* `NEW --(PLACE)--> RESERVING_STOCK`
* `RESERVING_STOCK --(RESERVE_OK)--> PAYMENT_PENDING`
  `RESERVING_STOCK --(RESERVE_FAIL)--> OUT_OF_STOCK`
* `PAYMENT_PENDING --(PAYMENT_OK)--> PAID`
  `PAYMENT_PENDING --(PAYMENT_FAIL)--> PAYMENT_FAILED (do: releaseStock)`
  `PAYMENT_PENDING --(TIMEOUT 15m)--> EXPIRED (do: releaseStock)`
  `PAYMENT_PENDING --(CANCEL)--> CANCELLED (do: releaseStock)`
* `PAID --(FULFILLMENT_OK)--> FULFILLING`
* `FULFILLING --(LABEL_OK)--> SHIPPED`
* `SHIPPED --(DELIVERY_CONFIRMED | timeout 14d)--> DELIVERED`

---

# API (minimal, idempotent)

## Catalog & Search

### `GET /products`

Query params:

* `q` (string; full-text), `category` (string), `minPrice` (number), `maxPrice` (number),
  `minRating` (number), `attrs[color]=black` etc., `inStock` (bool), `page` (int), `pageSize` (int)

Responses:

* `200 OK` → `{ items: [...], total: 123, page: 1, pageSize: 20 }`

### `GET /products/:slug`

* `200 OK` → product doc (with top N reviews)
* `404 Not Found`

### `POST /products/:slug/reviews`

Body: `{ stars: 1..5, title: string, body: string }`

* `201 Created` → `{ reviewId }` (embedded + optional long-tail write)
* Moderation status defaults to `pending` or `published` (configurable)

## Orders (state-machine backed)

### `POST /orders`

Headers: `Idempotency-Key: <uuid>`
Body: `{ sku: string, qty: number, addressId?: string }`
Behavior:

* Create order in `NEW`, dispatch `PLACE` to state machine.
* On successful reserve, order reaches `PAYMENT_PENDING` and returns client secret/payment intent token (if applicable).

Responses:

* `201 Created` → order summary `{ orderId, state, payment: { intentClientSecret? } }`
* `409 Conflict` if idempotency key reused with mismatched body.

### `GET /orders/:id`

* `200 OK` → full order doc (minus sensitive tokens)
* `404 Not Found`

### `POST /orders/:id/cancel`

* Allowed when state ∈ `{PAYMENT_PENDING, PAID}` and not yet `FULFILLING`.
* Emits `CANCEL` to state machine.
* `200 OK` → `{ state: "CANCELLED" }` (after transition)
* `409 Conflict` if invalid state

## Webhooks (translate to machine events)

### `POST /webhooks/payment`

Body: `{ orderId, provider, intentId, status: "ok|fail" }`

* `200 OK`

    * `ok` → emit `PAYMENT_OK`
    * `fail` → emit `PAYMENT_FAIL`

### `POST /webhooks/shipping`

Body: `{ orderId, carrier, tracking, status: "label_ok|delivered" }`

* `200 OK`

    * `label_ok` → emit `LABEL_OK`
    * `delivered` → emit `DELIVERY_CONFIRMED`

---

## Validation & Constraints (high level)

* **Transactions** wrap stock changes + order transitions when both are updated.
* **Idempotency** keys required for `POST /orders`; payment provider keys used to dedupe webhooks.
* **Document size**: cap embedded `reviews` (e.g., 20) to keep product docs < 16MB.
* **Timeouts**: `PAYMENT_PENDING` TTL = 15 minutes; `SHIPPED` auto-deliver = 14 days (configurable).
