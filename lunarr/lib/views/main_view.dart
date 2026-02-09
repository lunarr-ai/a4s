import 'package:flutter/material.dart';
import 'package:lunarr/models/agent_card_model.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/agent_card_service.dart';
import 'package:lunarr/services/channel_service.dart';
import 'package:lunarr/services/user_service.dart';
import 'package:lunarr/views/agent_chat_view.dart';
import 'package:lunarr/views/channel_chat_view.dart';

class MainView extends StatefulWidget {
  const MainView({super.key});

  @override
  State<MainView> createState() => _MainViewState();
}

class _MainViewState extends State<MainView> {
  int _selectedIndex = 0;

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;
    final List<ChannelModel> channelModels = ChannelService().channelModels;
    final List<AgentCardModel> agentCardModels =
        AgentCardService().agentCardModels;
    final int channelCount = channelModels.length;

    return Scaffold(
      backgroundColor: Colors.white,
      body: Row(
        children: [
          _buildNavigationDrawer(
            cs,
            tt,
            channelModels,
            agentCardModels,
            channelCount,
          ),
          Expanded(
            child: _selectedIndex < channelCount
                ? ChannelChatView(key: ValueKey(_selectedIndex))
                : AgentChatView(
                    key: ValueKey(_selectedIndex - channelCount),
                    agentId: agentCardModels[_selectedIndex - channelCount].id,
                  ),
          ),
        ],
      ),
    );
  }

  Container _buildNavigationDrawer(
    ColorScheme cs,
    TextTheme tt,
    List<ChannelModel> channelModels,
    List<AgentCardModel> agentCardModels,
    int channelCount,
  ) {
    return Container(
      color: cs.surfaceContainerLow,
      padding: EdgeInsets.all(12),
      child: NavigationDrawer(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() {
            _selectedIndex = index;
          });
          if (index < channelCount) {
            ChannelService().fetchChannelModel(index);
          } else {
            AgentCardService().fetchAgentCardModel(index - channelCount);
          }
        },
        header: Row(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.asset('assets/images/logo.png', width: 32, height: 32),
                Text(
                  'Lunarr',
                  style: tt.titleLarge?.copyWith(
                    color: cs.onSurface,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ],
            ),
          ],
        ),
        footer: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Row(
              spacing: 12,
              children: [
                CircleAvatar(
                  radius: 16,
                  child: Text(UserService().username![0].toUpperCase()),
                ),
                Text(
                  UserService().username!,
                  style: tt.titleLarge?.copyWith(color: cs.onSurfaceVariant),
                ),
              ],
            ),
            IconButton(
              onPressed: () {},
              icon: Icon(Icons.settings_outlined, color: cs.onSurface),
            ),
          ],
        ),
        children: [
          SizedBox(
            height: 56,
            child: Padding(
              padding: const EdgeInsets.only(left: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Channels',
                    style: tt.titleSmall?.copyWith(color: cs.onSurfaceVariant),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(Icons.more_vert, color: cs.onSurface),
                  ),
                ],
              ),
            ),
          ),
          ...channelModels.map(
            (channelModel) => NavigationDrawerDestination(
              icon: channelModel.getIcon(12),
              label: Text(channelModel.labelString),
            ),
          ),
          SizedBox(
            height: 56,
            child: Padding(
              padding: const EdgeInsets.only(left: 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    'Agents',
                    style: tt.titleSmall?.copyWith(color: cs.onSurfaceVariant),
                  ),
                  IconButton(
                    onPressed: () {},
                    icon: Icon(Icons.more_vert, color: cs.onSurface),
                  ),
                ],
              ),
            ),
          ),
          ...agentCardModels.map(
            (agentCardModel) => NavigationDrawerDestination(
              icon: agentCardModel.getIcon(12),
              label: Text(agentCardModel.name),
            ),
          ),
        ],
      ),
    );
  }
}
