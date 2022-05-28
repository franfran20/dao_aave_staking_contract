//SPDX-License-Identifier: MIT

pragma solidity 0.8.10;

import "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";

contract BonusToken is ERC20, Ownable{
    uint256 s_supply = 1000000e18;

    constructor (string memory _name, string memory _symbol) ERC20(_name, _symbol){}

    //we transfer ownership to contract after deployment
    function mint(address _to, uint256 _amount) public onlyOwner{
        require(_amount <= s_supply, "Maximum Supply Hit");
        _mint(_to, _amount);
    }
}