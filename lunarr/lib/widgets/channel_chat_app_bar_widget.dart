import 'package:flutter/material.dart';
import 'package:lunarr/models/channel_model.dart';
import 'package:lunarr/services/channel_service.dart';

class ChannelChatAppBarWidget extends StatelessWidget {
  const ChannelChatAppBarWidget({super.key});

  @override
  Widget build(BuildContext context) {
    ColorScheme cs = Theme.of(context).colorScheme;
    TextTheme tt = Theme.of(context).textTheme;
    final ChannelModel channelModel = ChannelService().channelModel!;

    return Padding(
      padding: const EdgeInsets.fromLTRB(16, 8, 12, 8),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            spacing: 12,
            children: [
              channelModel.getIcon(16),
              Text(
                channelModel.labelString,
                style: tt.titleLarge?.copyWith(color: cs.onSurface),
              ),
            ],
          ),
          Row(
            children: [
              TextButton.icon(
                icon: Icon(Icons.person),
                onPressed: () {},
                label: Text('${channelModel.agentsCount}'),
              ),
              IconButton(onPressed: () {}, icon: Icon(Icons.more_vert)),
            ],
          ),
        ],
      ),
    );
  }
}
