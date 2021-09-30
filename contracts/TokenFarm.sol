// stakeTokens
// unStakeTokens
// issueTokens
// addAllowedTokens
// getEthValue

// SPDX-License-Identifier: MIT

import "../node_modules/@openzeppelin/contracts/access/Ownable.sol";
import "../node_modules/@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@chainlink/contracts/src/v0.8/interfaces/AggregatorV3Interface.sol";

pragma solidity ^0.8.0;

contract TokenFarm is Ownable{

    mapping(address => mapping(address => uint256)) public stakingBalance;
    mapping(address => uint256) public uniqueTokensStaked;
    mapping(address => address) public tokenPriceFeedMapping;
    address[] public stakers;
    address[] public allowedTokens;
    IERC20 public dappToken;

    constructor(address _dappTokenAddress) public {
        dappToken = IERC20(_dappTokenAddress);
    }

    function setPriceFeedContract(address _token, address _priceFeed) public onlyOwner {
        tokenPriceFeedMapping[_token] = _priceFeed
    }

    function issueTokens() public onlyOwner {
        for (uint256 stakersIndex = 0; stakersIndex < stakers.length; stakersIndex++){
            address recipient = stakers[stakersIndex];
            uint256 userTotalValue = getUserTotalValue(recipient);
            dappToken.transfer(recipient, userTotalValue);
        }
    }

    function getUserTotalValue(address _user) public view returns (uint256) {
        uint256 totalValue = 0;
        require(uniqueTokensStaked[_user] > 0, "No tokens staked");
        for (uint256 allowedTokensIndex = 0; allowedTokensIndex < allowedTokens.length; allowedTokensIndex++) {
            totalValue = totalValue = totalValue + getUserSingleTokenValue(_user, allowedTokens[allowedTokensIndex])
        }
        return totalValue;
    }

    function getUserSingleTokenValue(address _user, address _token) public view returns (uint256) {
        if (uniqueTokensStaked[_user] <= 0) {
            return 0;
        }

        (uint256 price, uint256 decimals) = getTokenValue(_token);
        // 1000000000000000000000 ETH
        // ETH/USD -> 1000000000
        // 10 * 100 = 1,000
        return (stakingBalance[token][user] * price / 10**decimals);
    }

    function getTokenValue(address _token) public view returns (uint256, uint256) {
        address priceFeedAddress = tokenPriceFeedMapping[_token];
        AggregatoreV3Interface priceFeed = AggregatorV3Interface(priceFeedAddress);
        (,int126 price,,,) = priceFeed.latestRoundData();
        uint256 decimals = uint256(priceFeed.decimals());
        return (uint256(price), decimals)
    }

    function stakeTokens(uint256 _amount, address _token) public {
        require(_amount > 0, "Amount must be more than 0");
        require(tokenIsAllowed(_token), "Token is currently not allowed");
        IERC20(_token).transferFrom(msg.sender, address(this), _amount);
        updateUniqueTokensStaked(msg.sender, _token);
        stakingBalance[_token][msg.sender] = stakingBalance[_token][msg.sender] + _amount;
        if (uniqueTokensStaked[msg.sender] == 1) {
            stakers.push(msg.sender);
        }
    }

    function updateUniqueTokensStaked(address _user, address _token) internal {
        if (stakingBalance[_token][_user] <= 0) {
            uniqueTokensStaked[_user] = uniqueTokensStaked[_user] + 1;
        }
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