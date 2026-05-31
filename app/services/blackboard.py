import httpx
import asyncio
from base64 import b64encode
from datetime import datetime, timedelta
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class BlackboardClient:
    def __init__(self):
        self.base_url = settings.BLACKBOARD_API_URL
        self.client_id = settings.BLACKBOARD_CLIENT_ID
        self.client_secret = settings.BLACKBOARD_CLIENT_SECRET
        self.access_token = None
        self.token_expires_at = None
        
        # Throttling / Rate limit management
        self._lock = asyncio.Lock()
        self._calls_per_second_limit = 10  # Arbitrary limit, adjust based on Blackboard docs
        self._semaphore = asyncio.Semaphore(self._calls_per_second_limit)

    async def _get_auth_headers(self) -> dict:
        auth_str = f"{self.client_id}:{self.client_secret}"
        encoded_auth = b64encode(auth_str.encode()).decode()
        return {
            "Authorization": f"Basic {encoded_auth}",
            "Content-Type": "application/x-www-form-urlencoded"
        }

    async def authenticate(self):
        """Authenticates with Blackboard using Client Credentials flow."""
        url = f"{self.base_url}/learn/api/public/v1/oauth2/token"
        headers = await self._get_auth_headers()
        data = {"grant_type": "client_credentials"}
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)
            logger.info("Successfully authenticated with Blackboard API.")

    async def _ensure_authenticated(self):
        async with self._lock:
            if not self.access_token or not self.token_expires_at or datetime.now() >= self.token_expires_at:
                await self.authenticate()

    async def _wait_for_rate_limit(self, response: httpx.Response):
        """Handle Blackboard 429 Too Many Requests if applicable."""
        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 1))
            logger.warning(f"Rate limited by Blackboard. Waiting {retry_after} seconds.")
            await asyncio.sleep(retry_after)
            return True
        return False

    async def make_request(self, method: str, endpoint: str, params: dict = None, json_data: dict = None, max_retries: int = 3):
        """Makes an authenticated, rate-limited request to the Blackboard API."""
        await self._ensure_authenticated()
        
        url = f"{self.base_url}{endpoint}"
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        async with self._semaphore:
            async with httpx.AsyncClient() as client:
                for attempt in range(max_retries):
                    try:
                        # Simple throttling: sleep a tiny bit to prevent bursting
                        await asyncio.sleep(1.0 / self._calls_per_second_limit)
                        
                        start_time = datetime.now()
                        if method.upper() == "GET":
                            response = await client.get(url, headers=headers, params=params)
                        elif method.upper() == "POST":
                            response = await client.post(url, headers=headers, json=json_data)
                        else:
                            raise ValueError(f"Unsupported method: {method}")
                        
                        latency = (datetime.now() - start_time).total_seconds() * 1000
                        # TODO: Log latency to SystemMetric table if needed here or in ETL
                        
                        if await self._wait_for_rate_limit(response):
                            continue
                            
                        response.raise_for_status()
                        return response.json()
                    
                    except httpx.HTTPStatusError as e:
                        if e.response.status_code == 401:
                            logger.info("Token expired during request, re-authenticating.")
                            self.access_token = None
                            await self._ensure_authenticated()
                            headers["Authorization"] = f"Bearer {self.access_token}"
                            continue
                        logger.error(f"HTTP error on {endpoint}: {e}")
                        if attempt == max_retries - 1:
                            raise
                    except Exception as e:
                        logger.error(f"Request failed on {endpoint}: {e}")
                        if attempt == max_retries - 1:
                            raise
                        await asyncio.sleep(2 ** attempt)

bb_client = BlackboardClient()
