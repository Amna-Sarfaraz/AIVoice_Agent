import asyncio
from stt.deepgram_client import DeepgramSTT

async def main():
    stt=DeepgramSTT()
    try:
        await stt.run()
    except KeyboardInterrupt:
        stt.stop()
        print("\nStopped.")

if __name__=="__main__":              # it separates code that defines things from code that does things. Definition always runs. Execution only runs when you choose to.
    asyncio.run(main())               # Every Python file has a built-in variable called __name__. Python sets this variable automatically depending on how the file is being used.

