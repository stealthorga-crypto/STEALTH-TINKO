"""
PSP-001: Stripe Payment API Routes
Endpoints for creating checkout sessions, payment links, and handling webhooks.
"""
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
import os
import structlog

from ..db import get_db
from ..deps import get_current_user
from ..models import Transaction, RecoveryAttempt, User
from ..services.stripe_service import StripeService
from ..psp.dispatcher import PSPDispatcher
try:
    import stripe  # type: ignore
except Exception:
    stripe = None  # type: ignore

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1/payments/stripe", tags=["Stripe Payments"])


# Pydantic Schemas
class CreateCheckoutSessionRequest(BaseModel):
    transaction_ref: str = Field(..., description="Unique transaction reference")
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit (e.g., cents)")
    currency: str = Field(default="usd", description="Three-letter ISO currency code")
    customer_email: Optional[str] = Field(None, description="Customer email address")
    customer_phone: Optional[str] = Field(None, description="Customer phone number")
    success_url: Optional[str] = Field(None, description="Custom success redirect URL")
    cancel_url: Optional[str] = Field(None, description="Custom cancel redirect URL")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional metadata")


class CreatePaymentLinkRequest(BaseModel):
    transaction_ref: str = Field(..., description="Unique transaction reference")
    amount: int = Field(..., gt=0, description="Amount in smallest currency unit")
    currency: str = Field(default="usd", description="Three-letter ISO currency code")
    metadata: Optional[Dict[str, str]] = Field(default_factory=dict, description="Additional metadata")


class CheckoutSessionResponse(BaseModel):
    session_id: str
    payment_intent_id: Optional[str]
    checkout_url: str
    expires_at: datetime


class PaymentLinkResponse(BaseModel):
    payment_link_id: str
    url: str
    product_id: str
    price_id: str


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    payment_status: str
    amount_total: Optional[int]
    currency: Optional[str]
    customer_email: Optional[str]
    payment_intent_id: Optional[str]


# Endpoints
@router.post("/checkout-sessions", response_model=CheckoutSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a Stripe Checkout Session for payment recovery.
    
    This endpoint creates a hosted checkout page where customers can complete their payment.
    The session expires after 24 hours.
    """
    # Verify transaction exists and belongs to user's organization
    transaction = db.query(Transaction).filter(
        Transaction.transaction_ref == request.transaction_ref,
        Transaction.org_id == current_user.org_id
    ).first()
    
    if not transaction:
        logger.warning(
            "transaction_not_found",
            transaction_ref=request.transaction_ref,
            org_id=current_user.org_id,
            user_id=current_user.id
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {request.transaction_ref} not found"
        )
    
    # Add organization metadata
    metadata = {
        "org_id": str(current_user.org_id),
        "user_id": str(current_user.id),
        **request.metadata
    }
    
    try:
        # Create checkout session via PSP adapter (Stripe)
        adapter = PSPDispatcher.get_adapter("stripe")
        result = adapter.create_checkout_session(
            amount=request.amount,
            currency=request.currency,
            success_url=request.success_url or (os.getenv("BASE_URL", "http://localhost:3000") + "/pay/success?session_id={CHECKOUT_SESSION_ID}"),
            cancel_url=request.cancel_url or (os.getenv("BASE_URL", "http://localhost:3000") + "/pay/cancel"),
            metadata=metadata,
            product_name=f"Payment Recovery - {request.transaction_ref}"
        )
        
        # Update transaction with Stripe IDs
        raw = result.get("raw")
        transaction.stripe_checkout_session_id = result["session_id"]
        transaction.stripe_payment_intent_id = getattr(raw, "payment_intent", None)
        transaction.payment_link_url = result["url"]
        if request.customer_email:
            transaction.customer_email = request.customer_email
        if request.customer_phone:
            transaction.customer_phone = request.customer_phone
        
        db.commit()
        
        logger.info(
            "checkout_session_created",
            transaction_id=transaction.id,
            session_id=result["session_id"],
            amount=request.amount,
            currency=request.currency,
            org_id=current_user.org_id
        )
        
        # Build response compatible with existing schema
        return CheckoutSessionResponse(
            session_id=result["session_id"],
            payment_intent_id=getattr(raw, "payment_intent", None),
            checkout_url=result["url"],
            expires_at=datetime.fromtimestamp(getattr(raw, "expires_at", int(datetime.utcnow().timestamp())))
        )
        
    except Exception as e:
        db.rollback()
        logger.error(
            "checkout_session_creation_failed",
            error=str(e),
            transaction_ref=request.transaction_ref,
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )


@router.post("/payment-links", response_model=PaymentLinkResponse, status_code=status.HTTP_201_CREATED)
async def create_payment_link(
    request: CreatePaymentLinkRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a reusable Stripe Payment Link.
    
    Payment links are permanent and can be shared multiple times.
    Unlike checkout sessions, they don't expire.
    """
    # Verify transaction exists and belongs to user's organization
    transaction = db.query(Transaction).filter(
        Transaction.transaction_ref == request.transaction_ref,
        Transaction.org_id == current_user.org_id
    ).first()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transaction {request.transaction_ref} not found"
        )
    
    # Add organization metadata
    metadata = {
        "org_id": str(current_user.org_id),
        "user_id": str(current_user.id),
        **request.metadata
    }
    
    try:
        # Create payment link via PSP adapter (Stripe)
        adapter = PSPDispatcher.get_adapter("stripe")
        result = adapter.create_payment_link(
            amount=request.amount,
            currency=request.currency,
            metadata=metadata,
            product_name=f"Payment Recovery - {request.transaction_ref}"
        )
        
        # Update transaction with payment link URL
        transaction.payment_link_url = result["url"]
        db.commit()
        
        logger.info(
            "payment_link_created",
            transaction_id=transaction.id,
            payment_link_id=result["payment_link_id"],
            amount=request.amount,
            currency=request.currency,
            org_id=current_user.org_id
        )
        
        return PaymentLinkResponse(**result)
        
    except Exception as e:
        db.rollback()
        logger.error(
            "payment_link_creation_failed",
            error=str(e),
            transaction_ref=request.transaction_ref,
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create payment link: {str(e)}"
        )


@router.get("/sessions/{session_id}/status", response_model=SessionStatusResponse)
async def get_session_status(
    session_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the status of a Stripe Checkout Session.
    
    Use this to check if a customer has completed payment.
    """
    try:
        session = StripeService.retrieve_checkout_session(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        return SessionStatusResponse(
            session_id=session.id,
            status=session.status,
            payment_status=session.payment_status,
            amount_total=session.amount_total,
            currency=session.currency,
            customer_email=session.customer_details.email if session.customer_details else None,
            payment_intent_id=session.payment_intent
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "session_status_retrieval_failed",
            error=str(e),
            session_id=session_id,
            error_type=type(e).__name__
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve session status: {str(e)}"
        )


@router.post("/webhooks", status_code=status.HTTP_200_OK, include_in_schema=False)
async def stripe_webhook_handler(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events.
    
    This endpoint receives real-time notifications from Stripe about payment events.
    Signature verification is required for security.
    """
    # Get raw body and signature
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        logger.warning("stripe_webhook_missing_signature")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header"
        )
    
    # Verify webhook signature
    event = StripeService.verify_webhook_signature(payload, sig_header)
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid webhook signature"
        )
    
    event_type = event["type"]
    event_data = event["data"]["object"]
    
    logger.info(
        "stripe_webhook_received",
        event_type=event_type,
        event_id=event["id"]
    )
    
    # Handle different event types
    try:
        if event_type == "checkout.session.completed":
            await _handle_checkout_session_completed(event_data, db)
        elif event_type == "payment_intent.succeeded":
            await _handle_payment_intent_succeeded(event_data, db)
        elif event_type == "payment_intent.payment_failed":
            await _handle_payment_intent_failed(event_data, db)
        else:
            logger.info("stripe_webhook_event_ignored", event_type=event_type)
    
    except Exception as e:
        logger.error(
            "stripe_webhook_processing_failed",
            error=str(e),
            event_type=event_type,
            event_id=event["id"],
            error_type=type(e).__name__
        )
        # Return 200 to acknowledge receipt even if processing failed
        # Stripe will retry failed webhooks
    
    return {"status": "received"}


@router.get("/ping")
async def stripe_ping():
    """Lightweight readiness check for Stripe configuration on the server."""
    if stripe is None or not os.getenv("STRIPE_SECRET_KEY"):
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe not configured")
    try:
        stripe.api_key = os.getenv("STRIPE_SECRET_KEY")
        # Simple API call to verify credentials
        _ = stripe.Balance.retrieve()
        return {"ok": True}
    except Exception as e:
        logger.error("stripe_ping_failed", error=str(e))
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Stripe ping failed")


# Webhook event handlers
async def _handle_checkout_session_completed(session_data: Dict[str, Any], db: Session):
    """Handle successful checkout session completion."""
    session_id = session_data.get("id")
    payment_intent_id = session_data.get("payment_intent")
    metadata = session_data.get("metadata", {})
    transaction_ref = metadata.get("transaction_ref")
    
    if not transaction_ref:
        logger.warning("checkout_session_missing_transaction_ref", session_id=session_id)
        return
    
    # Update transaction status
    transaction = db.query(Transaction).filter(
        Transaction.transaction_ref == transaction_ref
    ).first()
    
    if transaction:
        transaction.stripe_payment_intent_id = payment_intent_id
        
        # Mark recovery attempt as completed
        recovery = db.query(RecoveryAttempt).filter(
            RecoveryAttempt.transaction_ref == transaction_ref,
            RecoveryAttempt.status.in_(["created", "sent", "opened"])
        ).first()
        
        if recovery:
            recovery.status = "completed"
            recovery.used_at = datetime.utcnow()
            logger.info(
                "recovery_completed_via_checkout",
                recovery_id=recovery.id,
                transaction_ref=transaction_ref,
                session_id=session_id
            )
        
        db.commit()
        logger.info(
            "checkout_session_processed",
            transaction_id=transaction.id,
            session_id=session_id,
            payment_intent_id=payment_intent_id
        )


async def _handle_payment_intent_succeeded(intent_data: Dict[str, Any], db: Session):
    """Handle successful payment intent."""
    payment_intent_id = intent_data.get("id")
    amount = intent_data.get("amount")
    currency = intent_data.get("currency")
    
    # Find transaction by payment intent ID
    transaction = db.query(Transaction).filter(
        Transaction.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if transaction:
        logger.info(
            "payment_intent_succeeded",
            transaction_id=transaction.id,
            payment_intent_id=payment_intent_id,
            amount=amount,
            currency=currency
        )
        db.commit()


async def _handle_payment_intent_failed(intent_data: Dict[str, Any], db: Session):
    """Handle failed payment intent."""
    payment_intent_id = intent_data.get("id")
    error_message = intent_data.get("last_payment_error", {}).get("message", "Unknown error")
    
    # Find transaction by payment intent ID
    transaction = db.query(Transaction).filter(
        Transaction.stripe_payment_intent_id == payment_intent_id
    ).first()
    
    if transaction:
        logger.warning(
            "payment_intent_failed",
            transaction_id=transaction.id,
            payment_intent_id=payment_intent_id,
            error=error_message
        )
        db.commit()
