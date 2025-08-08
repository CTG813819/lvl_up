package com.example.lvl_up

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.Context
import android.graphics.BitmapFactory
import android.graphics.Color
import android.os.Build
import android.util.Log
import android.widget.RemoteViews
import androidx.core.app.NotificationCompat
import io.flutter.plugin.common.MethodChannel
import java.io.File

class DynamicIslandService(private val context: Context) {
    companion object {
        const val CHANNEL_ID = "dynamic_island_channel"
        const val NOTIFICATION_ID = 1001
        const val METHOD_CHANNEL_NAME = "dynamic_island_channel"
        const val TAG = "DynamicIslandService"
    }

    private val notificationManager: NotificationManager by lazy {
        context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
    }

    init {
        createNotificationChannel()
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Dynamic Island",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Dynamic Island notifications"
                setShowBadge(false)
                enableLights(false)
                enableVibration(false)
                setSound(null, null)
            }
            notificationManager.createNotificationChannel(channel)
        }
    }

    fun showDynamicIsland(
        aiName: String = "AI",
        iconRes: Int = R.drawable.ic_brain,
        iconColor: Int = Color.WHITE,
        progress: Double = 0.0,
        progressText: String? = null,
        backgroundImagePath: String? = null,
        progressBarColor: Int? = null,
        aiSubtitle: String? = null,
        albumArtPath: String? = null,
        autoHideDuration: Long = 5000,
        onDismiss: (() -> Unit)? = null
    ) {
        Log.d(TAG, "showDynamicIsland called with aiName=$aiName, progress=$progress, iconRes=$iconRes")
        try {
            val notification = createDynamicIslandNotification(
                aiName, iconRes, iconColor, progress, progressText, backgroundImagePath, progressBarColor, aiSubtitle, albumArtPath
            )
            Log.d(TAG, "Notification built successfully")
            notificationManager.notify(NOTIFICATION_ID, notification)
            if (autoHideDuration > 0) {
                android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
                    hideDynamicIsland()
                    onDismiss?.invoke()
                }, autoHideDuration)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error showing dynamic island notification", e)
        }
    }

    fun hideDynamicIsland() {
        notificationManager.cancel(NOTIFICATION_ID)
    }

    fun updateProgress(progress: Double, progressText: String? = null) {
        // For now, just update the notification with new progress
        showDynamicIsland(
            progress = progress,
            progressText = progressText
        )
    }

    private fun createDynamicIslandNotification(
        aiName: String,
        iconRes: Int,
        iconColor: Int,
        progress: Double,
        progressText: String?,
        backgroundImagePath: String?,
        progressBarColor: Int?,
        aiSubtitle: String?,
        albumArtPath: String?
    ): Notification {
        Log.d(TAG, "createDynamicIslandNotification: aiName=$aiName, iconRes=$iconRes, progress=$progress")
        val remoteViews = RemoteViews(context.packageName, R.layout.notification_ai_media)
        try {
            // Set AI name
            remoteViews.setTextViewText(R.id.ai_title, aiName)
            // Set subtitle
            remoteViews.setTextViewText(R.id.ai_subtitle, aiSubtitle ?: "Leveling Progress")
            // Set icon in chip
            remoteViews.setImageViewResource(R.id.ai_icon, iconRes)
            // Set progress
            val progressInt = (progress * 100).toInt().coerceIn(0, 100)
            remoteViews.setProgressBar(R.id.ai_progress, 100, progressInt, false)
            if (progressBarColor != null) {
                remoteViews.setInt(R.id.ai_progress, "setProgressTintList", progressBarColor)
            }
            remoteViews.setTextViewText(R.id.ai_progress_text, progressText ?: "$progressInt%")
            // Set album art as background
            val artPath = albumArtPath ?: backgroundImagePath
            if (!artPath.isNullOrEmpty()) {
                val file = File(artPath)
                if (file.exists()) {
                    val bitmap = BitmapFactory.decodeFile(file.absolutePath)
                    remoteViews.setImageViewBitmap(R.id.album_art, bitmap)
                    remoteViews.setViewVisibility(R.id.album_art, android.view.View.VISIBLE)
                } else {
                    remoteViews.setViewVisibility(R.id.album_art, android.view.View.GONE)
                }
            } else {
                remoteViews.setViewVisibility(R.id.album_art, android.view.View.GONE)
            }
            // Overlay is always visible for readability
            remoteViews.setViewVisibility(R.id.overlay, android.view.View.VISIBLE)
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up RemoteViews", e)
        }
        return NotificationCompat.Builder(context, CHANNEL_ID)
            .setSmallIcon(iconRes)
            .setCustomContentView(remoteViews)
            .setOngoing(true)
            .setAutoCancel(false)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_STATUS)
            .setVisibility(NotificationCompat.VISIBILITY_PUBLIC)
            .build()
    }

    private fun getIconResourceId(iconName: String): Int {
        return when (iconName.lowercase()) {
            "brain" -> R.drawable.ic_brain
            "star" -> R.drawable.ic_close
            "heart" -> R.drawable.ic_close
            "war" -> R.drawable.war_icon
            "notify" -> R.drawable.notification_icon
            "icon_bg" -> R.drawable.icon_background
            "island_bg" -> R.drawable.dynamic_island_background
            "progress_fill" -> R.drawable.progress_fill
            "progress_bg" -> R.drawable.progress_background
            "launcher_fg" -> R.drawable.ic_launcher_foreground
            "launch_bg" -> R.drawable.launch_background
            else -> R.drawable.ic_brain
        }
    }

    fun setupMethodChannel(flutterEngine: io.flutter.embedding.engine.FlutterEngine) {
        MethodChannel(flutterEngine.dartExecutor.binaryMessenger, METHOD_CHANNEL_NAME)
            .setMethodCallHandler { call, result ->
                when (call.method) {
                    "isSupported" -> {
                        result.success(true)
                    }
                    "showDynamicIsland" -> {
                        try {
                            val arguments = call.arguments as? Map<*, *>
                            if (arguments != null) {
                                val aiName = arguments["aiName"] as? String ?: "AI"
                                val iconName = arguments["iconName"] as? String ?: "brain"
                                val iconRes = getIconResourceId(iconName)
                                val iconColor = (arguments["iconColor"] as? Int) ?: Color.WHITE
                                val progress = (arguments["progress"] as? Double) ?: 0.0
                                val progressText = arguments["progressText"] as? String
                                val backgroundImagePath = arguments["backgroundImagePath"] as? String
                                val progressBarColor = arguments["progressBarColor"] as? Int
                                val aiSubtitle = arguments["aiSubtitle"] as? String
                                val albumArtPath = arguments["albumArtPath"] as? String
                                val autoHideDuration = (arguments["autoHideDuration"] as? Long) ?: 5000
                                showDynamicIsland(
                                    aiName = aiName,
                                    iconRes = iconRes,
                                    iconColor = iconColor,
                                    progress = progress,
                                    progressText = progressText,
                                    backgroundImagePath = backgroundImagePath,
                                    progressBarColor = progressBarColor,
                                    aiSubtitle = aiSubtitle,
                                    albumArtPath = albumArtPath,
                                    autoHideDuration = autoHideDuration
                                )
                                result.success(true)
                            } else {
                                result.error("INVALID_ARGUMENTS", "Arguments are required", null)
                            }
                        } catch (e: Exception) {
                            result.error("SHOW_ERROR", e.message, null)
                        }
                    }
                    "hideDynamicIsland" -> {
                        try {
                            hideDynamicIsland()
                            result.success(true)
                        } catch (e: Exception) {
                            result.error("HIDE_ERROR", e.message, null)
                        }
                    }
                    "updateProgress" -> {
                        try {
                            val arguments = call.arguments as? Map<*, *>
                            if (arguments != null) {
                                val progress = (arguments["progress"] as? Double) ?: 0.0
                                val progressText = arguments["progressText"] as? String
                                updateProgress(progress, progressText)
                                result.success(true)
                            } else {
                                result.error("INVALID_ARGUMENTS", "Progress argument is required", null)
                            }
                        } catch (e: Exception) {
                            result.error("UPDATE_ERROR", e.message, null)
                        }
                    }
                    else -> {
                        result.notImplemented()
                    }
                }
            }
    }
} 