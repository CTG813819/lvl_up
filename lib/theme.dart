import 'package:flutter/material.dart';
import 'utils/dynamic_colors.dart';

class AppTheme {
  static final ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    scaffoldBackgroundColor: Colors.black,
    primaryColor: Colors.yellow[700],
    colorScheme: ColorScheme.dark(
      primary: Colors.yellow[700]!,
      secondary: Colors.yellow[800]!,
      background: Colors.black,
      surface: Colors.grey[900]!,
      onPrimary: Colors.black,
      onSecondary: Colors.black,
      onBackground: Colors.white,
      onSurface: Colors.white,
    ),
    textTheme: TextTheme(
      displayLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      displayMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      displaySmall: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      headlineLarge: TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      headlineMedium: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      headlineSmall: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      titleLarge: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      titleMedium: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      titleSmall: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        color: DynamicColors.getSecondaryTextColor(Colors.black),
      ),
      labelLarge: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      labelMedium: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getContrastingTextColor(Colors.black),
      ),
      labelSmall: TextStyle(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getTertiaryTextColor(Colors.black),
      ),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.black,
      foregroundColor: DynamicColors.getContrastingTextColor(Colors.black),
      iconTheme: IconThemeData(
        color: DynamicColors.getContrastingIconColor(Colors.black),
      ),
      titleTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.black),
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
      elevation: 0,
      centerTitle: true,
    ),
    cardTheme: CardThemeData(
      color: Colors.grey[900],
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.yellow[700],
        foregroundColor: DynamicColors.getContrastingTextColor(
          Colors.yellow[700]!,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    ),
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      backgroundColor: Colors.yellow[700],
      foregroundColor: DynamicColors.getContrastingTextColor(
        Colors.yellow[700]!,
      ),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: Colors.black,
      selectedItemColor: Colors.yellow[700],
      unselectedItemColor: Colors.grey,
    ),
    listTileTheme: ListTileThemeData(
      textColor: DynamicColors.getContrastingTextColor(Colors.grey[900]!),
      iconColor: DynamicColors.getContrastingIconColor(Colors.grey[900]!),
      titleTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.grey[900]!),
        fontSize: 16,
        fontWeight: FontWeight.w500,
      ),
      subtitleTextStyle: TextStyle(
        color: DynamicColors.getSecondaryTextColor(Colors.grey[900]!),
        fontSize: 14,
      ),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: Colors.grey[900],
      titleTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.grey[900]!),
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
      contentTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.grey[900]!),
        fontSize: 16,
      ),
    ),
    dividerTheme: DividerThemeData(
      color: DynamicColors.getDividerColor(Colors.black),
    ),
  );

  static final ThemeData lightTheme = ThemeData(
    brightness: Brightness.light,
    scaffoldBackgroundColor: Colors.white,
    primaryColor: Colors.blue[700],
    colorScheme: ColorScheme.light(
      primary: Colors.blue[700]!,
      secondary: Colors.blue[600]!,
      background: Colors.white,
      surface: Colors.grey[50]!,
      onPrimary: Colors.white,
      onSecondary: Colors.white,
      onBackground: Colors.black87,
      onSurface: Colors.black87,
    ),
    textTheme: TextTheme(
      displayLarge: TextStyle(
        fontSize: 32,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      displayMedium: TextStyle(
        fontSize: 28,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      displaySmall: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      headlineLarge: TextStyle(
        fontSize: 22,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      headlineMedium: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      headlineSmall: TextStyle(
        fontSize: 18,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      titleLarge: TextStyle(
        fontSize: 24,
        fontWeight: FontWeight.bold,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      titleMedium: TextStyle(
        fontSize: 20,
        fontWeight: FontWeight.w600,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      titleSmall: TextStyle(
        fontSize: 16,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      bodyLarge: TextStyle(
        fontSize: 16,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      bodyMedium: TextStyle(
        fontSize: 14,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      bodySmall: TextStyle(
        fontSize: 12,
        color: DynamicColors.getSecondaryTextColor(Colors.white),
      ),
      labelLarge: TextStyle(
        fontSize: 14,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      labelMedium: TextStyle(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getContrastingTextColor(Colors.white),
      ),
      labelSmall: TextStyle(
        fontSize: 10,
        fontWeight: FontWeight.w500,
        color: DynamicColors.getTertiaryTextColor(Colors.white),
      ),
    ),
    appBarTheme: AppBarTheme(
      backgroundColor: Colors.white,
      foregroundColor: DynamicColors.getContrastingTextColor(Colors.white),
      iconTheme: IconThemeData(
        color: DynamicColors.getContrastingIconColor(Colors.white),
      ),
      titleTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.white),
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
      elevation: 2,
      centerTitle: true,
    ),
    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
    ),
    elevatedButtonTheme: ElevatedButtonThemeData(
      style: ElevatedButton.styleFrom(
        backgroundColor: Colors.blue[700],
        foregroundColor: DynamicColors.getContrastingTextColor(
          Colors.blue[700]!,
        ),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
      ),
    ),
    floatingActionButtonTheme: FloatingActionButtonThemeData(
      backgroundColor: Colors.blue[700],
      foregroundColor: DynamicColors.getContrastingTextColor(Colors.blue[700]!),
    ),
    bottomNavigationBarTheme: BottomNavigationBarThemeData(
      backgroundColor: Colors.white,
      selectedItemColor: Colors.blue[700],
      unselectedItemColor: Colors.grey,
    ),
    listTileTheme: ListTileThemeData(
      textColor: DynamicColors.getContrastingTextColor(Colors.white),
      iconColor: DynamicColors.getContrastingIconColor(Colors.white),
      titleTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.white),
        fontSize: 16,
        fontWeight: FontWeight.w500,
      ),
      subtitleTextStyle: TextStyle(
        color: DynamicColors.getSecondaryTextColor(Colors.white),
        fontSize: 14,
      ),
    ),
    dialogTheme: DialogThemeData(
      backgroundColor: Colors.white,
      titleTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.white),
        fontSize: 20,
        fontWeight: FontWeight.bold,
      ),
      contentTextStyle: TextStyle(
        color: DynamicColors.getContrastingTextColor(Colors.white),
        fontSize: 16,
      ),
    ),
    dividerTheme: DividerThemeData(
      color: DynamicColors.getDividerColor(Colors.white),
    ),
  );
}
