import asyncio

data_global = 0 

async def f1() :
    global data_global
    while True :
        print("f1 something")
        data_global += 1 
        await asyncio.sleep(1)
    

async def f2() :
    global data_global
    while True : 
        print("data global from f2", data_global)
        await asyncio.sleep(1)

async def main() : 
    await asyncio.gather(
        f1(),
        f2()
    )

asyncio.run(main=main())