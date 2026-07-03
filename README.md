# Adjudicated Freelance Escrow Contract

An Intelligent Contract primitive built on **GenLayer** that facilitates trustless freelance agreements. The contract holds deposit funds in escrow and utilizes decentralized AI-validator consensus (the Equivalence Principle) to act as an impartial dispute resolution court if conflict arises.

---

## 📖 How It Works
1. **Escrow Setup**: The contract is deployed with the Client and Freelancer addresses along with the job requirements description.
2. **Funding**: The client deposits virtual or native funds to lock the contract in trust.
3. **Submission**: The freelancer submits their textual work.
4. **Resolution Paths**:
   - **Happy Path**: The client is satisfied and releases the funds directly to the freelancer.
   - **Dispute Path**: Either party can raise a dispute. The validator network's LLMs evaluate the freelancer's submission against the initial requirements and the client's dispute claim to reach consensus on a percentage-based split.

---

## ⚙️ Lifecycle States
```
[ AWAITING_DEPOSIT ] ──(deposit)──▶ [ FUNDED ] ──(submit_work)──▶ [ SUBMITTED ]
                                                                       │
                                      ┌────────────────────────────────┴──────────────┐
                              (release_payment)                                 (raise_dispute)
                                      ▼                                               ▼
                                 [ RESOLVED ]                                   [ DISPUTED ]
                                                                                      │
                                                                             (adjudicate_dispute)
                                                                                      ▼
                                                                                 [ RESOLVED ]
```

---

## 🛠️ Key Technical Features
*   **Consensus Optimization**: Avoids the "LLM reasoning disagreement" gotcha. The prompt instructs the LLM to output both reasoning and percentage, but the contract extracts and validates **only the objective percentage integer** inside the non-deterministic block. This ensures `strict_eq` consensus achieves instant single-round finalization.
*   **Case-Insensitive Normalization**: Automatically lowercases all EVM addresses during storage and checks to prevent transaction reversion caused by checksum character case mismatches.
*   **Tokenless & Sandbox Friendly**: Built to support simulated virtual deposits, allowing complete contract flow testing in local sandboxes with `0 GEN` balances.

---

## 🚀 How to Test in GenLayer Studio

Follow this step-by-step flow to simulate the entire state machine:

### 1. Deployment
Deploy the contract using the following constructor inputs:
*   **`client`**: Paste your active GenLayer account address (e.g. Account A).
*   **`freelancer`**: Paste a second address (e.g. Account B).
*   **`job_description`**: `"Build a responsive React analytics dashboard. Must include an active chart component and support user authentication."`

### 2. Deposit Funds
*   **Active Account**: Client (Account A)
*   Call `deposit()` with `amount` set to `100`.
*   *Status transitions to*: `FUNDED`

### 3. Submit Work
*   **Active Account**: Switch to Freelancer (Account B).
*   Call `submit_work()` with `submission_text`: `"Basic index page complete. Missed the deadline for auth and charts."`
*   *Status transitions to*: `SUBMITTED`

### 4. Dispute Payouts
*   **Active Account**: Switch back to Client (Account A).
*   Call `raise_dispute()` with `reason`: `"The freelancer failed to deliver the chart component and user auth as requested."`
*   *Status transitions to*: `DISPUTED`

### 5. Run Court Adjudication
*   Call `adjudicate_dispute()` from any account.
*   *Result*: The validator network reviews the submission, agrees on a percentage (e.g., `10%` or `0%` due to major missing deliverables), and resolves the state to `RESOLVED` in a single consensus round!
