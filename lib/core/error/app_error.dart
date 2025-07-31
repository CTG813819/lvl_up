class AppError implements Exception {
  final String message;
  final String? code;
  final dynamic originalError;
  final StackTrace? stackTrace;

  AppError(
    this.message,
    String s, {
    this.code,
    this.originalError,
    this.stackTrace,
  });

  @override
  String toString() {
    final buffer = StringBuffer('AppError: $message');
    if (code != null) {
      buffer.write(' (Code: $code)');
    }
    if (originalError != null) {
      buffer.write('\nOriginal Error: $originalError');
    }
    if (stackTrace != null) {
      buffer.write('\nStack Trace: $stackTrace');
    }
    return buffer.toString();
  }
}
