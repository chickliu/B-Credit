pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";

contract ControllerRoute is Pausable {

    // contract_name => version => address
    mapping(string => mapping(uint32 => address)) store;
    
    // contract_name => current_version
    mapping(string => uint32) currentVersionStore;
    
    // contract_name => max_version
    mapping(string => uint32) maxVersionStore;
    
    event SetContractAddress(
        address origin, 
        address caller, 
        string contract_name, 
        uint32 version, 
        address contract_address
    );
    event SetContractCurrentVersion(
        address origin, 
        address caller, 
        string contract_name, 
        uint32 version
    );
    
    function name(
    
    )
    whenNotPaused canCall public view 
    returns (
        string
    )
    {
        return "ControllerRoute";
    }
    
    function setCurrentVersion(
        string contract_name, 
        uint32 version
    ) 
    whenNotPaused canWrite public 
    {
        currentVersionStore[contract_name]= version;
        SetContractCurrentVersion(tx.origin, msg.sender, contract_name, version);
    }
    
    function setAddress(
       string contract_name, 
       address contract_address, 
       bool set_current
    ) 
    whenNotPaused canWrite public 
    {
        
        uint32 assume_version = 0;
        
        // unique the contract_address
        uint32 max_version = maxVersionStore[contract_name];
        for (uint32 i=0; i <= max_version; i++) {
            if(store[contract_name][i] != contract_address) continue;
            assume_version = i;
        }
        
        // if the contract_address not exists, then put it into the store
        if(assume_version == 0) {
            assume_version = ++maxVersionStore[contract_name];
            store[contract_name][assume_version] = contract_address;
            SetContractAddress(tx.origin, msg.sender, contract_name, assume_version, contract_address);
        }
        
        if(set_current) {
            setCurrentVersion(contract_name, assume_version);
        }
    }
    
    function getCurrentVersion(
        string contract_name
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return currentVersionStore[contract_name];
    }
    
    function getMaxVersion(
        string contract_name
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return maxVersionStore[contract_name];
    }
    
    function getAddress(
        string contract_name, 
        uint32 version
    ) 
    whenNotPaused canCall public view 
    returns (
        address dest
    ) 
    {
        dest = store[contract_name][version];
    }
    
    function getCurrentAddress(
        string contract_name
    ) 
    whenNotPaused canCall public view 
    returns (
        address dest
    ) 
    {
        dest = getAddress(contract_name, currentVersionStore[contract_name]);
    }
}


