"""Publisher regression tests; no GPIO or broker access is performed."""

import importlib.util
import json
import os
import sys
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

SOURCE = Path(__file__).resolve().parents[1] / "send_rabbitmq_humi_temp_2_1.py"


def load_publisher(environment):
    sensor = types.SimpleNamespace(
        DHT22=22, read_retry=MagicMock(return_value=(45.0, 21.0))
    )
    pika = types.SimpleNamespace(
        PlainCredentials=MagicMock(),
        ConnectionParameters=MagicMock(),
        BlockingConnection=MagicMock(),
    )
    spec = importlib.util.spec_from_file_location("iot_publisher_under_test", SOURCE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    with (
        patch.dict(sys.modules, {"Adafruit_DHT": sensor, "pika": pika}),
        patch.dict(os.environ, environment, clear=True),
    ):
        spec.loader.exec_module(module)
    return module, sensor, pika


class PublisherTests(unittest.TestCase):
    def test_import_does_not_read_sensor_or_connect(self):
        _module, sensor, pika = load_publisher({"RABBITMQ_PASSWORD": "fixture-only"})
        sensor.read_retry.assert_not_called()
        pika.BlockingConnection.assert_not_called()

    def test_missing_password_is_rejected_before_connecting(self):
        module, sensor, pika = load_publisher({})
        with (
            patch.dict(os.environ, {}, clear=True),
            self.assertRaisesRegex(ValueError, "RABBITMQ_PASSWORD"),
        ):
            module.Publisher()
        sensor.read_retry.assert_not_called()
        pika.BlockingConnection.assert_not_called()

    def test_invalid_port_is_rejected_with_configuration_error(self):
        module, _sensor, pika = load_publisher({})
        for port in ("not-a-port", "0", "65536"):
            with self.subTest(port=port):
                environment = {
                    "RABBITMQ_PASSWORD": "fixture-only",
                    "RABBITMQ_PORT": port,
                }
                with (
                    patch.dict(os.environ, environment, clear=True),
                    self.assertRaisesRegex(ValueError, "RABBITMQ_PORT"),
                ):
                    module.Publisher()
        pika.BlockingConnection.assert_not_called()

    def test_compose_credentials_and_local_defaults_are_used(self):
        environment = {
            "RABBITMQ_DEFAULT_USER": "compose-user",
            "RABBITMQ_DEFAULT_PASS": "compose-fixture",
        }
        module, _sensor, pika = load_publisher(environment)
        with patch.dict(os.environ, environment, clear=True):
            module.Publisher().main()
        pika.PlainCredentials.assert_called_once_with("compose-user", "compose-fixture")
        pika.ConnectionParameters.assert_called_once_with(
            "localhost", 5672, "egov", pika.PlainCredentials.return_value
        )

    def test_failed_sensor_reading_keeps_legacy_sentinel_payload(self):
        environment = {"RABBITMQ_PASSWORD": "fixture-only"}
        module, sensor, pika = load_publisher(environment)
        sensor.read_retry.return_value = (None, None)
        with patch.dict(os.environ, environment, clear=True):
            module.Publisher().main()
        channel = pika.BlockingConnection.return_value.channel.return_value
        body = channel.basic_publish.call_args.kwargs["body"]
        self.assertEqual(json.loads(body), {"temp": -100.0, "humidity": -1.0})
        pika.BlockingConnection.return_value.close.assert_called_once()

    def test_explicit_settings_reach_connection(self):
        environment = {
            "RABBITMQ_HOST": "broker.example.invalid",
            "RABBITMQ_PORT": "5673",
            "RABBITMQ_VHOST": "sensors",
            "RABBITMQ_USER": "sensor-user",
            "RABBITMQ_PASSWORD": "fixture-only",
            "RABBITMQ_EXCHANGE": "sensor-events",
            "RABBITMQ_ROUTING_KEY": "temperature",
            "RABBITMQ_DEFAULT_USER": "compose-user",
            "RABBITMQ_DEFAULT_PASS": "compose-fixture",
        }
        module, _sensor, pika = load_publisher(environment)
        with patch.dict(os.environ, environment, clear=True):
            publisher = module.Publisher()
            publisher.main()
        pika.PlainCredentials.assert_called_with("sensor-user", "fixture-only")
        pika.ConnectionParameters.assert_called_with(
            "broker.example.invalid",
            5673,
            "sensors",
            pika.PlainCredentials.return_value,
        )
        channel = pika.BlockingConnection.return_value.channel.return_value
        sent = channel.basic_publish.call_args.kwargs
        self.assertEqual(sent["exchange"], "sensor-events")
        self.assertEqual(sent["routing_key"], "temperature")
        self.assertEqual(json.loads(sent["body"]), {"temp": 21.0, "humidity": 45.0})


if __name__ == "__main__":
    unittest.main()
