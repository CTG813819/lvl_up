package com.example.lvl_up

import io.flutter.embedding.android.FlutterActivity
import io.flutter.embedding.engine.FlutterEngine

class MainActivity: FlutterActivity() {
    
    private lateinit var dynamicIslandService: DynamicIslandService
    
    override fun configureFlutterEngine(flutterEngine: FlutterEngine) {
        super.configureFlutterEngine(flutterEngine)
        
        // Initialize Dynamic Island service
        dynamicIslandService = DynamicIslandService(this)
        
        // Set up method channel
        dynamicIslandService.setupMethodChannel(flutterEngine)
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Clean up any ongoing notifications
        dynamicIslandService.hideDynamicIsland()
    }
}