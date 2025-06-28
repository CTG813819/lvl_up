import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:the_codex/mission.dart';
import 'entries/entry_pin_screen.dart';
import 'package:provider/provider.dart';
import '../providers/notification_provider.dart';
import '../widgets/notification_bell.dart';
import '../providers/proposal_provider.dart';
import '../providers/chaos_warp_provider.dart';
import '../widgets/ai_learning_dashboard.dart';
import 'codex_screen.dart';

class SideMenu extends StatelessWidget {
  final BuildContext parentContext;
  const SideMenu({Key? key, required this.parentContext}) : super(key: key);

  void _navigateToEntries(BuildContext context) {
    Navigator.of(parentContext).push(
      MaterialPageRoute(
        builder: (context) => EntryPinScreen(
          title: 'View Entries',
          isViewing: true,
          onPinEntered: (pin, context) {
            Navigator.of(parentContext).pushReplacementNamed('/entries');
          },
        ),
      ),
    );
  }

  void _navigateToMechanicumAnalytics() {
    Navigator.of(parentContext, rootNavigator: true).pushNamed('/mechanicum_analytics');
  }

  void _showTheCodex(BuildContext context) {
    Navigator.pop(context); // Close the drawer
    Navigator.of(parentContext).push(
      MaterialPageRoute(builder: (context) => const CodexScreen()),
    );
  }

  void _activateChaos(BuildContext context, ChaosWarpProvider provider) async {
    try {
      await provider.activateChaos();
      
      // Show success notification
      ScaffoldMessenger.of(parentContext).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.warning, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  'CHAOS MODE ACTIVATED! AI operations will run until 9 PM tomorrow.',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
            ],
          ),
          backgroundColor: Colors.purple,
          duration: Duration(seconds: 5),
          behavior: SnackBarBehavior.floating,
        ),
      );

      // Show notification provider
      final notificationProvider = Provider.of<NotificationProvider>(parentContext, listen: false);
      notificationProvider.addNotification(
        'CHAOS MODE ACTIVATED',
        'AI operations are now running outside normal hours until 9 PM tomorrow.',
        'chaos',
        DateTime.now(),
      );

    } catch (e) {
      // Show error notification
      ScaffoldMessenger.of(parentContext).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.error, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(
                child: Text('Failed to activate Chaos mode: ${e.toString()}'),
              ),
            ],
          ),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 3),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  void _activateWarp(BuildContext context, ChaosWarpProvider provider) async {
    try {
      if (provider.warpMode) {
        // Deactivate Warp mode
        await provider.deactivateWarp();
        
        ScaffoldMessenger.of(parentContext).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'WARP MODE DEACTIVATED. AI operations can resume.',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.green,
            duration: Duration(seconds: 3),
            behavior: SnackBarBehavior.floating,
          ),
        );

        // Show notification provider
        final notificationProvider = Provider.of<NotificationProvider>(parentContext, listen: false);
        notificationProvider.addNotification(
          'WARP MODE DEACTIVATED',
          'AI operations can now resume normally.',
          'warp',
          DateTime.now(),
        );
      } else {
        // Activate Warp mode
        await provider.activateWarp();
        
        ScaffoldMessenger.of(parentContext).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                Icon(Icons.block, color: Colors.white),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'WARP MODE ACTIVATED! All AI operations stopped. Only Chaos can restart them.',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
            backgroundColor: Colors.red,
            duration: Duration(seconds: 5),
            behavior: SnackBarBehavior.floating,
          ),
        );

        // Show notification provider
        final notificationProvider = Provider.of<NotificationProvider>(parentContext, listen: false);
        notificationProvider.addNotification(
          'WARP MODE ACTIVATED',
          'All AI operations have been stopped. Only Chaos mode can restart them.',
          'warp',
          DateTime.now(),
        );
      }
    } catch (e) {
      // Show error notification
      ScaffoldMessenger.of(parentContext).showSnackBar(
        SnackBar(
          content: Row(
            children: [
              Icon(Icons.error, color: Colors.white),
              const SizedBox(width: 8),
              Expanded(
                child: Text('Failed to toggle Warp mode: ${e.toString()}'),
              ),
            ],
          ),
          backgroundColor: Colors.red,
          duration: Duration(seconds: 3),
          behavior: SnackBarBehavior.floating,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: [_buildHeader(), _buildMenuItems(context)],
      ),
    );
  }

  Widget _buildHeader() {
    return DrawerHeader(
      decoration: const BoxDecoration(color: Colors.black),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Level Up',
            style: TextStyle(
              color: Colors.white,
              fontSize: 24,
              fontWeight: FontWeight.bold,
            ),
          ),
          SizedBox(height: 8),
          Text(
            'Track your progress',
            style: TextStyle(
              color: Colors.white.withOpacity(0.8),
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItems(BuildContext context) {
    return Column(
      children: [
        // Chaos and Warp Control Buttons
        Container(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Consumer<ChaosWarpProvider>(
                builder: (context, chaosWarpProvider, child) {
                  return Column(
                    children: [
                      // Chaos Button
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          icon: Icon(
                            chaosWarpProvider.chaosMode ? Icons.pause : Icons.play_arrow,
                            color: Colors.white,
                          ),
                          label: Text(
                            chaosWarpProvider.chaosMode 
                                ? 'CHAOS ACTIVE (${chaosWarpProvider.chaosRemainingTimeFormatted})'
                                : 'CHAOS',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.purple,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          onPressed: chaosWarpProvider.isLoading || chaosWarpProvider.warpMode
                              ? null
                              : () => _activateChaos(context, chaosWarpProvider),
                        ),
                      ),
                      const SizedBox(height: 8),
                      // Warp Button
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton.icon(
                          icon: Icon(
                            chaosWarpProvider.warpMode ? Icons.stop : Icons.block,
                            color: Colors.white,
                          ),
                          label: Text(
                            chaosWarpProvider.warpMode ? 'WARP ACTIVE' : 'WARP',
                            style: TextStyle(
                              color: Colors.white,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.red,
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          onPressed: chaosWarpProvider.isLoading
                              ? null
                              : () => _activateWarp(context, chaosWarpProvider),
                        ),
                      ),
                      if (chaosWarpProvider.isLoading) ...[
                        const SizedBox(height: 8),
                        SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            valueColor: AlwaysStoppedAnimation<Color>(Colors.grey[600]!),
                          ),
                        ),
                      ],
                    ],
                  );
                },
              ),
            ],
          ),
        ),
        const Divider(),
        _buildMenuItem(
          icon: Icons.flag,
          title: 'Missions',
          onTap: () => Navigator.pushNamed(parentContext, '/mission'),
        ),
        _buildMenuItem(
          icon: Icons.analytics,
          title: 'Summary',
          onTap: () => Navigator.pushNamed(parentContext, '/summary'),
        ),
        _buildMenuItem(
          icon: Icons.gavel,
          title: 'Judgement',
          onTap: () => Navigator.pushNamed(parentContext, '/tally'),
        ),
        _buildMenuItem(
          icon: Icons.book,
          title: 'Entries',
          onTap: () => _navigateToEntries(context),
        ),
        _buildMenuItem(
          icon: Icons.psychology,
          title: 'Masteries',
          onTap: () => Navigator.pushNamed(parentContext, '/mastery'),
        ),
        _buildMenuItem(
          icon: Icons.book,
          title: 'The Codex',
          onTap: () => _showTheCodex(context),
        ),
        Consumer<ProposalProvider>(
          builder: (context, provider, _) {
            final pendingCount = provider.pendingProposals.length;
            return ListTile(
              leading: Stack(
                clipBehavior: Clip.none,
                children: [
                  const Icon(Icons.rule),
                  if (pendingCount > 0)
                    Positioned(
                      right: -8,
                      top: -4,
                      child: Container(
                        padding: const EdgeInsets.all(2),
                        decoration: BoxDecoration(
                          color: Colors.amber,
                          borderRadius: BorderRadius.circular(10),
                        ),
                        constraints: const BoxConstraints(
                          minWidth: 18,
                          minHeight: 18,
                        ),
                        child: Text(
                          '$pendingCount',
                          style: const TextStyle(
                            color: Colors.black,
                            fontSize: 12,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                ],
              ),
              title: const Text('Imperium Proposals'),
              onTap: () {
                Navigator.pop(parentContext);
                Navigator.pushNamed(parentContext, '/proposal_approval');
              },
            );
          },
        ),
        Consumer<MissionProvider>(
          builder: (context, provider, _) {
            return ListTile(
              leading: Icon(
                Icons.shield,
                color: (provider.isSandboxWorking ?? false) ? Colors.redAccent : null,
              ),
              title: const Text('Mechanicum Analytics'),
              onTap: () {
                Navigator.pop(parentContext);
                _navigateToMechanicumAnalytics();
              },
            );
          },
        ),
      ],
    );
  }

  Widget _buildMenuItem({
    required IconData icon,
    required String title,
    required VoidCallback onTap,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title),
      onTap: () {
        Navigator.pop(parentContext); // Close drawer
        onTap();
      },
    );
  }
}
