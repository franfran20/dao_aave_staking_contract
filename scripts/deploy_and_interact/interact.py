from brownie import StakingContract, config, network, interface, accounts
from web3 import Web3
from scripts.tools import DAI_CONTRACT


pool_address_provider = interface.IPoolAddressesProvider(
    config["networks"][network.show_active()]["pool_addresses_provider"]
)
pool = interface.IPool(pool_address_provider.getPool())
aave_oracle = interface.IAaveOracle(
    config["networks"][network.show_active()]["aave_oracle"]
)


def get_my_data(acct):
    (
        collateral,
        debt,
        borrowable,
        liquidation_threshold,
        ltv,
        health_factor,
    ) = pool.getUserAccountData(acct.address, {"from": acct})
    print(
        f"Collateral: {collateral}, Debt: {debt}, Borrowable: {borrowable}, liquidation Threshold: {liquidation_threshold}, LTV: {ltv}, health factor: {health_factor}, for {acct.address}"
    )
    return borrowable


def stake_asset(contract, amount_to_stake, acct, assetName=None):
    print(f"staking {amount_to_stake} of {assetName}...")
    print(f" Balance of acct: {contract.balanceOf(acct.address)}")
    STAKING_CONTRACT = StakingContract[-1]

    tx = contract.approve(STAKING_CONTRACT.address, amount_to_stake, {"from": acct})
    tx.wait(1)
    tx_supply_asset = STAKING_CONTRACT.stakeAsset(
        amount_to_stake, contract.address, {"from": acct}
    )
    tx_supply_asset.wait(1)
    print(f"Staked {amount_to_stake}!")


def withdraw_form_aave(acct, contract, amount):
    print("Withdrawing...")
    tx_withdraw_from_aave = pool.withdraw(
        contract.address, amount, acct.address, {"from": acct}
    )
    tx_withdraw_from_aave.wait(1)
    print("Succesful!")


def borrow_from_aave(acct, contract, amount):
    print("Borrowing...")
    tx_borrow_from_aave = pool.borrow(
        contract.address, amount, 1, 0, acct.address, {"from": acct}
    )
    tx_borrow_from_aave.wait(1)
    print("Borrowed!")


def repay_loan_through_aave(acct, contract, amount):
    tx_approve = contract.approve(pool.address, amount, {"from": acct})
    tx_approve.wait(1)
    print("Repaying...")
    tx_repay_loan = pool.repay(
        contract.address, amount, 1, acct.address, {"from": acct}
    )
    tx_repay_loan.wait(1)
    print("Repaid!")


def get_assets_price(arr_token_addresses):
    # this function uses the aave oracle interfae to get the price of each asset in the base currency of the market.
    token_prices = aave_oracle.getAssetsPrices(arr_token_addresses)
    print(
        f"The price the respective asset(s): DAI: {token_prices[0]}, LINK: {token_prices[1]} and  AAVE:{token_prices[2]}"
    )
    return token_prices
