pragma solidity ^0.5.16;

contract Energy {
    //this contract is recalled for each time period by admin account
    //public state variables are accessible by everyone who invokes contract on the network 
    // Model a Peer
    struct Peer {
        uint id;
        address account;
        bool prosumer;
        uint8 building; //0 for commercial and 1 for residential
        bool isPeer;
    }

    //create an admin struct variable
    struct Admin {

        address admin_account;
        bool isAdmin;
    }

    Admin public admin;
    //keep public track of time_period and date: admin sets this at beginning of time-period
    uint public time_per=1;
    string public date = '2020-10-11';

    function setTimeDate(uint time, string memory date_set) public {
            require(msg.sender==admin.admin_account);
            time_per = time;
            date = date_set;
    }


     //constructor: lists registered peers and admin account
     //change for each ganache instance
     //will change for testing
     constructor () public {
        //set admin user
        admin = Admin(0x28533267708123eB23D50c34a49ed7eB0D0c06a5, true);
        addPeer(0x28533267708123eB23D50c34a49ed7eB0D0c06a5, true, 1, true);
        addPeer(0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7, true, 1, true);
        //addPeer(0x8DcD9E1535de39A4Df47243e982e2c8098Ad1566, true, 1, true);
        //addPeer(0x0263E592ca8C92a041a49C93424AC45850b928aa, true, 1, true);
        //addPeer(0x31D5154d76B65338f05099Fd32F55cBD722BdcB9, true, 1, true);
        

        //need to include these function calls for testing
        addLocalRes (0x28533267708123eB23D50c34a49ed7eB0D0c06a5, 11);
        addLocalRes (0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7, -12);

    }
    
    //add peer: admin sets this 
    function addPeer (address acc, bool role, uint8 build, bool user) public{
        require(msg.sender == admin.admin_account);
        peersCount ++;
        peers[acc] = Peer(peersCount, acc, role, build, user);
    }
    
    // Store Peers using their addresses
    // Fetch Peers
    mapping(address => Peer) public peers;
    //map peers to an integer id
    mapping(uint => Peer) public peersID;
    // Store Peers Count
    uint public peersCount;
    
    // list of trade_bids for current iteration for current time_period
    Trade_bid [] public trade_bids;
    
    //keep public track of iteration for this time-period: admin sets this?
    uint public iteration = 1;
    
    //keep track of number of how trade bids have been submitted for this iteration
    //set to 5 for testing
    uint public tradeCountIter = 5;

     //NB: will need to split up kwh into decimals as well
    struct Trade_bid {
        string date;
        uint time_period;
        address from;
        address to;
        int kwh; //need to decide on scaling factor
        uint price; //given in cents
        uint iteration;
    }
    
    //add trade bid to list of trade bids for this iteration
    function addTradeBid (string memory date_peer, uint time_period, address s, address b, int amount, uint price_c) public {
        //check if sender address is members of the microgrid
        require(peers[s].isPeer);
        //check if buyer address is member of the microgrid
        require(peers[b].isPeer);
        //requires that the person adding the trade bid is the account set as the sender
        require(msg.sender == s);
        //requires that the sender is not also the buyer
        require(msg.sender != b);
        //requires peer to insert correct time_period
        require(time_period==time_per);
        //requires peer to insert correct date
        require(keccak256(abi.encodePacked(date)) == keccak256(abi.encodePacked(date_peer)));
        trade_bids.push(Trade_bid(date, time_period, s, b, amount, price_c, iteration));
        tradeCountIter++;
        
    }
    //NB: will need to decide by what magnitude of 10 we will be multiplying actual residual value in order
    // to store it in this mapping

    struct localRes{

        address from;
        int local_res;
        uint iteration;

    }
    
    //maps addresses to local residuals for addresses 
    mapping (address => int) public localres;

    //keep track of how many peers have submitted local residuals for this iteration 
    uint public localresCounter;

    //store the submitted local residuals for this iteration
    localRes [] public localres_list;


    //add trade bid to list of trade bids for this iteration
    function addLocalRes (address s, int res) public {
        //requires that person submitting local residual to blockchain is a member of the microgrid
        require(peers[s].isPeer);
        //check that person hasn't submitted local residual to blockchain already for this iteration
        require(localres[s]==int(0x0));
        localresCounter++;
        localres[s] = res;
        //add localres to localres_list
        localres_list.push(localRes(s, res, iteration));

    }

    //only person SENDING money can create a Trade struct- by using their private key to sign this transaction, approves the transfer of money.  Almost like end of bidding process.
    struct Trade {
        address from;
        address to; 
        uint kwh;
        uint price_c;
        string id; //make an id for trade using date, time period, buyer and seller

    }

    //create mapping for id to trade
    mapping (string => Trade) public approved_trades;

    //create counter for trades
    //check if tradeCounterIter is correct and that localresCounter == peersCount for trade bid to be made
    function createTrade(address from, address to, uint amount, uint price, string memory id) public {
        require(msg.sender == from);
        require(msg.sender!=to);
        require(peers[msg.sender].isPeer);
        require(peers[to].isPeer);
        require(tradeCountIter == (peersCount*(peersCount-1)));
        require(localresCounter == peersCount);
        //check that this trade hasn't already been approved
        require(keccak256(abi.encodePacked(approved_trades[id].id)) == keccak256(abi.encodePacked('')));
        approved_trades[id] = Trade(from, to, amount, price, id);

    }
    
    //see if you can move testing.py into this directory so you don't have to keep redeploying
    //TO DO: see how to make time and date setting automatic and include in constructor
    //try to add a valid ID checker in createTrade function
    //do you need to include date and time string thing in peer and admin for checking purposes?  
}