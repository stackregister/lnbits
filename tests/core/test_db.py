import pytest

from lnbits.core.crud import (
    create_account,
    create_wallet,
    delete_wallet,
    get_wallet,
    get_wallet_for_key,
)


# make test to create wallet and delete wallet
@pytest.mark.asyncio
async def test_create_wallet_and_delete_wallet():
    # create wallet
    user = await create_account()
    wallet = await create_wallet(user_id=user.id, wallet_name="test_wallet_to")
    assert wallet

    #delete wallet
    await delete_wallet(user_id=user.id, wallet_id=wallet.id)

    # check if wallet is deleted
    del_wallet = await get_wallet(wallet.id)
    assert del_wallet is None

    del_wallet = await get_wallet_for_key(wallet.inkey)
    assert del_wallet is None
    