from scripts.helpful_scripts import get_account
from brownie import StakeToken, TokenFarm, network, config
from web3 import Web3

KEPT_BALANCE = Web3.toWei(100, "ether")

def deploy_token_farm_and_dapp_token():
    account = get_account()
    dapp_token = StakeToken.deploy({"from": account})
    token_farm = TokenFarm.deploy(dapp_token.address, {"from": account}, publish_source=config["networks"][network.show_active()].get("verify", False))
    tx = dapp_token.transfer(token_farm.address, dapp_token.totalSupply() - KEPT_BALANCE), {"from": accounts})
    tx.wait(1)

    weth_token = get_contract("weth_token")
    fau_token = get_contract("fau_token")
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed")
        fau_token: get_contract("dai_usd_price_feed")
        weth_token: get_contract("eth_usd_price_feed")
    }
    add_allowed_tokens(token_farm, dict_of_allowed_tokens ,account)

def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    pass

def main():
    deploy_token_farm_and_dapp_token()