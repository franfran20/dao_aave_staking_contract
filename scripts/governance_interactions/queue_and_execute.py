from brownie import StakingContract, GovernorContract, accounts, chain
from web3 import Web3
from scripts.tools import aave_token, description


def execute(account, proposalId):
    encoded_function = StakingContract[-1].addToken.encode_input(aave_token)
    description_hash = Web3.keccak(text=description)
    print(f"Is aave supported: {StakingContract[-1].isSupported(aave_token)}")
    print("EXECUTING...")
    tx_execute = GovernorContract[-1].execute(
        [StakingContract[-1].address],
        [0],
        [encoded_function],
        description_hash,
    )
    tx_execute.wait(1)
    print("PROPOSAL EXECUTED!")
    print(f"Is AAVE TOKEN supported: {StakingContract[-1].isSupported(aave_token)}")


def queue(acct):
    encoded_function = StakingContract[-1].addToken.encode_input(aave_token)
    description_hash = Web3.keccak(text=description).hex()
    print(f"Description Hash: {description_hash}")
    print("Queuing Proposal...")
    tx_queue = GovernorContract[-1].queue(
        [StakingContract[-1].address],
        [0],
        [encoded_function],
        description_hash,
        {"from": acct},
    )
    tx_queue.wait(1)
    print("Queued!")
