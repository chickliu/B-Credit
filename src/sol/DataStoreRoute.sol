pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";

contract DataStoreRoute is Pausable {

    // contract_address => version => data_store_address
    mapping(address => mapping(uint32 => address)) store;
    
    // contract_address => current_version
    mapping(address => uint32) currentVersionStore;
    
    // contract_address => max_version
    mapping(address => uint32) maxVersionStore;
    
    event SetDataStoreAddress(
        address origin, 
        address caller, 
        address data_owner, 
        uint32 version, 
        address data_address
    );
    event SetDataStoreCurrentVersion(
        address origin, 
        address caller, 
        address data_owner, 
        uint32 version
    );
    
    function name(
    
    )
    whenNotPaused canCall public view 
    returns (
        bytes32
    )
    {
        return "DataStoreRoute";
    }
    
    function setCurrentVersion(
        address data_owner, 
        uint32 version
    ) 
    whenNotPaused canWrite public 
    {
        currentVersionStore[data_owner]= version;
        SetDataStoreCurrentVersion(tx.origin, msg.sender, data_owner, version);
    }
    
    function setAddress(
        address data_owner, 
        address data_address, 
        bool set_current
    ) 
    whenNotPaused canWrite public 
    {
        
        uint32 assume_version = 0;
        
        // unique the data_address
        uint32 max_version = maxVersionStore[data_owner];
        for (uint32 i=0; i <= max_version; i++) {
            if(store[data_owner][i] != data_address) continue;
            assume_version = i;
        }
        
        // if the data_address not exists, then put it into the store
        if(assume_version == 0) {
            assume_version = ++maxVersionStore[data_owner];
            store[data_owner][assume_version] = data_address;
            SetDataStoreAddress(tx.origin, msg.sender, data_owner, assume_version, data_address);
        }
        
        if(set_current) {
            setCurrentVersion(data_owner, assume_version);
        }
    }
    
    function getCurrentVersion(
        address data_owner
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return currentVersionStore[data_owner];
    }
    
    function getMaxVersion(
        address data_owner
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return maxVersionStore[data_owner];
    }
    
    function getAddress(
        address data_owner, 
        uint32 version
    ) 
    whenNotPaused canCall public view 
    returns (
        address dest
    ) 
    {
        dest = store[data_owner][version];
    }
    
    function getCurrentAddress(
        address data_owner
    ) 
    whenNotPaused canCall public view 
    returns (
        address dest
    ) 
    {
        dest = getAddress(data_owner, getCurrentVersion(data_owner));
    }
}

