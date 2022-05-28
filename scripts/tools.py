from brownie import Wei, accounts, network, config, Contract, GovernanceToken
from scripts.abis import MintableERC20ABI


# Governance constants
MIN_DELAY = 600  # 10 minutes
VOTING_DELAY = 15  # blocks
VOTING_PERIOD = 20  # blocks
PROPOSAL_THRESHOLD = 0
QUORUM = 4

# token Addresses
dai_token = config["networks"][network.show_active()]["dai_token"]
link_token = config["networks"][network.show_active()]["link_token"]
aave_token = config["networks"][network.show_active()]["aave_token"]
SUPPORTED_TOKENS = [dai_token, link_token]

# proposal variables
description = (
    "PROPOSAL #1: I want the protocol to start supporting aave tokens...YUP!!!"
)

# AAVE addresses and contracts
POOL_ADDRESSES_PROVIDER = config["networks"][network.show_active()][
    "pool_addresses_provider"
]
DAI_CONTRACT = Contract.from_abi("DAI", dai_token, MintableERC20ABI)
LINK_CONTRACT = Contract.from_abi("LINK", link_token, MintableERC20ABI)
AAVE_CONTRACT = Contract.from_abi("AAVE", aave_token, MintableERC20ABI)


# custom forked environments
LOCAL_ENVIRONMENTS = ["rinkeby-fork", "mumbai-fork"]

# enum ProposalState {
#   Pending,
#   Active,
#   Canceled,
#   Defeated,
#   Succeeded,
#   Queued,
#   Expired,
#   Executed
# }


# switch accounts easily
def get_account(id=None, index=None):
    if network.show_active() in LOCAL_ENVIRONMENTS:
        return accounts[0]
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)


# mints aave mintable erc20 token for testing..
def mint_token(contract, account, amount=Wei("100 ether")):
    tx = contract.mint(account.address, amount, {"from": account})
    tx.wait(1)


# gets the asset ready for user to stake and interact...
def get_asset_ready(account):
    # we'll equip three accounts (Our main and two others) with 100 dai and link respectively.
    print("Funding the account 100 dai, link and aave...")
    # you could add more to this list francis...
    Contracts = [DAI_CONTRACT, LINK_CONTRACT, AAVE_CONTRACT]
    for Contract in Contracts:
        mint_token(Contract, account)

    print("funded!")


# helper function to distribute GT to different accounts
def distribute_governance_token(account, accounts1, accounts2, accounts3):
    addresses = [accounts1.address, accounts2.address, accounts3.address]
    print("Sharing governance tokens for delegating and voting for testing....")
    for address in addresses:
        tx = GovernanceToken[-1].transfer(address, Wei("200 ether"), {"from": account})
        tx.wait(1)
    print("Governance Token shared for testing!")


# delegate tokens for voting...
def delegate(account, account1, account2, account3):
    print("Accounts delegating their tokens...")
    tx_delegate = GovernanceToken[-1].delegate(account.address, {"from": account})
    tx_delegate.wait(1)

    tx_delegate = GovernanceToken[-1].delegate(account.address, {"from": account1})
    tx_delegate.wait(1)

    tx_delegate = GovernanceToken[-1].delegate(account.address, {"from": account2})
    tx_delegate.wait(1)

    tx_delegate = GovernanceToken[-1].delegate(account.address, {"from": account3})
    tx_delegate.wait(1)
    print("Accounts Delegated!")
