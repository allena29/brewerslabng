import pytest

from mock import patch, Mock, call
import unittest
import time

from blng.RabbitMq import Consumer, Producer


class ConsumerExtended(Consumer):

    def _open_connection(self):
        self.connection = Mock()
        self.channel = Mock()
        return True


class ProducerExtended(Producer):

    def _open_connection(self):
        self.connection = Mock()
        self.channel = Mock()
        return True


@pytest.fixture
def producer_subject():
    instance = ProducerExtended(exchange='my_exchange_id')

    yield instance


@pytest.fixture
def consumer_subject():
    instance = ConsumerExtended(exchange='my_exchange_id')

    yield instance


def test_producer(producer_subject):
    msg = {}
    port = 'portid'

    # Act
    producer_subject.send_message(msg, port)

    # Assert
    producer_subject.channel.basic_publish.assert_called_once_with(body='{"_operation": "unknown-app"}',
                                                                   exchange='my_exchange_id',
                                                                   routing_key='portid')
