pragma solidity ^0.5.16;

contract Energy {
    //public state variables are accessible by everyone who invokes contract on the network 
    //this contract assumes that every member of the blockchain is a member of the microgrid i.e. is able to participate in trades
    //add a deletePeers() function
        
    //set these tolerances in constructor
    int public pri_tol;
    int public dual_tol;
    //constructor: lists registered peers and admin account
    //change for each ganache instance
     constructor () public {
        //set admin user - needed for testing
        admin = Admin(0x9dd4CA3EfD1f01f7E043A049B3E8FddD924085Eb);
        pri_tol = 7;
        dual_tol =7;
        peersCount = 0;
        //adding peers for testing
        //addPeer(0x28533267708123eB23D50c34a49ed7eB0D0c06a5, true, 1);
        //addPeer(0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7, true, 1);
        //addPeer(0x8DcD9E1535de39A4Df47243e982e2c8098Ad1566, true, 1, true);
        //addPeer(0x0263E592ca8C92a041a49C93424AC45850b928aa, true, 1, true);
        //addPeer(0x31D5154d76B65338f05099Fd32F55cBD722BdcB9, true, 1, true);

        //need to include these function calls for testing
        //addLocalRes (0x28533267708123eB23D50c34a49ed7eB0D0c06a5, 11);
        //addLocalRes (0xAedA4d57bf6be1e2d68D08f0E6D471E0fB27f4A7, -12);

    }

    // Model a Peer
    struct Peer {
        int id;
        address account;
        bool prosumer;
        uint8 building; //0 for commercial and 1 for residential
        bool isPeerActive; //is peer participating in trading for this time period
        uint num_trades_pending; //number of trades for this time period pending this peer's approval
    }

    //create an admin struct variable
    //admin address/es can add peers and are responsible for initiating the trading period 
    struct Admin {
        address admin_account;
    }

    Admin public admin;
    //is trading period intiated? i.e. can trading iterations begin
    bool public init;
    //keep track of date and time set by admin- verifies that peers know they are trading at the correct date and time
    string date;
    uint time_per;
    //keep public track of iteration for this time-period
    uint public iteration;

    //allows admin to set new admin account
    function setAdmin(address new_admin) public {

        require(msg.sender == admin.admin_account);
        admin.admin_account = new_admin;
    }


    //add peer's address to list of peers that are connected in the microgrid- only admin can do this
    function addPeer(address acc, bool role, uint8 build) public{
        require(msg.sender == admin.admin_account);
        require(peers[acc].id == int(0x0));
        peersCount ++;
        peers[acc] = Peer(peersCount, acc, role, build, false, 0);
        
    }


    // Store Peers using their addresses
    // Fetch Peers
    mapping(address => Peer) public peers;
    //map peers to an integer id
    //mapping(int => Peer) public peersID;
    // Store Peers Count
    int public peersCount;

    function startTradingPer(string memory date_set, uint time_period) public {
            require(msg.sender == admin.admin_account);
            init = true;
            date = date_set;
            time_per = time_period;
            iteration = 0;
            tradeCountIter = 0;
            //delete trade_bids;
            delete trades_pending;
            //delete localres_list;
            localresCounter =0;
            iteration_complete = false;
            peersTrading =0;
            global_pres = 0;
            global_dres = 0;
            is_optimal = false;
            trade_penCount = 0;
            numApprovedTrades =0;
            //delete approved;

    }

    //Store how many peers have registered to trade in time period
    uint public peersTrading;
    
    //peer is registering to trade in time period
    function registerPeer() public {
        //peer needs to have been added by admin
        require(peers[msg.sender].account == msg.sender);
        //admin needs to have initiated trading period
        require(init);
        require(!peers[msg.sender].isPeerActive);
        peersTrading ++;
        peers[msg.sender].isPeerActive = true;
        peers[msg.sender].num_trades_pending = 0;
    }
    
    
    //keep track of number of how trade bids have been submitted for this iteration
    //set to 5 for testing
    uint public tradeCountIter;

     //NB: will need to split up kwh into decimals as well
    struct Trade_bid {
        string date;
        uint time_period;
        address from;
        address to;
        int kwh; //need to decide on scaling factor
        uint price; //given in cents
        uint iteration;
        int id;
    }
    
    int id_set;

    // list of trade_bids for current iteration for current time_period
    Trade_bid [] public trade_bids; 

    //create mapping of trade_bids to trade ids
    mapping(int => Trade_bid) public trade_bids_mapping;

    //add trade bid to list of trade bids for this iteration- assumes peer won't submit duplicate trade bids 
    function addTradeBid (string memory date_peer, uint time_period, address s, address buy, int amount, uint price_c) public {
        //if previous iteration was completed
        if (iteration_complete){newIteration();}
        //check that trading period is initiated
        require(init);
        require(!iteration_complete);
        //check if sender address is members of the microgrid
        require(peers[s].isPeerActive);
        //check if buyer address is member of the microgrid
        require(peers[buy].isPeerActive);
        //requires that the person adding the trade bid is the account set as the sender
        require(msg.sender == s);
        //requires that the sender is not also the buyer
        require(msg.sender != buy);
        //requires peer to insert correct time_period
        require(time_period==time_per);
        //requires peer to insert correct date
        require(keccak256(abi.encodePacked(date)) == keccak256(abi.encodePacked(date_peer)));
        if (tradeCountIter ==0){iteration++;}
        //set the id
        id_set = (peers[s].id * 10)+ (peers[buy].id);
        trade_bids.push(Trade_bid(date, time_period, s, buy, amount, price_c, iteration, id_set));
        trade_bids_mapping[id_set] = Trade_bid(date, time_period, s, buy, amount, price_c, iteration, id_set);
        tradeCountIter++;
        
    }
    //NB: will need to decide by what magnitude of 10 we will be multiplying actual residual value in order
    // to store it in this mapping

    function newIteration() private {

        tradeCountIter = 0;
        delete trades_pending;
        delete localres_list;
        localresCounter =0;
        iteration_complete = false;
        global_pres = 0;
        global_dres = 0;
        is_optimal = false;

    }
    struct localRes{

        address from;
        int primal_res;
        int dual_res;
        uint iteration;

    }
    
    //maps addresses to local residuals for addresses 
    mapping (address => localRes) public localres;

    //keep track of how many peers have submitted local residuals for this iteration 
    uint public localresCounter; 

    //store the submitted local residuals for this iteration
    localRes [] public localres_list; 

    //global residuals = running sum of local residuals.  Make these private after testing?
    int public global_pres;
    int public global_dres;


    //is iteration complete? i.e. have all local residuals for this iteration been submitted
    bool public iteration_complete;
    bool public is_optimal;

    //add trade bid to list of trade bids for this iteration- assumes that each peer will not submit more than one local res per iteration
    function addLocalRes (int p_res, int d_res) public {
        //all trade bids need to be submitted for local residuals to be submitted
        require(tradeCountIter == ((peersTrading)*(peersTrading-1)));
        require(init);
        require(!iteration_complete);
        //requires that person submitting local residual to blockchain is a member of the microgrid
        require(peers[msg.sender].isPeerActive);
        localresCounter++;
        localres[msg.sender] = localRes(msg.sender, p_res, d_res, iteration);
        //add localres to localres_list if people want to see local residuals currently sent to smart contract for this iteration
        localres_list.push(localRes(msg.sender, p_res, d_res, iteration));
        global_pres = global_pres + p_res;
        global_dres = global_dres + d_res;
        if (localresCounter == peersTrading){checkOptimal();}

    }

    function checkOptimal() private {
            iteration_complete=true;
            if ((global_pres<= pri_tol) && (global_dres<=dual_tol)){
                
                is_optimal = true;
                //end iteration cycle for this trading period
                init = false;
                
                
                }

    }


    //only person SENDING money can create a Trade struct- by using their private key to sign this transaction, approves the transfer of money.  Almost like end of bidding process.
    struct Trade {
        
        string date;
        uint time_period;
        address from;
        address to; 
        int kwh;
        uint price_c;
        int id; //make an id for trade using buyer and seller
        bool approve_from;
        bool approve_to;
        bool optimal;

    }

   
   //store pending trades for this time period.  Pending trades are trades that have been created by sender but are pending approval from recipient in order to be binding.
    Trade [] public trades_pending;
    uint public trade_penCount;
    mapping (int => Trade) public trades_pending_mapping;

    int private trade_id;
    //create counter for trades
    //check if tradeCounterIter is correct and that localresCounter == peersCount for trade bid to be made
    function createTrade(string memory date_peer, uint time_period, address from, address to, int amount, uint price) public {
        require(msg.sender == from);
        require(msg.sender!=to);
        require(peers[msg.sender].isPeerActive);
        require(peers[to].isPeerActive);
        require(time_period==time_per);
        require(0>=amount);
        //requires peer to insert correct date
        require(keccak256(abi.encodePacked(date)) == keccak256(abi.encodePacked(date_peer)));
        //make array of created trades for that time period
        trade_id = (peers[from].id) * 10 + peers[to].id;
        //if ((trade_bids_mapping[trade_id].kwh == amount) && (trade_bids_mapping[trade_id].price==price)){
        trades_pending.push(Trade(date, time_period, from, to, amount, price, trade_id, true, false, is_optimal));
        trades_pending_mapping[trade_id] = Trade(date, time_period, from, to, amount, price, trade_id, true, false, is_optimal);
        peers[to].num_trades_pending = peers[to].num_trades_pending + 1;
        trade_penCount ++;
        //}
        
        //else {

          //  trades_pending.push(Trade(date, time_period, from, to, amount, price, trade_id, true, false, false));
           // trade_penCount ++;
        //}

    }



    //create mapping for id to approved trades between those added peers for this time period
    mapping (int => Trade) public approved_trades; //do I need this mapping?
    Trade [] public approved; 

    //running counter of how many trades have been approved for this time period
    uint public numApprovedTrades;

    function approveTrade(string memory trade_date, uint trade_time, address trade_from, address trade_to, int trade_kwh, uint trade_price_c, int id, bool trade_approve_from, bool trade_approve_to, bool trade_optimal, string memory date_approved, uint time_approved, int trades_pending_ind) public {
            
            require(msg.sender == trade_to);
            //trade must be listed have been created correctly
            require(trades_pending_mapping[trades_pending_ind].from == trade_from);
            require(trades_pending_mapping[trades_pending_ind].kwh == trade_kwh);
            require(trades_pending_mapping[trades_pending_ind].price_c == trade_price_c);
            require(keccak256(abi.encodePacked(trade_date)) == keccak256(abi.encodePacked(date_approved)));
            require(time_approved==trade_time);
            require(!trade_approve_to);
            approved_trades[id]  = Trade(trade_date, trade_time, trade_from, trade_to, trade_kwh, trade_price_c, id, trade_approve_from, true, trade_optimal);
            approved.push(Trade(trade_date, trade_time, trade_from, trade_to, trade_kwh, trade_price_c, id, trade_approve_from, true, trade_optimal));
            numApprovedTrades++;


    
    }

    //peers need to call this to indicate that they have completed their trading for this time period
    function deregisterPeer() public {
        //peer needs to have been added by admin
        require(peers[msg.sender].account == msg.sender);
        //admin needs to have initiated trading period
        require(peers[msg.sender].isPeerActive);
        peersTrading --;
        peers[msg.sender].isPeerActive = false;
    }
    
}

