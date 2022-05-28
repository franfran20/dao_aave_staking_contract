//SPDX-License-Identifier: MIT

pragma solidity 0.8.10;

import "@aave/contracts/interfaces/IPool.sol";
import "@aave/contracts/interfaces/IPoolAddressesProvider.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./BonusToken.sol";


contract StakingContract is ReentrancyGuard, Ownable{
    error TokenNotSupported(address tokenAddress );
    error MultipleIdenticalTokens(address tokenAddress);

    IPool pool;
    BonusToken bonusToken;
    IPoolAddressesProvider poolAddressProvider;
    //supported tokens ahve to be supported by aave, there'll be a governance method to add or remove.
    mapping(address => bool) public isSupported;

    constructor (address _bonusToken, address _IPoolAddressesProvider, address _dai, address _link) public {
        
        isSupported[_dai] = true;
        isSupported[_link] = true;
        
        poolAddressProvider = IPoolAddressesProvider(_IPoolAddressesProvider);
        address poolAddress = poolAddressProvider.getPool();
        pool = IPool(poolAddress);
        bonusToken = BonusToken(_bonusToken);
    }
    
    //stakes tokens into aave from our contract
    //why not just go through aave?? You get a bonus(reward) for staking through us!!
    function stakeAsset(uint256 _amount, address _token) public{
        require(_amount > 0, "InsufficientTokenAmount");
        require(_token != address(0), "Invalid Address");
        if(!isSupported[_token]){
            revert TokenNotSupported(_token);
        }
        //stake more than 10 of any token through us and get the reward...
        if(_amount > 10e18){
            bonusToken.mint(msg.sender, 200e18);
        }
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        IERC20(_token).approve(address(pool), _amount);
        pool.supply(_token, _amount, msg.sender, 0);
    }


    //DAO FUNCTIONS
    function addToken(address _token) public onlyOwner {
        require(!isSupported[_token], "Token already in Platform!");
        isSupported[_token] = true;
    }

    function removeToken(address _token) public onlyOwner {
        require(isSupported[_token], "Token is not in Platform!");
        isSupported[_token] = false;
    }

}
