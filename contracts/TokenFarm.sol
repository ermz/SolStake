// stakeTokens
// unStakeTokens
// issueTokens
// addAllowedTokens
// getEthValue

// SPDX-License-Identifier: MIT

import "../node_modules/@openzeppelin/contracts/access/Ownable.sol";
import "../node_modules/@openzeppelin/contracts/token/ERC20/IERC20.sol";

pragma solidity ^0.8.0;

contract TokenFarm is Ownable{

    mapping(address => mapping(address => uint256)) public stakingBalance;
    address[] public allowedTokens;
    function stakeTokens(uint256 _amount, address _token) public {
        require(_amount > 0, "Amount must be more than 0");
        require(tokenIsAllowed(_token), "Token is currently not allowed");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount
    }

    function addAllowedTokens(address _token) public onlyOwner {
        allowedTokens.push(_token);
    }

    function tokenIsAllowed(address _token) public returns (bool) {
        for(uint256 allowedTokensIndex=0; allowedTokensIndex < allowedTokens.length; allowedTokensIndex++)
            if(allowedTokens[allowedTokensIndex] == _token) {
                return true;
            }
        return false;
    }
}