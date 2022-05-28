from brownie import GovernorContract, StakingContract, config, network
from scripts.tools import aave_token, description


def propose(account):
    encoded_function = StakingContract[0].addToken.encode_input(aave_token)
    print(f"Encoded Function: {encoded_function}")
    print("Making Proposal...")
    propose_tx = GovernorContract[-1].propose(
        [StakingContract[-1].address],
        [0],
        [encoded_function],
        description,
        {"from": account},
    )
    propose_tx.wait(1)
    proposal_id = propose_tx.return_value
    print("Proposal Submitted!")
    return proposal_id
