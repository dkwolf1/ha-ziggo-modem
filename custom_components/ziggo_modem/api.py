from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)


class ZiggoModemApiError(Exception):
    """Generic Ziggo modem API error."""


class ZiggoModemAuthError(ZiggoModemApiError):
    """Authentication error."""


class ZiggoModemApi:
    """Client for the Ziggo Sagemcom modem REST API."""

    def __init__(self, host: str, username: str, password: str) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._base_url = f"https://{host}/rest/v1"
        self._session: aiohttp.ClientSession | None = None
        self._token: str | None = None
        self._token_lock = asyncio.Lock()

    async def async_initialize(self) -> None:
        """Create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=20)
            connector = aiohttp.TCPConnector(ssl=False)

            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Content-Type": "application/json",
                },
            )

    async def async_close(self) -> None:
        """Close HTTP session."""
        try:
            await self.async_logout()
        except Exception:
            _LOGGER.debug("Logout failed during close", exc_info=True)

        if self._session and not self._session.closed:
            await self._session.close()

    async def async_login(self) -> None:
        """Authenticate and store token."""
        await self.async_initialize()

        if self._session is None:
            raise ZiggoModemApiError("HTTP session not initialized")

        url = f"{self._base_url}/user/login"
        payload = {
            "username": self._username,
            "password": self._password,
        }

        _LOGGER.debug("Logging in to Ziggo modem at %s", self._host)

        try:
            async with self._session.post(url, json=payload) as response:
                text = await response.text()

                if response.status in (401, 403):
                    raise ZiggoModemAuthError("Invalid modem credentials")

                if response.status not in (200, 201):
                    raise ZiggoModemApiError(
                        f"Unexpected login status {response.status}: {text}"
                    )

                data = await response.json()

        except aiohttp.ClientError as err:
            raise ZiggoModemApiError(f"Login request failed: {err}") from err

        token = data.get("created", {}).get("token")
        if not token:
            raise ZiggoModemAuthError("Login succeeded but no token was returned")

        self._token = token
        _LOGGER.debug("Login succeeded")

    async def async_logout(self) -> None:
        """Try to log out gracefully."""
        if self._session is None or self._session.closed or not self._token:
            return

        url = f"{self._base_url}/user/logout"

        try:
            async with self._session.post(
                url,
                headers=self._auth_headers(),
            ) as response:
                if response.status < 400:
                    _LOGGER.debug("Logout succeeded")
        except aiohttp.ClientError:
            _LOGGER.debug("Logout endpoint failed")

        self._token = None

    async def async_release_session(self) -> None:
        """Force release session."""
        _LOGGER.debug("Releasing Ziggo modem session")

        try:
            await self.async_logout()
        except Exception:
            _LOGGER.debug("Logout failed", exc_info=True)

        if self._session and not self._session.closed:
            await self._session.close()

        self._session = None
        self._token = None

    def _auth_headers(self) -> dict[str, str]:
        if not self._token:
            raise ZiggoModemAuthError("No token available")

        return {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._token}",
        }

    async def _async_request(
        self,
        method: str,
        path: str,
        *,
        retry_on_auth: bool = True,
        json_data: dict[str, Any] | None = None,
    ) -> Any:
        """Perform authenticated request."""
        await self.async_initialize()

        if self._session is None:
            raise ZiggoModemApiError("HTTP session not initialized")

        async with self._token_lock:
            if not self._token:
                await self.async_login()

        url = f"{self._base_url}/{path.lstrip('/')}"
        _LOGGER.debug("Request: %s %s", method, url)

        try:
            async with self._session.request(
                method,
                url,
                headers=self._auth_headers(),
                json=json_data,
            ) as response:

                if response.status in (401, 403) and retry_on_auth:
                    _LOGGER.debug("Token expired, re-authenticating")
                    async with self._token_lock:
                        await self.async_login()

                    return await self._async_request(
                        method,
                        path,
                        retry_on_auth=False,
                        json_data=json_data,
                    )

                text = await response.text()

                if response.status in (401, 403):
                    raise ZiggoModemAuthError("Authentication failed")

                if response.status >= 400:
                    raise ZiggoModemApiError(
                        f"{path} failed: {response.status} - {text}"
                    )

                if "application/json" in response.headers.get("Content-Type", ""):
                    return await response.json()

                return text

        except aiohttp.ClientError as err:
            raise ZiggoModemApiError(f"Request failed: {err}") from err

    async def async_get_state(self) -> dict[str, Any]:
        return await self._async_request("GET", "cablemodem/state_")

    async def async_get_downstream(self) -> dict[str, Any]:
        return await self._async_request("GET", "cablemodem/downstream")

    async def async_get_primary_downstream(self) -> dict[str, Any]:
        return await self._async_request("GET", "cablemodem/downstream/primary_")

    async def async_get_upstream(self) -> dict[str, Any]:
        return await self._async_request("GET", "cablemodem/upstream")

    async def async_get_serviceflows(self) -> dict[str, Any]:
        return await self._async_request("GET", "cablemodem/serviceflows")

    async def async_get_softwareupdate(self) -> dict[str, Any]:
        return await self._async_request("GET", "system/softwareupdate")

    async def async_reboot(self) -> None:
        """Reboot the modem."""
        data = await self._async_request(
            "POST",
            "system/reboot",
            json_data={"reboot": {"enable": True}},
        )

        if not isinstance(data, dict) or not data.get("accepted", False):
            raise ZiggoModemApiError("Modem reboot request was not accepted")

    async def async_get_data(self) -> dict[str, Any]:
        """Collect all modem data."""

        tasks = [
            self.async_get_state(),
            self.async_get_downstream(),
            self.async_get_primary_downstream(),
            self.async_get_upstream(),
            self.async_get_serviceflows(),
            self.async_get_softwareupdate(),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        keys = [
            "state",
            "downstream",
            "primary_downstream",
            "upstream",
            "serviceflows",
            "softwareupdate",
        ]

        data: dict[str, Any] = {}

        for key, result in zip(keys, results):
            if isinstance(result, Exception):
                _LOGGER.debug("Endpoint %s failed: %s", key, result)
                data[key] = {}
            else:
                data[key] = result

        return data
