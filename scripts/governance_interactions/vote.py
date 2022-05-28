from brownie import GovernorContract, StakingContract
from scripts.tools import aave_token, description


def vote(proposalId, account, account1, account2, account3):
    print("Accounts Voting.....")
    vote_tx = GovernorContract[-1].castVote(proposalId, 1, {"from": account})
    vote_tx.wait(1)

    vote_tx = GovernorContract[-1].castVote(proposalId, 1, {"from": account1})
    vote_tx.wait(1)

    vote_tx = GovernorContract[-1].castVote(proposalId, 1, {"from": account2})
    vote_tx.wait(1)

    vote_tx = GovernorContract[-1].castVote(proposalId, 1, {"from": account3})
    vote_tx.wait(1)
    print("Accounts Voted!!")
