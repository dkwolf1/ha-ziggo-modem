from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp

_LOGGER = logging.getLogger(__name__)

_POLL_RESPONSE_FIELDS = {
    "state": ("cablemodem", dict),
    "downstream": ("downstream", dict),
    "primary_downstream": ("channel", dict),
    "upstream": ("upstream", dict),
    "serviceflows": ("serviceFlows", list),
    "softwareupdate": ("softwareUpdate", dict),
}


def _valid_poll_response(endpoint: str, result: Any) -> bool:
    """Check the expected structure without requiring optional modem fields."""
    field, field_type = _POLL_RESPONSE_FIELDS[endpoint]
    if not isinstance(result, dict) or not isinstance(result.get(field), field_type):
        return False

    payload = result[field]
    if endpoint in {"downstream", "upstream"}:
        channels = payload.get("channels", [])
        return isinstance(channels, list) and all(
            isinstance(channel, dict) for channel in channels
        )
    if endpoint == "serviceflows":
        return all(
            isinstance(flow, dict) and isinstance(flow.get("serviceFlow", {}), dict)
            for flow in payload
        )
    return True


class ZiggoModemApiError(Exception):
    """Generic Ziggo modem API error."""

    def __init__(self, message: str, *, code: str = "request_error") -> None:
        super().__init__(message)
        self.code = code


class ZiggoModemAuthError(ZiggoModemApiError):
    """Authentication error."""


class ZiggoModemApi:
    """Client for the Ziggo Sagemcom modem REST API."""

    def __init__(
        self,
        host: str,
        username: str,
        password: str,
        session: aiohttp.ClientSession,
    ) -> None:
        self._host = host
        self._username = username
        self._password = password
        self._base_url = f"https://{host}/rest/v1"
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=20)
        self._request_headers = {
            "Accept": "application/json, text/plain, */*",
            "Content-Type": "application/json",
        }
        self._token: str | None = None
        self._token_lock = asyncio.Lock()
        self._last_endpoint_status: dict[str, str] = {}
        self._last_endpoint_errors: dict[str, str] = {}

    @property
    def host(self) -> str:
        """Return the modem host."""
        return self._host

    @property
    def last_endpoint_status(self) -> dict[str, str]:
        """Return the status of the last endpoint fetch."""
        return self._last_endpoint_status

    @property
    def last_endpoint_errors(self) -> dict[str, str]:
        """Return safe error codes for failed endpoints in the last poll."""
        return self._last_endpoint_errors

    @staticmethod
    async def _read_json(response: aiohttp.ClientResponse) -> Any:
        """Read JSON without including response bodies in errors."""
        try:
            return await response.json()
        except (aiohttp.ContentTypeError, ValueError) as err:
            raise ZiggoModemApiError(
                "Invalid JSON response from modem", code="invalid_response"
            ) from err

    async def async_close(self) -> None:
        """Release the authenticated modem session."""
        try:
            await self.async_logout()
        except Exception:
            _LOGGER.debug("Logout failed during close", exc_info=True)

    async def async_login(self) -> None:
        """Authenticate and store token."""
        if self._session.closed:
            raise ZiggoModemApiError("Home Assistant HTTP session is closed")

        url = f"{self._base_url}/user/login"
        payload = {"password": self._password}
        if self._username:
            payload["username"] = self._username

        _LOGGER.debug("Logging in to Ziggo modem at %s", self._host)

        try:
            async with self._session.post(
                url,
                json=payload,
                headers=self._request_headers,
                timeout=self._timeout,
            ) as response:
                if response.status in (401, 403):
                    raise ZiggoModemAuthError("Invalid modem credentials")

                if response.status not in (200, 201):
                    raise ZiggoModemApiError(
                        f"Unexpected login status {response.status}",
                        code=f"http_{response.status}",
                    )

                data = await self._read_json(response)

        except TimeoutError as err:
            raise ZiggoModemApiError("Login timed out", code="timeout") from err
        except aiohttp.ClientError as err:
            raise ZiggoModemApiError("Login request failed", code="network_error") from err

        created = data.get("created", {}) if isinstance(data, dict) else None
        if not isinstance(created, dict):
            raise ZiggoModemApiError(
                "Unexpected modem login response", code="invalid_response"
            )
        token = created.get("token")
        if not token:
            raise ZiggoModemAuthError("Login succeeded but no token was returned")

        self._token = token
        _LOGGER.debug("Login succeeded")

    async def async_logout(self) -> None:
        """Try to log out gracefully."""
        if self._session.closed or not self._token:
            return

        url = f"{self._base_url}/user/logout"

        try:
            async with self._session.post(
                url,
                headers=self._auth_headers(),
                timeout=self._timeout,
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
        if self._session.closed:
            raise ZiggoModemApiError("Home Assistant HTTP session is closed")

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
                timeout=self._timeout,
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

                if response.status in (401, 403):
                    raise ZiggoModemAuthError("Authentication failed")

                if response.status >= 400:
                    raise ZiggoModemApiError(
                        f"{path} failed: HTTP {response.status}",
                        code=f"http_{response.status}",
                    )

                if "application/json" in response.headers.get("Content-Type", ""):
                    return await self._read_json(response)

                return await response.text()

        except TimeoutError as err:
            raise ZiggoModemApiError("Modem request timed out", code="timeout") from err
        except aiohttp.ClientError as err:
            raise ZiggoModemApiError("Modem request failed", code="network_error") from err

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

        tasks = {
            "state": self.async_get_state(),
            "downstream": self.async_get_downstream(),
            "primary_downstream": self.async_get_primary_downstream(),
            "upstream": self.async_get_upstream(),
            "serviceflows": self.async_get_serviceflows(),
            "softwareupdate": self.async_get_softwareupdate(),
        }

        results = await asyncio.gather(*tasks.values(), return_exceptions=True)

        data: dict[str, Any] = {}
        endpoint_status: dict[str, str] = {}
        endpoint_errors: dict[str, str] = {}
        auth_error: ZiggoModemAuthError | None = None

        for key, result in zip(tasks, results, strict=True):
            if isinstance(result, asyncio.CancelledError):
                raise result
            if isinstance(result, ZiggoModemAuthError):
                auth_error = result
                code = "authentication"
            elif isinstance(result, ZiggoModemApiError):
                code = result.code
            elif isinstance(result, Exception):
                code = "unexpected_error"
            elif not _valid_poll_response(key, result):
                code = "invalid_response"
            else:
                data[key] = result
                endpoint_status[key] = "ok"
                continue

            _LOGGER.debug("Endpoint %s failed: %s", key, code)
            data[key] = {}
            endpoint_status[key] = "failed"
            endpoint_errors[key] = code

        self._last_endpoint_status = endpoint_status
        self._last_endpoint_errors = endpoint_errors

        if auth_error is not None:
            raise auth_error

        return data
