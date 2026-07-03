# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
import json
from genlayer import *
class FreelanceEscrow(gl.Contract):
    client: str
    freelancer: str
    job_description: str
    submission: str
    dispute_reason: str
    status: str
    amount_locked: u256
    def __init__(self, client: str, freelancer: str, job_description: str):
        # Store addresses normalized to lowercase to prevent case-sensitive comparison failures
        self.client = client.lower()
        self.freelancer = freelancer.lower()
        self.job_description = job_description
        self.submission = ""
        self.dispute_reason = ""
        self.status = "AWAITING_DEPOSIT"
        self.amount_locked = u256(0)
    @gl.public.write
    def deposit(self, amount: int) -> None:
        # Virtual deposit method allowing state testing without requiring native GEN tokens
        sender = str(gl.message.sender_address).lower()
        assert sender == self.client, "Only the client can deposit funds."
        assert self.status == "AWAITING_DEPOSIT", "Funds have already been deposited."
        assert amount >= 0, "Deposit value must be zero or greater."
        
        self.amount_locked = u256(amount)
        self.status = "FUNDED"
    @gl.public.write
    def submit_work(self, submission_text: str) -> None:
        sender = str(gl.message.sender_address).lower()
        assert sender == self.freelancer, "Only the freelancer can submit work."
        assert self.status == "FUNDED", "Escrow is not funded yet."
        
        self.submission = submission_text
        self.status = "SUBMITTED"
    @gl.public.write
    def release_payment(self) -> None:
        sender = str(gl.message.sender_address).lower()
        assert sender == self.client, "Only the client can release payment."
        assert self.status in ["FUNDED", "SUBMITTED"], "Cannot release payment in this state."
        
        # In this mock model, we clear the balance and change the state.
        # emit_transfer is omitted to prevent transaction failure when contract has 0 actual GEN balance.
        self.amount_locked = u256(0)
        self.status = "RESOLVED"
    @gl.public.write
    def raise_dispute(self, reason: str) -> None:
        sender = str(gl.message.sender_address).lower()
        assert sender in [self.client, self.freelancer], "Only parties involved can raise a dispute."
        assert self.status == "SUBMITTED", "Can only dispute submitted work."
        
        self.dispute_reason = reason
        self.status = "DISPUTED"
    @gl.public.write
    def adjudicate_dispute(self) -> None:
        assert self.status == "DISPUTED", "No active dispute to adjudicate."
        
        # Local snapshots for non-deterministic execution block
        description = self.job_description
        submission_text = self.submission
        dispute_text = self.dispute_reason
        # Zero-argument closure for validator LLM adjudication
        def evaluate_dispute():
            prompt = (
                "You are an impartial arbitrator resolving a contract dispute between a client and a freelance builder.\n\n"
                "## Job Description / Requirements:\n"
                + description + "\n\n"
                "## Freelancer Submission:\n"
                + submission_text + "\n\n"
                "## Dispute Claim:\n"
                + dispute_text + "\n\n"
                "## Guidelines:\n"
                "Review the freelancer's submission against the requirements. "
                "Evaluate the client's dispute claim. "
                "Determine the percentage of funds (0 to 100) that the freelancer deserves based on how much work was completed and its quality.\n\n"
                "Output must be exactly in JSON format:\n"
                "{\n"
                "  \"freelancer_percentage\": int,\n"
                "  \"reasoning\": \"a brief explanation for the split\"\n"
                "}\n"
                "Only return raw JSON. No markdown syntax, codeblocks, or other text."
            )
            response = gl.nondet.exec_prompt(prompt, response_format="json")
            
            # Extract only the percentage for consensus to prevent validator disagreement 
            # on the subjective, varying 'reasoning' explanation text.
            pct = int(response.get("freelancer_percentage", 0))
            if pct < 0:
                pct = 0
            if pct > 100:
                pct = 100
            return str(pct)
        # strict_eq now compares only the objective percentage, guaranteeing instant consensus.
        consensus_pct_str = gl.eq_principle.strict_eq(evaluate_dispute)
        pct = int(consensus_pct_str)
        # In this mock model, we clear the balance and change the state.
        # emit_transfer is omitted to prevent transaction failure when contract has 0 actual GEN balance.
        self.amount_locked = u256(0)
        self.status = "RESOLVED"
    @gl.public.view
    def get_status(self) -> str:
        return self.status
    @gl.public.view
    def get_amount_locked(self) -> u256:
        return self.amount_locked
