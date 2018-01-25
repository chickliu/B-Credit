pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";
import {LoanContractRoute} from "./LoanContractRoute.sol";
import {UserLoan} from "./UserLoan.sol";

contract LoanController is Pausable {

    LoanContractRoute router;
    
    //event
    event LoanControllerSetRouter(
        address origin, 
        address caller, 
        address loan_contract_route_address
    );
    
    function LoanController(
        address _loan_contract_route_address
    )
    public
    {
        require(_loan_contract_route_address != address(0));
        
        router = LoanContractRoute(_loan_contract_route_address);
        
        //event
        LoanControllerSetRouter(
            tx.origin,
            msg.sender,
            _loan_contract_route_address
        );
    }
    
    function name(
    
    )
    whenNotPaused canCall public view 
    returns (
        bytes32
    )
    {
        return "LoanController";
    }
    
    function setLoanContractRoute(
        address _loan_contract_route_address
    ) 
    whenNotPaused onlyAdmin public 
    {
        router = LoanContractRoute(_loan_contract_route_address);
        
        //event
        LoanControllerSetRouter(
            tx.origin,
            msg.sender,
            _loan_contract_route_address
        );
    }
    
    function getLoanContractRouteAddress(
    
    )
    whenNotPaused canCall public view
    returns(
        address
    )
    {
        return router;
    }
    
    function getLoanContractVersion(
        bytes32 _user_tag
    )
    whenNotPaused canCall public view
    returns(
        uint32
    )
    {
        return router.getCurrentVersion(_user_tag);
    }
    
    function getLoanContractAddress(
        bytes32 _user_tag
    )
    whenNotPaused canCall public view
    returns (
        address
    )
    {
        return router.getCurrentAddress(_user_tag);
    }
    
    function _getLoanContract(
        bytes32 _user_tag
    )
    whenNotPaused canCall internal view
    returns (
        UserLoan user_contract
    )
    {
        address loan_contract_address = getLoanContractAddress(_user_tag);
        require(loan_contract_address != address(0));
        return UserLoan(loan_contract_address);
    }
    
    function getUserLoanStoreRouteAddress(
        bytes32 _user_tag
    )
    whenNotPaused canCall public view
    returns(
        address
    )
    {
        return _getLoanContract(_user_tag).getUserLoanStoreRouteAddress();
    }
    
    function getUserLoanStoreVersion(
        bytes32 _user_tag
    )
    whenNotPaused canCall public view
    returns(
        uint32
    )
    {
        return _getLoanContract(_user_tag).getUserLoanStoreVersion();
    }
    
    function getUserLoanStoreAddress(
        bytes32 _user_tag
    )
    whenNotPaused canCall public view
    returns (
        address
    )
    {
        return _getLoanContract(_user_tag).getUserLoanStoreAddress();
    }
    
    function getLoanTimes(
        bytes32 _user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return _getLoanContract(_user_tag).getLoanTimes();
    }
    
    function getLatestUpdate(
        bytes32 _user_tag
    ) 
    whenNotPaused canCall public view 
    returns (
        uint
    ) 
    {
        return _getLoanContract(_user_tag).getLatestUpdate();
    }
    
    function updateLoan(
        bytes32 _user_tag,   // 用户唯一标识
        bytes32 _loan_tag,   // 借贷记录唯一标识
        bytes32 _platform,   // 平台
        uint32 _credit_limit // 授信额度
    ) 
    whenNotPaused canWrite public 
    {
        _getLoanContract(_user_tag).updateLoan(_loan_tag, _platform, _credit_limit);
    }
    
    function getLoanByIndex(
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
        return _getLoanContract(_user_tag).getLoanByIndex(_index);
    }
    
    function updateExpenditure(
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
        _getLoanContract(_user_tag).updateExpenditure(
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
    }
    
    function getExpendByIndex(
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
       return _getLoanContract(_user_tag).getExpendByIndex(_loan_index, _expend_index);
    }
    
    function updateInstallment(
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
        _getLoanContract(_user_tag).updateInstallment(
            _loan_tag,
            _expend_tag,
            _installment_tag, 
            _installment_number, 
            _repay_time, 
            _repay_amount
        );
    }
    
    function getInstallmentByIndex(
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
        return _getLoanContract(_user_tag).getInstallmentByIndex(
            _loan_index, 
            _expend_index,
            _installment_index
        );
    }
    
    function updateRepayment(
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
        _getLoanContract(_user_tag).updateRepayment(
            _loan_tag,
            _expend_tag,
            _repayment_tag,
            _installment_number, 
            _overdue_days, 
            _repay_types, 
            _repay_amount, 
            _repay_time
        );
    }
    
    function getRepaymentByIndex(
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
        return _getLoanContract(_user_tag).getRepaymentByIndex(
            _loan_index, 
            _expend_index, 
            _repayment_index
        );
    }
}

