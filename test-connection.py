import httpx
import asyncio

async def test_connection():
    client = httpx.AsyncClient()
    try:
        response = await client.get('http://outing-profile-service:80/')
        print(f'Status: {response.status_code}')
        print(f'Response: {response.text}')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        await client.aclose()

if __name__ == "__main__":
    asyncio.run(test_connection()) 