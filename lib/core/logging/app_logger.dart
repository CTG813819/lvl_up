import 'dart:developer' as developer;

class AppLogger {
  static void info(String message) {
    developer.log(message, name: 'AppLogger', level: 800);
  }

  static void warning(String message) {
    developer.log(message, name: 'AppLogger', level: 900);
  }

  static void error(String message, [dynamic error, StackTrace? stackTrace]) {
    developer.log(
      message,
      name: 'AppLogger',
      error: error,
      stackTrace: stackTrace,
      level: 1000,
    );
  }

  static void debug(String message) {
    developer.log(message, name: 'AppLogger', level: 700);
  }
}
