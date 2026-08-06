# Credits mechanics — read this before you quote anyone's balance

How `checkAndResetCredits` actually behaves, and why a balance you read is not
necessarily the balance that was there a second earlier.

`checkAndResetCredits` refills a stale row to the plan total (`DEFAULT_CREDITS` 333 /
`PRO_CREDITS` 9999). Three things follow, and all three have bitten:

1. **Refill is lazy, and reading a balance MUTATES it.** It is reachable from exactly one
   place — the `GET /api/accounts/{id}/credits` handler. The spend path never calls it
   (`autoRechargeOrFail` reads `remaining_credits` directly and mints a Checkout session on
   a shortfall). So an account nobody opens never refills, and *your* GET is what finally
   tops it up. That is the sanctioned one-call comp for a stale account.
2. **It SETS, it does not add** — and only fires when the row is **> 1 month old**. On a
   free-tier account sitting above 333 the same read silently **reduces** the balance.
   Check `timestamp` and `is_pro` *before* you call it on anyone.
3. **There is no staff-facing way to grant credits.** Every route under
   `/api/admins/credits` is a GET; only the Stripe webhook and auto-recharge increment. If
   the row is too fresh to refill, the only options are a deliberate raw DB write (breaks
   the SQL guardrail — get sign-off and log it) or putting them on a plan.

**`isPro` is derived from Stripe by account id**, so a customer whose Stripe record is
missing `metadata.accountId` resolves to **free tier while paying** — seen live on a
$5,000/mo account sitting on 333 credits. Check that linkage before diagnosing anything
credit-related.
