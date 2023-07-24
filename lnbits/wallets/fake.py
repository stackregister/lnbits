import asyncio
import hashlib
import random
from datetime import datetime
from typing import AsyncGenerator, Optional

from bolt11.decode import decode
from bolt11.encode import encode
from bolt11.types import Bolt11, MilliSatoshi
from loguru import logger

from lnbits.settings import settings

from .base import (
    InvoiceResponse,
    PaymentResponse,
    PaymentStatus,
    StatusResponse,
    Wallet,
)


class FakeWallet(Wallet):
    queue: asyncio.Queue = asyncio.Queue(0)
    secret: str = settings.fake_wallet_secret
    privkey: str = hashlib.pbkdf2_hmac(
        "sha256",
        secret.encode(),
        ("FakeWallet").encode(),
        2048,
        32,
    ).hex()

    async def status(self) -> StatusResponse:
        logger.info(
            "FakeWallet funding source is for using LNbits as a centralised, stand-alone payment system with brrrrrr."
        )
        return StatusResponse(None, 1000000000)

    async def create_invoice(
        self,
        amount: int,
        memo: Optional[str] = None,
        description_hash: Optional[bytes] = None,
        unhashed_description: Optional[bytes] = None,
        **kwargs,
    ) -> InvoiceResponse:

        tags = {}

        if description_hash:
            tags["h"] = description_hash.decode()
        elif unhashed_description:
            tags["h"] = hashlib.sha256(unhashed_description).digest()
        else:
            tags["d"] = memo

        if kwargs.get("expiry"):
            tags["x"] = kwargs.get("expiry")

        # random hash
        checking_id = (
            self.privkey[:6]
            + hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[6:]
        )

        tags["p"] = checking_id

        bolt11 = Bolt11(
            currency="bc",
            amount=MilliSatoshi(amount * 1000),
            timestamp=int(datetime.now().timestamp()),
            tags=tags,
        )

        payment_request = encode(bolt11, self.privkey)

        return InvoiceResponse(True, checking_id, payment_request)

    async def pay_invoice(self, bolt11: str, _: int) -> PaymentResponse:
        invoice = decode(bolt11)

        if not invoice.payment_hash:
            return PaymentResponse(ok=False, error_message="No payment hash.")

        if invoice.payment_hash[:6] == self.privkey[:6]:
            await self.queue.put(invoice)
            return PaymentResponse(True, invoice.payment_hash, 0)
        else:
            return PaymentResponse(
                ok=False, error_message="Only internal invoices can be used!"
            )

    async def get_invoice_status(self, _: str) -> PaymentStatus:
        return PaymentStatus(None)

    async def get_payment_status(self, _: str) -> PaymentStatus:
        return PaymentStatus(None)

    async def paid_invoices_stream(self) -> AsyncGenerator[str, None]:
        while True:
            value: Bolt11 = await self.queue.get()
            assert value.payment_hash, "No payment hash."
            yield value.payment_hash
