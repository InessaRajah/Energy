pragma solidity ^0.5.16;

contract Energy {
    //this contract is recalled for each time period
    // Model a Peer
    struct Peer {
        uint id;
        address account;
        bool prosumer;
        uint8 building; //0 for commercial and 1 for residential
        bool isPeer;
    }

    //create an admin struct/private variable?

     //constructor
     constructor () public {
        addPeer(0x28533267708123eB23D50c34a49ed7eB0D0c06a5, true, 1, true);
        addPeer(0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7, true, 1, true);
        addPeer(0x8DcD9E1535de39A4Df47243e982e2c8098Ad1566, true, 1, true);
        addPeer(0x0263E592ca8C92a041a49C93424AC45850b928aa, true, 1, true);
        addPeer(0x31D5154d76B65338f05099Fd32F55cBD722BdcB9, true, 1, true);
    }
    
    //add peer: admin sets this (declare admin account here)
    function addPeer (address acc, bool role, uint8 build, bool user) public{
        //require(msg.sender == 0x7a0429BC9Be5e4B555C06B5dEc4A385d2eA1D3b8);
        peersCount ++;
        peers[acc] = Peer(peersCount, acc, role, build, user);
    }
    
    // Store Peers using their addresses
    // Fetch Peers
    mapping(address => Peer) public peers;
    // Store Peers Count
    uint public peersCount;
    
    // list of trade_bids for current iteration for current time_period
    Trade_bid [] public trades;
    
    //keep public track of iteration for this time-period: admin sets this?
    uint public iteration = 1;
    
    //keep public track of time_period: admin sets this?
    uint public time_period = 1;
    
    //keep public track of date: admin sets this?
    string public date = "09/10/2020";
    
    //keep track of number of how trade bids have been submitted for this iteration
    uint public tradeCountIter;

     //NB: will need to split up kwh into decimals as well
    struct Trade_bid {
        //string date;
        uint time_period;
        address sender;
        address buyer;
        uint kwh;
        uint price; //given in cents
        uint iteration;
    }
    //variables to track if buying and selling addresses are members of microgrid
    Peer private temp;
    
    //add trade bid to list of trade bids for this iteration
    function addTradeBid (address s, address b, uint amount, uint price_c) public {
        //check if sender address is members of the microgrid
        require(peers[s].isPeer);
        //check if buyer address is member of the microgrid
        require(peers[b].isPeer);
        //requires that the person adding the trade bid is the account set as the sender
        require(msg.sender == s);
        //requires that the sender is not also the buyer
        require(msg.sender != b);
        trades.push(Trade_bid(time_period, s, b, amount, price_c, iteration));
        tradeCountIter++;
        
    }

    //maps addresses to local residuals for addresses 
    //NB: will need to decide by what magnitude of 10 we will be multiplying actual residual value in order
    // to store it in this mapping
    mapping (address => uint) public localres;

    //keep track of how many peers have submitted local residuals for this iteration 
    uint public localresCounter;


    //add trade bid to list of trade bids for this iteration
    function addLocalRes (address s, uint res) public {
        //requires that person submitting local residual to blockchain is a member of the microgrid
        require(peers[s].isPeer);
        localresCounter++;
        localres[msg.sender] = res;
        
    }

    
}