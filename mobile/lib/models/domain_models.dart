void _validateKeys(
  Map<String, Object?> json, {
  required Set<String> required,
  Set<String> optional = const {},
}) {
  final keys = json.keys.toSet();
  if (!keys.containsAll(required) ||
      !required.union(optional).containsAll(keys)) {
    throw FormatException('Unexpected or missing contract fields: $keys');
  }
}

T _field<T>(Map<String, Object?> json, String name) {
  final value = json[name];
  if (value is! T) throw FormatException('Invalid $name');
  return value;
}

List<String> _strings(Map<String, Object?> json, String name) {
  return _field<List<Object?>>(json, name)
      .map((item) {
        if (item is! String) throw FormatException('Invalid $name item');
        return item;
      })
      .toList(growable: false);
}

class DeviceSession {
  DeviceSession({
    required this.deviceSessionId,
    required this.accessToken,
    required this.accessExpiresAt,
    required this.renewalToken,
    required this.renewalExpiresAt,
    required this.backendName,
    required this.backendFingerprint,
  });

  factory DeviceSession.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {
        'device_session_id',
        'access_token',
        'access_expires_at',
        'renewal_token',
        'renewal_expires_at',
        'backend_name',
        'backend_fingerprint',
      },
    );
    return DeviceSession(
      deviceSessionId: _field(json, 'device_session_id'),
      accessToken: _field(json, 'access_token'),
      accessExpiresAt: DateTime.parse(_field(json, 'access_expires_at')),
      renewalToken: _field(json, 'renewal_token'),
      renewalExpiresAt: DateTime.parse(_field(json, 'renewal_expires_at')),
      backendName: _field(json, 'backend_name'),
      backendFingerprint: _field(json, 'backend_fingerprint'),
    );
  }

  final String deviceSessionId;
  final String accessToken;
  final DateTime accessExpiresAt;
  final String renewalToken;
  final DateTime renewalExpiresAt;
  final String backendName;
  final String backendFingerprint;

  Map<String, Object?> toJson() => {
    'device_session_id': deviceSessionId,
    'access_token': accessToken,
    'access_expires_at': accessExpiresAt.toUtc().toIso8601String(),
    'renewal_token': renewalToken,
    'renewal_expires_at': renewalExpiresAt.toUtc().toIso8601String(),
    'backend_name': backendName,
    'backend_fingerprint': backendFingerprint,
  };
}

class SharedContextPart {
  SharedContextPart({
    required this.partId,
    required this.kind,
    required this.mediaType,
    required this.sizeBytes,
    required this.digest,
    this.text,
    this.uploadId,
  });

  factory SharedContextPart.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {'part_id', 'kind', 'media_type', 'size_bytes', 'digest'},
      optional: {'text', 'upload_id'},
    );
    return SharedContextPart(
      partId: _field(json, 'part_id'),
      kind: _field(json, 'kind'),
      mediaType: _field(json, 'media_type'),
      sizeBytes: _field(json, 'size_bytes'),
      digest: _field(json, 'digest'),
      text: json['text'] as String?,
      uploadId: json['upload_id'] as String?,
    );
  }

  final String partId;
  final String kind;
  final String mediaType;
  final int sizeBytes;
  final String digest;
  final String? text;
  final String? uploadId;

  Map<String, Object?> toJson() => {
    'part_id': partId,
    'kind': kind,
    'media_type': mediaType,
    'size_bytes': sizeBytes,
    'digest': digest,
    if (text != null) 'text': text,
    if (uploadId != null) 'upload_id': uploadId,
  };
}

class ConsentReceipt {
  ConsentReceipt({
    required this.receiptId,
    required this.contentDigest,
    required this.purpose,
    required this.destinationSessionId,
    required this.approvedPartIds,
    required this.issuedAt,
    required this.expiresAt,
  });

  factory ConsentReceipt.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {
        'receipt_id',
        'content_digest',
        'purpose',
        'destination_session_id',
        'approved_part_ids',
        'issued_at',
        'expires_at',
      },
    );
    return ConsentReceipt(
      receiptId: _field(json, 'receipt_id'),
      contentDigest: _field(json, 'content_digest'),
      purpose: _field(json, 'purpose'),
      destinationSessionId: _field(json, 'destination_session_id'),
      approvedPartIds: _strings(json, 'approved_part_ids'),
      issuedAt: DateTime.parse(_field(json, 'issued_at')),
      expiresAt: DateTime.parse(_field(json, 'expires_at')),
    );
  }

  final String receiptId;
  final String contentDigest;
  final String purpose;
  final String destinationSessionId;
  final List<String> approvedPartIds;
  final DateTime issuedAt;
  final DateTime expiresAt;

  Map<String, Object?> toJson() => {
    'receipt_id': receiptId,
    'content_digest': contentDigest,
    'purpose': purpose,
    'destination_session_id': destinationSessionId,
    'approved_part_ids': approvedPartIds,
    'issued_at': issuedAt.toUtc().toIso8601String(),
    'expires_at': expiresAt.toUtc().toIso8601String(),
  };
}

class SharedContext {
  SharedContext({
    required this.conversationId,
    required this.source,
    required this.purpose,
    required this.parts,
    required this.consent,
  });

  factory SharedContext.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {'conversation_id', 'source', 'purpose', 'parts', 'consent'},
    );
    return SharedContext(
      conversationId: _field(json, 'conversation_id'),
      source: _field(json, 'source'),
      purpose: _field(json, 'purpose'),
      parts: _field<List<Object?>>(json, 'parts')
          .map(
            (item) => SharedContextPart.fromJson(item as Map<String, Object?>),
          )
          .toList(growable: false),
      consent: ConsentReceipt.fromJson(_field(json, 'consent')),
    );
  }

  final String conversationId;
  final String source;
  final String purpose;
  final List<SharedContextPart> parts;
  final ConsentReceipt consent;

  Map<String, Object?> toJson() => {
    'conversation_id': conversationId,
    'source': source,
    'purpose': purpose,
    'parts': parts.map((part) => part.toJson()).toList(growable: false),
    'consent': consent.toJson(),
  };
}

class Conversation {
  Conversation({
    required this.conversationId,
    required this.title,
    required this.status,
    required this.updatedAt,
  });

  factory Conversation.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {'conversation_id', 'title', 'status', 'updated_at'},
    );
    return Conversation(
      conversationId: _field(json, 'conversation_id'),
      title: _field(json, 'title'),
      status: _field(json, 'status'),
      updatedAt: DateTime.parse(_field(json, 'updated_at')),
    );
  }

  final String conversationId;
  final String title;
  final String status;
  final DateTime updatedAt;

  Map<String, Object?> toJson() => {
    'conversation_id': conversationId,
    'title': title,
    'status': status,
    'updated_at': updatedAt.toUtc().toIso8601String(),
  };
}

class EventEnvelope {
  EventEnvelope({
    required this.eventId,
    required this.sequence,
    required this.eventType,
    required this.resourceId,
    required this.correlationId,
    required this.occurredAt,
    this.fragment,
  });

  factory EventEnvelope.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {
        'event_id',
        'sequence',
        'event_type',
        'resource_id',
        'correlation_id',
        'occurred_at',
      },
      optional: {'fragment'},
    );
    return EventEnvelope(
      eventId: _field(json, 'event_id'),
      sequence: _field(json, 'sequence'),
      eventType: _field(json, 'event_type'),
      resourceId: _field(json, 'resource_id'),
      correlationId: _field(json, 'correlation_id'),
      occurredAt: DateTime.parse(_field(json, 'occurred_at')),
      fragment: json['fragment'] as String?,
    );
  }

  final String eventId;
  final int sequence;
  final String eventType;
  final String resourceId;
  final String correlationId;
  final DateTime occurredAt;
  final String? fragment;

  Map<String, Object?> toJson() => {
    'event_id': eventId,
    'sequence': sequence,
    'event_type': eventType,
    'resource_id': resourceId,
    'correlation_id': correlationId,
    'occurred_at': occurredAt.toUtc().toIso8601String(),
    if (fragment != null) 'fragment': fragment,
  };
}

class Approval {
  Approval({
    required this.approvalId,
    required this.status,
    required this.origin,
    required this.capability,
    required this.risk,
    required this.effectSummary,
    required this.disclosureSummary,
    required this.allowedScopes,
    required this.expiresAt,
    required this.actionKey,
  });

  factory Approval.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {
        'approval_id',
        'status',
        'origin',
        'capability',
        'risk',
        'effect_summary',
        'disclosure_summary',
        'allowed_scopes',
        'expires_at',
        'action_key',
      },
    );
    return Approval(
      approvalId: _field(json, 'approval_id'),
      status: _field(json, 'status'),
      origin: _field(json, 'origin'),
      capability: _field(json, 'capability'),
      risk: _field(json, 'risk'),
      effectSummary: _field(json, 'effect_summary'),
      disclosureSummary: _field(json, 'disclosure_summary'),
      allowedScopes: _strings(json, 'allowed_scopes'),
      expiresAt: DateTime.parse(_field(json, 'expires_at')),
      actionKey: _field(json, 'action_key'),
    );
  }

  final String approvalId;
  final String status;
  final String origin;
  final String capability;
  final String risk;
  final String effectSummary;
  final String disclosureSummary;
  final List<String> allowedScopes;
  final DateTime expiresAt;
  final String actionKey;

  Map<String, Object?> toJson() => {
    'approval_id': approvalId,
    'status': status,
    'origin': origin,
    'capability': capability,
    'risk': risk,
    'effect_summary': effectSummary,
    'disclosure_summary': disclosureSummary,
    'allowed_scopes': allowedScopes,
    'expires_at': expiresAt.toUtc().toIso8601String(),
    'action_key': actionKey,
  };
}

class UserTask {
  UserTask({
    required this.taskId,
    required this.kind,
    required this.status,
    required this.title,
    required this.origin,
    required this.updatedAt,
    this.scheduledFor,
  });

  factory UserTask.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {'task_id', 'kind', 'status', 'title', 'origin', 'updated_at'},
      optional: {'scheduled_for'},
    );
    return UserTask(
      taskId: _field(json, 'task_id'),
      kind: _field(json, 'kind'),
      status: _field(json, 'status'),
      title: _field(json, 'title'),
      origin: _field(json, 'origin'),
      scheduledFor: json['scheduled_for'] == null
          ? null
          : DateTime.parse(json['scheduled_for']! as String),
      updatedAt: DateTime.parse(_field(json, 'updated_at')),
    );
  }

  final String taskId;
  final String kind;
  final String status;
  final String title;
  final String origin;
  final DateTime? scheduledFor;
  final DateTime updatedAt;

  Map<String, Object?> toJson() => {
    'task_id': taskId,
    'kind': kind,
    'status': status,
    'title': title,
    'origin': origin,
    if (scheduledFor != null)
      'scheduled_for': scheduledFor!.toUtc().toIso8601String(),
    'updated_at': updatedAt.toUtc().toIso8601String(),
  };
}

class PrivacyRecord {
  PrivacyRecord({
    required this.recordId,
    required this.category,
    required this.location,
    required this.createdAt,
    required this.retentionExpiresAt,
  });

  factory PrivacyRecord.fromJson(Map<String, Object?> json) {
    _validateKeys(
      json,
      required: {
        'record_id',
        'category',
        'location',
        'created_at',
        'retention_expires_at',
      },
    );
    return PrivacyRecord(
      recordId: _field(json, 'record_id'),
      category: _field(json, 'category'),
      location: _field(json, 'location'),
      createdAt: DateTime.parse(_field(json, 'created_at')),
      retentionExpiresAt: json['retention_expires_at'] == null
          ? null
          : DateTime.parse(json['retention_expires_at']! as String),
    );
  }

  final String recordId;
  final String category;
  final String location;
  final DateTime createdAt;
  final DateTime? retentionExpiresAt;

  Map<String, Object?> toJson() => {
    'record_id': recordId,
    'category': category,
    'location': location,
    'created_at': createdAt.toUtc().toIso8601String(),
    'retention_expires_at': retentionExpiresAt?.toUtc().toIso8601String(),
  };
}
