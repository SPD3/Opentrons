# 8 to 1 Channel Pipette codebase

This code base shows how to convert an 8 channel p10 pipette to act as only a 
single channel pipette. The files in the directory 8_1_resources have all of the 
code necessary to do this. 8_to_1.py is code that needs to be added to the top 
of your protocol in order to access the new EightToSingleChannelPipette class.
SampleProtocol.py shows a very simple protocol that uses this new pipette class.