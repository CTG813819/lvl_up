enum HistoryCategory { mission, entry, system, error, security }

class AppHistoryEntry {
  final String id;
  final String title;
  final String description;
  final DateTime timestamp;
  final HistoryCategory category;
  final Map<String, dynamic>? metadata;
  final String? errorCode;
  final String? stackTrace;
  final String? errorType;
  final Map<String, dynamic>? errorContext;

  AppHistoryEntry({
    required this.id,
    required this.title,
    required this.description,
    required this.timestamp,
    required this.category,
    this.metadata,
    this.errorCode,
    this.stackTrace,
    this.errorType,
    this.errorContext,
  });

  Map<String, dynamic> toJson() => {
    'id': id,
    'title': title,
    'description': description,
    'timestamp': timestamp.toIso8601String(),
    'category': category.toString(),
    'metadata': metadata,
    'errorCode': errorCode,
    'stackTrace': stackTrace,
    'errorType': errorType,
    'errorContext': errorContext,
  };

  factory AppHistoryEntry.fromJson(Map<String, dynamic> json) {
    return AppHistoryEntry(
      id: json['id'],
      title: json['title'],
      description: json['description'],
      timestamp: DateTime.parse(json['timestamp']),
      category: HistoryCategory.values.firstWhere(
        (e) => e.toString() == json['category'],
      ),
      metadata: json['metadata'],
      errorCode: json['errorCode'],
      stackTrace: json['stackTrace'],
      errorType: json['errorType'],
      errorContext: json['errorContext'],
    );
  }

  // Factory method for creating error entries
  factory AppHistoryEntry.error({
    required String title,
    required String description,
    required String errorCode,
    String? stackTrace,
    String? errorType,
    Map<String, dynamic>? errorContext,
    Map<String, dynamic>? metadata,
  }) {
    return AppHistoryEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      description: description,
      timestamp: DateTime.now(),
      category: HistoryCategory.error,
      errorCode: errorCode,
      stackTrace: stackTrace,
      errorType: errorType,
      errorContext: errorContext,
      metadata: metadata,
    );
  }

  // Factory method for creating mission-related entries
  factory AppHistoryEntry.mission({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) {
    return AppHistoryEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      description: description,
      timestamp: DateTime.now(),
      category: HistoryCategory.mission,
      metadata: metadata,
    );
  }

  // Factory method for creating system-related entries
  factory AppHistoryEntry.system({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) {
    return AppHistoryEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      description: description,
      timestamp: DateTime.now(),
      category: HistoryCategory.system,
      metadata: metadata,
    );
  }

  // Factory method for creating security-related entries
  factory AppHistoryEntry.security({
    required String title,
    required String description,
    Map<String, dynamic>? metadata,
  }) {
    return AppHistoryEntry(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      title: title,
      description: description,
      timestamp: DateTime.now(),
      category: HistoryCategory.security,
      metadata: metadata,
    );
  }
}
