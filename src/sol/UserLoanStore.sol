pragma solidity ^0.4.18;

import {Pausable} from "./Pausable.sol";

contract UserLoanStore is Pausable {

    uint32 private loanCounter; // 借贷次数
    uint private latestUpdate;  // 最新的blockNumber, 用以指示最后的更改

    bytes32 private userTag;    // 用户信息使用keccak_256计算后的bytes
    
    event WriteData(
        address origin,
        address caller,
        uint256 block_number,
        string types
    );
    
    struct installment {
        uint32 installmentNumber; // 期数

        bytes32 installmentTag;   // 还款计划标识(可使用platform+recordId作为这个标识)使用keccak_256计算后的bytes

        uint repayTime;           // 还款时间
        uint repayAmount;         // 还款金额
    }
    
    struct repayment {
        uint32 repayTypes;        // 还款类型
        uint32 installmentNumber; // 期数
        uint32 overdueDays;       // 逾期天数

        bytes32 repaymentTag;     // 还款信息标识(可使用platform+recordId作为这个标识)使用keccak_256计算后的bytes

        uint repayAmount;         // 还款金额
        uint repayTime;           // 还款时间
    }
    
    struct expenditure {
        uint32 installmentCounter; // 分期数
        uint32 repaymentCounter;   // 还款次数
        uint32 overdueDays;        // 逾期天数

        bytes32 orderNumber;       // 订单号
        bytes32 bankCard;          // 银行卡
        bytes32 purpose;           // 用途
        bytes32 expendTag;         // 支用信息标识(可使用platform+recordId作为这个标识)使用keccak_256计算后的bytes

        uint applyAmount;          // 申请金额
        uint receiveAmount;        // 到账金额
        uint applyTime;            // 日期利息
        uint interest;             // 利息
        
        // 使用两个mapping的目的是为了方便既可以使用Counter来获取数据，也可以使用tag来更新或获取数据
        mapping(uint32 => installment) installments;  // 还款分期计划, installmentCounter和installment的映射关系
        mapping(bytes32 => uint32) installmentsIndex; // installmentTag与installmentCounter的映射关系
        
        mapping(uint32 => repayment) repayments;    // 还款记录, repaymentCounter和repayment的映射关系
        mapping(bytes32 => uint32) repaymentsIndex; // repaymentTag与repaymentCounter的映射关系
    }
    
    struct loan {
        uint32 expenditureCounter; // 支用次数
        uint32 creditLimit;        // 授信额度

        bytes32 platform;          // 平台
        bytes32 loanTag;           // 借贷信息标识(可使用platform+recordId作为这个标识)使用keccak_256计算后的bytes
        
        mapping(uint32 => expenditure) expenditures;  // 支用记录, expenditureCounter和expenditure的映射关系
        mapping(bytes32 => uint32) expendituresIndex; // expendTag与expenditure的映射关系
    }
    
    mapping(uint32 => loan) loans;         // 借贷记录, loanCounter和loan的映射关系
    mapping(bytes32 => uint32) loansIndex; // loanTag和loanCounter的映射关系
    
    function UserLoanStore(
        bytes32 _user_tag
    ) 
    public 
    {
        userTag = _user_tag;
    }
    
    function name(
    
    )
    whenNotPaused canCall public view 
    returns (
        bytes32
    )
    {
        return "UserLoanStore";
    }
    
    function getUserTag(
    
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32
    ) 
    {
        return userTag;
    }
    
    function getLoanTimes(
    
    ) 
    whenNotPaused canCall public view 
    returns (
        uint32
    ) 
    {
        return loanCounter;
    }
    
    function getLatestUpdate(
    
    ) 
    whenNotPaused canCall public view 
    returns (
        uint
    ) 
    {
        return latestUpdate;
    }
    
    function insertLoan(
        bytes32 _loan_tag,   // 借贷记录唯一标识
        bytes32 _platform,   // 平台
        uint32 _credit_limit // 授信额度
    ) 
    whenNotPaused internal 
    {
        //create a new storage loan
        loan storage _loan = loans[++loanCounter];
        
        _loan.loanTag = _loan_tag;
        _loan.platform = _platform;
        _loan.creditLimit = _credit_limit;
        
        // save this counter index
        loansIndex[_loan_tag] = loanCounter;
        
        // notify watchers of this update
        latestUpdate = block.number;
    }
    
    function updateLoan(
        bytes32 _loan_tag,   // 借贷记录唯一标识
        bytes32 _platform,   // 平台
        uint32 _credit_limit // 授信额度
    ) 
    whenNotPaused canWrite public 
    {
        uint32 _loanIndex = loansIndex[_loan_tag];
        
        // if the _loanTag not exists, insert it; else update it.
        if (_loanIndex == 0) {
        
            insertLoan(
                _loan_tag, 
                _platform,
                _credit_limit
            );
        
        } else {
            
            loan storage _loan = loans[_loanIndex];
            
            _loan.platform = _platform; 
            _loan.creditLimit = _credit_limit; 

            latestUpdate = block.number; 
        }
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateLoan"
        );
    }
    
    function _getLoanByIndex(
        uint32 _index
    ) 
    whenNotPaused internal view 
    returns (
        loan storage _loan
    ) 
    {
        require(0 < _index && _index <= loanCounter);
        _loan = loans[_index];
    }
    
    function _getLoanByTag(
        bytes32 _loan_tag
    ) 
    whenNotPaused internal view 
    returns (
        loan storage _loan
    ) 
    {
        _loan = _getLoanByIndex(loansIndex[_loan_tag]);
    }
    
    function getLoanByIndex(
        uint32 _index
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32, // 借贷记录唯一标识
        bytes32, // 平台
        uint32,  // 支用次数
        uint32   // 授信额度
    ) 
    {
        require(0 < _index && _index <= loanCounter);
        loan storage _loan = loans[_index];
        return (
            _loan.loanTag,
            _loan.platform, 
            _loan.expenditureCounter, 
            _loan.creditLimit
        );
    }
        
    function insertExpenditure(
        loan storage _loan, 
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
    whenNotPaused internal 
    {
        // create a storage expenditure
        expenditure storage _expend = _loan.expenditures[++_loan.expenditureCounter];
        
        _expend.applyAmount = _apply_amount;
        _expend.receiveAmount = _receive_amount;
        _expend.applyTime = _apply_time;
        _expend.interest = _interest;
        _expend.orderNumber = _order_number;
        _expend.bankCard = _bank_card;
        _expend.purpose = _purpose;
        _expend.overdueDays = _overdue_days;
        _expend.expendTag = _expend_tag;

        _loan.expendituresIndex[_expend_tag] = _loan.expenditureCounter;
        
        latestUpdate = block.number;
    }
    
    function updateExpenditure(
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
        loan storage _loan = _getLoanByTag(_loan_tag);
        uint32 _expendIndex = _loan.expendituresIndex[_expend_tag];
        
        if (_expendIndex == 0) {
            
            insertExpenditure(
                _loan, 
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
        } else {
            
            expenditure storage _expend = _loan.expenditures[_expendIndex];
            
            _expend.applyAmount = _apply_amount;
            _expend.receiveAmount = _receive_amount;
            _expend.applyTime = _apply_time;
            _expend.interest = _interest;
            _expend.orderNumber = _order_number;
            _expend.bankCard = _bank_card;
            _expend.purpose = _purpose;
            _expend.overdueDays = _overdue_days;
            
            latestUpdate = block.number;
            
        }
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateExpenditure"
        );
    }
    
    function _getExpendFromLoanByIndex(
        loan storage _loan, 
        uint32 _expend_index
    ) 
    whenNotPaused internal view 
    returns (
        expenditure storage _expend
    ) 
    {
        require(_expend_index > 0 && _expend_index <= _loan.expenditureCounter);
        _expend = _loan.expenditures[_expend_index];
    }
    
    function _getExpendFromLoanByTag(
        loan storage _loan, 
        bytes32 _expend_tag
    ) 
    whenNotPaused internal view 
    returns (
        expenditure storage _expend
    ) 
    {
        uint32 _expendIndex = _loan.expendituresIndex[_expend_tag];
        _expend = _getExpendFromLoanByIndex(_loan, _expendIndex);
    }
    
    function _getExpendByTag(
        bytes32 _loan_tag, 
        bytes32 _expend_tag
    ) 
    whenNotPaused internal view 
    returns (
        expenditure storage _expend
    ) 
    {
        loan storage _loan = _getLoanByTag(_loan_tag);
        _expend = _getExpendFromLoanByTag(_loan, _expend_tag);
    }
    
    function _getExpendByIndex(
        uint32 _loan_index, 
        uint32 _expend_index
    ) 
    whenNotPaused internal view 
    returns (
        expenditure storage _expend
    ) 
    {
        loan storage _loan = _getLoanByIndex(_loan_index);
        _expend = _getExpendFromLoanByIndex(_loan, _expend_index);
    }
    
    function getExpendByIndex(
        uint32 _loan_index, 
        uint32 _expend_index
    ) 
    whenNotPaused canCall public view 
    returns (
        bytes32,  // 支用记录唯一标识
        bytes32,  // 订单号
        bytes32,  // 银行卡
        bytes32,  // 用途
        uint32,   // 还款计划的条目数
        uint32,   // 还款次数
        uint32,   // 逾期天数
        uint,     // 申请金额
        uint,     // 到账金额
        uint,     // 日期
        uint      // 利息
    ) 
    {
        expenditure storage _expend = _getExpendByIndex(_loan_index, _expend_index);
        return (
            _expend.expendTag,          // 支用记录唯一标识
            _expend.orderNumber,        // 订单号
            _expend.bankCard,           // 银行卡
            _expend.purpose,            // 用途
            _expend.installmentCounter, // 还款计划条目数
            _expend.repaymentCounter,   // 还款次数
            _expend.overdueDays,        // 逾期天数
            _expend.applyAmount,        // 申请金额
            _expend.receiveAmount,      // 到账金额
            _expend.applyTime,          // 日期
            _expend.interest            // 利息
        );
    }
    

    function insertInstallment(
        expenditure storage _expend,
        bytes32 _installment_tag,   // 还款计划记录唯一标识
        uint32 _installment_number, // 期数
        uint _repay_time,           // 还款时间
        uint _repay_amount          // 还款金额
    ) 
    whenNotPaused internal 
    {
        installment storage _installment = _expend.installments[++_expend.installmentCounter];
        
        _installment.installmentNumber = _installment_number;
        _installment.repayTime = _repay_time;
        _installment.repayAmount = _repay_amount;
        _installment.installmentTag = _installment_tag;
        
        _expend.installmentsIndex[_installment_tag] = _expend.installmentCounter;
        
        latestUpdate = block.number;
    }
    
    function updateInstallment(
        bytes32 _loan_tag,          // 借贷记录唯一标识
        bytes32 _expend_tag,        // 支用记录唯一标识
        bytes32 _installment_tag,   // 还款计划记录唯一标识
        uint32 _installment_number, // 期数
        uint _repay_time,           // 还款时间
        uint _repay_amount          // 还款金额
    ) 
    whenNotPaused canWrite public 
    {
        expenditure storage _expend = _getExpendByTag(_loan_tag, _expend_tag);
        
        uint32 _installmentIndex = _expend.installmentsIndex[_installment_tag];
        
        if (_installmentIndex == 0) {
            
            insertInstallment(
                _expend,
                _installment_tag, 
                _installment_number, 
                _repay_time, 
                _repay_amount
            );
        } else {
            installment storage _installment = _expend.installments[_installmentIndex];
            
            _installment.installmentNumber = _installment_number;
            _installment.repayTime = _repay_time;
            _installment.repayAmount = _repay_amount;
            
            latestUpdate = block.number;
        }
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateInstallment"
        );
    }
    
    function _getInstallmentFromExpendByIndex(
        expenditure storage _expend, 
        uint32 _installment_index
    ) 
    whenNotPaused internal view 
    returns (
        installment storage _installment
    ) 
    {
        require(_installment_index > 0 && _installment_index <= _expend.installmentCounter);
        _installment = _expend.installments[_installment_index];
    }
    
    function _getInstallmentFromExpendByTag(
        expenditure storage _expend, 
        bytes32 _installment_tag
    ) 
    whenNotPaused internal view 
    returns (
        installment storage _installment
    ) 
    {
        uint32 _installmentIndex = _expend.installmentsIndex[_installment_tag];
        _installment = _getInstallmentFromExpendByIndex(_expend, _installmentIndex);
    }
    
    function _getInstallmentByIndex(
        uint32 _loan_index, 
        uint32 _expend_index, 
        uint32 _installment_index
    ) 
    whenNotPaused internal view 
    returns (
        installment storage _installment
    ) 
    {
        expenditure storage _expend = _getExpendByIndex(_loan_index, _expend_index);
        _installment = _getInstallmentFromExpendByIndex(_expend, _installment_index);
    }
    
    function getInstallmentByIndex(
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
        installment storage _installment = _getInstallmentByIndex(_loan_index, _expend_index, _installment_index);
        return (
            _installment.installmentTag,    // 还款计划记录唯一标识
            _installment.installmentNumber, // 期数
            _installment.repayTime,         // 还款时间
            _installment.repayAmount        // 还款金额
        );
    }
    
    function insertRepayment(
        expenditure storage _expend,
        bytes32 _repayment_tag,     // 还款记录唯一标识
        uint32 _installment_number, // 期数
        uint32 _overdue_days,       // 逾期天数
        uint32 _repay_types,        // 还款类型
        uint _repay_amount,         // 还款金额
        uint _repay_time            // 还款时间
    ) 
    whenNotPaused internal 
    {
        repayment storage _repayment = _expend.repayments[++_expend.repaymentCounter];
        
        _repayment.installmentNumber = _installment_number;
        _repayment.repayAmount = _repay_amount;
        _repayment.repayTime = _repay_time;
        _repayment.overdueDays = _overdue_days;
        _repayment.repayTypes = _repay_types;
        _repayment.repaymentTag = _repayment_tag;
        
        _expend.repaymentsIndex[_repayment_tag] = _expend.repaymentCounter;
        
        latestUpdate = block.number;
    }
    
    function updateRepayment(
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
        expenditure storage _expend = _getExpendByTag(_loan_tag, _expend_tag);
        uint32 _repaymentIndex = _expend.repaymentsIndex[_repayment_tag];
        if (_repaymentIndex == 0) {
            
            insertRepayment(
                _expend, 
                _repayment_tag, 
                _installment_number, 
                _overdue_days, 
                _repay_types, 
                _repay_amount, 
                _repay_time
            );
        } else {
            
            repayment storage _repayment = _expend.repayments[_repaymentIndex];

            _repayment.installmentNumber = _installment_number;
            _repayment.repayTime = _repay_time;
            _repayment.repayAmount = _repay_amount;
            _repayment.overdueDays = _overdue_days;
            _repayment.repayTypes = _repay_types;
            
            latestUpdate = block.number;
        }
        
        //event
        WriteData(
            tx.origin,
            msg.sender,
            block.number,
            "updateRepayment"
        );
    }
    
    function _getRepaymentFromExpendByIndex(
        expenditure storage _expend, 
        uint32 _repayment_index
    ) 
    whenNotPaused internal view 
    returns (
        repayment storage _repayment
    ) 
    {
        require(_repayment_index > 0 && _repayment_index <= _expend.repaymentCounter);
        _repayment = _expend.repayments[_repayment_index];
    }
    
    function _getRepaymentFromExpendByTag(
        expenditure storage _expend, 
        bytes32 _repayment_tag
    ) 
    whenNotPaused internal view 
    returns (
        repayment storage _repayment
    ) 
    {
        uint32 _repaymentIndex = _expend.repaymentsIndex[_repayment_tag];
        _repayment = _getRepaymentFromExpendByIndex(_expend, _repaymentIndex);
    }
    
    function _getRepaymentByIndex(
        uint32 _loan_index,     // 插入借贷记录时loanCounter的值
        uint32 _expend_index,   // 插入支用记录时expenditureCounter的值
        uint32 _repayment_index // 插入还款记录时repaymentCounter的值
    ) 
    whenNotPaused internal view 
    returns (
        repayment storage _repayment
    ) 
    {
        expenditure storage _expend = _getExpendByIndex(_loan_index, _expend_index);
        _repayment = _getRepaymentFromExpendByIndex(_expend, _repayment_index);
    }
    
    function getRepaymentByIndex(
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
        repayment storage _repayment = _getRepaymentByIndex(_loan_index, _expend_index, _repayment_index);
        return (
            _repayment.repaymentTag,      // 还款记录唯一标识
            _repayment.installmentNumber, // 期数
            _repayment.overdueDays,       // 逾期天数
            _repayment.repayTypes,        // 还款类型
            _repayment.repayAmount,       // 还款金额
            _repayment.repayTime          // 还款时间
        );
    }
}

