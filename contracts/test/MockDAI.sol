// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "../node_modules/@openzeppelin/token/ERC20/ERC20.sol";

contract MockDai is ERC20 {
    constructor() public ERC20("Mock DAI", "DAI"){}
}