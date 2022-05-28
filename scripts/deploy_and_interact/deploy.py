from brownie import (
    StakingContract,
    GovernorContract,
    TimeLock,
    GovernanceToken,
    BonusToken,
    accounts,
    chain,
    network,
)
from web3 import Web3
from scripts.tools import (
    AAVE_CONTRACT,
    DAI_CONTRACT,
    LINK_CONTRACT,
    LOCAL_ENVIRONMENTS,
    MIN_DELAY,
    PROPOSAL_THRESHOLD,
    QUORUM,
    VOTING_DELAY,
    VOTING_PERIOD,
    delegate,
    distribute_governance_token,
    get_account,
    POOL_ADDRESSES_PROVIDER,
    get_asset_ready,
)
from scripts.governance_interactions.propose import propose
from scripts.governance_interactions.vote import vote
from scripts.governance_interactions.queue_and_execute import queue, execute
from scripts.deploy_and_interact.interact import (
    get_assets_price,
    stake_asset,
    borrow_from_aave,
    repay_loan_through_aave,
    withdraw_form_aave,
    get_my_data,
)


# get account for easily switching from development to live
acct = get_account()

# for
def deploy():
    print(f"Deploying Governance Token..")
    GOVERNANCE_TOKEN = GovernanceToken.deploy({"from": acct})

    print("Deploying TimeLock...")
    TIME_LOCK = TimeLock.deploy(MIN_DELAY, [], [], {"from": acct})

    governance_token_balance = Web3.toWei(
        GovernanceToken[-1].balanceOf(accounts[1].address), "ether"
    )
    print(f"Balance of Deployer: {governance_token_balance}")

    print("Deploying Governor contract...")
    GOVERNOR_CONTRACT = GovernorContract.deploy(
        GOVERNANCE_TOKEN.address,
        TIME_LOCK.address,
        VOTING_DELAY,
        VOTING_PERIOD,
        PROPOSAL_THRESHOLD,
        QUORUM,
        {"from": acct},
    )

    print("Assigning Roles and revoking admin role....")
    admin_role = TIME_LOCK.TIMELOCK_ADMIN_ROLE()
    proposer_role = TIME_LOCK.PROPOSER_ROLE()
    executor_role = TIME_LOCK.EXECUTOR_ROLE()

    tx_propser_role = TIME_LOCK.grantRole(
        proposer_role, GOVERNOR_CONTRACT, {"from": acct}
    )
    tx_propser_role.wait(1)
    tx_exeuctor_role = TIME_LOCK.grantRole(
        executor_role, "0x0000000000000000000000000000000000000000", {"from": acct}
    )
    tx_exeuctor_role.wait(1)
    tx_revoke_role = TIME_LOCK.revokeRole(admin_role, acct.address, {"from": acct})
    tx_revoke_role.wait(1)

    print("Deploying BonusToken...")
    BONUS_TOKEN = BonusToken.deploy("Bonus", "BTK", {"from": acct})

    print("Deploying StakingContract...")
    STAKING_CONTRACT = StakingContract.deploy(
        BONUS_TOKEN.address,
        POOL_ADDRESSES_PROVIDER,
        DAI_CONTRACT.address,
        LINK_CONTRACT.address,
        {"from": acct},
    )

    print("Transferring Ownership of staking contract from deployer to timelock...")
    print()
    tx = STAKING_CONTRACT.transferOwnership(TIME_LOCK.address, {"from": acct})
    tx.wait(1)
    print(f"New StakingContract Owner: {TIME_LOCK.address}")

    print(
        "Tranferring Ownership of BonusToken contract from deployer to Staking contract..."
    )
    tx_ownerTranfer = BONUS_TOKEN.transferOwnership(
        STAKING_CONTRACT.address, {"from": acct}
    )
    tx_ownerTranfer.wait(1)

    print("Setup Completed... Awesome!!")

    # get_my_data()
    return STAKING_CONTRACT, BONUS_TOKEN


def governance_process():
    proposal_id = propose(accounts[1])
    # share governance tokens to different accounts
    distribute_governance_token(acct, accounts[1], accounts[2], accounts[3])
    print(f"Proposal State: {GovernorContract[-1].state(proposal_id) }")
    # delegating tokens for voting...
    delegate(acct, accounts[1], accounts[2], accounts[3])

    # skip voting delay on our local mumbai fork by mining blocks...
    if network.show_active() in LOCAL_ENVIRONMENTS:
        print("Skipping voting delay...")
        chain.mine(15)  # our voting delay was 273 blocks
    # checking the proposal state..
    print(f"Proposal State: {GovernorContract[-1].state(proposal_id) }")
    # Time to Vote!!
    vote(proposal_id, acct, accounts[1], accounts[2], accounts[3])

    # time to skip voting period locally..
    if network.show_active() in LOCAL_ENVIRONMENTS:
        print("Skipping voting period....")
        chain.mine(21)

    # checking proposal state again..
    print(f"Proposal State: {GovernorContract[-1].state(proposal_id) }")
    # queueing proposal
    queue(acct)
    # giving time fornusers to exit if they dont like the proposla with our minimum delay..
    print("Skipping min delay...")
    chain.sleep(601)  # our min delay was 600 seconds...
    # executing proposal because it was accepted
    execute(accounts[0], proposal_id)
    print(f"Proposal State: {GovernorContract[-1].state(proposal_id) }")


def interactions():
    amount_to_stake = Web3.toWei(100, "ether")
    get_my_data(acct)
    # we mint some dai, link and aave to ourselves to stake....
    get_asset_ready(acct)
    # we get the price, stake and get our data every time we interact....
    # for more in depth reasons on the amounts we used and why I used em...
    # check the bottom of this code.
    get_assets_price(
        [DAI_CONTRACT.address, LINK_CONTRACT.address, AAVE_CONTRACT.address]
    )
    stake_asset(AAVE_CONTRACT, amount_to_stake, acct, "AAVE")
    get_my_data(acct)
    borrow_from_aave(acct, DAI_CONTRACT, Web3.toWei(72, "ether"))
    # Our dai balance should increase with + 72 dai
    print(f"DAI balance: {DAI_CONTRACT.balanceOf(acct.address)}")
    get_my_data(acct)
    # we repay our loan...
    repay_loan_through_aave(acct, DAI_CONTRACT, Web3.toWei(72, "ether"))
    get_my_data(acct)
    # we withdraw our deposit not all because we had some interest on our borrow
    withdraw_form_aave(acct, AAVE_CONTRACT, Web3.toWei(90, "ether"))
    get_my_data(acct)
    borrow_from_aave(acct, DAI_CONTRACT, Web3.toWei(10, "ether"))

    # AWESOME!


def main():
    deploy()
    governance_process()
    interactions()
    # we just used our contract to allow us stake aave tokens which wasnt allowed previously through governance
    # we then recevied our bonus tokens
    # went straight to aave and borrowe
    # we repaid and withdraw our funds!!


# CALCULATIONS

# I brought these our to be able to do calculations and borrow a different asset(ALL OUR CALCULATIONS ARE IN WEI)
# And yes! Its Francis who's writing this, feel free to make contributons to better ways to do this.

# These are the price of the three assets we have in wei in the markets base currency (i'm assumng USD).
# got this from aave price oracle interface because the chainlink mumbai prices don't add up.
# I suppose they're different on mumbai.
# DAI: 100000000, LINK: 3000000000 and  AAVE:30000000000 (all in 8 decimals USD)

# This is our account data after staking 100 AAVE tokens
# I left out the health factor because its some crazy number.. :D
# Collateral: 3000000000000, Debt: 0, Borrowable: 1800000000000, liquidation Threshold: 7000,
# LTV: 6000

# So if we want to borrow some dai and stay on the safe side... Say 40% of our borrowable
# AAVE uses 8 decimals for their base currency(USD). So we even things out then get the wei value
# 40% of our borrowable = 1800000000000/10**10 * 0.40 = 72 USD
# If we're to borrow this amount in dai. It'll be
# 1 dai = 1 usd
# X dai = 72
# amount of dai' we're borrowing = 72 dai = 72 * 10**18 wei

# Then we repay back the same amount and wthdraw our collateral in aave
# which was our amount_to_stake minus some tiny amount to cover for our loan intererst
