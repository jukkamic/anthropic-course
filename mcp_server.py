from mcp.server.fastmcp import FastMCP
from pydantic import Field
import json

mcp = FastMCP("CustomerMCP", log_level="ERROR")

# Mock database
customers = {"C-123": {"name": "Alice", "verified": True}}
orders = {"O-999": {"customer_id": "C-123", "amount": 450.00, "status": "delivered"}}

from pydantic import Field
from mcp.server.fastmcp.prompts import base


docs = {}

@mcp.tool(
    name="get_customer",
    description="""Retrieves customer verification status. 
    MUST be used FIRST when a customer requests account changes, refunds, or order details.
    Input should be the exact customer ID (e.g., C-123). Do not use this for order numbers."""
)
def get_customer(customer_id: str = Field(description="The customer ID, starting with C-")):
    if customer_id not in customers:
        return json.dumps({
            "errorCategory": "validation",
            "isRetryable": True,
            "message": f"Customer {customer_id} not found. Please ask the user to verify their ID."
        })
    return json.dumps(customers[customer_id])

@mcp.tool(
    name="lookup_order",
    description="""Retrieves order details (items, cost, status).
    BOUNDARY: Do not use this until you have successfully verified the user with get_customer.
    Input must be an order ID (e.g., O-999)."""
)
def lookup_order(order_id: str = Field(description="The order ID, starting with O-")):
    if order_id not in orders:
         return json.dumps({
            "errorCategory": "validation",
            "isRetryable": True,
            "message": f"Order {order_id} not found."
        })
    return json.dumps(orders[order_id])

@mcp.tool(
    name="process_refund",
    description="Processes a refund for a specific order. Requires prior verification via get_customer."
)
def process_refund(
    order_id: str = Field(description="The order ID to refund"),
    amount: float = Field(description="The amount to refund in USD")
):
    # Programmatic Interception: The Business Rule
    if amount > 500.0:
        # Returning a structured error with isRetryable: false forces the agent 
        # to realize it cannot brute-force the tool and must escalate.
        return json.dumps({
            "errorCategory": "permission",
            "isRetryable": False,
            "message": f"Refunds over $500 require human authorization. Amount requested: ${amount}. Initiate escalation workflow."
        })
    
    if order_id not in orders:
        return json.dumps({
            "errorCategory": "validation",
            "isRetryable": True,
            "message": "Invalid order ID."
        })

    return json.dumps({"status": "success", "refunded_amount": amount, "order": order_id})

@mcp.resource("docs://documents", mime_type="application/json")
def list_docs() -> list[str]:
    return list(docs.keys())


@mcp.resource("docs://documents/{doc_id}", mime_type="text/plain")
def fetch_doc(doc_id: str) -> str:
    if doc_id not in docs:
        raise ValueError(f"Doc with id {doc_id} not found")
    return docs[doc_id]


if __name__ == "__main__":
    mcp.run(transport="stdio")
