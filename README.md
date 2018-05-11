TitanBox is a client - server system which demonstrates the Dual-Level Message Locked Encryption for secure Large file deduplication. Files are uploaded by user by logging into client system. System checks on the fly whether file is stored in server or not. If file is present in server, then there will be no uploading. Also files are encrypted through key provided by user. For encryption, we used a scheme known as message level encryption proposed by Rongmao Chen, Yi Mu, Guoin Yang and Fuchun Guo.

Below are the instructions for installation : 

1. Install mysql server on your system.

2. Log into mysql server.

3. Run tables.sql file as
	source (path to 'tables.sql');

4. Run titanBoxServer/main.py.

5. Run titanBoxClient/titanBoxClient.py.

6. Enjoy.
