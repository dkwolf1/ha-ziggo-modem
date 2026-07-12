from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .api import ZiggoModemApi, ZiggoModemApiError, ZiggoModemAuthError
from .const import (
    CONF_HOST,
    CONF_LANGUAGE,
    CONF_PASSWORD,
    CONF_SCAN_INTERVAL,
    CONF_USERNAME,
    CONF_VERBOSE_DIAGNOSTICS,
    DEFAULT_HOST,
    DEFAULT_LANGUAGE,
    DEFAULT_SCAN_INTERVAL,
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
            username = user_input[CONF_USERNAME]
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
                        CONF_VERBOSE_DIAGNOSTICS: DEFAULT_VERBOSE_DIAGNOSTICS,
                        CONF_LANGUAGE: language,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_HOST, default=DEFAULT_HOST): str,
                    vol.Required(CONF_USERNAME): str,
                    vol.Required(CONF_PASSWORD): str,
                    vol.Required(
                        CONF_LANGUAGE,
                        default=DEFAULT_LANGUAGE,
                    ): vol.In(LANGUAGE_SELECTOR),
                }
            ),
            errors=errors,
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

        if user_input is not None:
            host = user_input[CONF_HOST]
            username = user_input[CONF_USERNAME]
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
                    vol.Required(CONF_USERNAME, default=current_username): str,
                    vol.Required(CONF_PASSWORD, default=current_password): str,
                    vol.Required(
                        CONF_SCAN_INTERVAL,
                        default=current_scan_interval,
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=3600)),
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
