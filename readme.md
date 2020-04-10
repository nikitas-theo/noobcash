## Noobcash : a blockchain system implementation 
 
The system was implemented for the  2019-20 Distributed Systems course at the NTUA

A joint effort of :    <[nikitas-theo](https://github.com/nikitas-theo)\> , <[stelkasouridis](https://github.com/stelkasouridis)\>, <[orestischar](https://github.com/orestischar)\> 

* Consensus is guaranteed by Proof of Work. 
* Communication is achieved  with Flask REST API
* A coordinator is resposnible for bootstraping the system. After initial communication is established each client functions as an independent agent.
* A command-line interface (CLI) provides user functionality, interacting in the background with the server by REST point requests. 
   
The system can be tested locally for 5 nodes by running the scripts in *testing* directory. One output log will be produced for each client and server. The reports containt server-client interaction, requests, and useful system information.
 
install requirements with ` pip install -r requirements.txt` 

