import pytest
import brownie
from brownie import network, StakeToken, TokenFarm, MockDAI, MockWETH
from scripts.helpful_scripts import LOCAL_BLOCKCHAIN_ENVIRONMENTS, INITIAL_VALUE, get_account, get_contract, deploy_mocks
from scripts.deploy import deploy_token_farm_and_dapp_token
from web3 import Web3

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
    token_farm.stakeTokens(amount_staked, dapp_token.address, {"from": account})
    assert token_farm.uniqueTokensStaked(account) == 1
    assert token_farm.stakingBalance(dapp_token.address, account) == amount_staked
    assert token_farm.stakers(0) == account
    return token_farm, dapp_token

def test_issue_tokens(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    account = get_account()
    non_owner = get_account(index=1)
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account)
    with brownie.reverts():
        token_farm.issueTokens({"from": non_owner})
    token_farm.issueTokens({"from": account})
    assert Web3.toWei(2099, "ether") == (starting_balance + INITIAL_VALUE)
    assert (
        dapp_token.balanceOf(account)
        == starting_balance + INITIAL_VALUE
    )

def test_get_token_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    assert token_farm.getTokenValue(dapp_token.address) == (INITIAL_VALUE, 18)

def test_get_user_single_token_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    account = get_account()
    non_owner = get_account(index=1)
    assert token_farm.getUserSingleTokenValue(account, dapp_token.address) == INITIAL_VALUE
    assert token_farm.getUserSingleTokenValue(non_owner, dapp_token.address) == 0

def test_user_total_value(amount_staked):
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local testing!")
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    account = get_account()
    non_owner = get_account(index=1)
    assert token_farm.getUserTotalValue(account) == INITIAL_VALUE
    mock_weth_token = get_contract("weth_token")
    assert mock_weth_token.balanceOf(account) == Web3.toWei(1000000, "ether")
    mock_weth_token.approve(token_farm.address, amount_staked, {"from": account})
    assert token_farm.uniqueTokensStaked(account) == 1
    token_farm.stakeTokens(amount_staked, mock_weth_token.address, {"from": account})
    assert token_farm.stakingBalance(mock_weth_token.address, account) == amount_staked
    assert token_farm.uniqueTokensStaked(account) == 2
    assert token_farm.getUserTotalValue(account) == INITIAL_VALUE + INITIAL_VALUE
