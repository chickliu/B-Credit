pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";

contract ControllerRoute is Pausable {

    // controller_name => version => address
    mapping(string => mapping(uint32 => address)) store;
    
    // controller_name => current_version
    mapping(string => uint32) currentVersionStore;
    
    // controller_name => max_version
    mapping(string => uint32) maxVersionStore;
    
    event SetControllerAddress(
        address origin, 
        address caller, 
        string controller_name, 
        uint32 version, 
        address controller_address
    );
    event SetControllerVersion(
        address origin, 
        address caller, 
        string controller_name, 
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
        string _controller_name, 
        uint32 _version
    ) 
    whenNotPaused canWrite public 
    {
        require(_version > 0 && _version <= maxVersionStore[_controller_name]);
        currentVersionStore[_controller_name]= _version;
        SetControllerVersion(tx.origin, msg.sender, _controller_name, _version);
    }
    
    function setAddress(
       string _controller_name, 
       address _controller_address, 
       bool set_current
    ) 
    whenNotPaused canWrite public 
    returns(
        uint32
    )
    {
        
        uint32 assume_version = 0;
        
        // unique the contract_address
        uint32 max_version = maxVersionStore[_controller_name];
        for (uint32 i=1; i <= max_version; i++) {
            if(store[_controller_name][i] != _controller_address) continue;
            assume_version = i;
        }
        
        // if the contract_address not exists, then put it into the store
        if(assume_version == 0) {
            assume_version = ++maxVersionStore[_controller_name];
            store[_controller_name][assume_version] = _controller_address;
            
            SetControllerAddress(
                tx.origin, 
                msg.sender, 
                _controller_name, 
                assume_version, 
                _controller_address
            );
        }
        
        if(set_current) {
            setCurrentVersion(_controller_name, assume_version);
        }
        
        return assume_version;
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


