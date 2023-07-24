import pytest

from lnbits.core.crud import (
    create_wallet,
    delete_wallet,
    get_wallet,
    get_wallet_for_key,
)


# make test to create wallet and delete wallet
@pytest.mark.asyncio
async def test_create_wallet_and_delete_wallet(app, to_user):
    # create wallet
    wallet = await create_wallet(user_id=to_user.id, wallet_name="test_wallet_delete")
    assert wallet

    # delete wallet
    await delete_wallet(user_id=to_user.id, wallet_id=wallet.id)

    # check if wallet is deleted
    del_wallet = await get_wallet(wallet.id)
    assert del_wallet is None

    del_wallet = await get_wallet_for_key(wallet.inkey)
    assert del_wallet is None
