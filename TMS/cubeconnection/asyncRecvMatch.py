from pymavlink import mavutil
import asyncio

'''
mavlink recv_match is badly written and not asynchronous
therefore the performance is quite slow

this code sets to rewrite messages such that 
'''


refresh_time = 0.05
async def asyncRecvMatch(connection, type: str, blocking: bool=False):
    ## blocking isn't necessary
    print(type)
    while True:
        m = connection.recv_msg()
        if m is None:
            continue        
        await asyncio.sleep(refresh_time) ## poll through messages
        ## probably easier if there's just one massive message handler
        
        if type == m.get_type():
            print(m)
            return m.to_dict()