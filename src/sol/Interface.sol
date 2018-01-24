pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";
import {ControllerRoute} from "./ControllerRoute.sol";
import {UserController} from "./UserController.sol";

contract Interface is Pausable {
    ControllerRoute router;
    
    //event
    event InterfaceSetRouter(
        address origin, 
        address caller, 
        address controller_route_address
    );
    event InterfaceSetController(
        address origin,
        address caller,
        string controller_name,
        address controller_address
    );
    event WriteData(
        address origin,
        address caller,
        uint256 tx_hash,
        string types
    );
    
    function Interface(
        address _controller_route_address
    )
    public
    {
        require(_controller_route_address != address(0));
        router = ControllerRoute(_controller_route_address);
        
        // event
        InterfaceSetRouter(
            tx.origin, 
            msg.sender, 
            _controller_route_address
        );
    }
    
    function name(
    
    )
    whenNotPaused canCall public view 
    returns (
        bytes32
    )
    {
        return "Interface";
    }
    
    function setRouter(
        address _controller_route_address
    )
    whenNotPaused canWrite public
    {
        require(_controller_route_address != address(0));
        router = ControllerRoute(_controller_route_address);
        
        // event
        InterfaceSetRouter(
            tx.origin, 
            msg.sender, 
            _controller_route_address
        );
    }
    
    function setController(
        string _controller_name,
        address _contorller_address
    )
    whenNotPaused canWrite public
    {
        router.setAddress(_controller_name, _contorller_address, true);
    
        //event
        InterfaceSetController(
            tx.origin,
            msg.sender,
            _controller_name,
            _contorller_address
        );
    }
    
    function getControllerAddress(
        string _controller_name
    )
    whenNotPaused canCall public view
    returns (
        address
    )
    {
        return router.getCurrentAddress(_controller_name);
    }
    
    function _getUserController(
        string _controller_name
    )
    whenNotPaused canCall internal view
    returns (
        UserController user_controller
    )
    {
        address user_controller_address = getControllerAddress(_controller_name);
        require(user_controller_address != address(0));
        return UserController(user_controller_address);
    }
    
    function getUserContractAddress(
        string _controller_name,
        bytes32 _user_tag
    )
    whenNotPaused canCall public view
    returns (
        address
    )
    {
        return _getUserController(_controller_name).getUserContractAddress(_user_tag);
    }
    
    function getLoanTimes(
        string _controller_name,
        bytes32 _user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return _getUserController(_controller_name).getLoanTimes(_user_tag);
    }
    
    function getLatestUpdate(
        string _controller_name,
        bytes32 _user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        uint
    ) 
    {
        return _getUserController(_controller_name).getLatestUpdate(_user_tag);
    }
    
    function updateLoan(
        string _controller_name,
        bytes32 _user_tag,   // 用户唯一标识
        bytes32 _loan_tag,   // 借贷记录唯一标识
        bytes32 _platform,   // 平台
        uint32 _credit_limit // 授信额度
    ) 
    whenNotPaused canWrite public 
    {
        _getUserController(_controller_name).updateLoan(
            _user_tag, 
            _loan_tag, 
            _platform, 
            _credit_limit
        );
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateLoan"
        );
    }
    
    function getLoanByIndex(
        string _controller_name,
        bytes32 _user_tag,  // 用户唯一标识
        uint32 _index       // 插入借贷记录时的loanCounter值
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32, // 借贷记录唯一标识
        bytes32, // 平台
        uint32,  // 支用次数
        uint32   // 授信额度
    ) 
    {
        return _getUserController(_controller_name).getLoanByIndex(
            _user_tag, 
            _index
        );
    }
    
    function updateExpenditure(
        string _controller_name,
        bytes32 _user_tag,     // 用户唯一标识
        bytes32 _loan_tag,     // 借贷记录唯一标识
        bytes32 _expend_tag,   // 支用记录唯一标识
        bytes32 _order_number, // 订单号
        bytes32 _bank_card,    // 银行卡
        bytes32 _purpose,      // 用途
        uint32 _overdue_days,  // 逾期天数
        uint _apply_amount,    // 申请金额
        uint _receive_amount,  // 到账金额
        uint _apply_time,      // 日期
        uint _interest         // 利息
    ) 
    whenNotPaused canWrite public 
    {
        _getUserController(_controller_name).updateExpenditure(
            _user_tag,
            _loan_tag,
            _expend_tag,
            _order_number, 
            _bank_card, 
            _purpose, 
            _overdue_days,
            _apply_amount, 
            _receive_amount, 
            _apply_time, 
            _interest
        );
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateExpenditure"
        );
    }
    
    function getExpendByIndex(
        string _controller_name,
        bytes32 _user_tag,    // 用户唯一标识
        uint32 _loan_index,   // 插入借贷记录时的loanCounter值
        uint32 _expend_index  // 插入支用记录时的expenditureCounter值
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32,  // 支用记录唯一标识
        bytes32 , // 订单号
        bytes32 , // 银行卡
        bytes32 , // 用途
        uint32 ,  // 还款计划的条目数
        uint32 ,  // 还款次数
        uint32 ,  // 逾期天数
        uint,     // 申请金额
        uint,     // 到账金额
        uint,     // 日期
        uint      // 利息
    ) 
    {
        return _getUserController(_controller_name).getExpendByIndex(
            _user_tag, 
            _loan_index, 
            _expend_index
        );
    }
    
    function updateInstallment(
        string _controller_name,
        bytes32 _user_tag,          // 用户唯一标识
        bytes32 _loan_tag,          // 借贷记录唯一标识
        bytes32 _expend_tag,        // 支用记录唯一标识
        bytes32 _installment_tag,   // 还款计划记录唯一标识
        uint32 _installment_number, // 期数
        uint _repay_time,           // 还款时间
        uint _repay_amount          // 还款金额
    ) 
    whenNotPaused canWrite public 
    {
        _getUserController(_controller_name).updateInstallment(
            _user_tag,
            _loan_tag,
            _expend_tag,
            _installment_tag, 
            _installment_number, 
            _repay_time, 
            _repay_amount
        );
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateInstallment"
        );
    }
    
    function getInstallmentByIndex(
        string _controller_name,
        bytes32 _user_tag,          // 用户唯一标识
        uint32 _loan_index,       // 插入借贷记录时的loanCounter值
        uint32 _expend_index,     // 插入支用记录时的expenditureCounter值
        uint32 _installment_index // 插入还款计划记录时的installmentCounter值
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32, // 还款计划记录唯一标识
        uint32,  // 期数
        uint,    // 还款时间
        uint     // 还款金额
    ) 
    {
        return _getUserController(_controller_name).getInstallmentByIndex(
            _user_tag,
            _loan_index, 
            _expend_index,
            _installment_index
        );
    }
    
    function updateRepayment(
        string _controller_name,
        bytes32 _user_tag,          // 用户唯一标识
        bytes32 _loan_tag,          // 借贷记录唯一标识
        bytes32 _expend_tag,        // 支用记录唯一标识
        bytes32 _repayment_tag,     // 还款记录唯一标识
        uint32 _installment_number, // 期数
        uint32 _overdue_days,       // 逾期天数
        uint32 _repay_types,        // 还款类型
        uint _repay_amount,         // 还款金额
        uint _repay_time            // 还款时间
    ) 
    whenNotPaused canWrite public 
    {
        _getUserController(_controller_name).updateRepayment(
            _user_tag,
            _loan_tag,
            _expend_tag,
            _repayment_tag,
            _installment_number, 
            _overdue_days, 
            _repay_types, 
            _repay_amount, 
            _repay_time
        );
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateRepayment"
        );
    }
    
    function getRepaymentByIndex(
        string _controller_name,
        bytes32 _user_tag,          // 用户唯一标识
        uint32 _loan_index,     // 插入借贷记录时loanCounter的值
        uint32 _expend_index,   // 插入支用记录时expenditureCounter的值
        uint32 _repayment_index // 插入还款记录时repaymentCounter的值
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32, // 还款记录唯一标识
        uint32,  // 期数
        uint32,  // 逾期天数
        uint32,  // 还款类型
        uint,    // 还款金额
        uint     // 还款时间
    ) 
    {
        return _getUserController(_controller_name).getRepaymentByIndex(
            _user_tag,
            _loan_index, 
            _expend_index, 
            _repayment_index
        );
    }
}

