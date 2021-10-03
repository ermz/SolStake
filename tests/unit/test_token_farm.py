import pytest
import brownie
from brownie import network, StakeToken, TokenFarm
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account, get_contract
from scripts.deploy import deploy_token_farm_and_dapp_token

def test_set_price_feed_contract():
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    with brownie.reverts():
        token_farm.setPriceFeedContract(dapp_token.address, get_contract("eth_usd_price_feed"), {"from": non_owner})
    token_farm.setPriceFeedContract(dapp_token.address, get_contract("eth_usd_price_feed"), {"from": account})
    assert token_farm.tokenPriceFeedMapping(dapp_token.address) == get_contract("eth_usd_price_feed")

def test_stake_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    assert token_farm.uniqueTokensStaked(account) == 0
    assert token_farm.stakingBalance(dapp_token.address, account) == 0
    token_farm.stakeTokens(1, dapp_token.address, {"from": account})
    assert token_farm.uniqueTokensStaked(account) == 1
    assert token_farm.stakingBalance(dapp_token.address, account) > 0

def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()
    dapp_token.approve(token_farm.address, amount_staked, {"from": account})
    token_farm.stakeTokens(1, dapp_token.address, {"from": account})
    with brownie.reverts():
        token_farm.issueTokens({"from": non_owner})
    token_farm.issueTokens({"from": account})
    