import 'package:flutter/material.dart';

enum DynamicIslandType {
  progress,
  achievement,
  warning,
  error,
  info,
  levelUp,
  conquest,
  learning,
  proposal,
  system,
}

enum ProgressAnimationType {
  linear,
  circular,
  wave,
  pulse,
  bounce,
  shimmer,
  spin,
  shake,
  pop,
  flip,
  custom,
}

class DynamicIslandDesign {
  final Color backgroundColor;
  final Color progressBarColor;
  final Color textColor;
  final Color iconColor;
  final double borderRadius;
  final double elevation;
  final bool showShadow;
  final bool showGradient;
  final List<Color>? gradientColors;
  final String? backgroundImage;
  final double opacity;
  final String? userImagePath; // New: user-selected image file path
  final List<int>? userImageBytes; // New: user-selected image bytes (optional)

  DynamicIslandDesign({
    this.backgroundColor = const Color(0xFF1E1E1E),
    this.progressBarColor = Colors.blue,
    this.textColor = Colors.white,
    this.iconColor = Colors.white,
    this.borderRadius = 20.0,
    this.elevation = 8.0,
    this.showShadow = true,
    this.showGradient = false,
    this.gradientColors,
    this.backgroundImage,
    this.opacity = 0.95,
    this.userImagePath,
    this.userImageBytes,
  });

  DynamicIslandDesign copyWith({
    Color? backgroundColor,
    Color? progressBarColor,
    Color? textColor,
    Color? iconColor,
    double? borderRadius,
    double? elevation,
    bool? showShadow,
    bool? showGradient,
    List<Color>? gradientColors,
    String? backgroundImage,
    double? opacity,
    String? userImagePath,
    List<int>? userImageBytes,
  }) {
    return DynamicIslandDesign(
      backgroundColor: backgroundColor ?? this.backgroundColor,
      progressBarColor: progressBarColor ?? this.progressBarColor,
      textColor: textColor ?? this.textColor,
      iconColor: iconColor ?? this.iconColor,
      borderRadius: borderRadius ?? this.borderRadius,
      elevation: elevation ?? this.elevation,
      showShadow: showShadow ?? this.showShadow,
      showGradient: showGradient ?? this.showGradient,
      gradientColors: gradientColors ?? this.gradientColors,
      backgroundImage: backgroundImage ?? this.backgroundImage,
      opacity: opacity ?? this.opacity,
      userImagePath: userImagePath ?? this.userImagePath,
      userImageBytes: userImageBytes ?? this.userImageBytes,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'backgroundColor': backgroundColor.value,
      'progressBarColor': progressBarColor.value,
      'textColor': textColor.value,
      'iconColor': iconColor.value,
      'borderRadius': borderRadius,
      'elevation': elevation,
      'showShadow': showShadow,
      'showGradient': showGradient,
      'gradientColors': gradientColors?.map((c) => c.value).toList(),
      'backgroundImage': backgroundImage,
      'opacity': opacity,
      'userImagePath': userImagePath,
      'userImageBytes': userImageBytes,
    };
  }

  factory DynamicIslandDesign.fromJson(Map<String, dynamic> json) {
    return DynamicIslandDesign(
      backgroundColor: Color(json['backgroundColor'] ?? 0xFF1E1E1E),
      progressBarColor: Color(json['progressBarColor'] ?? 0xFF2196F3),
      textColor: Color(json['textColor'] ?? 0xFFFFFFFF),
      iconColor: Color(json['iconColor'] ?? 0xFFFFFFFF),
      borderRadius: json['borderRadius']?.toDouble() ?? 20.0,
      elevation: json['elevation']?.toDouble() ?? 8.0,
      showShadow: json['showShadow'] ?? true,
      showGradient: json['showGradient'] ?? false,
      gradientColors:
          json['gradientColors']?.map<Color>((c) => Color(c)).toList(),
      backgroundImage: json['backgroundImage'],
      opacity: json['opacity']?.toDouble() ?? 0.95,
      userImagePath: json['userImagePath'],
      userImageBytes:
          json['userImageBytes'] != null
              ? List<int>.from(json['userImageBytes'])
              : null,
    );
  }
}

class DynamicIslandIcon {
  final IconData icon;
  final ProgressAnimationType animationType;
  final Duration animationDuration;
  final Curve animationCurve;
  final bool isPulsing;
  final double pulseIntensity;
  final bool isSpinning; // New
  final bool isShaking; // New
  final bool isFlipping; // New
  final bool isPopping; // New
  final bool isCustom; // New
  final String? customAnimationName; // New

  DynamicIslandIcon({
    required this.icon,
    this.animationType = ProgressAnimationType.pulse,
    this.animationDuration = const Duration(milliseconds: 1000),
    this.animationCurve = Curves.easeInOut,
    this.isPulsing = false,
    this.pulseIntensity = 1.2,
    this.isSpinning = false,
    this.isShaking = false,
    this.isFlipping = false,
    this.isPopping = false,
    this.isCustom = false,
    this.customAnimationName,
  });

  DynamicIslandIcon copyWith({
    IconData? icon,
    ProgressAnimationType? animationType,
    Duration? animationDuration,
    Curve? animationCurve,
    bool? isPulsing,
    double? pulseIntensity,
    bool? isSpinning,
    bool? isShaking,
    bool? isFlipping,
    bool? isPopping,
    bool? isCustom,
    String? customAnimationName,
  }) {
    return DynamicIslandIcon(
      icon: icon ?? this.icon,
      animationType: animationType ?? this.animationType,
      animationDuration: animationDuration ?? this.animationDuration,
      animationCurve: animationCurve ?? this.animationCurve,
      isPulsing: isPulsing ?? this.isPulsing,
      pulseIntensity: pulseIntensity ?? this.pulseIntensity,
      isSpinning: isSpinning ?? this.isSpinning,
      isShaking: isShaking ?? this.isShaking,
      isFlipping: isFlipping ?? this.isFlipping,
      isPopping: isPopping ?? this.isPopping,
      isCustom: isCustom ?? this.isCustom,
      customAnimationName: customAnimationName ?? this.customAnimationName,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'icon': icon.codePoint,
      'animationType': animationType.name,
      'animationDuration': animationDuration.inMilliseconds,
      'animationCurve': animationCurve.toString(),
      'isPulsing': isPulsing,
      'pulseIntensity': pulseIntensity,
      'isSpinning': isSpinning,
      'isShaking': isShaking,
      'isFlipping': isFlipping,
      'isPopping': isPopping,
      'isCustom': isCustom,
      'customAnimationName': customAnimationName,
    };
  }

  factory DynamicIslandIcon.fromJson(Map<String, dynamic> json) {
    return DynamicIslandIcon(
      icon: IconData(json['icon'], fontFamily: 'MaterialIcons'),
      animationType: ProgressAnimationType.values.firstWhere(
        (e) => e.name == json['animationType'],
        orElse: () => ProgressAnimationType.pulse,
      ),
      animationDuration: Duration(
        milliseconds: json['animationDuration'] ?? 1000,
      ),
      animationCurve: Curves.easeInOut, // Default curve
      isPulsing: json['isPulsing'] ?? false,
      pulseIntensity: json['pulseIntensity']?.toDouble() ?? 1.2,
      isSpinning: json['isSpinning'] ?? false,
      isShaking: json['isShaking'] ?? false,
      isFlipping: json['isFlipping'] ?? false,
      isPopping: json['isPopping'] ?? false,
      isCustom: json['isCustom'] ?? false,
      customAnimationName: json['customAnimationName'],
    );
  }
}

/// AI Island Profile - Individual AI configuration
class AIIslandProfile {
  final String aiId;
  final String aiName;
  final String currentLevel;
  final double currentProgress;
  final double experienceToNextLevel;
  final DynamicIslandDesign design;
  final DynamicIslandIcon icon;
  final bool isActive;
  final DateTime lastActivity;
  final Map<String, dynamic> metadata;

  AIIslandProfile({
    required this.aiId,
    required this.aiName,
    required this.currentLevel,
    required this.currentProgress,
    required this.experienceToNextLevel,
    required this.design,
    required this.icon,
    this.isActive = true,
    required this.lastActivity,
    this.metadata = const {},
  });

  AIIslandProfile copyWith({
    String? aiId,
    String? aiName,
    String? currentLevel,
    double? currentProgress,
    double? experienceToNextLevel,
    DynamicIslandDesign? design,
    DynamicIslandIcon? icon,
    bool? isActive,
    DateTime? lastActivity,
    Map<String, dynamic>? metadata,
  }) {
    return AIIslandProfile(
      aiId: aiId ?? this.aiId,
      aiName: aiName ?? this.aiName,
      currentLevel: currentLevel ?? this.currentLevel,
      currentProgress: currentProgress ?? this.currentProgress,
      experienceToNextLevel:
          experienceToNextLevel ?? this.experienceToNextLevel,
      design: design ?? this.design,
      icon: icon ?? this.icon,
      isActive: isActive ?? this.isActive,
      lastActivity: lastActivity ?? this.lastActivity,
      metadata: metadata ?? this.metadata,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'aiId': aiId,
      'aiName': aiName,
      'currentLevel': currentLevel,
      'currentProgress': currentProgress,
      'experienceToNextLevel': experienceToNextLevel,
      'design': design.toJson(),
      'icon': icon.toJson(),
      'isActive': isActive,
      'lastActivity': lastActivity.toIso8601String(),
      'metadata': metadata,
    };
  }

  factory AIIslandProfile.fromJson(Map<String, dynamic> json) {
    return AIIslandProfile(
      aiId: json['aiId'],
      aiName: json['aiName'],
      currentLevel: json['currentLevel'],
      currentProgress: json['currentProgress']?.toDouble() ?? 0.0,
      experienceToNextLevel: json['experienceToNextLevel']?.toDouble() ?? 100.0,
      design: DynamicIslandDesign.fromJson(json['design']),
      icon: DynamicIslandIcon.fromJson(json['icon']),
      isActive: json['isActive'] ?? true,
      lastActivity: DateTime.parse(json['lastActivity']),
      metadata: json['metadata'] ?? {},
    );
  }

  /// Calculate progress percentage
  double get progressPercentage => currentProgress / experienceToNextLevel;

  /// Check if AI is ready to level up
  bool get isReadyToLevelUp => currentProgress >= experienceToNextLevel;

  /// Get level as integer
  int get levelAsInt => int.tryParse(currentLevel) ?? 1;

  /// Get next level
  String get nextLevel => (levelAsInt + 1).toString();
}

class AINotification {
  final String id;
  final String title;
  final String body;
  final String aiSource;
  final IconData icon;
  final Color iconColor;
  final DateTime timestamp;
  bool isRead;

  /// Dynamic Island specific properties
  final DynamicIslandType type;
  final double? progress;
  final String? progressText;
  final DynamicIslandDesign? design;
  final DynamicIslandIcon? animatedIcon;
  final bool showDynamicIsland;
  final Duration? autoHideDuration;
  final bool isPersistent;
  final Map<String, dynamic>? metadata;

  /// AI Island specific properties
  final String? aiId;
  final AIIslandProfile? aiProfile;
  final bool isAILevelUp;

  /// Media notification specific properties
  final Map<String, bool>?
  mediaControls; // e.g., {'play': true, 'pause': true, 'next': false}
  final String? albumArtPath;

  AINotification({
    required this.id,
    required this.title,
    required this.body,
    required this.aiSource,
    required this.icon,
    required this.iconColor,
    required this.timestamp,
    this.isRead = false,
    this.type = DynamicIslandType.info,
    this.progress,
    this.progressText,
    this.design,
    this.animatedIcon,
    this.showDynamicIsland = false,
    this.autoHideDuration,
    this.isPersistent = false,
    this.metadata,
    this.aiId,
    this.aiProfile,
    this.isAILevelUp = false,
    this.mediaControls,
    this.albumArtPath,
  });

  AINotification copyWith({
    String? id,
    String? title,
    String? body,
    String? aiSource,
    IconData? icon,
    Color? iconColor,
    DateTime? timestamp,
    bool? isRead,
    DynamicIslandType? type,
    double? progress,
    String? progressText,
    DynamicIslandDesign? design,
    DynamicIslandIcon? animatedIcon,
    bool? showDynamicIsland,
    Duration? autoHideDuration,
    bool? isPersistent,
    Map<String, dynamic>? metadata,
    String? aiId,
    AIIslandProfile? aiProfile,
    bool? isAILevelUp,
    Map<String, bool>? mediaControls,
    String? albumArtPath,
  }) {
    return AINotification(
      id: id ?? this.id,
      title: title ?? this.title,
      body: body ?? this.body,
      aiSource: aiSource ?? this.aiSource,
      icon: icon ?? this.icon,
      iconColor: iconColor ?? this.iconColor,
      timestamp: timestamp ?? this.timestamp,
      isRead: isRead ?? this.isRead,
      type: type ?? this.type,
      progress: progress ?? this.progress,
      progressText: progressText ?? this.progressText,
      design: design ?? this.design,
      animatedIcon: animatedIcon ?? this.animatedIcon,
      showDynamicIsland: showDynamicIsland ?? this.showDynamicIsland,
      autoHideDuration: autoHideDuration ?? this.autoHideDuration,
      isPersistent: isPersistent ?? this.isPersistent,
      metadata: metadata ?? this.metadata,
      aiId: aiId ?? this.aiId,
      aiProfile: aiProfile ?? this.aiProfile,
      isAILevelUp: isAILevelUp ?? this.isAILevelUp,
      mediaControls: mediaControls ?? this.mediaControls,
      albumArtPath: albumArtPath ?? this.albumArtPath,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'title': title,
      'body': body,
      'aiSource': aiSource,
      'icon': icon.codePoint,
      'iconColor': iconColor.value,
      'timestamp': timestamp.toIso8601String(),
      'isRead': isRead,
      'type': type.name,
      'progress': progress,
      'progressText': progressText,
      'design': design?.toJson(),
      'animatedIcon': animatedIcon?.toJson(),
      'showDynamicIsland': showDynamicIsland,
      'autoHideDuration': autoHideDuration?.inMilliseconds,
      'isPersistent': isPersistent,
      'metadata': metadata,
      'aiId': aiId,
      'aiProfile': aiProfile?.toJson(),
      'isAILevelUp': isAILevelUp,
      'mediaControls': mediaControls,
      'albumArtPath': albumArtPath,
    };
  }

  factory AINotification.fromJson(Map<String, dynamic> json) {
    return AINotification(
      id: json['id'],
      title: json['title'],
      body: json['body'],
      aiSource: json['aiSource'],
      icon: Icons.notifications, // fallback, icon not serialized
      iconColor: Colors.grey, // fallback, color not serialized
      timestamp: DateTime.parse(json['timestamp']),
      isRead: json['isRead'] ?? false,
      /// You can add more fields if needed
    );
  }
}
