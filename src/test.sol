pragma solidity ^0.4.17;

contract UserMapsContract{
    
    address private owner;
    
    mapping(bytes32 => address) userToAddress;
    
    function UserMapsContract() public {
        owner = msg.sender;
    }
    
    function name() public pure returns (string) {
        return "testContract";
    }
    
    function createUserStorage(string userName, string idNo, string phoneNo) private returns (address) {
        bytes32 userTag = getUserTag(userName, idNo, phoneNo);
        UserContract useraddr = new UserContract(userTag);
        userToAddress[userTag] = address(useraddr);
        return useraddr;
    }
    
    function getUserTag(string userName, string idNo, string phoneNo) public pure returns (bytes32) {
        return keccak256(userName, idNo, phoneNo);
    }
    
    function createUserContract(string userName, string idNo, string phoneNo) public returns (address) {
        address useraddr = userToAddress[getUserTag(userName, idNo, phoneNo)];
        if (bytes20(useraddr) & 0xff == 0) {
            useraddr = createUserStorage(userName, idNo, phoneNo); 
        }
        return useraddr;
    }
    
    function getUserContractAddrByTag(bytes32 _userTag) public constant returns (address) {
        return userToAddress[_userTag];
    }
    
    function getUserContractAddr(string userName, string idNo, string phoneNo) public constant returns (address) {
        return userToAddress[getUserTag(userName, idNo, phoneNo)];
    }
}


contract UserContract {
    
    address public owner;
    address public creator;
    bytes32 public userTag;
    
    uint32 private loanCounter;    // 借贷次数
    uint private latestUpdate;
    
    struct installment {
        uint32 repayTime;         // 还款时间
        uint32 repayAmount;       // 还款金额
        uint32 installmentNumber; // 期数
        bytes32 installmentTag;
        address owner;
    }
    
    struct repayment {
        uint32 repayAmount;       // 还款金额
        uint32 repayTime;         // 还款时间
        uint32 overdueDays;       // 逾期天数
        uint32 repayTypes;        // 还款类型
        uint32 installmentNumber; // 期数
        bytes32 repaymentTag;
        address owner;
    }
    
    struct expenditure {
        uint32 applyAmount;   // 申请金额
        uint32 receiveAmount; // 到账金额
        uint32 timeStamp;     // 日期
        uint32 interest;      // 利率。貌似没有浮点，估计要坐下转换。
        bytes32 orderNumber;   // 订单号
        uint32 overdueDays;   // 逾期天数
        uint32 installmentCounter; // 分期数
        uint32 repaymentCounter;    // 还款次数
        bytes32 bankCard;     // 银行卡
        bytes32 purpose;      // 用途
        bytes32 expendTag;
        address owner;
        
        mapping(uint32=> installment) installments; // 还款分期计划
        //业务数据中的分期计划标识与installments的key的映射关系
        mapping(bytes32 => uint32) installmentsIndex;
        
        mapping(uint32=> repayment) repayments;  // 还款信息
        //业务数据中的还款信息标识与repayments的key的映射关系
        mapping(bytes32 => uint32) repaymentsIndex;
    }
    
    struct loan {
        address owner;
        uint32 creditLimit;         // 授信额度
        uint32 expenditureCounter;  // 支用次数
        bytes32 platform;           // 平台
        bytes32 loanTag;
        
        mapping(uint32=> expenditure) expenditures;  // 支用记录
        //业务数据中的支用记录标识与expenditures的key的映射关系
        mapping(bytes32 => uint32) expendituresIndex;
    }
    
    mapping(uint32=> loan) loans;  // 借贷记录
    //业务数据中的借贷记录标识与loans的key的映射关系
    mapping(bytes32 => uint32) loansIndex;
    
    function UserContract(bytes32 _userTag) public {
        require(msg.sender != tx.origin);
        userTag = _userTag;
        creator = msg.sender;
        owner = tx.origin;
        latestUpdate = now;
        
    }
    
    function resetOwner(address newOwner) public {
        require(owner == tx.origin);
        owner = newOwner;
    }
    
    function getCaller() public view returns (address) {
        return tx.origin;
    }
    
    function loanTag(uint32 _loanId) public view returns (bytes32) {
        return keccak256(tx.origin, _loanId);
    }
    
    function expenditureTag(uint32 _loanId, uint32 _orderId) public view returns (bytes32) {
        return keccak256(tx.origin, _loanId, _orderId);
    }
    
    function installmentTag(uint32 _loanId, uint32 _orderId, uint32 _installmentId) public view returns (bytes32) {
        return keccak256(tx.origin, _loanId, _orderId, _installmentId);
    }
    
    function repaymentTag(uint32 _loanId, uint32 _orderId, uint32 _repaymentId) public view returns (bytes32) {
        return keccak256(tx.origin, _loanId, _orderId, _repaymentId);
    } 

    function insertLoan(uint32 _loanId, uint32 _creditLimit, bytes32 _platform) internal returns (bytes32 _loanTag) {
        _loanTag = loanTag(_loanId);
        loan memory _loan = loan({owner: tx.origin, loanTag: _loanTag, platform: _platform, creditLimit: _creditLimit, expenditureCounter: 0});
        ++loanCounter;
        loans[loanCounter] = _loan;
        loansIndex[_loanTag] = loanCounter;
        latestUpdate = now;
    }
    
    function updateLoan(uint32 _loanId, uint32 _creditLimit, bytes32 _platform) public returns (bytes32 _loanTag) {
        _loanTag = loanTag(_loanId);
        uint32 _loanIndex = loansIndex[_loanTag];
        if (_loanIndex == 0) {
            insertLoan(_loanId, _creditLimit, _platform);
        } else {
            loan storage _loan = loans[_loanIndex];
            require(_loan.owner == tx.origin);
            if (_platform != _loan.platform) _loan.platform = _platform; latestUpdate=now;
            if (_creditLimit != _loan.creditLimit) _loan.creditLimit = _creditLimit;latestUpdate = now;
        }
    }
    
    function getLoanTimes() public view returns (uint32) {
        return loanCounter;
    }
    
    function getLatestUpdate() public view returns (uint) {
        return latestUpdate;
    }
    
    function _getLoanByIndex(uint32 index) internal view returns (loan storage _loan) {
        require(0 < index && index <= loanCounter);
        _loan = loans[index];
    }
    
    function _getLoanByTag(bytes32 _userTag) internal view returns (loan storage _loan) {
        _loan = _getLoanByIndex(loansIndex[_userTag]);
    }
    
    function _getLoanById(uint32 _loanId) internal view returns (loan storage _loan) {
        _loan = _getLoanByTag(loanTag(_loanId));
    }
    
    function getLoanByIndex(uint32 index) public view returns (bytes32, uint32, uint32, address, bytes32) {
        require(0 < index && index <= loanCounter);
        loan storage _loan = loans[index];
        return (_loan.platform, _loan.creditLimit, _loan.expenditureCounter, _loan.owner, _loan.loanTag);
    }
    
    function getLoanById(uint32 _loanId) public view returns (bytes32, uint32, uint32, address) {
        loan storage _loan = _getLoanById(_loanId);
        return (_loan.platform, _loan.creditLimit, _loan.expenditureCounter, _loan.owner);
    }
    
    function getLoanByTag(bytes32 _userTag) public view returns (bytes32, uint32, uint32, address) {
        loan storage _loan = _getLoanByTag(_userTag);
        return (_loan.platform, _loan.creditLimit, _loan.expenditureCounter, _loan.owner);
    }
    
    function resetLoanOwner(uint32 _loanId, address newOwner) public {
        loan storage _loan = _getLoanById(_loanId);
        require(_loan.owner == tx.origin);
        _loan.owner = newOwner;
        latestUpdate = now;
    }

    function insertExpend(
        uint32 _loanId, 
        uint32 _expendId, 
        uint32 applyAmount,   // 申请金额
        uint32 receiveAmount, // 到账金额
        uint32 timeStamp,     // 日期
        uint32 interest,      // 利率。貌似没有浮点，估计要坐下转换。
        bytes32 orderNumber,   // 订单号
        uint32 overdueDays,   // 逾期天数
        bytes32 bankCard,     // 银行卡
        bytes32 purpose       // 用途
    ) internal returns (bytes32) {
        loan storage _loan = _getLoanById(_loanId);
        bytes32 _expendTag = expenditureTag(_loanId, _expendId);
        expenditure memory _expend = expenditure({
            applyAmount: applyAmount,   // 申请金额
            receiveAmount: receiveAmount, // 到账金额
            timeStamp: timeStamp,     // 日期
            interest: interest,      // 利率。貌似没有浮点，估计要坐下转换。
            orderNumber: orderNumber,   // 订单号
            overdueDays: overdueDays,   // 逾期天数
            bankCard: bankCard,     // 银行卡
            purpose: purpose,       // 用途
            expendTag: _expendTag,
            installmentCounter: 0,
            repaymentCounter: 0,
            owner: tx.origin
        });
        ++_loan.expenditureCounter;
        _loan.expenditures[_loan.expenditureCounter] = _expend;
        _loan.expendituresIndex[_expendTag] = _loan.expenditureCounter;
        latestUpdate = now;
        return _expendTag;
    }
    
    function updateExpend(
        uint32 _loanId, 
        uint32 _expendId, 
        uint32 applyAmount,   // 申请金额
        uint32 receiveAmount, // 到账金额
        uint32 timeStamp,     // 日期
        uint32 interest,      // 利率。貌似没有浮点，估计要坐下转换。
        bytes32 orderNumber,   // 订单号
        uint32 overdueDays,   // 逾期天数
        bytes32 bankCard,     // 银行卡
        bytes32 purpose       // 用途
    ) 
        public 
        returns (bytes32) 
    {
        loan storage _loan = _getLoanById(_loanId);
        bytes32 _expendTag = expenditureTag(_loanId, _expendId);
        uint32 _expendIndex = _loan.expendituresIndex[_expendTag];
        if (_expendIndex == 0) {
            insertExpend(_loanId, _expendId, applyAmount, receiveAmount, timeStamp, interest, orderNumber, overdueDays, bankCard, purpose);
        } else {
            expenditure storage _expend = _loan.expenditures[_expendIndex];
            require(_expend.owner == tx.origin);
            if (applyAmount != _expend.applyAmount) _expend.applyAmount = applyAmount; latestUpdate = now;
            if (receiveAmount != _expend.receiveAmount) _expend.receiveAmount = receiveAmount; latestUpdate = now;
            if (timeStamp != _expend.timeStamp) _expend.timeStamp = timeStamp; latestUpdate = now;
            if (interest != _expend.interest) _expend.interest = interest; latestUpdate = now;
            if (orderNumber != _expend.orderNumber) _expend.orderNumber = orderNumber; latestUpdate = now;
            if (overdueDays != _expend.overdueDays) _expend.overdueDays = overdueDays; latestUpdate = now;
            if (bankCard != _expend.bankCard) _expend.bankCard = bankCard; latestUpdate = now;
            if (purpose != _expend.purpose) _expend.purpose = purpose; latestUpdate = now;
        }

        return _expendTag;
    }
    
    function _getExpendFromLoanByIndex(loan storage _loan, uint32 _expendIndex) internal view returns (expenditure storage _expend) {
        require(_expendIndex > 0 && _expendIndex <= _loan.expenditureCounter);
        _expend = _loan.expenditures[_expendIndex];
    }
    
    function _getExpendFromLoanByTag(loan storage _loan, bytes32 _expendTag) internal view returns (expenditure storage _expend) {
        uint32 _expendIndex = _loan.expendituresIndex[_expendTag];
        _expend = _getExpendFromLoanByIndex(_loan, _expendIndex);
    }
    
    function _getExpendById(uint32 _loanId, uint32 _expendId) internal view returns (expenditure storage _expend) {
        loan storage _loan = _getLoanById(_loanId);
        bytes32 _expendTag = expenditureTag(_loanId, _expendId);
        _expend = _getExpendFromLoanByTag(_loan, _expendTag);
    }
    
    function _getExpendByIndex(uint32 _loanIndex, uint32 _expendIndex) internal view returns (expenditure storage _expend) {
        loan storage _loan = _getLoanByIndex(_loanIndex);
        _expend = _getExpendFromLoanByIndex(_loan, _expendIndex);
    }
    
    function resetExpendOwner(uint32 _loanId, uint32 _expendId, address newOwner) public {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        require(_expend.owner == tx.origin);
        _expend.owner = newOwner;
        latestUpdate = now;
    }

    
    function getExpendByIndex(
        uint32 _loanIndex, 
        uint32 _expendIndex
    ) 
        public 
        view 
        returns (
            uint32 , // 申请金额
            uint32 , // 到账金额
            uint32 ,     // 日期
            uint32 ,      // 利率。貌似没有浮点，估计要坐下转换。
            bytes32 ,   // 订单号
            uint32 ,   // 逾期天数
            bytes32 ,     // 银行卡
            bytes32 ,       // 用途
            uint32 ,
            uint32 ,
            address,
            bytes32
        ) 
    {
        expenditure storage _expend = _getExpendByIndex(_loanIndex, _expendIndex);
        return (
            _expend.applyAmount,   // 申请金额
            _expend.receiveAmount, // 到账金额
            _expend.timeStamp,     // 日期
            _expend.interest,      // 利率。貌似没有浮点，估计要坐下转换。
            _expend.orderNumber,   // 订单号
            _expend.overdueDays,   // 逾期天数
            _expend.bankCard,     // 银行卡
            _expend.purpose,       // 用途
            _expend.installmentCounter,
            _expend.repaymentCounter,
            _expend.owner,
            _expend.expendTag
        );
    }
    

    function insertInstallment(
        uint32 _loanId, 
        uint32 _expendId,
        uint32 _installmentId,
        uint32 installmentNumber, // 期数
        uint32 repayTime,         // 还款时间
        uint32 repayAmount        // 还款金额
    ) internal returns (bytes32) {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        bytes32 _installmentTag = installmentTag(_loanId, _expendId, _installmentId);
        installment memory _installment = installment({
            installmentNumber: installmentNumber, 
            repayTime:repayTime, 
            repayAmount:repayAmount, 
            installmentTag: _installmentTag,
            owner: tx.origin
        });
        ++_expend.installmentCounter;
        _expend.installments[_expend.installmentCounter] = _installment;
        _expend.installmentsIndex[_installmentTag] = _expend.installmentCounter;
        latestUpdate = now;
        return _installmentTag;
    }
    
    function updateInstallment(
        uint32 _loanId, 
        uint32 _expendId,
        uint32 _installmentId,
        uint32 installmentNumber, // 期数
        uint32 repayTime,         // 还款时间
        uint32 repayAmount        // 还款金额
    ) 
        public 
        returns (bytes32) 
    {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        bytes32 _installmentTag = installmentTag(_loanId, _expendId, _installmentId);
        uint32 _installmentIndex = _expend.installmentsIndex[_installmentTag];
        if (_installmentIndex == 0) {
            insertInstallment(_loanId, _expendId, _installmentId, installmentNumber, repayTime, repayAmount);
        } else {
            installment storage _installment = _expend.installments[_installmentIndex];
            require(_installment.owner == tx.origin);
            if (installmentNumber != _installment.installmentNumber) _installment.installmentNumber = installmentNumber; latestUpdate = now;
            if (repayTime != _installment.repayTime) _installment.repayTime = repayTime; latestUpdate = now;
            if (repayAmount != _installment.repayAmount) _installment.repayAmount = repayAmount; latestUpdate = now;
        }

        return _installmentTag;
    }
    
    function _getInstallmentFromExpendByIndex(expenditure storage _expend, uint32 _installmentIndex) internal view returns (installment storage _installment) {
        require(_installmentIndex > 0 && _installmentIndex <= _expend.installmentCounter);
        _installment = _expend.installments[_installmentIndex];
    }
    
    function _getInstallmentFromExpendByTag(expenditure storage _expend, bytes32 _installmentTag) internal view returns (installment storage _installment) {
        uint32 _installmentIndex = _expend.installmentsIndex[_installmentTag];
        _installment = _getInstallmentFromExpendByIndex(_expend, _installmentIndex);
    }
    
    function _getInstallmentById(uint32 _loanId, uint32 _expendId, uint32 _installmentId) internal view returns (installment storage _installment) {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        bytes32 _installmentTag = installmentTag(_loanId, _expendId, _installmentId);
        _installment = _getInstallmentFromExpendByTag(_expend, _installmentTag);
    }
    
    function _getInstallmentByIndex(uint32 _loanIndex, uint32 _expendIndex, uint32 _installmentIndex) internal view returns (installment storage _installment) {
        expenditure storage _expend = _getExpendByIndex(_loanIndex, _expendIndex);
        _installment = _getInstallmentFromExpendByIndex(_expend, _installmentIndex);
    }
    
    function resetInstallmentOwner(uint32 _loanId, uint32 _expendId, uint32 _installmentId, address newOwner) public {
        installment storage _installment = _getInstallmentById(_loanId, _expendId, _installmentId);
        require(_installment.owner == tx.origin);
        _installment.owner = newOwner;
        latestUpdate = now;
    }
    
    function getInstallmentByIndex(
        uint32 _loanIndex, 
        uint32 _expendIndex,
        uint32 _installmentIndex
    ) 
        public 
        view 
        returns (
            uint32 ,   // 期数
            uint32 ,           // 还款时间
            uint32 ,          // 还款金额
            address,
            bytes32
        ) 
    {
        installment storage _installment = _getInstallmentByIndex(_loanIndex, _expendIndex, _installmentIndex);
        return (
            _installment.installmentNumber,   // 期数
            _installment.repayTime,           // 还款时间
            _installment.repayAmount,          // 还款金额
            _installment.owner,
            _installment.installmentTag
        );
    }
    
    
    
    function insertRepayment(
        uint32 _loanId, 
        uint32 _expendId,
        uint32 _repaymentId,
        uint32 installmentNumber, // 期数
        uint32 repayAmount,       // 还款金额
        uint32 repayTime,         // 还款时间
        uint32 overdueDays,       // 逾期天数
        uint32 repayTypes         // 还款类型
    ) internal returns (bytes32) {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        bytes32 _repaymentTag = repaymentTag(_loanId, _expendId, _repaymentId);
        repayment memory _repayment = repayment({
            installmentNumber: installmentNumber, 
            repayAmount:repayAmount,
            repayTime:repayTime, 
            overdueDays: overdueDays,
            repayTypes:repayTypes,
            repaymentTag: _repaymentTag,
            owner: tx.origin
        });
        ++_expend.repaymentCounter;
        _expend.repayments[_expend.repaymentCounter] = _repayment;
        _expend.repaymentsIndex[_repaymentTag] = _expend.repaymentCounter;
        latestUpdate = now;
        return _repaymentTag;
    }
    
    function updateRepayment(
        uint32 _loanId, 
        uint32 _expendId,
        uint32 _repaymentId,
        uint32 installmentNumber, // 期数
        uint32 repayAmount,       // 还款金额
        uint32 repayTime,         // 还款时间
        uint32 overdueDays,       // 逾期天数
        uint32 repayTypes         // 还款类型
    ) 
        public 
        returns (bytes32) 
    {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        bytes32 _repaymentTag = repaymentTag(_loanId, _expendId, _repaymentId);
        uint32 _repaymentIndex = _expend.repaymentsIndex[_repaymentTag];
        if (_repaymentIndex == 0) {
            insertRepayment(_loanId, _expendId, _repaymentId, installmentNumber, repayAmount, repayTime, overdueDays, repayTypes);
        } else {
            repayment storage _repayment = _expend.repayments[_repaymentIndex];
            require(_repayment.owner == tx.origin);
            if (installmentNumber != _repayment.installmentNumber) _repayment.installmentNumber = installmentNumber; latestUpdate = now;
            if (repayTime != _repayment.repayTime) _repayment.repayTime = repayTime; latestUpdate = now;
            if (repayAmount != _repayment.repayAmount) _repayment.repayAmount = repayAmount; latestUpdate = now;
            if (overdueDays != _repayment.overdueDays) _repayment.overdueDays = overdueDays; latestUpdate = now;
            if (repayTypes != _repayment.repayTypes) _repayment.repayTypes = repayTypes; latestUpdate = now;
        }

        return _repaymentTag;
    }
    
    function _getRepaymentFromExpendByIndex(expenditure storage _expend, uint32 _repaymentIndex) internal view returns (repayment storage _repayment) {
        require(_repaymentIndex > 0 && _repaymentIndex <= _expend.repaymentCounter);
        _repayment = _expend.repayments[_repaymentIndex];
    }
    
    function _getRepaymentFromExpendByTag(expenditure storage _expend, bytes32 _repaymentTag) internal view returns (repayment storage _repayment) {
        uint32 _repaymentIndex = _expend.repaymentsIndex[_repaymentTag];
        _repayment = _getRepaymentFromExpendByIndex(_expend, _repaymentIndex);
    }
    
    function _getRepaymentById(uint32 _loanId, uint32 _expendId, uint32 _repaymentId) internal view returns (repayment storage _repayment) {
        expenditure storage _expend = _getExpendById(_loanId, _expendId);
        bytes32 _repaymentTag = repaymentTag(_loanId, _expendId, _repaymentId);
        _repayment = _getRepaymentFromExpendByTag(_expend, _repaymentTag);
    }
    
    function _getRepaymentByIndex(uint32 _loanIndex, uint32 _expendIndex, uint32 _repaymentIndex) internal view returns (repayment storage _repayment) {
        expenditure storage _expend = _getExpendByIndex(_loanIndex, _expendIndex);
        _repayment = _getRepaymentFromExpendByIndex(_expend, _repaymentIndex);
    }
    
    function resetRepaymentOwner(uint32 _loanId, uint32 _expendId, uint32 _repaymentId, address newOwner) public {
        repayment storage _repayment = _getRepaymentById(_loanId, _expendId, _repaymentId);
        require(_repayment.owner == tx.origin);
        _repayment.owner = newOwner;
        latestUpdate = now;
    }
    
    function getRepaymentByIndex(
        uint32 _loanIndex, 
        uint32 _expendIndex,
        uint32 _repaymentIndex
    ) 
        public 
        view 
        returns (
            uint32 , // 期数
            uint32 , // 还款金额
            uint32 , // 还款时间
            uint32 , // 逾期天数
            uint32 , // 还款类型
            address ,
            bytes32 
        ) 
    {
        repayment storage _repayment = _getRepaymentByIndex(_loanIndex, _expendIndex, _repaymentIndex);
        return (
            _repayment.installmentNumber,   // 期数
            _repayment.repayAmount,         // 还款金额
            _repayment.repayTime,           // 还款时间
            _repayment.overdueDays,         // 逾期天数
            _repayment.repayTypes,           // 还款类型
            _repayment.owner,
            _repayment.repaymentTag
        );
    }
}

