import 'dart:convert';
import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:hermes_pocket/models/domain_models.dart';

void main() {
  test('all versioned API model fixtures round trip without field loss', () {
    final fixture =
        jsonDecode(
              File(
                '../contracts/fixtures/v1/api-models.json',
              ).readAsStringSync(),
            )
            as Map<String, Object?>;

    final roundTrips = <String, Map<String, Object?>>{
      'session': DeviceSession.fromJson(_map(fixture['session'])).toJson(),
      'shared_context': SharedContext.fromJson(
        _map(fixture['shared_context']),
      ).toJson(),
      'conversation': Conversation.fromJson(
        _map(fixture['conversation']),
      ).toJson(),
      'event': EventEnvelope.fromJson(_map(fixture['event'])).toJson(),
      'approval': Approval.fromJson(_map(fixture['approval'])).toJson(),
      'task': UserTask.fromJson(_map(fixture['task'])).toJson(),
      'privacy_record': PrivacyRecord.fromJson(
        _map(fixture['privacy_record']),
      ).toJson(),
    };

    for (final entry in roundTrips.entries) {
      expect(entry.value, _map(fixture[entry.key]), reason: entry.key);
    }
  });

  test('typed models reject undeclared native or API metadata', () {
    expect(
      () => EventEnvelope.fromJson({
        'event_id': 'event-1',
        'sequence': 1,
        'event_type': 'response_started',
        'resource_id': 'conversation-1',
        'correlation_id': 'request-1',
        'occurred_at': '2031-01-01T00:00:00.000Z',
        'raw_backend_payload': 'not allowed',
      }),
      throwsFormatException,
    );
  });
}

Map<String, Object?> _map(Object? value) {
  return (value as Map<String, Object?>);
}
