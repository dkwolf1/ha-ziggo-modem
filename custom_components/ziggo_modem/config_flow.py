from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .api import ZiggoModemApi, ZiggoModemApiError, ZiggoModemAuthError
from .const import (
    CONF_DOWNSTREAM_POWER_MAX,
    CONF_DOWNSTREAM_POWER_MIN,
    CONF_DOWNSTREAM_SNR_MIN,
    CONF_HOST,
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_UPSTREAM_POWER_MAX,
    CONF_USERNAME,
    CONF_VERBOSE_DIAGNOSTICS,
    DEFAULT_DOWNSTREAM_POWER_MAX,
    DEFAULT_DOWNSTREAM_POWER_MIN,
    DEFAULT_DOWNSTREAM_SNR_MIN,
    DEFAULT_HOST,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
    DEFAULT_UPSTREAM_POWER_MAX,
    DEFAULT_VERBOSE_DIAGNOSTICS,
    DOMAIN,
    LANGUAGE_EN,
    LANGUAGE_NL,
)

LANGUAGE_SELECTOR = {
    LANGUAGE_NL: "Nederlands",
    LANGUAGE_EN: "English",
}


class ZiggoModemConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ziggo Modem."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            username = user_input.get(CONF_USERNAME, "")
            password = user_input[CONF_PASSWORD]
            language = user_input[CONF_LANGUAGE]

            api = ZiggoModemApi(host, username, password)

            try:
                await api.async_initialize()
                await api.async_login()
            except ZiggoModemAuthError:
                errors["base"] = "invalid_auth"
            except ZiggoModemApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            finally:
                await api.async_close()

            if not errors:
                await self.async_set_unique_id(host)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"Ziggo Modem ({host})",
                    data=user_input,
                    options={
                        CONF_SCAN_INTERVAL: DEFAULT_SCAN_INTERVAL,
                        CONF_DOWNSTREAM_POWER_MIN: DEFAULT_DOWNSTREAM_POWER_MIN,
                        CONF_DOWNSTREAM_POWER_MAX: DEFAULT_DOWNSTREAM_POWER_MAX,
                        CONF_DOWNSTREAM_SNR_MIN: DEFAULT_DOWNSTREAM_SNR_MIN,
                        CONF_UPSTREAM_POWER_MAX: DEFAULT_UPSTREAM_POWER_MAX,
                        CONF_VERBOSE_DIAGNOSTICS: DEFAULT_VERBOSE_DIAGNOSTICS,
                        CONF_LANGUAGE: language,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Optional(CONF_USERNAME, default=""): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(
                        CONF_LANGUAGE,
                        default=DEFAULT_LANGUAGE,
                    ): vol.In(LANGUAGE_SELECTOR),
                }
            ),
            errors=errors,
        )

    async def async_step_reauth(
        self,
        entry_data: Mapping[str, Any],
    ) -> FlowResult:
        """Start reauthentication for an existing config entry."""
        return await self.async_step_reauth_confirm()

    async def async_step_reauth_confirm(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Validate and store replacement modem credentials."""
        entry = self._get_reauth_entry()
        host = entry.options.get(
            CONF_HOST,
            entry.data.get(CONF_HOST, DEFAULT_HOST),
        )
        current_username = entry.options.get(
            CONF_USERNAME,
            entry.data.get(CONF_USERNAME, ""),
        )
        errors: dict[str, str] = {}

        if user_input is not None:
            username = user_input.get(CONF_USERNAME, "")
            password = user_input[CONF_PASSWORD]
            api = ZiggoModemApi(host, username, password)

            try:
                await api.async_initialize()
                await api.async_login()
            except ZiggoModemAuthError:
                errors["base"] = "invalid_auth"
            except ZiggoModemApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            finally:
                await api.async_close()

            if not errors:
                await self.async_set_unique_id(entry.unique_id or host)
                self._abort_if_unique_id_mismatch()

                credential_updates = {
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                }
                self.hass.config_entries.async_update_entry(
                    entry,
                    options={
                        **entry.options,
                        **credential_updates,
                    },
                )
                return self.async_update_reload_and_abort(
                    entry,
                    data_updates=credential_updates,
                )

        return self.async_show_form(
            step_id="reauth_confirm",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_USERNAME,
                        default=current_username,
                    ): str,
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        )
                    ),
                }
            ),
            errors=errors,
            description_placeholders={"host": host},
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return ZiggoModemOptionsFlow()


class ZiggoModemOptionsFlow(config_entries.OptionsFlow):
    """Handle Ziggo Modem options."""

    async def async_step_init(self, user_input=None) -> FlowResult:
        errors: dict[str, str] = {}

        current_host = self.config_entry.options.get(
            CONF_HOST,
            self.config_entry.data.get(CONF_HOST, DEFAULT_HOST),
        )
        current_username = self.config_entry.options.get(
            CONF_USERNAME,
            self.config_entry.data.get(CONF_USERNAME, ""),
        )
        current_password = self.config_entry.options.get(
            CONF_PASSWORD,
            self.config_entry.data.get(CONF_PASSWORD, ""),
        )
        current_scan_interval = self.config_entry.options.get(
            CONF_SCAN_INTERVAL,
            DEFAULT_SCAN_INTERVAL,
        )
        current_verbose_diagnostics = self.config_entry.options.get(
            CONF_VERBOSE_DIAGNOSTICS,
            DEFAULT_VERBOSE_DIAGNOSTICS,
        )
        current_language = self.config_entry.options.get(
            CONF_LANGUAGE,
            DEFAULT_LANGUAGE,
        )
        current_downstream_power_min = self.config_entry.options.get(
            CONF_DOWNSTREAM_POWER_MIN,
            DEFAULT_DOWNSTREAM_POWER_MIN,
        )
        current_downstream_power_max = self.config_entry.options.get(
            CONF_DOWNSTREAM_POWER_MAX,
            DEFAULT_DOWNSTREAM_POWER_MAX,
        )
        current_downstream_snr_min = self.config_entry.options.get(
            CONF_DOWNSTREAM_SNR_MIN,
            DEFAULT_DOWNSTREAM_SNR_MIN,
        )
        current_upstream_power_max = self.config_entry.options.get(
            CONF_UPSTREAM_POWER_MAX,
            DEFAULT_UPSTREAM_POWER_MAX,
        )

        if user_input is not None:
            host = user_input[CONF_HOST]
            username = user_input.get(CONF_USERNAME, "")
            password = user_input[CONF_PASSWORD]

            api = ZiggoModemApi(host, username, password)

            try:
                await api.async_initialize()
                await api.async_login()
            except ZiggoModemAuthError:
                errors["base"] = "invalid_auth"
            except ZiggoModemApiError:
                errors["base"] = "cannot_connect"
            except Exception:
                errors["base"] = "unknown"
            finally:
                await api.async_close()

            if not errors:
                entry_data = self.hass.data.get(DOMAIN, {}).get(
                    self.config_entry.entry_id
                )
                if entry_data:
                    entry_data[CONF_VERBOSE_DIAGNOSTICS] = user_input[
                        CONF_VERBOSE_DIAGNOSTICS
                    ]
                    entry_data[CONF_LANGUAGE] = user_input[CONF_LANGUAGE]
                    entry_data["coordinator"].async_update_listeners()

                return self.async_create_entry(
                    title="",
                    data={
                        CONF_HOST: host,
                        CONF_USERNAME: username,
                        CONF_PASSWORD: password,
                        CONF_SCAN_INTERVAL: user_input[CONF_SCAN_INTERVAL],
                        CONF_DOWNSTREAM_POWER_MIN: user_input[
                            CONF_DOWNSTREAM_POWER_MIN
                        ],
                        CONF_DOWNSTREAM_POWER_MAX: user_input[
                            CONF_DOWNSTREAM_POWER_MAX
                        ],
                        CONF_DOWNSTREAM_SNR_MIN: user_input[
                            CONF_DOWNSTREAM_SNR_MIN
                        ],
                        CONF_UPSTREAM_POWER_MAX: user_input[
                            CONF_UPSTREAM_POWER_MAX
                        ],
                        CONF_VERBOSE_DIAGNOSTICS: user_input[
                            CONF_VERBOSE_DIAGNOSTICS
                        ],
                        CONF_LANGUAGE: user_input[CONF_LANGUAGE],
                    },
                )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=current_host): str,
                    vol.Optional(CONF_USERNAME, default=current_username): str,
                    vol.Required(CONF_PASSWORD, default=current_password): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
                    vol.Required(
                        CONF_DOWNSTREAM_POWER_MIN,
                        default=current_downstream_power_min,
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=-30, max=-0.1),
                    ),
                    vol.Required(
                        CONF_DOWNSTREAM_POWER_MAX,
                        default=current_downstream_power_max,
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=0.1, max=30),
                    ),
                    vol.Required(
                        CONF_DOWNSTREAM_SNR_MIN,
                        default=current_downstream_snr_min,
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=20, max=50),
                    ),
                    vol.Required(
                        CONF_UPSTREAM_POWER_MAX,
                        default=current_upstream_power_max,
                    ): vol.All(
                        vol.Coerce(float),
                        vol.Range(min=30, max=65),
                    ),
                    vol.Required(
                        CONF_VERBOSE_DIAGNOSTICS,
                        default=current_verbose_diagnostics,
                    ): bool,
                    vol.Required(
                        CONF_LANGUAGE,
                        default=current_language,
                    ): vol.In(LANGUAGE_SELECTOR),
                }
            ),
            errors=errors,
        )
