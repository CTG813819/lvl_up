# Dynamic Island Implementation

This implementation provides a custom Dynamic Island notification system for Android that integrates with Flutter via platform channels. It creates a pill-shaped notification with gradient backgrounds, animated icons, and progress bars.

## Features

- **Pill-shaped Design**: Custom XML layout with rounded corners and gradient backgrounds
- **Platform Channel Integration**: Seamless communication between Flutter and Android
- **Progress Animations**: Animated progress bars with smooth transitions
- **Multiple Icon Support**: Various animated icons for different notification types
- **Auto-hide Functionality**: Configurable auto-hide duration
- **Customizable Themes**: Multiple predefined design themes
- **Real-time Updates**: Live progress updates via platform channel

## Architecture

### Android Components

1. **DynamicIslandService.kt**: Main service handling notification display
2. **MainActivity.kt**: Platform channel setup and integration
3. **dynamic_island_notification.xml**: Custom notification layout
4. **Drawable Resources**: Background gradients, icons, and progress bars
5. **Color Resources**: Theme colors and styling

### Flutter Components

1. **DynamicIslandPlatformService**: Platform channel communication
2. **DynamicIslandProvider**: State management and notification creation
3. **DynamicIslandTestWidget**: Demo widget for testing functionality

## File Structure

```
android/app/src/main/
├── kotlin/com/example/lvl_up/
│   ├── MainActivity.kt
│   └── DynamicIslandService.kt
├── res/
│   ├── layout/
│   │   └── dynamic_island_notification.xml
│   ├── drawable/
│   │   ├── dynamic_island_background.xml
│   │   ├── icon_background.xml
│   │   ├── progress_background.xml
│   │   ├── progress_fill.xml
│   │   ├── ic_brain.xml
│   │   └── ic_close.xml
│   └── values/
│       └── colors.xml

lib/
├── services/
│   └── dynamic_island_platform_service.dart
├── providers/
│   └── dynamic_island_provider.dart
└── widgets/
    └── dynamic_island_test_widget.dart
```

## Usage

### Basic Implementation

```dart
// Create a notification
final notification = DynamicIslandProvider().createProgressNotification(
  title: 'AI Processing',
  body: 'Processing your request...',
  aiSource: 'Guardian AI',
  progress: 0.75,
  progressText: '75% complete',
);

// Show the notification
DynamicIslandProvider().showDynamicIsland(notification);
```

### Platform Channel Usage

```dart
// Show Dynamic Island notification
await DynamicIslandPlatformService.showDynamicIsland(
  title: 'Level Up! 🎉',
  description: 'Chaos AI reached level 5!',
  progress: 1.0,
  progressText: 'Level 5 achieved!',
  iconName: 'crown',
  autoHideDuration: Duration(seconds: 8),
);

// Hide notification
await DynamicIslandPlatformService.hideDynamicIsland();

// Update progress
await DynamicIslandPlatformService.updateProgress(
  progress: 0.5,
  progressText: '50% complete',
);
```

### Notification Types

1. **Progress Notifications**: Show progress bars with percentages
2. **Level Up Notifications**: Celebratory notifications with crown icons
3. **Conquest Notifications**: Building progress with rocket icons
4. **Learning Notifications**: AI learning activities with brain icons

## Customization

### Adding New Icons

1. Create a new vector drawable in `android/app/src/main/res/drawable/`
2. Add the icon mapping in `DynamicIslandService.kt`:

```kotlin
private fun getIconResourceId(iconName: String): Int {
    return when (iconName.lowercase()) {
        "your_icon" -> R.drawable.your_icon
        // ... existing mappings
    }
}
```

### Adding New Themes

1. Add color definitions in `android/app/src/main/res/values/colors.xml`
2. Create new background drawables in `android/app/src/main/res/drawable/`
3. Update the layout to use the new colors

### Customizing Animations

The progress bar animations are handled in `DynamicIslandService.kt`. You can modify the animation duration and easing by updating the progress bar implementation.

## Testing

Use the `DynamicIslandTestWidget` to test all functionality:

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => const DynamicIslandTestWidget(),
  ),
);
```

## Permissions

The following permissions are required in `AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.POST_NOTIFICATIONS"/>
<uses-permission android:name="android.permission.VIBRATE"/>
```

## Platform Support

- **Android**: Full support with custom notification layout
- **iOS**: Falls back to standard notifications (no Dynamic Island support)
- **Web**: Falls back to browser notifications
- **Desktop**: Falls back to system notifications

## Performance Considerations

1. **Memory Management**: Notifications are automatically cleaned up when hidden
2. **Battery Optimization**: Uses efficient notification channels
3. **Smooth Animations**: Hardware-accelerated progress bar animations
4. **Platform Detection**: Graceful fallback for unsupported platforms

## Troubleshooting

### Common Issues

1. **Notification not showing**: Check notification permissions
2. **Platform channel errors**: Verify method channel name matches
3. **Layout issues**: Ensure all drawable resources are properly defined
4. **Icon not displaying**: Verify icon resource mapping in service

### Debug Steps

1. Check Android logs for notification errors
2. Verify platform channel communication
3. Test with different notification types
4. Validate XML layout syntax

## Future Enhancements

1. **iOS Dynamic Island**: Native iOS Dynamic Island support
2. **Custom Animations**: More sophisticated animation types
3. **Interactive Elements**: Touch gestures and interactions
4. **Multiple Islands**: Support for multiple concurrent notifications
5. **Themes**: User-customizable themes and colors
6. **Accessibility**: Enhanced accessibility features

## Contributing

When adding new features:

1. Update both Android and Flutter components
2. Add comprehensive tests
3. Update documentation
4. Follow existing code patterns
5. Test on multiple Android versions

## License

This implementation is part of the LVL_UP project and follows the project's licensing terms. 