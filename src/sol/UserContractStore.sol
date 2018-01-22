pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";

contract UserContractStore is Pausable {

    // user_tag => version => user_contract_address
    mapping(bytes32 => mapping(uint32 => address)) store;
    
    // user_tag => current_version
    mapping(bytes32 => uint32) currentVersionStore;
    
    // user_tag => max_version
    mapping(bytes32 => uint32) maxVersionStore;
    
    event SetUserContractAddress(
        address origin, 
        address caller, 
        bytes32 user_tag, 
        uint32 version, 
        address user_contract_address
    );
    event SetUserContractCurrentVersion(
        address origin, 
        address caller, 
        bytes32 user_tag, 
        uint32 version
    );
    
    function name(
    
    )
    whenNotPaused canCall public view 
    returns (
        bytes32
    )
    {
        return "UserContractStore";
    }
    
    function setCurrentVersion(
        bytes32 user_tag, 
        uint32 version
    ) 
    whenNotPaused canWrite public 
    {
        currentVersionStore[user_tag]= version;
        SetUserContractCurrentVersion(tx.origin, msg.sender, user_tag, version);
    }
    
    function setAddress(
        bytes32 user_tag, 
        address user_contract_address, 
        bool set_current
    ) 
    whenNotPaused canWrite public 
    {
        
        uint32 assume_version = 0;
        
        // unique the user_contract_address
        uint32 max_version = maxVersionStore[user_tag];
        for (uint32 i=0; i <= max_version; i++) {
            if(store[user_tag][i] != user_contract_address) continue;
            assume_version = i;
        }
        
        // if the user_contract_address not exists, then put it into the store
        if(assume_version == 0) {
            assume_version = ++maxVersionStore[user_tag];
            store[user_tag][assume_version] = user_contract_address;
            SetUserContractAddress(tx.origin, msg.sender, user_tag, assume_version, user_contract_address);
        }
        
        if(set_current) {
            setCurrentVersion(user_tag, assume_version);
        }
    }
    
    function getCurrentVersion(
        bytes32 user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return currentVersionStore[user_tag];
    }
    
    function getMaxVersion(
        bytes32 user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return maxVersionStore[user_tag];
    }
    
    function getAddress(
        bytes32 user_tag, 
        uint32 version
    ) 
    whenNotPaused canCall public view 
    returns (
        address dest
    ) 
    {
        dest = store[user_tag][version];
    }
    
    function getCurrentAddress(
        bytes32 user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        address dest
    ) 
    {
        dest = getAddress(user_tag, getCurrentVersion(user_tag));
    }
}
